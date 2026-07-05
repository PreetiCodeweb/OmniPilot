"""
WhatsApp Agent
--------------
Opens WhatsApp Web in a browser, finds the contact by name, and sends a message.
No API key needed — uses your WhatsApp Web session (scan QR once, sessions persist).
"""

import asyncio
import os
from typing import AsyncGenerator
from config.settings import settings
from agents.common import build_agent_llm, run_simulation, validate_agent_preflight


async def run_whatsapp_agent(task: dict) -> AsyncGenerator[str, None]:
    try:
        from browser_use import Agent
    except ImportError:
        async for msg in run_simulation(task, "whatsapp", task.get("action", "send_message")):
            yield msg
        return

    issues = validate_agent_preflight("whatsapp")
    if issues:
        yield "⚠️ Live automation prerequisites are incomplete. Switching to safe simulation mode."
        async for msg in run_simulation(task, "whatsapp", task.get("action", "send_message")):
            yield msg
        return

    recipient = task.get("recipient", "")
    message = task.get("message", "")

    if not recipient or not message:
        yield "❌ Missing recipient or message. Tell me who to send it to and what to say."
        return

    yield f"📱 Opening WhatsApp Web..."
    yield f"👤 Recipient: {recipient}"
    yield f"💬 Message: \"{message}\""
    await asyncio.sleep(0.3)

    # Ensure session directory exists for persistent login
    session_dir = os.path.abspath(settings.whatsapp_session_dir)
    os.makedirs(session_dir, exist_ok=True)

    browser_task = f"""
    You are controlling a browser to send a WhatsApp message.

    Step 1: Go to https://web.whatsapp.com
    Step 2: Wait for the page to fully load
      - If you see a QR code: STOP and tell the user to scan the QR code with their phone WhatsApp app, then wait for them to confirm before continuing
      - If you see the chat list: continue to step 3
    Step 3: Look for the search icon (magnifying glass) at the top left
    Step 4: Click it and type "{recipient}"
    Step 5: Wait for search results and click on the contact named "{recipient}"
    Step 6: Click on the message input box at the bottom
    Step 7: Type this exact message: "{message}"
    Step 8: Press Enter or click the Send button (paper airplane icon)
    Step 9: Confirm the message was sent by checking it appears in the chat with a checkmark

    Important:
    - Do not send to the wrong contact
    - If the contact is not found, report it and stop
    - Wait for the message to show sent checkmarks before finishing
    - Reuse the existing WhatsApp Web session when the browser offers it
    """

    try:
        agent = Agent(task=browser_task, llm=build_agent_llm())

        yield "🤖 Browser agent started — WhatsApp Web is opening..."
        yield "⚠️  If you see a QR code prompt, scan it with your phone once!"
        result = await agent.run()

        yield f"✅ WhatsApp message sent to {recipient}!"
        yield f"📨 Message delivered: \"{message}\""

    except Exception as e:
        yield f"❌ Error during WhatsApp automation: {str(e)}"
        yield "💡 Tip: WhatsApp Web needs to be linked to your phone. Open WhatsApp > Linked Devices > Link a Device"
