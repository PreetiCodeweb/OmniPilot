"""
Agent Router
------------
Receives a parsed task dict from the LLM service and dispatches it
to the correct platform agent. Streams log messages back.
"""

from typing import AsyncGenerator
from agents.twitter_agent import run_twitter_agent
from agents.linkedin_agent import run_linkedin_agent
from agents.reddit_agent import run_reddit_agent
from agents.whatsapp_agent import run_whatsapp_agent


async def route_task(task: dict) -> AsyncGenerator[str, None]:
    platform = task.get("platform", "unknown").lower()
    action = task.get("action", "")

    if action == "clarify":
        yield task.get("reply", "Could you clarify what you'd like me to do?")
        return

    yield f"🧠 Platform detected: {platform.upper()}"
    yield f"⚙️  Action: {action}"
    await _sleep(0.2)

    if platform == "twitter":
        async for msg in run_twitter_agent(task):
            yield msg

    elif platform == "linkedin":
        async for msg in run_linkedin_agent(task):
            yield msg

    elif platform == "reddit":
        async for msg in run_reddit_agent(task):
            yield msg

    elif platform == "whatsapp":
        async for msg in run_whatsapp_agent(task):
            yield msg

    else:
        yield f"❓ Unknown platform: '{platform}'. I support Twitter, LinkedIn, Reddit, and WhatsApp."


async def _sleep(seconds: float):
    import asyncio
    await asyncio.sleep(seconds)
