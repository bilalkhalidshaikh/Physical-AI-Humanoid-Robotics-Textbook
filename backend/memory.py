"""Conversation memory management for chat sessions."""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4


@dataclass
class Message:
    """A single message in a conversation."""

    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)


@dataclass
class ConversationSession:
    """A conversation session with memory."""

    session_id: str
    messages: List[Message] = field(default_factory=list)
    context_type: str = "general"
    context_source: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def add_message(self, role: str, content: str, metadata: Dict = None) -> Message:
        """Add a message to the conversation."""
        msg = Message(
            role=role,
            content=content,
            metadata=metadata or {},
        )
        self.messages.append(msg)
        self.updated_at = datetime.now()
        return msg

    def get_history(self, max_messages: int = 10) -> List[Dict]:
        """Get recent message history for context."""
        recent = self.messages[-max_messages:] if max_messages else self.messages
        return [
            {"role": msg.role, "content": msg.content}
            for msg in recent
            if msg.role != "system"
        ]

    def get_context_summary(self) -> str:
        """Get a summary of the conversation context."""
        if self.context_type == "selection":
            return f"Selection context: {self.context_source[:100]}..."
        elif self.context_type == "chapter":
            return f"Chapter context: {self.context_source}"
        return "General context"


class ConversationMemory:
    """In-memory conversation storage for active sessions."""

    def __init__(self, max_sessions: int = 1000):
        self._sessions: Dict[str, ConversationSession] = {}
        self._user_sessions: Dict[str, List[str]] = defaultdict(list)
        self._max_sessions = max_sessions

    def create_session(
        self,
        user_id: Optional[str] = None,
        context_type: str = "general",
        context_source: Optional[str] = None,
    ) -> ConversationSession:
        """Create a new conversation session."""
        session_id = str(uuid4())
        session = ConversationSession(
            session_id=session_id,
            context_type=context_type,
            context_source=context_source,
        )

        self._sessions[session_id] = session

        if user_id:
            self._user_sessions[user_id].append(session_id)

        # Cleanup old sessions if needed
        self._cleanup_if_needed()

        return session

    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Get a session by ID."""
        return self._sessions.get(session_id)

    def get_or_create_session(
        self,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        context_type: str = "general",
        context_source: Optional[str] = None,
    ) -> ConversationSession:
        """Get an existing session or create a new one."""
        if session_id:
            session = self.get_session(session_id)
            if session:
                # Update context if provided
                if context_type != "general":
                    session.context_type = context_type
                    session.context_source = context_source
                return session

        return self.create_session(
            user_id=user_id,
            context_type=context_type,
            context_source=context_source,
        )

    def get_user_sessions(self, user_id: str) -> List[ConversationSession]:
        """Get all sessions for a user."""
        session_ids = self._user_sessions.get(user_id, [])
        return [
            self._sessions[sid]
            for sid in session_ids
            if sid in self._sessions
        ]

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]

            # Remove from user sessions
            for user_sessions in self._user_sessions.values():
                if session_id in user_sessions:
                    user_sessions.remove(session_id)

            return True
        return False

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Dict = None,
    ) -> Optional[Message]:
        """Add a message to a session."""
        session = self.get_session(session_id)
        if session:
            return session.add_message(role, content, metadata)
        return None

    def get_history(
        self, session_id: str, max_messages: int = 10
    ) -> List[Dict]:
        """Get message history for a session."""
        session = self.get_session(session_id)
        if session:
            return session.get_history(max_messages)
        return []

    def _cleanup_if_needed(self) -> None:
        """Remove oldest sessions if over limit."""
        if len(self._sessions) <= self._max_sessions:
            return

        # Sort by updated_at and remove oldest
        sorted_sessions = sorted(
            self._sessions.items(),
            key=lambda x: x[1].updated_at,
        )

        # Remove oldest 10%
        to_remove = len(sorted_sessions) // 10
        for session_id, _ in sorted_sessions[:to_remove]:
            self.delete_session(session_id)


# Global memory instance
memory = ConversationMemory()
