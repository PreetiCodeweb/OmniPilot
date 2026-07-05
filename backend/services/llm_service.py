"""
LLM Service
-----------
Translates natural language chat messages into structured agent tasks.
Supports Anthropic Claude (default) and OpenAI as fallback.
"""

import json
import re
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
        self.client = None
        self.provider = settings.effective_llm_provider

    def _client(self):
        if self.client:
            return self.client

        if settings.effective_llm_provider == "anthropic":
            self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        elif settings.effective_llm_provider == "openai":
            self.client = openai.OpenAI(api_key=settings.openai_api_key)

        self.provider = settings.effective_llm_provider
        return self.client

    def parse_intent(self, user_message: str, history: list[dict] = []) -> dict:
        """Convert a natural language message into a structured task dict."""
        messages = history + [{"role": "user", "content": user_message}]

        if settings.effective_llm_provider == "local":
            return self._rule_parse(user_message)

        try:
            client = self._client()
            if self.provider == "anthropic":
                response = client.messages.create(
                    model=settings.anthropic_model,
                    max_tokens=512,
                    system=SYSTEM_PROMPT,
                    messages=messages
                )
                raw = response.content[0].text.strip()
            else:
                response = client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
                    max_tokens=512
                )
                raw = response.choices[0].message.content.strip()
        except Exception as exc:
            task = self._rule_parse(user_message)
            task["reply"] = (
                f"{task['reply']} I used the local parser because the LLM call failed: {type(exc).__name__}."
            )
            return task

        # Strip markdown code fences if present
        raw = re.sub(r"```json|```", "", raw).strip()

        try:
            task = json.loads(raw)
            return self._normalize_task(task, user_message)
        except json.JSONDecodeError:
            return self._rule_parse(user_message)

    def chat_response(self, user_message: str, context: str = "") -> str:
        """Plain conversational response for non-task messages."""
        system = "You are a friendly AI social media automation assistant. Keep replies short and helpful."
        if context:
            system += f"\n\nContext: {context}"

        if settings.effective_llm_provider == "local":
            return "Tell me the platform and action, like 'Follow AI accounts on Twitter' or 'Send WhatsApp to Riya: I am on my way'."

        client = self._client()
        if self.provider == "anthropic":
            response = client.messages.create(
                model=settings.anthropic_model,
                max_tokens=256,
                system=system,
                messages=[{"role": "user", "content": user_message}]
            )
            return response.content[0].text.strip()
        else:
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=256
            )
            return response.choices[0].message.content.strip()

    def _normalize_task(self, task: dict, user_message: str) -> dict:
        task.setdefault("platform", "unknown")
        task.setdefault("action", "clarify")
        task.setdefault("targets", [])
        task.setdefault("count", 5)
        task.setdefault("query", " ".join(task.get("targets", [])))
        task.setdefault("reply", "I'm on it.")

        if task["platform"] == "whatsapp":
            task.setdefault("recipient", "")
            task.setdefault("message", "")

        return task

    def _rule_parse(self, user_message: str) -> dict:
        text = user_message.strip()
        lower = text.lower()

        platform = "unknown"
        for candidate in ("twitter", "linkedin", "reddit", "whatsapp"):
            if candidate in lower or (candidate == "twitter" and " x " in f" {lower} "):
                platform = candidate
                break

        count_match = re.search(r"\b(\d{1,2})\b", lower)
        count = int(count_match.group(1)) if count_match else 5
        count = max(1, min(20, count))

        if platform == "whatsapp":
            recipient = ""
            message = ""
            match = re.search(r"(?:to|for)\s+([^:]+?)(?:\s+saying|\s+that|:|$)", text, re.IGNORECASE)
            if match:
                recipient = match.group(1).strip()
            message_match = re.search(r"(?:saying|that|:)\s*(.+)$", text, re.IGNORECASE)
            if message_match:
                message = message_match.group(1).strip()
            return {
                "platform": "whatsapp",
                "action": "send_message" if recipient and message else "clarify",
                "recipient": recipient,
                "message": message,
                "targets": [],
                "count": 1,
                "reply": (
                    f"I'll send {recipient} your WhatsApp message."
                    if recipient and message
                    else "Who should I message on WhatsApp, and what should I say?"
                ),
            }

        if platform == "unknown":
            return {
                "platform": "unknown",
                "action": "clarify",
                "targets": [],
                "count": count,
                "query": "",
                "reply": "Which platform should I use: Twitter, LinkedIn, Reddit, or WhatsApp?",
            }

        action = "subscribe" if platform == "reddit" else "search_and_follow"
        cleaned = re.sub(r"\b(follow|subscribe|join|top|best|accounts|people|companies|subreddits|on|twitter|linkedin|reddit|x)\b", " ", lower)
        targets = [part.strip(" .,#") for part in re.split(r",| and | & ", cleaned) if part.strip(" .,#")]
        if not targets:
            targets = ["ai", "software", "business"] if platform == "linkedin" else ["technology", "ai"]

        query = " ".join(targets[:4])
        return {
            "platform": platform,
            "action": action,
            "targets": targets,
            "count": count,
            "query": query,
            "reply": f"I'll use {platform.title()} to run a {action.replace('_', ' ')} task for: {query}.",
        }


llm_service = LLMService()
