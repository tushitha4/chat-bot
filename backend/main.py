from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import json
import asyncio

from transcript_extractor import TranscriptExtractor
from engagement_calculator import EngagementCalculator
from vector_store import VectorStore
from rag_chain import RAGChain


app = FastAPI(title="Video RAG Chatbot")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
transcript_extractor = TranscriptExtractor()
vector_store: Optional[VectorStore] = None
rag_chain: Optional[RAGChain] = None
video_data: Dict[str, Any] = {}


class VideoURL(BaseModel):
    url: str
    video_id: str  # "A" or "B"


class ChatQuery(BaseModel):
    question: str


class ProcessVideosRequest(BaseModel):
    video_a_url: str
    video_b_url: str
    use_openai: bool = False


@app.on_event("startup")
async def startup_event():
    """Initialize vector store and RAG chain on startup."""
    global vector_store, rag_chain
    vector_store = VectorStore(use_openai=False)
    rag_chain = RAGChain(vector_store, use_openai=False)


@app.get("/")
async def root():
    return {"message": "Video RAG Chatbot API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/process-videos")
async def process_videos(request: ProcessVideosRequest, background_tasks: BackgroundTasks):
    """Process two videos and store transcripts in vector DB."""
    global video_data, vector_store, rag_chain
    
    try:
        # Clear previous data
        vector_store.clear_collection()
        rag_chain.clear_memory()
        video_data = {}
        
        # Process Video A
        if "youtube.com" in request.video_a_url or "youtu.be" in request.video_a_url:
            video_a = transcript_extractor.extract_youtube_transcript(request.video_a_url)
        elif "instagram.com" in request.video_a_url:
            video_a = transcript_extractor.extract_instagram_transcript(request.video_a_url)
        else:
            raise HTTPException(status_code=400, detail="Unsupported URL for Video A")
        
        if "error" in video_a:
            raise HTTPException(status_code=400, detail=video_a["error"])
        
        # Process Video B
        if "youtube.com" in request.video_b_url or "youtu.be" in request.video_b_url:
            video_b = transcript_extractor.extract_youtube_transcript(request.video_b_url)
        elif "instagram.com" in request.video_b_url:
            video_b = transcript_extractor.extract_instagram_transcript(request.video_b_url)
        else:
            raise HTTPException(status_code=400, detail="Unsupported URL for Video B")
        
        if "error" in video_b:
            raise HTTPException(status_code=400, detail=video_b["error"])
        
        # Store in global state
        video_data["A"] = video_a
        video_data["B"] = video_b
        
        # Add transcripts to vector store
        vector_store.add_transcript("A", video_a["transcript"], video_a["metadata"])
        vector_store.add_transcript("B", video_b["transcript"], video_b["metadata"])
        
        # Reinitialize RAG chain with new data
        rag_chain = RAGChain(vector_store, use_openai=request.use_openai)
        
        # Calculate engagement rates
        engagement_comparison = EngagementCalculator.compare_videos(
            video_a, video_b
        )
        
        return {
            "status": "success",
            "video_a": {
                "video_id": video_a.get("video_id"),
                "metadata": video_a.get("metadata"),
                "engagement_rate": engagement_comparison["video_a_engagement_rate"]
            },
            "video_b": {
                "video_id": video_b.get("video_id"),
                "metadata": video_b.get("metadata"),
                "engagement_rate": engagement_comparison["video_b_engagement_rate"]
            },
            "comparison": engagement_comparison
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/videos")
async def get_videos():
    """Get processed video data."""
    if not video_data:
        raise HTTPException(status_code=404, detail="No videos processed yet")
    
    engagement_comparison = EngagementCalculator.compare_videos(
        video_data.get("A", {}),
        video_data.get("B", {})
    )
    
    return {
        "video_a": {
            "video_id": video_data.get("A", {}).get("video_id"),
            "metadata": video_data.get("A", {}).get("metadata"),
            "transcript": video_data.get("A", {}).get("transcript"),
            "engagement_rate": engagement_comparison["video_a_engagement_rate"]
        },
        "video_b": {
            "video_id": video_data.get("B", {}).get("video_id"),
            "metadata": video_data.get("B", {}).get("metadata"),
            "transcript": video_data.get("B", {}).get("transcript"),
            "engagement_rate": engagement_comparison["video_b_engagement_rate"]
        },
        "comparison": engagement_comparison
    }


@app.post("/api/chat")
async def chat(query: ChatQuery):
    """Query the RAG system with streaming response."""
    global rag_chain
    
    if not rag_chain:
        raise HTTPException(status_code=404, detail="No videos processed yet")
    
    async def generate():
        try:
            async for chunk in rag_chain.query(query.question):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/api/chat/sync")
async def chat_sync(query: ChatQuery):
    """Synchronous chat endpoint (non-streaming)."""
    global rag_chain
    
    if not rag_chain:
        raise HTTPException(status_code=404, detail="No videos processed yet")
    
    try:
        result = rag_chain.query_sync(query.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/clear-memory")
async def clear_memory():
    """Clear conversation memory."""
    global rag_chain
    
    if rag_chain:
        rag_chain.clear_memory()
    
    return {"status": "success", "message": "Memory cleared"}


@app.post("/api/reset")
async def reset_system():
    """Reset the entire system."""
    global vector_store, rag_chain, video_data
    
    vector_store.clear_collection()
    rag_chain.clear_memory()
    video_data = {}
    
    return {"status": "success", "message": "System reset"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
