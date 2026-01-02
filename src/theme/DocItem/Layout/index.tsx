import React, { useState, useEffect } from "react";
import OriginalLayout from "@theme-original/DocItem/Layout";
import { useDoc } from "@docusaurus/plugin-content-docs/client";
import type { Props } from "@theme/DocItem/Layout";
import ChapterToolbar from "../../../components/ChapterToolbar";

/**
 * Swizzled DocItem Layout that wraps the original with ChapterToolbar
 * for translation and personalization features.
 */
export default function DocItemLayout(props: Props): JSX.Element {
  const { metadata } = useDoc();
  const [displayContent, setDisplayContent] = useState<string | null>(null);
  const [contentElement, setContentElement] = useState<HTMLElement | null>(
    null
  );

  // Get the source file path for the toolbar
  const sourcePath = metadata.source?.replace(/^@site\//, "") || "";

  // Store original content for fallback - initialize as null for SSR
  const [originalContent, setOriginalContent] = useState<string | null>(null);

  // Capture the original content when the component mounts
  useEffect(() => {
    // Small delay to ensure DOM is ready
    const timer = setTimeout(() => {
      const docContent = document.querySelector(".theme-doc-markdown");
      if (docContent instanceof HTMLElement) {
        setContentElement(docContent);
        // Only set displayContent if not already set
        if (!displayContent) {
          setDisplayContent(docContent.innerHTML);
        }
      }
    }, 100);

    return () => clearTimeout(timer);
  }, [displayContent]);

  // Capture original content once on mount
  useEffect(() => {
    if (!originalContent) {
      const docContent = document.querySelector(".theme-doc-markdown");
      if (docContent instanceof HTMLElement && docContent.innerHTML.trim().length > 0) {
        setOriginalContent(docContent.innerHTML);
      }
    }
  }, [originalContent]);

  // Minimum length for valid translation (avoids garbage 3-char responses)
  const MIN_VALID_CONTENT_LENGTH = 50;

  // Handle content changes from the toolbar
  // Safety: Never set empty or garbage content to prevent vanishing bug
  const handleContentChange = (newContent: string) => {
    // Check if newContent is valid - must be at least 50 chars to be a real translation
    const isValidContent = newContent && newContent.trim().length >= MIN_VALID_CONTENT_LENGTH;

    if (contentElement) {
      if (isValidContent) {
        contentElement.innerHTML = newContent;
        setDisplayContent(newContent);
        console.log(`Translation applied: ${newContent.length} chars`);
      } else {
        // Fallback to original content - NEVER show blank or garbage
        console.log(`Translation fallback triggered - received ${newContent?.length || 0} chars (min ${MIN_VALID_CONTENT_LENGTH}), showing original`);
        if (originalContent && originalContent.trim().length > 0) {
          contentElement.innerHTML = originalContent;
          setDisplayContent(originalContent);
        }
        // If even originalContent is empty, do nothing (keep current DOM)
      }
    }
  };

  // Safe getter for toolbar content - only called after mount
  const getContentForToolbar = () => {
    // Return displayContent if we have it, otherwise return empty string for SSR
    // The toolbar will handle the empty case gracefully
    if (displayContent) {
      return displayContent;
    }
    // If we have originalContent from the effect, use it
    if (originalContent) {
      return originalContent;
    }
    // During SSR or before mount, return empty string
    return "";
  };

  // Check if we're running in the browser
  const [isBrowser, setIsBrowser] = useState(false);
  useEffect(() => {
    setIsBrowser(true);
  }, []);

  return (
    <>
      {/* Chapter Toolbar for translation/personalization */}
      <div style={{ marginBottom: "1rem" }}>
        <ChapterToolbar
          sourcePath={sourcePath}
          content={isBrowser ? getContentForToolbar() : ""}
          onContentChange={handleContentChange}
        />
      </div>

      {/* Original DocItem Layout */}
      <OriginalLayout {...props} />
    </>
  );
}
