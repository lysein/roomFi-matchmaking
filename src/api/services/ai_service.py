import httpx
import json
import logging
from typing import Dict, Any, Optional, Tuple, List

from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate

from src.api.config import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# ------------------------------
# Pydantic models for structured output
# ------------------------------
class EnhancedPreferenceExtraction(BaseModel):
    budget_min: Optional[int] = Field(None, description="Minimum budget extracted or estimated")
    budget_max: Optional[int] = Field(None, description="Maximum budget extracted or estimated")
    location_preference: Optional[str] = Field(None, description="Location preference")
    lifestyle_tags: Optional[List[str]] = Field(None, description="Lifestyle preferences and amenities")
    confidence_scores: Optional[Dict[str, float]] = Field(None, description="Confidence level for each field (0-1)")
    estimated_fields: Optional[List[str]] = Field(None, description="Fields that were estimated vs explicitly mentioned")
    missing_critical_info: Optional[List[str]] = Field(None, description="Critical information still missing")
    suggestions: Optional[List[str]] = Field(None, description="Suggestions to improve search results")


# ------------------------------
# Cloudflare AI service
# ------------------------------
class CloudflareAIService:
    """
    Pipeline:
      1) translate_to_english (detect src lang; no-op if already English)
      2) extract_preferences (update or create)
      3) return slim ai_insights + explicit error/fallback info
      4) ensure suggestions/missing_critical_info are in the user's prompt language
    """

    def __init__(self) -> None:
        self.account_id: str = settings.CLOUDFLARE_ACCOUNT_ID
        self.api_token: str = settings.CLOUDFLARE_API_TOKEN
        self.llm_model: str = getattr(settings, "LLM_MODEL", "@cf/openai/gpt-oss-120b")
        self.translation_model: str = getattr(settings, "TRANSLATION_MODEL", self.llm_model)
        self.base_url: str = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run"

        # Structured parser to enforce JSON schema
        self.parser: PydanticOutputParser = PydanticOutputParser(
            pydantic_object=EnhancedPreferenceExtraction
        )

    # ---------- Internal helpers ----------
    async def _make_request(self, model: str, prompt: str) -> Optional[Dict[str, Any]]:
        """Make async request to Cloudflare AI API (expects {'input': <text>})."""
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        payload = {"input": prompt}
        url = f"{self.base_url}/{model}"

        logger.info(f"Cloudflare AI endpoint: {url}")
        logger.info(f"Cloudflare AI payload (truncated): {json.dumps(payload, ensure_ascii=False)[:1000]}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload, timeout=30.0)
                logger.info(f"Cloudflare AI response status: {response.status_code}")
                logger.info(f"Cloudflare AI response body (truncated): {response.text[:1000]}")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Cloudflare AI request failed: {e}")
            return None

    @staticmethod
    def _extract_text_from_cf(cf_json: Optional[Dict[str, Any]]) -> Optional[str]:
        """
        Extract generated text from Cloudflare Workers AI responses.

        Handles responses that include:
          - result.response (string)
          - result.text (string)
          - result.output: list of blocks, where each block has "content": [...]
              - Prefer content items with type == "output_text"
              - Fallback to any content item with a "text" string
          - result.message.content (list of items with "text")
          - cf_json["output_text"] (rare)
        """
        if not cf_json:
            return None

        result = cf_json.get("result") or {}

        # Simple shapes
        for key in ("response", "text"):
            val = result.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()

        # Typical shape: list of outputs with nested content
        outputs = result.get("output")
        if isinstance(outputs, list):
            # Pass 1: prefer explicit output_text chunks
            for out in outputs:
                content = out.get("content")
                if isinstance(content, list):
                    for c in content:
                        if isinstance(c, dict) and c.get("type") == "output_text":
                            t = c.get("text")
                            if isinstance(t, str) and t.strip():
                                return t.strip()
            # Pass 2: accept any content item with text
            for out in outputs:
                content = out.get("content")
                if isinstance(content, list):
                    for c in content:
                        t = c.get("text") if isinstance(c, dict) else None
                        if isinstance(t, str) and t.strip():
                            return t.strip()

        # Some models use message.content
        message = result.get("message")
        if isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, list):
                for c in content:
                    t = c.get("text") if isinstance(c, dict) else None
                    if isinstance(t, str) and t.strip():
                        return t.strip()

        # Very rare fallback
        t = cf_json.get("output_text")
        if isinstance(t, str) and t.strip():
            return t.strip()

        return None

    @staticmethod
    def _is_empty_profile(user: Optional[Dict[str, Any]]) -> bool:
        """Return True if no useful fields are present."""
        if not user:
            return True
        keys = ("budget_min", "budget_max", "location_preference", "lifestyle_tags")
        for k in keys:
            v = user.get(k)
            if v not in (None, "", [], {}):
                return False
        return True

    @staticmethod
    def _has_sufficient_preferences(prefs: Dict[str, Any]) -> bool:
        """
        Minimal heuristic to proceed with matching:
          - Have at least one budget bound (min or max)
          - AND either a location or at least one lifestyle tag
        """
        has_budget = prefs.get("budget_min") is not None or prefs.get("budget_max") is not None
        has_where = bool(prefs.get("location_preference")) or (
            isinstance(prefs.get("lifestyle_tags"), list) and len(prefs.get("lifestyle_tags") or []) > 0
        )
        return bool(has_budget and has_where)

    @staticmethod
    def _safe_load_json(text: str) -> Optional[Any]:
        try:
            return json.loads(text)
        except Exception:
            return None

    async def _translate_list_to_lang(self, items: List[str], target_lang: str) -> List[str]:
        """
        Translate a list of strings to the target language in one call.
        Returns the translated list or the original on failure.
        """
        if not items or not target_lang:
            return items

        src = json.dumps(items, ensure_ascii=False)
        prompt = (
            "Translate EACH item in the following JSON array into the target language.\n"
            f"Target language code or name: {target_lang}\n"
            "Return ONLY a JSON array of strings, same order, no extra commentary.\n\n"
            f"Array:\n{src}"
        )
        resp = await self._make_request(self.translation_model, prompt)
        out = self._extract_text_from_cf(resp)
        if not out:
            return items
        parsed = self._safe_load_json(out)
        if isinstance(parsed, list) and all(isinstance(x, str) for x in parsed):
            return parsed
        return items

    @staticmethod
    def _pluck_insights(preferences_result: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build the slim ai_insights with:
          - suggestions
          - missing_critical_info
          - profile_status
          - has_sufficient_for_matching
          - ai_enhancements.confidence_scores
          - ai_enhancements.estimated_fields
        Prefers the ai_enhancements block; falls back to the extracted block when needed.
        """
        insights = {
            "suggestions": [],
            "missing_critical_info": [],
            "profile_status": None,
            "has_sufficient_for_matching": None,
            "ai_enhancements": {
                "confidence_scores": {},
                "estimated_fields": [],
            },
        }

        if not isinstance(preferences_result, dict):
            return insights

        insights["profile_status"] = preferences_result.get("profile_status")
        insights["has_sufficient_for_matching"] = preferences_result.get("has_sufficient_for_matching")

        # Prefer ai_enhancements
        enh = preferences_result.get("ai_enhancements", {})
        if isinstance(enh, dict):
            if isinstance(enh.get("confidence_scores"), dict):
                insights["ai_enhancements"]["confidence_scores"] = enh["confidence_scores"]
            if isinstance(enh.get("estimated_fields"), list):
                insights["ai_enhancements"]["estimated_fields"] = [str(e) for e in enh["estimated_fields"]]
            if isinstance(enh.get("suggestions"), list):
                insights["suggestions"] = [str(s) for s in enh["suggestions"]]
            if isinstance(enh.get("missing_critical_info"), list):
                insights["missing_critical_info"] = [str(m) for m in enh["missing_critical_info"]]

        # Fallback to extracted
        extracted = preferences_result.get("extracted", {})
        if isinstance(extracted, dict):
            if not insights["suggestions"] and isinstance(extracted.get("suggestions"), list):
                insights["suggestions"] = [str(s) for s in extracted["suggestions"]]
            if not insights["missing_critical_info"] and isinstance(extracted.get("missing_critical_info"), list):
                insights["missing_critical_info"] = [str(m) for m in extracted["missing_critical_info"]]
            if not insights["ai_enhancements"]["confidence_scores"] and isinstance(extracted.get("confidence_scores"), dict):
                insights["ai_enhancements"]["confidence_scores"] = extracted["confidence_scores"]
            if not insights["ai_enhancements"]["estimated_fields"] and isinstance(extracted.get("estimated_fields"), list):
                insights["ai_enhancements"]["estimated_fields"] = [str(e) for e in extracted["estimated_fields"]]

        return insights

    @staticmethod
    def _derive_status(
        translation_ok: bool,
        extraction_success: bool,
        preferences_result: Optional[Dict[str, Any]],
    ) -> Tuple[str, Optional[str], Optional[str], Optional[str]]:
        """
        Return (status, fallback_mode, fallback_reason, error)
        """
        status = "failed"
        fallback_mode: Optional[str] = None
        fallback_reason: Optional[str] = None
        error: Optional[str] = None

        if isinstance(preferences_result, dict):
            # Pull any AI-layer error text
            enh = preferences_result.get("ai_enhancements")
            if isinstance(enh, dict):
                if isinstance(enh.get("error"), str) and enh["error"].strip():
                    error = enh["error"].strip()
                    fallback_reason = error

            has_sufficient = preferences_result.get("has_sufficient_for_matching")
            profile_status = preferences_result.get("profile_status")

            if extraction_success:
                if has_sufficient:
                    status = "success" if translation_ok else "partial"
                else:
                    status = "insufficient_data"
            else:
                if profile_status == "existing_preferences":
                    if has_sufficient:
                        status = "fallback_to_existing"
                        fallback_mode = "existing_preferences"
                        if not fallback_reason:
                            fallback_reason = "AI failed; using existing preferences"
                    else:
                        status = "insufficient_data"
                        if not fallback_reason:
                            fallback_reason = "AI failed and existing preferences insufficient"
                else:
                    status = "failed"
                    if not fallback_reason:
                        fallback_reason = "AI failed and no existing preferences available"

        return status, fallback_mode, fallback_reason, error

    # ---------- Public API ----------
    async def translate_to_english(self, text: str) -> Tuple[str, bool, Optional[str]]:
        """
        Detect language and translate to English if needed.
        Returns (translated_text, success_flag, source_language_code_or_name).
        """
        prompt = (
            "Detect the language of the INPUT and translate it to English only if needed. "
            "Respond ONLY as compact JSON with keys 'lang' and 'text', where 'lang' is the INPUT language "
            "(ISO 639-1 like 'en', 'es' preferred; if unsure, write a readable name), and 'text' is the English text "
            "or the original text if already English.\n"
            "Example: {\"lang\":\"es\",\"text\":\"hello\"}\n\n"
            f"INPUT:\n{text}"
        )
        response = await self._make_request(self.translation_model, prompt)
        out_text = self._extract_text_from_cf(response)
        if out_text:
            parsed = self._safe_load_json(out_text)
            if isinstance(parsed, dict) and isinstance(parsed.get("text"), str):
                lang = parsed.get("lang") if isinstance(parsed.get("lang"), str) else None
                return parsed["text"], True, lang
            # Fallback if model returned plain text
            return out_text, True, None

        logger.warning("Failed to translate/detect language, using original")
        return text, False, None

    async def extract_preferences(self, user_prompt: str, current_prefs: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
        """
        Extract or update housing preferences based on the user prompt.
        Returns (result_dict, success_flag).
        """
        has_existing_prefs = not self._is_empty_profile(current_prefs)
        profile_status = "existing_preferences" if has_existing_prefs else "empty_profile"
        format_instructions = self.parser.get_format_instructions()

        if has_existing_prefs:
            # Update existing preferences
            prompt_template = PromptTemplate(
                template="""You are an AI assistant that intelligently updates housing preferences based on user queries.

CURRENT USER PREFERENCES (from database):
- Budget: {budget_min} - {budget_max}
- Location: {location}
- Lifestyle tags: {lifestyle_tags}

TASK: Based on the user's new query below, determine what preferences should be UPDATED or ADDED.
- If user mentions new budget, OVERRIDE the existing budget
- If user mentions new location, OVERRIDE the existing location
- If user mentions new amenities/lifestyle, ADD to existing lifestyle tags (avoid duplicates)
- Provide confidence scores (0-1) for each field
- List which fields were estimated vs explicitly mentioned
- Suggest missing critical information

User query: {user_prompt}

{format_instructions}

Analyze the query and return the enhanced preferences:""",
                input_variables=["budget_min", "budget_max", "location", "lifestyle_tags", "user_prompt"],
                partial_variables={"format_instructions": format_instructions},
            )
            formatted_prompt = prompt_template.format(
                budget_min=current_prefs.get("budget_min", "not set"),
                budget_max=current_prefs.get("budget_max", "not set"),
                location=current_prefs.get("location_preference", "not set"),
                lifestyle_tags=current_prefs.get("lifestyle_tags", []),
                user_prompt=user_prompt,
            )
        else:
            # Extract from scratch
            prompt_template = PromptTemplate(
                template="""You are an AI assistant that extracts complete housing preferences from user queries and provides intelligent defaults for missing information.

USER PROFILE STATUS: Empty (no existing preferences in database)

TASK: Extract ALL housing preferences from the user query below. For missing critical information, provide reasonable estimates. Be explicit about what is estimated.

- Include: budget_min, budget_max, location_preference, lifestyle_tags
- Provide confidence_scores (0-1) per field
- Mark estimated_fields
- List missing_critical_info and provide helpful suggestions

User query: {user_prompt}

{format_instructions}

Extract complete preferences with intelligent gap filling:""",
                input_variables=["user_prompt"],
                partial_variables={"format_instructions": format_instructions},
            )
            formatted_prompt = prompt_template.format(user_prompt=user_prompt)

        # Call the model
        response = await self._make_request(self.llm_model, formatted_prompt)
        if not response:
            logger.warning("Failed to get response from AI")
            if has_existing_prefs:
                return {
                    "original": current_prefs,
                    "extracted": {},
                    "updated": current_prefs,
                    "profile_status": profile_status,
                    "has_sufficient_for_matching": self._has_sufficient_preferences(current_prefs),
                    "ai_enhancements": {"error": "AI service unavailable, using existing preferences"},
                }, False  # extraction_success = False
            else:
                return {
                    "original": current_prefs,
                    "extracted": {},
                    "updated": current_prefs,
                    "profile_status": profile_status,
                    "has_sufficient_for_matching": False,
                    "ai_enhancements": {"error": "AI service unavailable and no existing preferences available"},
                }, False

        ai_response = self._extract_text_from_cf(response)
        if not ai_response:
            logger.error("Could not extract AI response text from Cloudflare output")
            if has_existing_prefs:
                return {
                    "original": current_prefs,
                    "extracted": {},
                    "updated": current_prefs,
                    "profile_status": profile_status,
                    "has_sufficient_for_matching": self._has_sufficient_preferences(current_prefs),
                    "ai_enhancements": {"error": "Malformed AI response, using existing preferences"},
                }, False
            else:
                return {
                    "original": current_prefs,
                    "extracted": {},
                    "updated": current_prefs,
                    "profile_status": profile_status,
                    "has_sufficient_for_matching": False,
                    "ai_enhancements": {"error": "Malformed AI response and no existing preferences available"},
                }, False

        # Parse to schema
        try:
            extracted_result: EnhancedPreferenceExtraction = self.parser.parse(ai_response)
            extracted_dict: Dict[str, Any] = {k: v for k, v in extracted_result.dict().items() if v is not None}
        except Exception as parse_error:
            logger.error(f"LangChain parsing failed: {parse_error}")
            logger.error(f"AI response was: {ai_response}")
            if has_existing_prefs:
                return {
                    "original": current_prefs,
                    "extracted": {},
                    "updated": current_prefs,
                    "profile_status": profile_status,
                    "has_sufficient_for_matching": self._has_sufficient_preferences(current_prefs),
                    "ai_enhancements": {"error": "AI parsing failed, using existing preferences"},
                }, False
            else:
                return {
                    "original": current_prefs,
                    "extracted": {},
                    "updated": current_prefs,
                    "profile_status": profile_status,
                    "has_sufficient_for_matching": False,
                    "ai_enhancements": {"error": "AI parsing failed and no existing preferences available"},
                }, False

        # Merge intelligently with existing
        updated_prefs: Dict[str, Any] = dict(current_prefs) if has_existing_prefs else {}

        if "budget_min" in extracted_dict:
            try:
                updated_prefs["budget_min"] = int(extracted_dict["budget_min"]) if extracted_dict["budget_min"] is not None else None
            except Exception:
                updated_prefs["budget_min"] = extracted_dict["budget_min"]
        if "budget_max" in extracted_dict:
            try:
                updated_prefs["budget_max"] = int(extracted_dict["budget_max"]) if extracted_dict["budget_max"] is not None else None
            except Exception:
                updated_prefs["budget_max"] = extracted_dict["budget_max"]
        if "location_preference" in extracted_dict and extracted_dict["location_preference"]:
            updated_prefs["location_preference"] = str(extracted_dict["location_preference"]).strip()
        if "lifestyle_tags" in extracted_dict and extracted_dict["lifestyle_tags"]:
            existing_tags = set(updated_prefs.get("lifestyle_tags") or [])
            new_tags = set(extracted_dict["lifestyle_tags"] or [])
            merged_tags = sorted({str(t).strip() for t in (existing_tags | new_tags) if str(t).strip()})
            updated_prefs["lifestyle_tags"] = merged_tags

        result = {
            "original": current_prefs,
            "extracted": extracted_dict,
            "updated": updated_prefs,
            "profile_status": profile_status,
            "has_sufficient_for_matching": self._has_sufficient_preferences(updated_prefs),
            "ai_enhancements": {
                "confidence_scores": extracted_dict.get("confidence_scores", {}),
                "estimated_fields": extracted_dict.get("estimated_fields", []),
                "missing_critical_info": extracted_dict.get("missing_critical_info", []),
                "suggestions": extracted_dict.get("suggestions", []),
            },
        }
        return result, True

    async def process_user_prompt(self, prompt: str, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main pipeline. Returns ai_insights with:
          - suggestions (in user's language)
          - missing_critical_info (in user's language)
          - profile_status
          - has_sufficient_for_matching
          - ai_enhancements.confidence_scores
          - ai_enhancements.estimated_fields
          - status, fallback_mode, fallback_reason, error, translation_note
        """
        try:
            # 1) Translation (and language detection)
            translated_prompt, translation_ok, src_lang = await self.translate_to_english(prompt)
            translation_note = None if translation_ok else "Translation/Lang detection failed or skipped; using original text."
            source_language = (src_lang or "").lower().strip()

            # 2) Preference extraction
            preferences_result, extraction_success = await self.extract_preferences(translated_prompt, current_user)

            # 3) Slim insights
            ai_insights = self._pluck_insights(preferences_result)

            # 4) Status + fallback/error
            status, fallback_mode, fallback_reason, error = self._derive_status(
                translation_ok=translation_ok,
                extraction_success=extraction_success,
                preferences_result=preferences_result,
            )

            # 5) Ensure suggestions & missing_critical_info are in the user's prompt language
            # Only translate back if we know the source was not English and we have items to translate.
            backtranslated = False
            if source_language and not source_language.startswith("en"):
                to_fix_any = bool(ai_insights.get("suggestions") or ai_insights.get("missing_critical_info"))
                if to_fix_any:
                    if ai_insights.get("suggestions"):
                        ai_insights["suggestions"] = await self._translate_list_to_lang(ai_insights["suggestions"], source_language)
                        backtranslated = True
                    if ai_insights.get("missing_critical_info"):
                        ai_insights["missing_critical_info"] = await self._translate_list_to_lang(
                            ai_insights["missing_critical_info"], source_language
                        )
                        backtranslated = True

            if backtranslated:
                # Append note so you can observe when we post-process to match user language
                translation_note = (translation_note + " " if translation_note else "") + \
                                   f"Suggestions and missing_critical_info translated back to '{source_language}'."

            ai_insights.update(
                {
                    "status": status,
                    "fallback_mode": fallback_mode,
                    "fallback_reason": fallback_reason,
                    "error": error,
                    "translation_note": translation_note,
                }
            )
            return ai_insights

        except Exception as e:
            logger.error(f"Error in process_user_prompt: {e}")
            # On error, return minimal structure with error details
            return {
                "suggestions": [],
                "missing_critical_info": [],
                "profile_status": None,
                "has_sufficient_for_matching": None,
                "ai_enhancements": {
                    "confidence_scores": {},
                    "estimated_fields": [],
                },
                "status": "failed",
                "fallback_mode": None,
                "fallback_reason": "Unhandled exception in AI processing",
                "error": str(e),
                "translation_note": None,
            }


# Create global instance
ai_service = CloudflareAIService()
