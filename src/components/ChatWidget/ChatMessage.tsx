import React from "react";
import type { ChatMessage as ChatMessageType } from "../../lib/api-client";
import styles from "./styles.module.css";

interface Props {
  message: ChatMessageType;
}

export default function ChatMessage({ message }: Props) {
  const isUser = message.role === "user";
  const hasSourceReferences =
    message.source_references && message.source_references.length > 0;

  return (
    <div
      className={`${styles.message} ${
        isUser ? styles.userMessage : styles.assistantMessage
      }`}
    >
      <div className={styles.messageContent}>
        {/* Message text */}
        <div className={styles.messageText}>
          {message.content.split("\n").map((line, i) => (
            <p key={i}>{line || <br />}</p>
          ))}
        </div>

        {/* Source references */}
        {hasSourceReferences && (
          <div className={styles.sources}>
            <span className={styles.sourcesLabel}>Sources:</span>
            <div className={styles.sourcesList}>
              {message.source_references!.map((ref, index) => (
                <span key={index} className={styles.sourceTag}>
                  {ref.section || ref.file}
                  <span className={styles.sourceScore}>
                    {Math.round(ref.score * 100)}%
                  </span>
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
