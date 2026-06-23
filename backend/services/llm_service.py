"""
LLM Service
-----------
Translates natural language chat messages into structured agent tasks.
Supports Anthropic Claude (default) and OpenAI as fallback.
"""

import json
import re
from typing import Optional
import anthropic
import openai
from config.settings import settings


SYSTEM_PROMPT = """You are an AI assistant that controls a browser to automate social media tasks.

When the user gives you an instruction, extract the intent and output ONLY valid JSON with this schema:

{
  "platform": "twitter" | "linkedin" | "reddit" | "whatsapp",
  "action": "follow" | "subscribe" | "send_message" | "search_and_follow",
  "targets": ["list", "of", "accounts", "or", "topics"],
  "message": "only for whatsapp — the text to send",
  "recipient": "only for whatsapp — the contact name",
  "count": 10,
  "query": "search term used to find accounts, e.g. 'algorithmic trading'",
  "reply": "a short friendly confirmation of what you're about to do, in plain English"
}

Rules:
- If platform is unclear from context, ask for clarification (set action to "clarify")
- For WhatsApp, always extract both recipient and message
- For follow/subscribe, extract topics or explicit account names from the message
- count defaults to 10 if not specified
- Always populate the reply field with a friendly confirmation

Examples:
User: "follow top trading accounts on twitter"
→ {"platform":"twitter","action":"search_and_follow","targets":["trading","algorithmic trading","stock market","forex"],"count":10,"query":"trading finance stocks","reply":"On it! I'll search Twitter for the top trading accounts and follow 10 of them for you. 🚀"}

User: "send a whatsapp message to Riya saying I'll be late by 30 mins"
→ {"platform":"whatsapp","action":"send_message","recipient":"Riya","message":"Hey! I'll be late by 30 minutes, sorry!","reply":"Sure! I'll open WhatsApp Web and send Riya a message that you'll be 30 minutes late."}

User: "subscribe to coding subreddits on reddit"
→ {"platform":"reddit","action":"subscribe","targets":["programming","learnpython","webdev","coding","MachineLearning","devops"],"count":6,"query":"coding programming development","reply":"Got it! I'll find and subscribe to the top coding subreddits on Reddit for you."}
"""


class LLMService:
    def __init__(self):
        if settings.llm_provider == "anthropic" and settings.anthropic_api_key:
            self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            self.provider = "anthropic"
        elif settings.openai_api_key:
            self.client = openai.OpenAI(api_key=settings.openai_api_key)
            self.provider = "openai"
        else:
            raise ValueError("No LLM API key configured. Set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env")

    def parse_intent(self, user_message: str, history: list[dict] = []) -> dict:
        """Convert a natural language message into a structured task dict."""
        messages = history + [{"role": "user", "content": user_message}]

        if self.provider == "anthropic":
            response = self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=512,
                system=SYSTEM_PROMPT,
                messages=messages
            )
            raw = response.content[0].text.strip()
        else:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
                max_tokens=512
            )
            raw = response.choices[0].message.content.strip()

        # Strip markdown code fences if present
        raw = re.sub(r"```json|```", "", raw).strip()

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {
                "platform": "unknown",
                "action": "clarify",
                "reply": "I didn't quite catch that. Could you be more specific? For example: 'Follow top trading accounts on Twitter' or 'Send a WhatsApp to Ankit saying I'm on my way'."
            }

    def chat_response(self, user_message: str, context: str = "") -> str:
        """Plain conversational response for non-task messages."""
        system = "You are a friendly AI social media automation assistant. Keep replies short and helpful."
        if context:
            system += f"\n\nContext: {context}"

        if self.provider == "anthropic":
            response = self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=256,
                system=system,
                messages=[{"role": "user", "content": user_message}]
            )
            return response.content[0].text.strip()
        else:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=256
            )
            return response.choices[0].message.content.strip()


llm_service = LLMService()
