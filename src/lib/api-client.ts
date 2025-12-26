/**
 * RAG Backend API Client
 *
 * Handles all communication with the Python FastAPI backend
 * for chat, search, translation, and personalization.
 */

// const backendUrl = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";
const backendUrl = "https://bilalanjum-physical-ai-backend.hf.space";

interface ChatRequest {
  message: string;
  session_id?: string;
  context_type?: "general" | "selection" | "chapter";
  context_source?: string;
}

interface SourceReference {
  file: string;
  section?: string;
  chunk_id: string;
  score: number;
}

interface ChatMessage {
  id?: string;
  role: "user" | "assistant" | "system";
  content: string;
  source_references?: SourceReference[];
  created_at?: string;
}

interface ChatResponse {
  session_id: string;
  message: ChatMessage;
  context_type: string;
  context_active: boolean;
}

interface SearchRequest {
  query: string;
  limit?: number;
  filter_module?: string;
}

interface SearchResult {
  chunk_id: string;
  text: string;
  source_file: string;
  section?: string;
  score: number;
  module?: string;
}

interface SearchResponse {
  query: string;
  results: SearchResult[];
  total: number;
}

interface TranslateRequest {
  content: string;
  source_path: string;
  target_language?: string;
}

interface PersonalizeRequest {
  content: string;
  source_path: string;
  user_id: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      credentials: "include",
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Unknown error" }));
      throw new Error(error.detail || `Request failed: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string; qdrant: string }> {
    return this.request("/health");
  }

  /**
   * Send a chat message
   */
  async chat(request: ChatRequest): Promise<ChatResponse> {
    return this.request("/chat", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  /**
   * Search the knowledge base
   */
  async search(request: SearchRequest): Promise<SearchResponse> {
    return this.request("/search", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  /**
   * Translate content to Urdu
   */
  async translate(request: TranslateRequest): Promise<{ translated_content: string }> {
    const params = new URLSearchParams({
      content: request.content,
      source_path: request.source_path,
      target_language: request.target_language || "ur",
    });

    return this.request(`/translate?${params}`, {
      method: "POST",
    });
  }

  /**
   * Personalize content based on user background
   */
  async personalize(request: PersonalizeRequest): Promise<{ personalized_content: string }> {
    const params = new URLSearchParams({
      content: request.content,
      source_path: request.source_path,
      user_id: request.user_id,
    });

    return this.request(`/personalize?${params}`, {
      method: "POST",
    });
  }

  /**
   * Get chat sessions for authenticated user
   */
  async getChatSessions(): Promise<{ sessions: any[]; total: number }> {
    return this.request("/chat/sessions");
  }

  /**
   * Get a specific chat session with messages
   */
  async getChatSession(sessionId: string): Promise<any> {
    return this.request(`/chat/sessions/${sessionId}`);
  }

  /**
   * Delete a chat session
   */
  async deleteChatSession(sessionId: string): Promise<{ success: boolean }> {
    return this.request(`/chat/sessions/${sessionId}`, {
      method: "DELETE",
    });
  }
}

// Export singleton instance
export const apiClient = new ApiClient(backendUrl);

// Export types
export type {
  ChatRequest,
  ChatResponse,
  ChatMessage,
  SourceReference,
  SearchRequest,
  SearchResponse,
  SearchResult,
  TranslateRequest,
  PersonalizeRequest,
};
