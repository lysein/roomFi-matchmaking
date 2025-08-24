from fastapi import APIRouter, Query, HTTPException, Body
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from src.api.config import settings
from src.api.services.ai_service import ai_service
from supabase import create_client, Client
import logging

router = APIRouter()
client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)



class MatchmakingRequest(BaseModel):
    user_prompt: Optional[str] = None

@router.post("/match/top")
async def match_top(
    user_id: str,
    top_k: Optional[int] = Query(5, ge=1, le=20),
    ai_query: Optional[bool] = Query(False, description="Enable AI processing of user prompt"),
    body: Optional[MatchmakingRequest] = Body(None)
):
    try:
        # Validate AI query parameters
        user_prompt = body.user_prompt if (body and body.user_prompt) else None
        if ai_query:
            if not user_prompt:
                raise HTTPException(
                    status_code=422,
                    detail="user_prompt is required in the request body when ai_query=True"
                )
        
        # Initialize AI insights for response
        ai_insights = None
        
        # 1. Fetch user
        try:
            user_resp = client.table("user_profiles").select("*").eq("user_id", user_id).single().execute()
            user = user_resp.data
        except Exception as e:
            logging.error(f"Error fetching user profile: {e}")
            raise HTTPException(status_code=404, detail="User not found or Supabase error")

        if not user:
            raise HTTPException(status_code=404, detail="User profile is empty")

        # 2. Process AI query if enabled
        if ai_query and user_prompt:
            try:
                logging.info(f"Processing AI query for user {user_id}")
                ai_insights = await ai_service.process_user_prompt(user_prompt, user)
                
                # Handle AI processing results with enhanced fallback logic
                if ai_insights.get("processing_status") in ["success", "partial"]:
                    # AI succeeded - use updated preferences
                    extracted_preferences = ai_insights.get("extracted_preferences", {})
                    if extracted_preferences.get("updated"):
                        user.update(extracted_preferences["updated"])
                        logging.info(f"Updated user preferences with AI insights")
                
                elif ai_insights.get("processing_status") == "fallback_to_existing":
                    # AI failed but we have existing preferences - continue with original user data
                    logging.info(f"AI failed, falling back to existing preferences for user {user_id}")
                
                elif ai_insights.get("processing_status") == "insufficient_data":
                    # AI succeeded but data is still insufficient
                    raise HTTPException(
                        status_code=422,
                        detail={
                            "error": "Insufficient preferences for matching",
                            "message": "Could not extract enough information from your query to perform matching. Please provide more details about your budget, location, or lifestyle preferences.",
                            "ai_insights": ai_insights,
                            "suggestions": ai_insights.get("extracted_preferences", {}).get("ai_enhancements", {}).get("suggestions", [])
                        }
                    )
                
                elif ai_insights.get("processing_status") == "failed":
                    # AI failed and no existing preferences
                    if ai_insights.get("fallback_reason") and "no existing preferences" in ai_insights.get("fallback_reason", ""):
                        raise HTTPException(
                            status_code=422,
                            detail={
                                "error": "Unable to process request",
                                "message": "Could not extract preferences from your query and you don't have existing preferences saved. Please provide clear information about your budget range, preferred location, and any lifestyle preferences.",
                                "ai_insights": ai_insights,
                                "suggestions": [
                                    "Include budget range (e.g., '$1000-1500 per month')",
                                    "Specify location (e.g., 'in Brooklyn' or 'near downtown')",
                                    "Mention lifestyle preferences (e.g., 'gym', 'quiet', 'pet-friendly')"
                                ]
                            }
                        )
                    else:
                        # AI failed but we might have existing preferences - let it continue to validation
                        logging.warning(f"AI processing failed for user {user_id}, attempting to use existing preferences")
                
            except HTTPException:
                # Re-raise HTTP exceptions
                raise
            except Exception as e:
                logging.error(f"AI processing failed for user {user_id}: {e}")
                # Set failed status but continue with existing preferences if available
                ai_insights = {
                    "original_prompt": user_prompt,
                    "translated_prompt": None,
                    "extracted_preferences": None,
                    "processing_status": "failed",
                    "fallback_reason": f"Exception in AI processing: {str(e)}",
                    "error": str(e)
                }

        budget_min = user.get("budget_min")
        budget_max = user.get("budget_max")
        location = user.get("location_preference")
        if location:
            location = location.strip().upper()
        lifestyle_tags = set(user.get("lifestyle_tags") or [])

        if not all([budget_min, budget_max, location]):
            raise HTTPException(status_code=422, detail="User profile is missing required fields")

        # 3. Fetch roommate candidates
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

        # 4. Fetch property candidates
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

        # 5. Score functions
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

        # 6. Sort and return
        top_roommates = sorted(roommates, key=roommate_score, reverse=True)[:min(top_k, len(roommates))]
        top_properties = sorted(properties, key=property_score, reverse=True)[:min(top_k, len(properties))]

        # Prepare response
        response = {
            "roommate_matches": [
                {**rm, "score": roommate_score(rm)} for rm in top_roommates
            ],
            "property_matches": [
                {**prop, "score": property_score(prop)} for prop in top_properties
            ]
        }
        
        # Add AI insights if AI query was used
        if ai_query and ai_insights:
            response["ai_insights"] = ai_insights

        return response

    except HTTPException as e:
        raise e
    except Exception as e:
        logging.exception("Unhandled matchmaking error")
        raise HTTPException(status_code=500, detail="Internal server error during matchmaking")
