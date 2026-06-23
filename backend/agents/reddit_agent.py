"""
Reddit Agent
------------
Logs into Reddit and subscribes to subreddits matching the user's interests
(trading, business, coding, AI, etc.)
"""

import asyncio
from typing import AsyncGenerator
from config.settings import settings


# Curated default subreddits by category
DEFAULT_SUBREDDITS = {
    "trading": ["algotrading", "stocks", "investing", "Daytrading", "options", "wallstreetbets", "StockMarket"],
    "business": ["Entrepreneur", "smallbusiness", "startups", "business", "marketing", "SideProject"],
    "coding": ["programming", "learnprogramming", "Python", "webdev", "MachineLearning", "artificial", "LocalLLaMA"],
    "finance": ["personalfinance", "financialindependence", "Fire", "CryptoCurrency", "Bitcoin"],
    "ai": ["MachineLearning", "artificial", "LocalLLaMA", "ChatGPT", "singularity", "AIAssistants"]
}


async def run_reddit_agent(task: dict) -> AsyncGenerator[str, None]:
    try:
        from browser_use import Agent
        from langchain_anthropic import ChatAnthropic
        from langchain_openai import ChatOpenAI
    except ImportError:
        yield "❌ browser-use not installed. Run: pip install browser-use langchain-anthropic"
        return

    targets = task.get("targets", ["programming", "trading", "business"])
    count = task.get("count", 8)

    # Build smart subreddit list from targets
    subreddit_pool = []
    for target in targets:
        for key, subs in DEFAULT_SUBREDDITS.items():
            if key in target.lower() or target.lower() in key:
                subreddit_pool.extend(subs)

    if not subreddit_pool:
        subreddit_pool = targets  # Use targets directly as subreddit names

    # Deduplicate and limit
    subreddit_pool = list(dict.fromkeys(subreddit_pool))[:max(count, len(subreddit_pool))]

    subreddit_list = ", ".join([f"r/{s}" for s in subreddit_pool[:count]])

    yield "🌐 Launching browser for Reddit..."
    yield f"📋 Target subreddits: {subreddit_list}"
    await asyncio.sleep(0.3)

    browser_task = f"""
    You are controlling a browser to subscribe to subreddits on Reddit.

    Step 1: Go to https://www.reddit.com/login
    Step 2: Enter username="{settings.reddit_username}" and password="{settings.reddit_password}"
    Step 3: Click Log In and wait for the home feed
    Step 4: For each of these subreddits, subscribe to them:
            {subreddit_list}

    For each subreddit:
    a) Go to https://www.reddit.com/r/SUBREDDIT_NAME
    b) Click the "Join" or "Subscribe" button (it may be orange)
    c) Wait 1 second
    d) Move to the next subreddit

    Step 5: Return a list of all subreddits successfully subscribed

    Important:
    - If a subreddit is NSFW, skip it
    - If already subscribed, note it and move on
    - If a subreddit doesn't exist, skip and continue
    """

    try:
        if settings.llm_provider == "anthropic" and settings.anthropic_api_key:
            llm = ChatAnthropic(
                model="claude-sonnet-4-6",
                api_key=settings.anthropic_api_key,
                temperature=0
            )
        else:
            llm = ChatOpenAI(
                model="gpt-4o",
                api_key=settings.openai_api_key,
                temperature=0
            )

        agent = Agent(task=browser_task, llm=llm)

        yield "🤖 Browser agent started!"
        result = await agent.run()

        yield "✅ Reddit task complete!"
        yield f"📊 Subscribed to: {subreddit_list}"
        yield f"🔎 Agent result: {str(result)[:200]}"

    except Exception as e:
        yield f"❌ Error during Reddit automation: {str(e)}"
        yield "💡 Make sure REDDIT_USERNAME and REDDIT_PASSWORD are set in .env"
