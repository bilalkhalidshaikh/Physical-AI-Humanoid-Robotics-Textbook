"""RAG Agent with search_knowledge_base tool.

This module defines the RAG agent that uses OpenAI function calling
to search the knowledge base and generate contextual responses.
"""

import os
import json
from typing import List, Optional
from dotenv import load_dotenv
from openai import OpenAI

from rag_service import (
    search_knowledge_base,
    get_openai_client,
    CHAT_MODEL,
    _is_gemini_endpoint,
    GEMINI_MODEL_VARIANTS,
)
from models.chat import SearchResult

load_dotenv()


# Tool definition for search_knowledge_base
SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "search_knowledge_base",
        "description": "Search the Physical AI & Humanoid Robotics textbook for relevant content. Use this to find information about ROS 2, Gazebo, Isaac Sim, manipulation, navigation, and VLA models.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to find relevant textbook content",
                },
                "filter_module": {
                    "type": "string",
                    "description": "Optional filter by module: 'ros2', 'gazebo', 'isaac_sim', 'vla', 'manipulation', 'navigation'",
                    "enum": ["ros2", "gazebo", "isaac_sim", "vla", "manipulation", "navigation"],
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 5)",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
}


# System prompt for the agent
AGENT_SYSTEM_PROMPT = """You are an expert AI assistant for the "Physical AI & Humanoid Robotics" textbook.
Your role is to help students learn about robotics concepts including ROS 2, Gazebo simulation,
Isaac Sim, manipulation, navigation, and vision-language-action models.

You have access to a search_knowledge_base tool that retrieves relevant content from the textbook.

Guidelines:
1. ALWAYS use the search_knowledge_base tool to find relevant information before answering
2. Base your answers on the retrieved content from the textbook
3. If the search doesn't return relevant results, say so clearly
4. Use technical terminology accurately
5. Provide code examples when appropriate
6. Reference specific sections when citing information
7. Be encouraging and educational in tone

When given context about a specific text selection, focus your answer on that selection."""


class RAGAgent:
    """RAG Agent with tool calling capabilities."""

    def __init__(self):
        self.client = get_openai_client()
        self.tools = [SEARCH_TOOL]

    async def _execute_tool(self, tool_name: str, arguments: dict) -> str:
        """Execute a tool and return the result as a string."""
        if tool_name == "search_knowledge_base":
            results = await search_knowledge_base(
                query=arguments.get("query", ""),
                limit=arguments.get("limit", 5),
                filter_module=arguments.get("filter_module"),
            )
            return self._format_search_results(results)
        return f"Unknown tool: {tool_name}"

    def _format_search_results(self, results: List[SearchResult]) -> str:
        """Format search results for the LLM context."""
        if not results:
            return "No relevant content found in the textbook."

        formatted = []
        for i, result in enumerate(results, 1):
            source_info = f"[Source: {result.source_file}"
            if result.section:
                source_info += f" - {result.section}"
            source_info += f" (score: {result.score:.2f})]"

            formatted.append(f"{i}. {source_info}\n{result.text}\n")

        return "\n".join(formatted)

    def _generate_completion(
        self,
        messages: List[dict],
        tools: Optional[List[dict]] = None,
    ) -> dict:
        """Generate completion with model fallback for Gemini."""
        models_to_try = [CHAT_MODEL]

        if _is_gemini_endpoint():
            for variant in GEMINI_MODEL_VARIANTS:
                if variant != CHAT_MODEL and variant not in models_to_try:
                    models_to_try.append(variant)

        last_error = None
        for try_model in models_to_try:
            try:
                kwargs = {
                    "model": try_model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1500,
                }
                if tools:
                    kwargs["tools"] = tools
                    kwargs["tool_choice"] = "auto"

                completion = self.client.chat.completions.create(**kwargs)
                return completion
            except Exception as e:
                last_error = e
                error_str = str(e)
                if "404" in error_str or "not found" in error_str.lower():
                    continue
                raise

        raise last_error

    async def run(
        self,
        message: str,
        context_type: str = "general",
        context_source: Optional[str] = None,
        conversation_history: Optional[List[dict]] = None,
    ) -> tuple[str, List[SearchResult]]:
        """
        Run the agent to answer a question.

        Returns:
            Tuple of (response_content, source_references)
        """
        # Build initial messages
        messages = [{"role": "system", "content": AGENT_SYSTEM_PROMPT}]

        # Add selection context if provided
        if context_type == "selection" and context_source:
            messages.append({
                "role": "system",
                "content": f"The user has selected the following text and is asking about it:\n---\n{context_source}\n---",
            })

        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-10:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", ""),
                })

        # Add current user message
        messages.append({"role": "user", "content": message})

        # First call - let the model decide to use tools
        collected_results: List[SearchResult] = []

        try:
            completion = self._generate_completion(messages, tools=self.tools)
            response_message = completion.choices[0].message

            # Check if the model wants to use tools
            if response_message.tool_calls:
                # Add assistant message with tool calls
                messages.append(response_message.model_dump())

                # Execute each tool call
                for tool_call in response_message.tool_calls:
                    tool_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

                    # Execute the tool
                    if tool_name == "search_knowledge_base":
                        results = await search_knowledge_base(
                            query=arguments.get("query", ""),
                            limit=arguments.get("limit", 5),
                            filter_module=arguments.get("filter_module"),
                        )
                        collected_results.extend(results)
                        tool_result = self._format_search_results(results)
                    else:
                        tool_result = f"Unknown tool: {tool_name}"

                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result,
                    })

                # Second call - generate final response with tool results
                completion = self._generate_completion(messages)
                response_content = completion.choices[0].message.content
            else:
                # Model didn't use tools, return direct response
                response_content = response_message.content

        except Exception as e:
            # Fallback: search directly and generate response
            results = await search_knowledge_base(query=message, limit=5)
            collected_results = results

            # Build context from results
            context = self._format_search_results(results)
            messages.append({
                "role": "system",
                "content": f"Relevant textbook content:\n{context}",
            })

            completion = self._generate_completion(messages)
            response_content = completion.choices[0].message.content

        return response_content, collected_results[:3]


# Singleton agent instance
_agent: Optional[RAGAgent] = None


def get_agent() -> RAGAgent:
    """Get or create the RAG agent instance."""
    global _agent
    if _agent is None:
        _agent = RAGAgent()
    return _agent


async def agent_query(
    message: str,
    session_id: Optional[str] = None,
    context_type: str = "general",
    context_source: Optional[str] = None,
    conversation_history: Optional[List[dict]] = None,
) -> tuple[str, List[SearchResult]]:
    """
    Query the RAG agent.

    This is the main entry point for agent-based queries.
    """
    agent = get_agent()
    return await agent.run(
        message=message,
        context_type=context_type,
        context_source=context_source,
        conversation_history=conversation_history,
    )
