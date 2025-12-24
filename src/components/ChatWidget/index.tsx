import React, { useState, useRef, useEffect } from "react";
import { useChat } from "../../context/ChatContext";
import { useAuth } from "../../context/AuthContext";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import styles from "./styles.module.css";

export default function ChatWidget() {
  const {
    messages,
    isLoading,
    error,
    isOpen,
    setIsOpen,
    sendMessage,
    startNewSession,
    contextType,
    contextSource,
    clearContext,
    sessions,
    fetchSessions,
    loadSession,
  } = useChat();

  const { isAuthenticated } = useAuth();
  const [showHistory, setShowHistory] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Load sessions when history panel opens
  useEffect(() => {
    if (showHistory && isAuthenticated) {
      fetchSessions();
    }
  }, [showHistory, isAuthenticated, fetchSessions]);

  const handleToggle = () => {
    setIsOpen(!isOpen);
    if (!isOpen) {
      setShowHistory(false);
    }
  };

  const handleSend = (message: string) => {
    sendMessage(message);
  };

  const handleNewChat = () => {
    startNewSession();
    setShowHistory(false);
  };

  const handleSessionSelect = (sessionId: string) => {
    loadSession(sessionId);
    setShowHistory(false);
  };

  return (
    <div className={styles.container}>
      {/* Toggle Button */}
      <button
        className={`${styles.toggleButton} ${isOpen ? styles.open : ""}`}
        onClick={handleToggle}
        aria-label={isOpen ? "Close chat" : "Open chat"}
      >
        {isOpen ? (
          <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
          </svg>
        ) : (
          <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
            <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z" />
          </svg>
        )}
      </button>

      {/* Chat Panel */}
      {isOpen && (
        <div className={styles.panel}>
          {/* Header */}
          <div className={styles.header}>
            <div className={styles.headerLeft}>
              <h3 className={styles.title}>AI Assistant</h3>
              {contextType !== "general" && (
                <span className={styles.contextBadge}>
                  {contextType === "selection" ? "Selection" : "Chapter"}
                </span>
              )}
            </div>
            <div className={styles.headerActions}>
              {isAuthenticated && (
                <button
                  className={styles.headerButton}
                  onClick={() => setShowHistory(!showHistory)}
                  title="Chat history"
                >
                  <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                    <path d="M13 3c-4.97 0-9 4.03-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42C8.27 19.99 10.51 21 13 21c4.97 0 9-4.03 9-9s-4.03-9-9-9zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z" />
                  </svg>
                </button>
              )}
              <button
                className={styles.headerButton}
                onClick={handleNewChat}
                title="New chat"
              >
                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                  <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" />
                </svg>
              </button>
            </div>
          </div>

          {/* Context Banner */}
          {contextType !== "general" && contextSource && (
            <div className={styles.contextBanner}>
              <span className={styles.contextText}>
                {contextType === "selection"
                  ? `Asking about: "${contextSource.slice(0, 50)}..."`
                  : `Context: ${contextSource}`}
              </span>
              <button
                className={styles.clearContext}
                onClick={clearContext}
              >
                Clear
              </button>
            </div>
          )}

          {/* History Panel */}
          {showHistory && (
            <div className={styles.historyPanel}>
              <div className={styles.historyHeader}>
                <span>Recent Chats</span>
                <button onClick={() => setShowHistory(false)}>×</button>
              </div>
              <div className={styles.historyList}>
                {sessions.length === 0 ? (
                  <p className={styles.emptyHistory}>No previous chats</p>
                ) : (
                  sessions.map((session) => (
                    <button
                      key={session.id}
                      className={styles.historyItem}
                      onClick={() => handleSessionSelect(session.id)}
                    >
                      <span className={styles.historyTitle}>
                        {session.title || "Untitled chat"}
                      </span>
                      <span className={styles.historyMeta}>
                        {session.messageCount} messages
                      </span>
                    </button>
                  ))
                )}
              </div>
            </div>
          )}

          {/* Messages */}
          <div className={styles.messages}>
            {messages.length === 0 && (
              <div className={styles.welcome}>
                <p>Hi! I'm your AI assistant for the Physical AI & Humanoid Robotics textbook.</p>
                <p>Ask me anything about ROS 2, Gazebo, Isaac Sim, or robotics concepts!</p>
              </div>
            )}
            {messages.map((msg, index) => (
              <ChatMessage key={index} message={msg} />
            ))}
            {isLoading && (
              <div className={styles.loading}>
                <span className={styles.loadingDot} />
                <span className={styles.loadingDot} />
                <span className={styles.loadingDot} />
              </div>
            )}
            {error && <div className={styles.error}>{error}</div>}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <ChatInput onSend={handleSend} disabled={isLoading} />
        </div>
      )}
    </div>
  );
}
