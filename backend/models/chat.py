"""Pydantic models for chat functionality."""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum


class ContextType(str, Enum):
    """Types of chat context."""
    GENERAL = "general"
    SELECTION = "selection"
    CHAPTER = "chapter"


class MessageRole(str, Enum):
    """Chat message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class SourceReference(BaseModel):
    """Reference to source document in RAG response."""

    file: str = Field(..., description="Source file path")
    section: Optional[str] = Field(None, description="Section heading")
    chunk_id: str = Field(..., description="Vector DB chunk ID")
    score: float = Field(..., ge=0, le=1, description="Relevance score")


class ChatMessage(BaseModel):
    """A single chat message."""

    id: Optional[str] = Field(None, description="Message UUID")
    role: MessageRole = Field(..., description="Message sender role")
    content: str = Field(..., min_length=1, description="Message content")
    source_references: List[SourceReference] = Field(
        default_factory=list,
        description="RAG source citations"
    )
    created_at: Optional[datetime] = None

    class Config:
        use_enum_values = True


class ChatRequest(BaseModel):
    """Request to send a chat message."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User message content"
    )
    session_id: Optional[str] = Field(
        None,
        description="Existing session ID to continue conversation"
    )
    context_type: ContextType = Field(
        default=ContextType.GENERAL,
        description="Type of context for the query"
    )
    context_source: Optional[str] = Field(
        None,
        description="Source path or selected text for context"
    )

    class Config:
        use_enum_values = True


class ChatResponse(BaseModel):
    """Response from chat endpoint."""

    session_id: str = Field(..., description="Chat session UUID")
    message: ChatMessage = Field(..., description="Assistant response")
    context_type: str = Field(default="general")
    context_active: bool = Field(
        default=False,
        description="Whether context is currently active"
    )


class ChatSession(BaseModel):
    """A chat session/conversation thread."""

    id: str = Field(..., description="Session UUID")
    user_id: Optional[str] = Field(None, description="Owner user ID (null for anonymous)")
    title: Optional[str] = Field(None, description="Auto-generated session title")
    context_type: ContextType = Field(default=ContextType.GENERAL)
    context_source: Optional[str] = None
    is_active: bool = Field(default=True)
    message_count: int = Field(default=0)
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None

    class Config:
        use_enum_values = True


class ChatSessionResponse(BaseModel):
    """Response with session and messages."""

    session: ChatSession
    messages: List[ChatMessage] = Field(default_factory=list)


class ChatSessionListResponse(BaseModel):
    """List of chat sessions for a user."""

    sessions: List[ChatSession]
    total: int


class SearchRequest(BaseModel):
    """Request to search the knowledge base."""

    query: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(default=5, ge=1, le=20)
    filter_module: Optional[str] = Field(
        None,
        description="Filter by module: ros2, gazebo, isaac_sim, vla"
    )


class SearchResult(BaseModel):
    """A single search result."""

    chunk_id: str
    text: str
    source_file: str
    section: Optional[str] = None
    score: float
    module: Optional[str] = None


class SearchResponse(BaseModel):
    """Search response with results."""

    query: str
    results: List[SearchResult]
    total: int
