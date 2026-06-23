"""
Social AI Agent — FastAPI Backend
==================================
Endpoints:
  POST /api/chat          → parse intent + queue task, returns task JSON
  WS   /ws/run/{task_id} → stream live agent logs back to the browser
  GET  /api/history       → last 50 chat messages
  GET  /api/health        → health check
"""

import asyncio
import json
import uuid
from collections import deque
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config.settings import settings
from services.llm_service import llm_service
from agents.agent_router import route_task

app = FastAPI(title="Social AI Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory stores
chat_history: deque[dict] = deque(maxlen=100)
pending_tasks: dict[str, dict] = {}     # task_id → task dict
task_logs: dict[str, list[str]] = {}    # task_id → list of log lines


# ── Models ──────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    message: str
    history: list[dict] = []


# ── Routes ──────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok", "llm_provider": settings.llm_provider}


@app.get("/api/history")
async def get_history():
    return {"messages": list(chat_history)}


@app.post("/api/chat")
async def chat(body: ChatMessage):
    """
    Parse a user message into a structured task.
    Returns the parsed task + a task_id for WebSocket streaming.
    """
    user_msg = body.message.strip()

    # Store user message
    chat_history.append({"role": "user", "content": user_msg})

    # Parse intent
    task = llm_service.parse_intent(user_msg, body.history)
    reply = task.get("reply", "I'm on it!")

    # Store assistant reply
    chat_history.append({"role": "assistant", "content": reply})

    # If it's an actionable task (not just a clarification), queue it
    task_id = None
    if task.get("action") not in ("clarify", None) and task.get("platform") != "unknown":
        task_id = str(uuid.uuid4())
        pending_tasks[task_id] = task
        task_logs[task_id] = []

    return {
        "reply": reply,
        "task": task,
        "task_id": task_id
    }


@app.websocket("/ws/run/{task_id}")
async def run_task_ws(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint — streams live agent logs for a given task_id.
    Frontend connects here after receiving a task_id from /api/chat.
    """
    await websocket.accept()

    if task_id not in pending_tasks:
        await websocket.send_text(json.dumps({"type": "error", "message": "Task not found"}))
        await websocket.close()
        return

    task = pending_tasks.pop(task_id)

    try:
        async for log_line in route_task(task):
            msg = json.dumps({"type": "log", "message": log_line})
            await websocket.send_text(msg)
            task_logs.setdefault(task_id, []).append(log_line)
            await asyncio.sleep(0.05)   # tiny yield so messages stream visibly

        await websocket.send_text(json.dumps({"type": "done", "message": "✅ Task finished!"}))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
    finally:
        await websocket.close()


# ── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
