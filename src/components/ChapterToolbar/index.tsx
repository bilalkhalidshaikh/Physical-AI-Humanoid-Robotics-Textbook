import React, { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { apiClient } from "../../lib/api-client";
import styles from "./styles.module.css";

interface Props {
  sourcePath: string;
  content: string;
  onContentChange: (content: string) => void;
}

type ViewMode = "original" | "translated" | "personalized";

export default function ChapterToolbar({
  sourcePath,
  content,
  onContentChange,
}: Props) {
  const { isAuthenticated, profile, setShowOnboarding } = useAuth();
  const [isTranslating, setIsTranslating] = useState(false);
  const [isPersonalizing, setIsPersonalizing] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>("original");
  const [originalContent] = useState(content);
  const [error, setError] = useState<string | null>(null);

  const handleTranslate = async () => {
    if (viewMode === "translated") {
      // Show original
      onContentChange(originalContent);
      setViewMode("original");
      return;
    }

    setIsTranslating(true);
    setError(null);

    try {
      const response = await apiClient.translate({
        content: originalContent,
        source_path: sourcePath,
        target_language: "ur",
      });

      // Validate response - never set empty content (prevents vanishing bug)
      const translatedContent = response?.translated_content;
      console.log("Translation response received:", {
        hasContent: !!translatedContent,
        contentLength: translatedContent?.length || 0,
        trimmedLength: translatedContent?.trim().length || 0,
      });

      if (translatedContent && translatedContent.trim().length > 0) {
        onContentChange(translatedContent);
        setViewMode("translated");
      } else {
        // API returned empty/null - keep original content visible
        console.log("Translation fallback: API returned empty content");
        setError("Translation returned empty content. Showing original.");
        // Explicitly restore original content as safety measure
        onContentChange(originalContent);
      }
    } catch (err) {
      // On error, keep showing original content
      console.log("Translation fallback: API error", err);
      setError(err instanceof Error ? err.message : "Translation failed");
      // Explicitly restore original content as safety measure
      onContentChange(originalContent);
    } finally {
      setIsTranslating(false);
    }
  };

  const handlePersonalize = async () => {
    if (!isAuthenticated) {
      return;
    }

    if (!profile?.onboardingCompleted) {
      setShowOnboarding(true);
      return;
    }

    if (viewMode === "personalized") {
      // Show original
      onContentChange(originalContent);
      setViewMode("original");
      return;
    }

    setIsPersonalizing(true);
    setError(null);

    try {
      const response = await apiClient.personalize({
        content: originalContent,
        source_path: sourcePath,
        user_id: profile.userId,
      });

      // Validate response - never set empty content (prevents vanishing bug)
      const personalizedContent = response?.personalized_content;
      console.log("Personalization response received:", {
        hasContent: !!personalizedContent,
        contentLength: personalizedContent?.length || 0,
        trimmedLength: personalizedContent?.trim().length || 0,
      });

      if (personalizedContent && personalizedContent.trim().length > 0) {
        onContentChange(personalizedContent);
        setViewMode("personalized");
      } else {
        // API returned empty/null - keep original content visible
        console.log("Personalization fallback: API returned empty content");
        setError("Personalization returned empty content. Showing original.");
        // Explicitly restore original content as safety measure
        onContentChange(originalContent);
      }
    } catch (err) {
      // On error, keep showing original content
      console.log("Personalization fallback: API error", err);
      setError(err instanceof Error ? err.message : "Personalization failed");
      // Explicitly restore original content as safety measure
      onContentChange(originalContent);
    } finally {
      setIsPersonalizing(false);
    }
  };

  const showOriginal = () => {
    onContentChange(originalContent);
    setViewMode("original");
  };

  return (
    <div className={styles.toolbar}>
      <div className={styles.actions}>
        {/* Translate button */}
        <button
          className={`${styles.button} ${
            viewMode === "translated" ? styles.active : ""
          }`}
          onClick={handleTranslate}
          disabled={isTranslating || isPersonalizing}
          title="Translate to Urdu"
        >
          {isTranslating ? (
            <span className={styles.spinner} />
          ) : (
            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
              <path d="M12.87 15.07l-2.54-2.51.03-.03c1.74-1.94 2.98-4.17 3.71-6.53H17V4h-7V2H8v2H1v2h11.17C11.5 7.92 10.44 9.75 9 11.35 8.07 10.32 7.3 9.19 6.69 8h-2c.73 1.63 1.73 3.17 2.98 4.56l-5.09 5.02L4 19l5-5 3.11 3.11.76-2.04zM18.5 10h-2L12 22h2l1.12-3h4.75L21 22h2l-4.5-12zm-2.62 7l1.62-4.33L19.12 17h-3.24z" />
            </svg>
          )}
          <span>
            {viewMode === "translated" ? "Show Original" : "اردو میں ترجمہ"}
          </span>
        </button>

        {/* Personalize button */}
        <button
          className={`${styles.button} ${
            viewMode === "personalized" ? styles.active : ""
          } ${!isAuthenticated ? styles.disabled : ""}`}
          onClick={handlePersonalize}
          disabled={isTranslating || isPersonalizing || !isAuthenticated}
          title={
            isAuthenticated
              ? "Personalize based on your background"
              : "Sign in to personalize content"
          }
        >
          {isPersonalizing ? (
            <span className={styles.spinner} />
          ) : (
            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
            </svg>
          )}
          <span>
            {viewMode === "personalized"
              ? "Show Original"
              : "Personalize for Me"}
          </span>
        </button>
      </div>

      {/* View mode indicator */}
      {viewMode !== "original" && (
        <div className={styles.viewIndicator}>
          <span>
            {viewMode === "translated" ? "🌐 Urdu Translation" : "✨ Personalized"}
          </span>
          <button onClick={showOriginal} className={styles.resetButton}>
            Show Original
          </button>
        </div>
      )}

      {/* Error message */}
      {error && <div className={styles.error}>{error}</div>}
    </div>
  );
}
