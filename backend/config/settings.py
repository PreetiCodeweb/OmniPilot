from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    # LLM
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    llm_provider: str = os.getenv("LLM_PROVIDER", "anthropic")
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Platforms
    twitter_username: str = os.getenv("TWITTER_USERNAME", "")
    twitter_password: str = os.getenv("TWITTER_PASSWORD", "")

    linkedin_email: str = os.getenv("LINKEDIN_EMAIL", "")
    linkedin_password: str = os.getenv("LINKEDIN_PASSWORD", "")

    reddit_username: str = os.getenv("REDDIT_USERNAME", "")
    reddit_password: str = os.getenv("REDDIT_PASSWORD", "")

    whatsapp_session_dir: str = os.getenv("WHATSAPP_SESSION_DIR", "./sessions/whatsapp")

    # Server
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", 8000))
    cors_origin: str = os.getenv("CORS_ORIGIN", "http://localhost:5173")
    reload: bool = os.getenv("RELOAD", "false").lower() == "true"

    # Browser
    browser_headless: bool = os.getenv("BROWSER_HEADLESS", "false").lower() == "true"
    browser_slow_mo: int = int(os.getenv("BROWSER_SLOW_MO", 500))

    @property
    def effective_llm_provider(self) -> str:
        if self.llm_provider == "anthropic" and self.anthropic_api_key:
            return "anthropic"
        if self.openai_api_key:
            return "openai"
        return "local"

    @property
    def effective_llm_model(self) -> str:
        if self.effective_llm_provider == "anthropic":
            return self.anthropic_model
        if self.effective_llm_provider == "openai":
            return self.openai_model
        return "rule-parser"

settings = Settings()
