# FinanceAI — Smart Financial Advisor

A full-stack AI-powered financial advisor chatbot with built-in financial calculators. Built with FastAPI (backend) and vanilla JavaScript (frontend).

## Features

- **AI Chat** — Ask any financial question, get clear answers powered by LLMs
- **3-Model Fallback** — Cascading fallback across DeepSeek, Mixtral, and GPT-OSS for high availability
- **Streaming Responses** — Real-time token-by-token output via Server-Sent Events
- **Financial Calculators** — Compound Interest, EMI, SIP Returns, and Inflation Impact
- **Conversation History** — Persistent chat sessions stored in the browser

## Tech Stack

| Layer    | Technology                     |
|----------|--------------------------------|
| Backend  | Python, FastAPI, Uvicorn       |
| Frontend | HTML, CSS, JavaScript, Vite    |
| LLM API  | Fireworks AI (OpenAI-compatible) |

## Project Structure

```
finance-bot/
├── .env                    # API keys and model config (not committed)
├── requirements.txt        # Python dependencies
├── backend/
│   ├── main.py             # FastAPI app entry point
│   ├── config.py           # Environment config loader
│   ├── models/
│   │   └── schemas.py      # Pydantic request/response models
│   ├── routers/
│   │   ├── chat.py         # /api/chat endpoints
│   │   └── tools.py        # /api/tools calculator endpoints
│   └── services/
│       └── llm_service.py  # LLM calls with fallback logic
└── frontend/
    ├── index.html           # App shell
    ├── style.css            # Design system
    ├── main.js              # Application logic
    ├── package.json         # Node dependencies
    └── vite.config.js       # Dev server + API proxy
```

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- A [Fireworks AI](https://fireworks.ai) API key

### 1. Clone the repository

```bash
git clone https://github.com/Anish-S-tech/finance-chatbot.git
cd finance-chatbot
```

### 2. Configure environment

Create a `.env` file in the project root:

```env
LLM_API_KEY=your_fireworks_api_key
API_BASE_URL=https://api.fireworks.ai/inference/v1
MODEL_PRIMARY=accounts/fireworks/models/deepseek-v3p2
MODEL_SECONDARY=accounts/fireworks/models/mixtral-8x22b-instruct
MODEL_TERTIARY=accounts/fireworks/models/gpt-oss-20b
SYSTEM_PROMPT=You are a helpful financial advisor who explains things clearly to users.
```

### 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 4. Install frontend dependencies

```bash
cd frontend
npm install
```

### 5. Run the application

Open two terminals:

```bash
# Terminal 1 — Backend (from project root)
python -m uvicorn backend.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev
```

Open **http://localhost:3000** in your browser.

## API Endpoints

| Method | Endpoint                    | Description              |
|--------|-----------------------------|--------------------------|
| GET    | `/health`                   | Health check + model list|
| POST   | `/api/chat`                 | Chat (non-streaming)     |
| POST   | `/api/chat/stream`          | Chat (SSE streaming)     |
| POST   | `/api/tools/compound-interest` | Compound interest calc|
| POST   | `/api/tools/emi`            | EMI calculator           |
| POST   | `/api/tools/sip`            | SIP returns calculator   |
| POST   | `/api/tools/inflation`      | Inflation impact calc    |

## License

MIT
