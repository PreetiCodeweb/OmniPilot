"""
LinkedIn Agent
--------------
Logs into LinkedIn, searches for people/companies in business/trading/coding,
and sends connection requests or follows pages.
"""

import asyncio
from typing import AsyncGenerator
from config.settings import settings
from agents.common import build_agent_llm, clamp_count, compact_list, run_simulation, validate_agent_preflight


async def run_linkedin_agent(task: dict) -> AsyncGenerator[str, None]:
    try:
        from browser_use import Agent
    except ImportError:
        async for msg in run_simulation(task, "linkedin", task.get("action", "search_and_follow")):
            yield msg
        return

    issues = validate_agent_preflight("linkedin")
    if issues:
        yield "⚠️ Live automation prerequisites are incomplete. Switching to safe simulation mode."
        async for msg in run_simulation(task, "linkedin", task.get("action", "search_and_follow")):
            yield msg
        return

    targets = compact_list(task.get("targets", []), ["business", "trading", "coding", "AI"])
    count = clamp_count(task.get("count"), default=5)
    query = task.get("query", " ".join(targets))

    yield "🌐 Launching browser for LinkedIn..."
    yield f"🔍 Will search for: {query}"
    yield f"🎯 Targeting {count} connections/follows"
    await asyncio.sleep(0.3)

    browser_task = f"""
    You are controlling a browser to follow people and companies on LinkedIn.

    Step 1: Go to https://www.linkedin.com/login
    Step 2: Enter email="{settings.linkedin_email}" and password="{settings.linkedin_password}"
    Step 3: Click Sign In and wait for the feed to load
    Step 4: Click the search bar at the top
    Step 5: Search for "{query}"
    Step 6: Filter results by "People" first
    Step 7: For each person in results (up to {count // 2}): click "Follow" or "Connect"
    Step 8: Go back and filter by "Companies"
    Step 9: For each company (up to {count // 2}): click "Follow"
    Step 10: Return a list of all profiles/companies followed or connected with

    Important:
    - Prefer "Follow" over "Connect" unless the user specifically asked for connections
    - Wait 3 seconds between each action
    - Skip promoted/sponsored results
    - If you see a "Connect" limit warning, stop and report it
    """

    try:
        agent = Agent(task=browser_task, llm=build_agent_llm())

        yield "🤖 Browser agent started — watch your browser!"
        result = await agent.run()

        yield "✅ LinkedIn task complete!"
        yield f"📊 Result: {str(result)[:300]}"

    except Exception as e:
        yield f"❌ Error during LinkedIn automation: {str(e)}"
        yield "💡 Make sure your LINKEDIN_EMAIL and LINKEDIN_PASSWORD are set in .env"
