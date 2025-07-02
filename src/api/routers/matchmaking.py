# src/api/routers/matchmaking.py

from fastapi import APIRouter, Query
from datetime import datetime
from typing import Optional
from src.api.config import settings
from supabase import create_client

router = APIRouter()

# Create Supabase client using settings
client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

@router.post("/match/top")
def match_top(user_id: str, top_k: Optional[int] = Query(5, ge=1, le=20)):
    user = client.table("user_profiles").select("*").eq("user_id", user_id).single().execute().data
    if not user:
        return {"error": "User not found"}

    budget_min = user["budget_min"]
    budget_max = user["budget_max"]
    location = user["location_preference"]
    lifestyle_tags = set(user.get("lifestyle_tags") or [])

    roommates = client.table("user_profiles") \
        .select("*") \
        .neq("user_id", user_id) \
        .eq("location_preference", location) \
        .gte("budget_max", budget_min) \
        .lte("budget_min", budget_max) \
        .execute().data

    properties = client.table("properties") \
        .select("*") \
        .eq("location", location) \
        .gte("price", budget_min) \
        .lte("price", budget_max) \
        .lte("available_from", datetime.utcnow().isoformat()) \
        .execute().data

    def roommate_score(rm):
        rm_tags = set(rm.get("lifestyle_tags") or [])
        tag_score = len(lifestyle_tags & rm_tags) / len(lifestyle_tags | rm_tags) if lifestyle_tags and rm_tags else 0
        rm_budget_avg = (rm["budget_min"] + rm["budget_max"]) / 2
        user_budget_avg = (budget_min + budget_max) / 2
        budget_score = 1 - abs(user_budget_avg - rm_budget_avg) / max(user_budget_avg, rm_budget_avg)
        return round(0.5 * budget_score + 0.5 * tag_score, 3)

    def property_score(prop):
        prop_amenities = set(prop.get("amenities") or [])
        amenity_score = len(lifestyle_tags & prop_amenities) / len(lifestyle_tags | prop_amenities) if lifestyle_tags and prop_amenities else 0
        price_score = 1 - abs(((budget_min + budget_max) / 2) - prop["price"]) / budget_max
        return round(0.7 * price_score + 0.3 * amenity_score, 3)

    top_roommates = sorted(roommates, key=roommate_score, reverse=True)[:top_k]
    top_properties = sorted(properties, key=property_score, reverse=True)[:top_k]

    return {
        "roommate_matches": [
            {"user_id": rm["user_id"], "score": roommate_score(rm)} for rm in top_roommates
        ],
        "property_matches": [
            {"property_id": prop["id"], "score": property_score(prop)} for prop in top_properties
        ]
    }
