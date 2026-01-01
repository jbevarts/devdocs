# DevDocs AI - Intelligent Documentation Assistant

A full-stack AI application for intelligent code documentation and assistance, built with FastAPI, Next.js, and Claude Sonnet 4.5.

## Architecture

The frontend routes all requests through the FastAPI backend, which handles conversation management, context summarization, and language-specific prompts. The Vercel AI SDK v6 serves as a streaming format adapter, while all business logic and AI orchestration lives in the backend for better security, scalability, and maintainability.

## Tech Stack

### Backend
- Python 3.11+ with FastAPI
- LangChain/LangGraph for orchestration
- PostgreSQL + pgvector for RAG
- Redis for caching and rate limiting

### Frontend
- Next.js 14 (App Router) with TypeScript
- Vercel AI SDK v6 (@ai-sdk/react) for streaming responses
- Tailwind CSS for styling

### AI/ML
- Anthropic Claude Sonnet 4.5 (primary)
- OpenAI GPT-4 (fallback)
- Voyage AI or OpenAI embeddings for RAG (planned)
- LangSmith for observability (planned)

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

## Current Status

✅ **Fully Functional Chat Interface**
- Real-time streaming responses with AI SDK v6
- Multi-turn conversations with context management
- Auto-scroll to latest messages
- Language-specific prompt selection
- Conversation summarization for long threads
- Modern, responsive UI with dark mode

## Development Plan

- **Week 1-2**: Context Engineering + Basic Setup ✅
- **Week 3-4**: RAG Implementation
- **Week 5-6**: Advanced Features
- **Week 7-8**: Production Deployment

## Quick Links

- [Setup Guide](./SETUP.md) - Detailed setup instructions
- [API Documentation](http://localhost:8000/docs) - FastAPI auto-generated docs (when backend is running)
- [Development Blog](./blog/README.md) - Technical blog documenting the development journey

## Development Blog

This project includes a technical blog that documents the development process, technical decisions, and learnings:

- **[Blog Index](./blog/README.md)** - Overview and navigation
- **[Post 001: Context Engineering Fundamentals](./blog/posts/001-context-engineering-fundamentals.md)** - System prompt design, token management, and context window strategies

The blog showcases:
- System prompt architecture and iterations
- Token counting and context window strategies
- Prompt format experiments with before/after comparisons
- Context utilization metrics and analysis
- Technical decision-making process

