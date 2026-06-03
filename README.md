# Video RAG Chatbot

Full-stack RAG chatbot for video analytics using LangChain, ChromaDB, and Next.js.

## Features

- **Video Processing**: Extract transcripts and metadata from YouTube and Instagram Reels
- **Engagement Analytics**: Calculate and compare engagement rates
- **RAG Chat Interface**: Ask questions about videos with AI-powered responses
- **Streaming Responses**: Real-time streaming with source citations
- **Conversation Memory**: Maintain context across chat turns
- **Vector Database**: ChromaDB with BGE embeddings (open-source, free)

## Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **LangChain**: Orchestration framework for RAG
- **ChromaDB**: Vector database (local, free)
- **BGE Embeddings**: Open-source embeddings (BAAI/bge-small-en-v1.5)
- **OpenAI GPT-4o**: LLM for responses (configurable to GPT-3.5-turbo for cost savings)
- **yt-dlp**: YouTube metadata extraction
- **youtube-transcript-api**: YouTube transcript extraction
- **instaloader**: Instagram metadata extraction

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type safety
- **Tailwind CSS**: Utility-first styling
- **Lucide React**: Icon library

## Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- OpenAI API key

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
```

5. Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

6. Run the server:
```bash
python main.py
```

Backend will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run development server:
```bash
npm run dev
```

Frontend will run on `http://localhost:3000`

## Usage

1. Open `http://localhost:3000` in your browser
2. Enter two video URLs (YouTube or Instagram Reels)
3. Click "Process Videos" to analyze
4. View side-by-side video cards with engagement metrics
5. Ask questions in the chat panel:
   - "Why did Video A get more engagement than Video B?"
   - "What's the engagement rate of each?"
   - "Compare the hooks in the first 5 seconds."
   - "Who's the creator of Video B and what's their follower count?"
   - "Suggest improvements for B based on what worked in A."

## API Endpoints

- `POST /api/process-videos` - Process two video URLs
- `GET /api/videos` - Get processed video data
- `POST /api/chat` - Streaming chat endpoint
- `POST /api/chat/sync` - Synchronous chat endpoint
- `POST /api/clear-memory` - Clear conversation memory
- `POST /api/reset` - Reset the entire system

## Cost Analysis & Scalability

See [COST_ANALYSIS.md](./COST_ANALYSIS.md) for detailed cost breakdown and scalability recommendations.

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Next.js   │────────▶│   FastAPI    │────────▶│  LangChain  │
│  Frontend   │         │   Backend    │         │   RAG Chain │
└─────────────┘         └──────────────┘         └──────┬──────┘
                                                        │
                              ┌─────────────────────────┼──────────────────┐
                              │                         │                  │
                              ▼                         ▼                  ▼
                       ┌─────────────┐         ┌─────────────┐    ┌─────────────┐
                       │  ChromaDB   │         │   OpenAI    │    │  Video APIs  │
                       │  Vector DB  │         │     LLM     │    │ (yt-dlp, etc)│
                       └─────────────┘         └─────────────┘    └─────────────┘
```

## Notes

- Instagram Reels don't have native transcripts. For production, integrate Whisper or AssemblyAI for transcription.
- ChromaDB runs locally by default. For production, consider cloud-hosted alternatives (Pinecone, Weaviate).
- BGE embeddings are free and run locally. For better quality, consider OpenAI embeddings.
- GPT-4o provides high-quality responses. For cost savings, use GPT-3.5-turbo.
