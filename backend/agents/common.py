from __future__ import annotations

import asyncio
import importlib.util
from typing import AsyncGenerator, Iterable

from config.settings import settings


PLATFORM_REQUIREMENTS = {
    "twitter": ("twitter_username", "twitter_password"),
    "linkedin": ("linkedin_email", "linkedin_password"),
    "reddit": ("reddit_username", "reddit_password"),
    "whatsapp": (),
}


def platform_ready(platform: str) -> tuple[bool, list[str]]:
    missing = [
        name.upper()
        for name in PLATFORM_REQUIREMENTS.get(platform, ())
        if not getattr(settings, name, "")
    ]
    return len(missing) == 0, missing


def llm_ready() -> bool:
    return bool(settings.anthropic_api_key or settings.openai_api_key)


def optional_dependency_status() -> dict[str, bool]:
    packages = {
        "browser_use": "browser_use",
        "playwright": "playwright",
        "langchain_anthropic": "langchain_anthropic",
        "langchain_openai": "langchain_openai",
    }
    return {name: importlib.util.find_spec(module) is not None for name, module in packages.items()}


def get_capabilities() -> dict:
    deps = optional_dependency_status()
    platforms = {}
    for platform in ("twitter", "linkedin", "reddit", "whatsapp"):
        ready, missing = platform_ready(platform)
        platforms[platform] = {
            "ready": ready,
            "missing": missing,
            "requiresCredentials": list(PLATFORM_REQUIREMENTS[platform]),
        }

    browser_ready = deps["browser_use"] and deps["playwright"]
    agent_llm_ready = llm_ready() and (deps["langchain_anthropic"] or deps["langchain_openai"])

    return {
        "llm": {
            "ready": llm_ready(),
            "provider": settings.effective_llm_provider,
            "model": settings.effective_llm_model,
        },
        "browser": {
            "ready": browser_ready,
            "headless": settings.browser_headless,
            "slowMo": settings.browser_slow_mo,
        },
        "agentLlm": {"ready": agent_llm_ready},
        "dependencies": deps,
        "platforms": platforms,
    }


def validate_agent_preflight(platform: str) -> list[str]:
    issues: list[str] = []
    capabilities = get_capabilities()

    if not capabilities["browser"]["ready"]:
        issues.append("Install browser-use and Playwright, then run: python -m playwright install chromium")
    if not capabilities["agentLlm"]["ready"]:
        issues.append("Set ANTHROPIC_API_KEY or OPENAI_API_KEY and install langchain-anthropic/langchain-openai")

    ready, missing = platform_ready(platform)
    if not ready:
        issues.append(f"Missing {', '.join(missing)} in backend/.env")

    return issues


def clamp_count(value, default: int = 5, minimum: int = 1, maximum: int = 20) -> int:
    try:
        count = int(value)
    except (TypeError, ValueError):
        count = default
    return max(minimum, min(maximum, count))


def compact_list(values: Iterable[str], default: list[str]) -> list[str]:
    cleaned = [str(value).strip() for value in values if str(value).strip()]
    return cleaned or default


async def run_simulation(task: dict, platform: str, action: str) -> AsyncGenerator[str, None]:
    targets = compact_list(task.get("targets", []), ["automation", "social", "growth"])
    count = clamp_count(task.get("count"), default=3)
    query = task.get("query", " ".join(targets))

    yield f"🧪 Safe simulation mode for {platform.title()}."
    yield f"⚙️ Planned action: {action.replace('_', ' ')}"
    yield f"🔎 Search/query: {query}"
    yield f"🎯 Target count: {count}"
    await asyncio.sleep(0.2)

    if platform == "whatsapp":
        recipient = task.get("recipient", "")
        message = task.get("message", "")
        yield f"📱 Would send to {recipient or 'the selected contact'}: {message or 'your message'}"
    else:
        yield f"📋 Would target {', '.join(targets[:count])}"

    yield "✅ Simulation completed. Configure credentials and browser tools to switch to live automation."


def build_agent_llm():
    try:
        from langchain_anthropic import ChatAnthropic
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise RuntimeError("Install langchain-anthropic and langchain-openai for browser agents") from exc

    if settings.effective_llm_provider == "anthropic" and settings.anthropic_api_key:
        llm = ChatAnthropic(
            model=settings.anthropic_model,
            api_key=settings.anthropic_api_key,
            temperature=0,
        )
        llm.provider = "anthropic"
        llm.model_name = getattr(llm, "model_name", settings.anthropic_model)
        return llm

    if settings.openai_api_key:
        llm = ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0,
        )
        llm.provider = "openai"
        llm.model_name = getattr(llm, "model_name", settings.openai_model)
        return llm

    raise RuntimeError("No LLM API key configured for browser agents")
