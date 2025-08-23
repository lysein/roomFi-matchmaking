from pydantic_settings import BaseSettings
from dotenv import load_dotenv, find_dotenv
import logging
logger = logging.getLogger(__name__)

# Automatically find and load the .env file
load_dotenv(find_dotenv())

class Settings(BaseSettings):
    DATABASE_URL: str
    SUPABASE_JWT_SECRET: str
    SUPABASE_ANON_KEY: str
    SUPABASE_URL: str
    JUNO_BASE_URL: str
    JUNO_API_KEY: str
    JUNO_API_SECRET: str
    CLOUDFLARE_ACCOUNT_ID: str
    CLOUDFLARE_API_TOKEN: str
    LLM_MODEL: str

settings = Settings()

logger.info("Configuration loaded successfully.")
logger.info(f"DATABASE_URL: {settings.DATABASE_URL}")
logger.info(f"SUPABASE_JWT_SECRET: {settings.SUPABASE_JWT_SECRET}")

from supabase import create_client, Client

SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_KEY = settings.SUPABASE_ANON_KEY
client = create_client(SUPABASE_URL, SUPABASE_KEY)
