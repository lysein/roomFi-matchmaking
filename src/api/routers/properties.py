from fastapi import APIRouter, HTTPException
from src.api.db.schemas.property import PropertyCreate
from src.api.config import client

router = APIRouter()

@router.post("/new/property")
def create_property(payload: PropertyCreate):
    # Optional: check if similar property already exists (e.g., same address + owner)
    existing = client.table("properties") \
        .select("id") \
        .eq("owner_user_id", str(payload.owner_user_id)) \
        .eq("address", payload.address) \
        .execute()

    if existing.data:
        raise HTTPException(status_code=400, detail="Property already exists for this owner at this address")

    # Insert into Supabase
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
        "created_at": payload.created_at.isoformat(),
        "updated_at": payload.updated_at.isoformat()
    }).execute()

    return {"message": "Property created", "property_id": result.data[0]["id"]}

@router.get("/get/property")
def get_property(property_id: str):
    # Fetch property by ID
    response = client.table("properties").select("*").eq("id", property_id).single().execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Property not found")

    return response.data