from fastapi import APIRouter, HTTPException
from src.api.config import client
from src.api.db.schemas.inputs.landlord import LandlordProfileCreate
from src.api.db.schemas.outputs.landlord import LandlordProfileOut
from datetime import datetime
from src.api.services.juno import create_clabe_for_user  # ✅ Reuse service

router = APIRouter()

@router.post("/new/landlord")
async def create_landlord_profile(payload: LandlordProfileCreate):
    # Check if landlord profile already exists
    existing = client.table("landlord_profile").select("user_id").eq("user_id", str(payload.user_id)).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Landlord profile already exists")

    # Create CLABE from JUNO service
    try:
        clabe = await create_clabe_for_user()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to create CLABE: {e}")

    # Insert new landlord profile with first_name, last_name, clabe
    result = client.table("landlord_profile").insert({
        "user_id": str(payload.user_id),
        "first_name": payload.first_name,
        "last_name": payload.last_name,
        "phone_number": payload.phone_number,
        "verified": payload.verified,
        "bio": payload.bio,
        "profile_image_url": payload.profile_image_url,
        "joined_at": payload.joined_at.isoformat() if payload.joined_at else datetime.utcnow().isoformat(),
        "preferred_locations": payload.preferred_locations,
        "clabe": clabe
    }).execute()

    return {
        "message": "Landlord profile created",
        "user_id": payload.user_id,
        "clabe": clabe
    }

@router.get("/get/landlord", response_model=LandlordProfileOut)
def get_landlord_profile(user_id: str):
    # Fetch landlord profile
    response = client.table("landlord_profile").select("*").eq("user_id", user_id).single().execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Landlord profile not found")
    return response.data

@router.get("/get/landlord/properties")
def get_landlord_properties(user_id: str):
    # Fetch properties owned by the landlord
    response = client.table("properties").select("*").eq("owner_user_id", user_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="No properties found for this landlord")
    return response.data
