"""FastAPI RAG Backend for Physical AI Book."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import os
from dotenv import load_dotenv

from db.connection import init_db_pool, close_db_pool
from models.chat import (
    ChatRequest,
    ChatResponse,
    SearchRequest,
    SearchResponse,
)

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("🚀 Starting RAG backend...")
    try:
        await init_db_pool()
        print("✅ Database connection pool initialized")
    except Exception as e:
        print(f"⚠️ Database connection failed: {e}")

    yield

    # Shutdown
    print("🛑 Shutting down RAG backend...")
    await close_db_pool()
    print("✅ Database connection pool closed")


app = FastAPI(
    title="Physical AI Book RAG Backend",
    description="RAG chatbot API for the Physical AI & Humanoid Robotics textbook",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_status = "configured" if qdrant_url else "not configured"

    return {
        "status": "healthy",
        "service": "rag-backend",
        "qdrant": qdrant_status,
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the RAG chatbot.

    This endpoint:
    1. Creates or continues a chat session
    2. Retrieves relevant documents from Qdrant
    3. Generates a response using OpenAI
    4. Returns the response with source references
    """
    # Import here to avoid circular imports
    from rag_service import query_rag

    try:
        response = await query_rag(
            message=request.message,
            session_id=request.session_id,
            context_type=request.context_type,
            context_source=request.context_source,
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat request failed: {str(e)}"
        )


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Search the knowledge base directly.

    Returns matching document chunks without generating a response.
    """
    from rag_service import search_knowledge_base

    try:
        results = await search_knowledge_base(
            query=request.query,
            limit=request.limit,
            filter_module=request.filter_module,
        )
        return SearchResponse(
            query=request.query,
            results=results,
            total=len(results),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@app.post("/translate")
async def translate(
    content: str,
    source_path: str,
    target_language: str = "ur",
):
    """
    Translate chapter content to Urdu.

    - Preserves code blocks in English
    - Caches translations for performance
    """
    from translation_service import translate_content

    try:
        translated = await translate_content(
            content=content,
            source_path=source_path,
            target_language=target_language,
        )
        return {"translated_content": translated}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Translation failed: {str(e)}"
        )


@app.post("/personalize")
async def personalize(
    content: str,
    source_path: str,
    user_id: str,
):
    """
    Personalize chapter content based on user background.

    - Requires authenticated user with completed profile
    - Caches personalized content
    """
    from personalization_service import personalize_content

    try:
        personalized = await personalize_content(
            content=content,
            source_path=source_path,
            user_id=user_id,
        )
        return {"personalized_content": personalized}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Personalization failed: {str(e)}"
        )


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
        },
    )


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    uvicorn.run(app, host=host, port=port)
