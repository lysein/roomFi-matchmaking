from fastapi import APIRouter, Query, HTTPException
from datetime import datetime
from typing import Optional
from src.api.config import settings
from supabase import create_client, Client
import logging

router = APIRouter()
client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

@router.post("/match/top")
def match_top(user_id: str, top_k: Optional[int] = Query(5, ge=1, le=20)):
    try:
        # 1. Fetch user
        try:
            user_resp = client.table("user_profiles").select("*").eq("user_id", user_id).single().execute()
            user = user_resp.data
        except Exception as e:
            logging.error(f"Error fetching user profile: {e}")
            raise HTTPException(status_code=404, detail="User not found or Supabase error")

        if not user:
            raise HTTPException(status_code=404, detail="User profile is empty")

        budget_min = user.get("budget_min")
        budget_max = user.get("budget_max")
        location = user.get("location_preference")
        location = location.strip().upper()
        lifestyle_tags = set(user.get("lifestyle_tags") or [])

        if not all([budget_min, budget_max, location]):
            raise HTTPException(status_code=422, detail="User profile is missing required fields")

        # 2. Fetch roommate candidates
        try:
            roommates_resp = client.table("user_profiles") \
                .select("*") \
                .neq("user_id", user_id) \
                .eq("location_preference", location) \
                .gte("budget_max", budget_min) \
                .lte("budget_min", budget_max) \
                .execute()
            roommates = roommates_resp.data or []
        except Exception as e:
            logging.error(f"Error fetching roommates: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch roommates from Supabase")

        # 3. Fetch property candidates
        try:
            properties_resp = client.table("properties") \
                .select("*") \
                .eq("location", location) \
                .gte("price", budget_min) \
                .lte("price", budget_max) \
                .lte("available_from", datetime.utcnow().isoformat()) \
                .execute()
            properties = properties_resp.data or []
        except Exception as e:
            logging.error(f"Error fetching properties: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch properties from Supabase")

        # 4. Score functions
        def roommate_score(rm):
            rm_tags = set(rm.get("lifestyle_tags") or [])
            tag_score = len(lifestyle_tags & rm_tags) / len(lifestyle_tags | rm_tags) if lifestyle_tags and rm_tags else 0
            rm_budget_avg = (rm.get("budget_min", 0) + rm.get("budget_max", 0)) / 2
            user_budget_avg = (budget_min + budget_max) / 2
            budget_score = 1 - abs(user_budget_avg - rm_budget_avg) / max(user_budget_avg, rm_budget_avg) if rm_budget_avg else 0
            return round(0.5 * budget_score + 0.5 * tag_score, 3)

        def property_score(prop):
            amenities = set(prop.get("amenities") or [])
            amenity_score = len(lifestyle_tags & amenities) / len(lifestyle_tags | amenities) if lifestyle_tags and amenities else 0
            price_score = 1 - abs(((budget_min + budget_max) / 2) - prop.get("price", 0)) / budget_max
            return round(0.7 * price_score + 0.3 * amenity_score, 3)

        # 5. Sort and return
        top_roommates = sorted(roommates, key=roommate_score, reverse=True)[:min(top_k, len(roommates))]
        top_properties = sorted(properties, key=property_score, reverse=True)[:min(top_k, len(properties))]

        return {
            "roommate_matches": [
                {**rm, "score": roommate_score(rm)} for rm in top_roommates
            ],
            "property_matches": [
                {**prop, "score": property_score(prop)} for prop in top_properties
            ]
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logging.exception("Unhandled matchmaking error")
        raise HTTPException(status_code=500, detail="Internal server error during matchmaking")
