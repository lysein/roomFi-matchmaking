from fastapi import APIRouter, HTTPException
from src.api.db.schemas.inputs.property import PropertyCreate
from src.api.db.schemas.outputs.property import PropertyOut
from src.api.config import client
from src.api.services.juno import create_clabe_for_user
from datetime import datetime

router = APIRouter()

@router.post("/new/property")
async def create_property(payload: PropertyCreate):
    # Optional: check if similar property already exists (same address + owner)
    existing = client.table("properties") \
        .select("id") \
        .eq("owner_user_id", str(payload.owner_user_id)) \
        .eq("address", payload.address) \
        .execute()

    if existing.data:
        raise HTTPException(status_code=400, detail="Property already exists for this owner at this address")

    # Create CLABE for this property (optional)
    try:
        clabe = await create_clabe_for_user()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to create CLABE: {e}")

    # Insert property with latitude and longitude
    result = client.table("properties").insert({
        "owner_user_id": str(payload.owner_user_id),
        "address": payload.address,
        "location": payload.location,
        "price": payload.price,
        "amenities": payload.amenities,
        "num_rooms": payload.num_rooms,
        "bathrooms": payload.bathrooms,
        "available_from": payload.available_from.isoformat(),
        "available_to": payload.available_to.isoformat(),
        "created_at": payload.created_at.isoformat() if payload.created_at else datetime.utcnow().isoformat(),
        "updated_at": payload.updated_at.isoformat() if payload.updated_at else datetime.utcnow().isoformat(),
        "latitude": payload.latitude,
        "longitude": payload.longitude,
        "clabe": clabe
    }).execute()

    return {
        "message": "Property created",
        "property_id": result.data[0]["id"],
        "clabe": clabe
    }

@router.get("/get/property", response_model=PropertyOut)
def get_property(property_id: str):
    # Fetch property by ID
    response = client.table("properties").select("*").eq("id", property_id).single().execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="Property not found")

    return response.data
