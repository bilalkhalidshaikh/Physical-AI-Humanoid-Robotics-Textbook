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
    ChatSessionResponse,
    ChatSessionListResponse,
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
frontend_url = os.getenv("FRONTEND_URL", "https://bilalkhalidshaikh.github.io")
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
    5. Persists session and messages for authenticated users
    """
    # Import here to avoid circular imports
    from rag_service import query_rag
    from db.connection import (
        create_chat_session,
        save_chat_message,
        get_chat_session_with_messages
    )

    # 1. Provide conversation history if session exists
    history = []
    if request.session_id:
        session_data = await get_chat_session_with_messages(request.session_id)
        if session_data:
            history = session_data["messages"]

    try:
        # 2. Query RAG pipeline
        response = await query_rag(
            message=request.message,
            session_id=request.session_id,
            context_type=request.context_type,
            context_source=request.context_source,
            conversation_history=history
        )

        # 3. Persist messages for authenticated users
        if request.user_id:
            try:
                # Ensure session exists
                await create_chat_session(
                    session_id=response.session_id,
                    user_id=request.user_id,
                    context_type=request.context_type,
                    context_source=request.context_source
                )

                # Save user message
                from uuid import uuid4
                await save_chat_message(
                    message_id=str(uuid4()),
                    session_id=response.session_id,
                    role="user",
                    content=request.message
                )

                # Save assistant response
                await save_chat_message(
                    message_id=response.message.id or str(uuid4()),
                    session_id=response.session_id,
                    role="assistant",
                    content=response.message.content,
                    source_references=response.message.source_references
                )
            except Exception as db_err:
                print(f"⚠️ Failed to persist chat: {db_err}")
                # Don't fail the request if persistence fails

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


@app.get("/chat/sessions", response_model=ChatSessionListResponse)
async def list_chat_sessions(user_id: str):
    """List all chat sessions for a user."""
    from db.connection import get_user_chat_sessions

    try:
        sessions = await get_user_chat_sessions(user_id)
        return ChatSessionListResponse(
            sessions=sessions,
            total=len(sessions)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch sessions: {str(e)}"
        )


@app.get("/chat/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(session_id: str):
    """Get chat session details and message history."""
    from db.connection import get_chat_session_with_messages

    try:
        data = await get_chat_session_with_messages(session_id)
        if not data:
            raise HTTPException(status_code=404, detail="Session not found")
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch session: {str(e)}"
        )


@app.delete("/chat/sessions/{session_id}")
async def delete_chat_session_endpoint(session_id: str, user_id: str):
    """Delete a chat session."""
    from db.connection import delete_chat_session

    try:
        success = await delete_chat_session(session_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found or not owned by user")
        return {"status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete session: {str(e)}"
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
