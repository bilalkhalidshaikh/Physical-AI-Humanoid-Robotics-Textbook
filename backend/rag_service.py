"""RAG service for knowledge base search and chat.

This module uses a custom RobustQdrantClient that communicates with Qdrant Cloud
via REST API (httpx), bypassing gRPC issues on Windows.
"""

import os
from typing import List, Optional, Any
from uuid import uuid4

import httpx
from dotenv import load_dotenv
from openai import OpenAI

from models.chat import (
    ChatMessage,
    ChatResponse,
    SourceReference,
    SearchResult,
    MessageRole,
)

load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")  # For Gemini compatibility
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "physical_ai_book")

# Chat model configuration for Google Gemini Free Tier
# Using /openai/ endpoint which handles model names without prefix
CHAT_MODEL = os.getenv("CHAT_MODEL", "gemini-2.5-flash")

# Google Gemini model variants - only gemini-1.5-flash for free tier
GEMINI_MODEL_VARIANTS = [
    "gemini-2.5-flash",
]

# Embedding model for Google AI
EMBEDDING_MODEL = "text-embedding-004"

def _is_gemini_endpoint() -> bool:
    """Check if we're using Google's Gemini endpoint."""
    return OPENAI_BASE_URL and "generativelanguage.googleapis.com" in OPENAI_BASE_URL


class RobustQdrantClient:
    """Custom Qdrant client using REST API via httpx.

    This implementation bypasses gRPC issues on Windows by making direct
    HTTP requests to the Qdrant Cloud REST API endpoint.
    """

    def __init__(self, url: str, api_key: Optional[str] = None):
        """Initialize the REST-based Qdrant client.

        Args:
            url: Qdrant Cloud REST endpoint (e.g., https://xxx.cloud.qdrant.io:6333)
            api_key: Qdrant Cloud API key
        """
        self.base_url = url.rstrip('/')
        self.api_key = api_key
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["api-key"] = api_key
        self._client = httpx.Client(headers=headers, timeout=30.0)
        self._async_client: Optional[httpx.AsyncClient] = None

    def _get_async_client(self) -> httpx.AsyncClient:
        """Get or create async client."""
        if self._async_client is None:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["api-key"] = self.api_key
            self._async_client = httpx.AsyncClient(headers=headers, timeout=30.0)
        return self._async_client

    def search(
        self,
        collection_name: str,
        query_vector: List[float],
        query_filter: Optional[dict] = None,
        limit: int = 5,
        score_threshold: Optional[float] = None,
    ) -> List[Any]:
        """Search vectors via REST API (synchronous).

        Args:
            collection_name: Name of the Qdrant collection
            query_vector: Query embedding vector
            query_filter: Optional filter conditions
            limit: Maximum number of results
            score_threshold: Minimum similarity score

        Returns:
            List of search results with id, score, and payload
        """
        endpoint = self.base_url + "/collections/" + collection_name + "/points/search"
        payload: dict = {
            "vector": query_vector,
            "limit": limit,
            "with_payload": True,
        }
        if score_threshold is not None:
            payload["score_threshold"] = score_threshold
        if query_filter is not None:
            payload["filter"] = query_filter

        response = self._client.post(endpoint, json=payload)
        response.raise_for_status()
        result = response.json().get("result", [])

        return [QdrantSearchHit(hit) for hit in result]

    async def search_async(
        self,
        collection_name: str,
        query_vector: List[float],
        query_filter: Optional[dict] = None,
        limit: int = 5,
        score_threshold: Optional[float] = None,
    ) -> List[Any]:
        """Search vectors via REST API (asynchronous).

        Args:
            collection_name: Name of the Qdrant collection
            query_vector: Query embedding vector
            query_filter: Optional filter conditions
            limit: Maximum number of results
            score_threshold: Minimum similarity score

        Returns:
            List of search results with id, score, and payload
        """
        client = self._get_async_client()
        endpoint = self.base_url + "/collections/" + collection_name + "/points/search"
        payload: dict = {
            "vector": query_vector,
            "limit": limit,
            "with_payload": True,
        }
        if score_threshold is not None:
            payload["score_threshold"] = score_threshold
        if query_filter is not None:
            payload["filter"] = query_filter

        response = await client.post(endpoint, json=payload)
        response.raise_for_status()
        result = response.json().get("result", [])

        return [QdrantSearchHit(hit) for hit in result]

    async def close(self):
        """Close async client."""
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None


class QdrantSearchHit:
    """Wrapper class to provide attribute access to Qdrant search results."""

    def __init__(self, data: dict):
        self.id = data.get("id")
        self.score = data.get("score", 0.0)
        self.payload = data.get("payload", {})

    def __repr__(self):
        return f"QdrantSearchHit(id={self.id}, score={self.score})"


# System prompt for the RAG chatbot
SYSTEM_PROMPT = """You are an expert AI assistant for the "Physical AI & Humanoid Robotics" textbook.
Your role is to help students learn about robotics concepts including ROS 2, Gazebo simulation,
Isaac Sim, manipulation, navigation, and vision-language-action models.

Guidelines:
1. Answer questions based on the provided context from the textbook
2. If the context doesn't contain relevant information, say so clearly
3. Use technical terminology accurately
4. Provide code examples when appropriate
5. Reference specific sections when citing information
6. Be encouraging and educational in tone

When given context about a specific text selection, focus your answer on that selection."""


