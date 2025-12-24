import React, { useState, useEffect, useCallback } from "react";
import { useChat } from "../../context/ChatContext";
import styles from "./styles.module.css";

interface PopupPosition {
  x: number;
  y: number;
}

export default function TextSelectionHandler() {
  const { setSelectionContext, setIsOpen } = useChat();
  const [showPopup, setShowPopup] = useState(false);
  const [position, setPosition] = useState<PopupPosition>({ x: 0, y: 0 });
  const [selectedText, setSelectedText] = useState("");

  const handleMouseUp = useCallback((e: MouseEvent) => {
    // Ignore if clicking inside chat widget or modal
    const target = e.target as HTMLElement;
    if (
      target.closest("[data-chat-widget]") ||
      target.closest("[data-modal]")
    ) {
      return;
    }

    const selection = window.getSelection();
    const text = selection?.toString().trim();

    if (text && text.length > 10 && text.length < 2000) {
      // Get selection position
      const range = selection?.getRangeAt(0);
      const rect = range?.getBoundingClientRect();

      if (rect) {
        setPosition({
          x: rect.left + rect.width / 2,
          y: rect.top - 10,
        });
        setSelectedText(text);
        setShowPopup(true);
      }
    } else {
      setShowPopup(false);
    }
  }, []);

  const handleClick = useCallback((e: MouseEvent) => {
    const target = e.target as HTMLElement;
    if (!target.closest(`.${styles.popup}`)) {
      setShowPopup(false);
    }
  }, []);

  useEffect(() => {
    document.addEventListener("mouseup", handleMouseUp);
    document.addEventListener("click", handleClick);

    return () => {
      document.removeEventListener("mouseup", handleMouseUp);
      document.removeEventListener("click", handleClick);
    };
  }, [handleMouseUp, handleClick]);

  const handleAskAbout = () => {
    // Get current page path for source
    const sourcePath = window.location.pathname;

    setSelectionContext({
      text: selectedText,
      sourcePath,
    });

    setIsOpen(true);
    setShowPopup(false);

    // Clear selection
    window.getSelection()?.removeAllRanges();
  };

  if (!showPopup) return null;

  return (
    <div
      className={styles.popup}
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
      }}
    >
      <button className={styles.askButton} onClick={handleAskAbout}>
        <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
          <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z" />
        </svg>
        Ask about this
      </button>
    </div>
  );
}
