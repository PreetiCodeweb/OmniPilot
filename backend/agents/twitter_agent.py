"""
Twitter Agent
-------------
Uses browser-use to control a real Chromium browser and follow accounts on Twitter/X.
Logs in with your credentials, searches for target topics, and follows accounts.
"""

import asyncio
from typing import AsyncGenerator
from config.settings import settings
from agents.common import build_agent_llm, clamp_count, compact_list, run_simulation, validate_agent_preflight


async def run_twitter_agent(task: dict) -> AsyncGenerator[str, None]:
    """
    Stream log messages while executing a Twitter follow/search task.

    task keys:
        action  : "follow" | "search_and_follow"
        targets : list of search terms
        count   : how many accounts to follow
        query   : combined search string
    """
    try:
        from browser_use import Agent
    except ImportError:
        async for msg in run_simulation(task, "twitter", task.get("action", "search_and_follow")):
            yield msg
        return

    issues = validate_agent_preflight("twitter")
    if issues:
        yield "⚠️ Live automation prerequisites are incomplete. Switching to safe simulation mode."
        async for msg in run_simulation(task, "twitter", task.get("action", "search_and_follow")):
            yield msg
        return

    yield "🌐 Launching browser for Twitter..."
    await asyncio.sleep(0.3)

    targets = compact_list(task.get("targets", []), ["trading", "coding", "stocks"])
    count = clamp_count(task.get("count"), default=5)
    query = task.get("query", " ".join(targets))

    browser_task = f"""
    You are controlling a browser to follow accounts on Twitter/X.

    Step 1: Go to https://twitter.com/login
    Step 2: Log in with username="{settings.twitter_username}" and password="{settings.twitter_password}"
    Step 3: Wait for the home feed to load
    Step 4: Use the search bar to search for "{query}"
    Step 5: Click on "People" tab in the search results
    Step 6: Follow the first {count} accounts that appear in the results
    Step 7: For each account you follow, note their username
    Step 8: Return a summary of all accounts followed

    Important:
    - Click "Follow" button for each account (not "Following" — skip already followed)
    - Wait 2 seconds between each follow to avoid rate limiting
    - If a captcha appears, describe it and pause
    """

    yield f"🔍 Searching Twitter for: {query}"
    yield f"🎯 Will follow up to {count} accounts"
    await asyncio.sleep(0.3)

    try:
        agent = Agent(task=browser_task, llm=build_agent_llm())

        yield "🤖 Browser agent started — watch your browser window!"
        result = await agent.run()

        yield f"✅ Twitter task complete!"
        yield f"📊 Result: {str(result)[:300]}"

    except Exception as e:
        yield f"❌ Error during Twitter automation: {str(e)}"
        yield "💡 Make sure your TWITTER_USERNAME and TWITTER_PASSWORD are set in .env"
