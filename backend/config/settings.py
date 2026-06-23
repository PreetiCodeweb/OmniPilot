from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    # LLM
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    llm_provider: str = os.getenv("LLM_PROVIDER", "anthropic")

    # Platforms
    twitter_username: str = os.getenv("TWITTER_USERNAME", "")
    twitter_password: str = os.getenv("TWITTER_PASSWORD", "")

    linkedin_email: str = os.getenv("LINKEDIN_EMAIL", "")
    linkedin_password: str = os.getenv("LINKEDIN_PASSWORD", "")

    reddit_username: str = os.getenv("REDDIT_USERNAME", "")
    reddit_password: str = os.getenv("REDDIT_PASSWORD", "")

    whatsapp_session_dir: str = os.getenv("WHATSAPP_SESSION_DIR", "./sessions/whatsapp")

    # Server
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", 8000))
    cors_origin: str = os.getenv("CORS_ORIGIN", "http://localhost:5173")

    # Browser
    browser_headless: bool = os.getenv("BROWSER_HEADLESS", "false").lower() == "true"
    browser_slow_mo: int = int(os.getenv("BROWSER_SLOW_MO", 500))

settings = Settings()
