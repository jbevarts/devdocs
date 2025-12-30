# Setup Guide

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys:
# - ANTHROPIC_API_KEY (required)
# - OPENAI_API_KEY (optional, for fallback)
# - LANGSMITH_API_KEY (optional, for observability)
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables (optional)
cp .env.example .env.local
# Edit .env.local if you want to use a different backend URL
```

### 3. Start Services

#### Using Docker for Database/Redis:

```bash
# From project root
docker-compose up -d postgres redis

# Start backend (in one terminal)
cd backend
source venv/bin/activate
uvicorn main:app --reload

# Start frontend (in another terminal)
cd frontend
npm run dev
```

#### Without Docker:

Make sure you have PostgreSQL and Redis running locally, then update the connection strings in `backend/.env`.

## Features Implemented (Week 1-2)

✅ **Monorepo Structure**
- FastAPI backend with organized structure
- Next.js 14 frontend with App Router

✅ **Multi-turn Conversations**
- Conversation history management
- Context-aware responses

✅ **Language-Specific Prompts**
- Support for Python, JavaScript, TypeScript, Java, Go, Rust, C++, C
- Automatic prompt selection based on language context

✅ **Context Management**
- Conversation summarization for long threads
- Configurable thresholds for summarization
- In-memory storage (ready for Redis/DB migration)

✅ **Modern UI**
- Clean, responsive chat interface
- Language selector
- Streaming responses
- Dark mode support

## Next Steps (Week 3-4)

- [ ] Implement RAG with PostgreSQL + pgvector
- [ ] Add embedding support (Voyage AI or OpenAI)
- [ ] Set up LangSmith for observability
- [ ] Add rate limiting with Redis
- [ ] Implement conversation persistence in database
- [ ] Add authentication (optional)

## Troubleshooting

### Backend won't start
- Check that Python 3.11+ is installed: `python --version`
- Verify virtual environment is activated
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that `.env` file exists and has `ANTHROPIC_API_KEY`

### Frontend won't start
- Check Node.js version: `node --version` (should be 18+)
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check for port conflicts (default: 3000)

### Database connection errors
- Ensure PostgreSQL is running
- Check `DATABASE_URL` in `.env` matches your setup
- For Docker: `docker-compose ps` to verify containers are running

