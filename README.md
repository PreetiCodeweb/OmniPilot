# 🤖 OmniPilot

A full-stack AI automation app that lets you control Twitter, LinkedIn, Reddit, and WhatsApp using natural language. Just type "Follow top trading accounts on Twitter" and the AI controls your browser and does it automatically.

---

## 📁 Project Structure

```
social-ai-agent/
├── backend/                  # FastAPI Python backend
│   ├── main.py               # Server + WebSocket streaming
│   ├── requirements.txt
│   ├── .env.example          # Copy to .env and fill in your keys
│   ├── config/
│   │   └── settings.py       # All config loaded from .env
│   ├── services/
│   │   └── llm_service.py    # Parses natural language → task JSON (Anthropic/OpenAI)
│   └── agents/
│       ├── agent_router.py   # Routes tasks to the right platform agent
│       ├── twitter_agent.py  # Browser-use agent for Twitter follows
│       ├── linkedin_agent.py # Browser-use agent for LinkedIn follows
│       ├── reddit_agent.py   # Browser-use agent for Reddit subscribes
│       └── whatsapp_agent.py # Browser-use agent for WhatsApp messages
│
├── frontend-app/             # React + Vite chat UI
│   ├── src/
│   │   ├── App.jsx           # Main layout
│   │   ├── hooks/
│   │   │   └── useChat.js    # Chat state + WebSocket task streaming
│   │   ├── components/
│   │   │   ├── Sidebar.jsx       # Platform list + backend status
│   │   │   ├── ChatMessage.jsx   # User / AI / log message bubbles
│   │   │   ├── LogStream.jsx     # Live browser agent log viewer
│   │   │   ├── ChatInput.jsx     # Message input bar
│   │   │   ├── QuickPrompts.jsx  # One-click example tasks
│   │   │   └── PlatformBadge.jsx # Twitter/LinkedIn/Reddit/WhatsApp badge
│   │   └── utils/
│   │       └── api.js            # All fetch + WebSocket calls
│   └── .env.example
│
├── n8n-workflows/            # Import these into n8n for visual automation
│   ├── twitter-follow-workflow.json
│   └── whatsapp-message-workflow.json
│
└── docs/
    └── SETUP.md
```

---

## ⚡ Quick Start

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (required for browser-use)
playwright install chromium

# Copy env and fill in your keys
cp .env.example .env
# Edit .env — add your ANTHROPIC_API_KEY and platform credentials

# Start the server
python main.py
# → Running on http://localhost:8000
```

### 2. Frontend Setup

```bash
cd frontend-app

# Install dependencies
npm install

# Copy env
cp .env.example .env

# Start dev server
npm run dev
# → Running on http://localhost:5173
```

### 3. Open the app

Go to **http://localhost:5173** in your browser.

---

## 🔑 Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in:

| Variable              | Required | Description |
|-----------------------|----------|-------------|
| `ANTHROPIC_API_KEY`   | ✅       | Your Claude API key (get from console.anthropic.com) |
| `OPENAI_API_KEY`      | Optional | Fallback LLM if no Anthropic key |
| `TWITTER_USERNAME`    | For Twitter | Your Twitter/X handle |
| `TWITTER_PASSWORD`    | For Twitter | Your Twitter/X password |
| `LINKEDIN_EMAIL`      | For LinkedIn | Your LinkedIn email |
| `LINKEDIN_PASSWORD`   | For LinkedIn | Your LinkedIn password |
| `REDDIT_USERNAME`     | For Reddit | Your Reddit username |
| `REDDIT_PASSWORD`     | For Reddit | Your Reddit password |
| `BROWSER_HEADLESS`    | Optional | Set `true` to hide browser window |

**WhatsApp**: No credentials needed! The agent opens WhatsApp Web and you scan the QR code once with your phone.

---

## 💬 Example Commands

```
"Follow top 10 trading accounts on Twitter"
"Follow algorithmic trading and finance people on Twitter"
"Subscribe to the best coding subreddits on Reddit"
"Subscribe to r/algotrading r/Python and r/MachineLearning"
"Follow AI companies and software engineers on LinkedIn"
"Send a WhatsApp message to Riya saying I'll be 20 mins late"
"Send WhatsApp to Mom: Coming home for dinner tonight!"
```

---

## 🏗️ How It Works

```
You type → LLM parses intent → Agent Router → Browser Use Agent → Real browser action
                ↓                                      ↓
        Structured task JSON              Live logs streamed via WebSocket
        {platform, action, targets}       to your chat UI in real time
```

1. **You type** a natural language command in the chat
2. **LLM Service** (Claude/GPT) converts it to a structured task: `{platform, action, targets, count}`
3. **Agent Router** sends the task to the right platform agent
4. **Browser Use Agent** opens a real Chromium browser, logs in, and executes the task
5. **Live logs** stream back to your chat via WebSocket so you can watch progress

---

## 🔧 n8n Integration

For visual no-code automation, import the workflows from `/n8n-workflows/` into your n8n instance:

1. Open n8n (run `npx n8n` or use n8n.cloud)
2. Go to Workflows → Import from File
3. Import `twitter-follow-workflow.json` or `whatsapp-message-workflow.json`
4. These workflows call your backend via webhook and can be triggered on schedules

---

## ⚠️ Important Notes

- **WhatsApp Web QR**: First time you run a WhatsApp task, your browser will open WhatsApp Web. Scan the QR with your phone. After that, sessions persist.
- **Rate limits**: The agents add delays between actions to mimic human behavior. Don't set count > 20 per session.
- **Platform ToS**: Use responsibly. Don't spam or mass-follow. These agents are for personal productivity use.
- **BROWSER_HEADLESS=false** by default so you can watch the browser work in real time.