def get_openai_client() -> OpenAI:
    """Get OpenAI client (supports Gemini via OPENAI_BASE_URL)."""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is required")

    # Support Gemini compatibility via base_url
    if OPENAI_BASE_URL:
        return OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
    return OpenAI(api_key=OPENAI_API_KEY)


# Singleton instance for the Qdrant client
_qdrant_client: Optional[RobustQdrantClient] = None


def get_qdrant_client() -> RobustQdrantClient:
    """Get Qdrant client using REST API (bypasses gRPC issues)."""
    global _qdrant_client

    if _qdrant_client is None:
        if not QDRANT_URL:
            raise ValueError("QDRANT_URL environment variable is required")

        _qdrant_client = RobustQdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
        )

    return _qdrant_client


def generate_embedding(text: str) -> List[float]:
    """Generate embedding for a query."""
    client = get_openai_client()
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


async def search_knowledge_base(
    query: str,
    limit: int = 5,
    filter_module: Optional[str] = None,
    score_threshold: float = 0.5,
) -> List[SearchResult]:
    """Search the knowledge base for relevant documents."""
    qdrant = get_qdrant_client()

    # Generate query embedding
    query_embedding = generate_embedding(query)

    # Build filter for REST API format
    search_filter = None
    if filter_module:
        search_filter = {
            "must": [
                {
                    "key": "module",
                    "match": {"value": filter_module}
                }
            ]
        }

    # Search using async REST API
    results = await qdrant.search_async(
        collection_name=QDRANT_COLLECTION,
        query_vector=query_embedding,
        query_filter=search_filter,
        limit=limit,
        score_threshold=score_threshold,
    )

    return [
        SearchResult(
            chunk_id=str(hit.id),
            text=hit.payload.get("text", ""),
            source_file=hit.payload.get("source_file", ""),
            section=hit.payload.get("section"),
            score=hit.score,
            module=hit.payload.get("module"),
        )
        for hit in results
    ]


def build_context_prompt(
    search_results: List[SearchResult],
    context_type: str = "general",
    context_source: Optional[str] = None,
) -> str:
    """Build context prompt from search results."""
    context_parts = []

    # Add selection context if provided
    if context_type == "selection" and context_source:
        context_parts.append(
            f"The user has selected the following text and is asking about it:\n"
            f"---\n{context_source}\n---\n"
        )

    # Add search results
    if search_results:
        context_parts.append("Relevant content from the textbook:\n")
        for i, result in enumerate(search_results, 1):
            source_info = f"[Source: {result.source_file}"
            if result.section:
                source_info += f" - {result.section}"
            source_info += "]"

            context_parts.append(f"\n{i}. {source_info}\n{result.text}\n")

    return "\n".join(context_parts)


def _generate_chat_completion(
    openai_client: OpenAI,
    messages: List[dict],
    model: str,
) -> str:
    """Generate chat completion with fallback for Gemini models.

    If using Gemini endpoint and the primary model fails with 404,
    tries alternative model variants.
    """
    import logging

    models_to_try = [model]

    # If using Gemini, add fallback models
    if _is_gemini_endpoint():
        # Add variants that aren't already the primary model
        for variant in GEMINI_MODEL_VARIANTS:
            if variant != model and variant not in models_to_try:
                models_to_try.append(variant)

    last_error = None
    for try_model in models_to_try:
        try:
            logging.info(f"Trying chat model: {try_model}")
            completion = openai_client.chat.completions.create(
                model=try_model,
                messages=messages,
                temperature=0.7,
                max_tokens=1500,
            )
            return completion.choices[0].message.content
        except Exception as e:
            last_error = e
            error_str = str(e)
            # Only retry on 404 (model not found) errors
            if "404" in error_str or "not found" in error_str.lower():
                logging.warning(f"Model {try_model} not found, trying next variant...")
                continue
            # For other errors, raise immediately
            raise

    # If all models failed, raise the last error
    raise last_error


async def query_rag(
    message: str,
    session_id: Optional[str] = None,
    context_type: str = "general",
    context_source: Optional[str] = None,
    conversation_history: Optional[List[dict]] = None,
) -> ChatResponse:
    """Process a RAG query and generate a response."""
    openai_client = get_openai_client()

    # Search for relevant documents
    search_results = await search_knowledge_base(
        query=message,
        limit=5,
    )

    # Build context
    context = build_context_prompt(
        search_results=search_results,
        context_type=context_type,
        context_source=context_source,
    )

    # Build messages for chat completion
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    # Add context as system message
    if context:
        messages.append(
            {"role": "system", "content": f"Context:\n{context}"}
        )

    # Add conversation history
    if conversation_history:
        for msg in conversation_history[-10:]:  # Last 10 messages
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", ""),
            })

    # Add current user message
    messages.append({"role": "user", "content": message})

    # Generate response with model fallback support
    response_content = _generate_chat_completion(
        openai_client=openai_client,
        messages=messages,
        model=CHAT_MODEL,
    )

    # Build source references
    source_refs = [
        SourceReference(
            file=result.source_file,
            section=result.section,
            chunk_id=result.chunk_id,
            score=result.score,
        )
        for result in search_results[:3]  # Top 3 sources
    ]

    # Create response
    return ChatResponse(
        session_id=session_id or str(uuid4()),
        message=ChatMessage(
            id=str(uuid4()),
            role=MessageRole.ASSISTANT,
            content=response_content,
            source_references=source_refs,
        ),
        context_type=context_type,
        context_active=bool(context_source),
    )
