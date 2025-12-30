# DevDocs AI - Intelligent Documentation Assistant

A full-stack AI application for intelligent code documentation and assistance, built with FastAPI, Next.js, and Claude 3.5 Sonnet.

## Tech Stack

### Backend
- Python 3.11+ with FastAPI
- LangChain/LangGraph for orchestration
- PostgreSQL + pgvector for RAG
- Redis for caching and rate limiting

### Frontend
- Next.js 14 (App Router) with TypeScript
- Vercel AI SDK for streaming responses
- Tailwind CSS for styling

### AI/ML
- Anthropic Claude 3.5 Sonnet (primary)
- OpenAI GPT-4 (fallback)
- Voyage AI or OpenAI embeddings for RAG
- LangSmith for observability

### Infrastructure
- Docker for local development
- GitHub Actions for CI/CD
- Vercel for frontend hosting
- Railway/Render for backend hosting

## Project Structure

```
.
├── backend/          # FastAPI backend
├── frontend/         # Next.js frontend
├── docker-compose.yml
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker and Docker Compose (optional, for local DB/Redis)
- Anthropic API key

### Local Development

#### Option 1: Docker Compose (Recommended)

1. **Set up environment variables:**
   ```bash
   # Backend
   cd backend
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   
   # Frontend
   cd ../frontend
   cp .env.example .env.local
   ```

2. **Start services:**
   ```bash
   # From project root
   docker-compose up -d postgres redis
   
   # Start backend
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn main:app --reload
   
   # In another terminal, start frontend
   cd frontend
   npm install
   npm run dev
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

#### Option 2: Local Development (No Docker)

1. Set up PostgreSQL and Redis locally
2. Update `DATABASE_URL` and `REDIS_URL` in backend `.env`
3. Follow the same steps as above for backend and frontend

## Development Plan

- **Week 1-2**: Context Engineering + Basic Setup ✅
- **Week 3-4**: RAG Implementation
- **Week 5-6**: Advanced Features
- **Week 7-8**: Production Deployment

