# Video RAG Chatbot Backend

FastAPI backend for video analytics RAG chatbot.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file:
```
OPENAI_API_KEY=your_api_key_here
```

3. Run the server:
```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `POST /api/process-videos` - Process two video URLs
- `GET /api/videos` - Get processed video data
- `POST /api/chat` - Streaming chat endpoint
- `POST /api/chat/sync` - Synchronous chat endpoint
- `POST /api/clear-memory` - Clear conversation memory
- `POST /api/reset` - Reset the entire system
