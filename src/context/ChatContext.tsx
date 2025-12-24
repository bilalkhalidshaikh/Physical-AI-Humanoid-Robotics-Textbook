import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  ReactNode,
} from "react";
import { apiClient, type ChatMessage, type SourceReference } from "../lib/api-client";

type ContextType = "general" | "selection" | "chapter";

interface ChatSession {
  id: string;
  title: string | null;
  contextType: ContextType;
  contextSource: string | null;
  messageCount: number;
  createdAt: string;
  updatedAt: string;
}

interface SelectionContext {
  text: string;
  sourcePath: string;
}

interface ChatContextValue {
  // State
  messages: ChatMessage[];
  currentSessionId: string | null;
  sessions: ChatSession[];
  isLoading: boolean;
  error: string | null;

  // Context state
  contextType: ContextType;
  contextSource: string | null;
  selectionContext: SelectionContext | null;

  // UI State
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;

  // Actions
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => void;
  startNewSession: () => void;
  loadSession: (sessionId: string) => Promise<void>;
  deleteSession: (sessionId: string) => Promise<void>;
  fetchSessions: () => Promise<void>;

  // Context actions
  setSelectionContext: (selection: SelectionContext | null) => void;
  clearContext: () => void;
}

const ChatContext = createContext<ChatContextValue | undefined>(undefined);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);

  // Context state
  const [contextType, setContextType] = useState<ContextType>("general");
  const [contextSource, setContextSource] = useState<string | null>(null);
  const [selectionContext, setSelectionContextState] = useState<SelectionContext | null>(null);

  // Send a message
  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim()) return;

      setIsLoading(true);
      setError(null);

      // Add user message to UI immediately
      const userMessage: ChatMessage = {
        role: "user",
        content: content.trim(),
        source_references: [],
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);

      try {
        const response = await apiClient.chat({
          message: content.trim(),
          session_id: currentSessionId || undefined,
          context_type: contextType,
          context_source: contextSource || undefined,
        });

        // Update session ID if new
        if (!currentSessionId) {
          setCurrentSessionId(response.session_id);
        }

        // Add assistant response
        setMessages((prev) => [...prev, response.message]);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Failed to send message";
        setError(errorMessage);

        // Add error message to chat
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: `Sorry, I encountered an error: ${errorMessage}. Please try again.`,
            source_references: [],
          },
        ]);
      } finally {
        setIsLoading(false);
      }
    },
    [currentSessionId, contextType, contextSource]
  );

  // Clear messages and start fresh
  const clearMessages = useCallback(() => {
    setMessages([]);
    setCurrentSessionId(null);
    setError(null);
  }, []);

  // Start a new session
  const startNewSession = useCallback(() => {
    clearMessages();
    setContextType("general");
    setContextSource(null);
    setSelectionContextState(null);
  }, [clearMessages]);

  // Load an existing session
  const loadSession = useCallback(async (sessionId: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await apiClient.getChatSession(sessionId);

      setCurrentSessionId(data.session.id);
      setMessages(data.messages || []);
      setContextType(data.session.context_type || "general");
      setContextSource(data.session.context_source || null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to load session";
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Delete a session
  const deleteSession = useCallback(
    async (sessionId: string) => {
      try {
        await apiClient.deleteChatSession(sessionId);
        setSessions((prev) => prev.filter((s) => s.id !== sessionId));

        // If deleted current session, start fresh
        if (sessionId === currentSessionId) {
          startNewSession();
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Failed to delete session";
        setError(errorMessage);
      }
    },
    [currentSessionId, startNewSession]
  );

  // Fetch user's sessions
  const fetchSessions = useCallback(async () => {
    try {
      const data = await apiClient.getChatSessions();
      setSessions(
        data.sessions.map((s: any) => ({
          id: s.id,
          title: s.title,
          contextType: s.context_type || "general",
          contextSource: s.context_source,
          messageCount: s.message_count || 0,
          createdAt: s.created_at,
          updatedAt: s.updated_at,
        }))
      );
    } catch (err) {
      console.error("Failed to fetch sessions:", err);
    }
  }, []);

  // Set selection context
  const setSelectionContext = useCallback((selection: SelectionContext | null) => {
    setSelectionContextState(selection);
    if (selection) {
      setContextType("selection");
      setContextSource(selection.text);
    }
  }, []);

  // Clear context
  const clearContext = useCallback(() => {
    setContextType("general");
    setContextSource(null);
    setSelectionContextState(null);
  }, []);

  const value: ChatContextValue = {
    messages,
    currentSessionId,
    sessions,
    isLoading,
    error,
    contextType,
    contextSource,
    selectionContext,
    isOpen,
    setIsOpen,
    sendMessage,
    clearMessages,
    startNewSession,
    loadSession,
    deleteSession,
    fetchSessions,
    setSelectionContext,
    clearContext,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

export function useChat() {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error("useChat must be used within a ChatProvider");
  }
  return context;
}

// Export types
export type { ChatContextValue, ChatSession, SelectionContext, ContextType };
