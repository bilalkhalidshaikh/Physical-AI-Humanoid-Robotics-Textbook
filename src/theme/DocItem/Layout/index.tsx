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

  // Capture the original content when the component mounts
  useEffect(() => {
    // Small delay to ensure DOM is ready
    const timer = setTimeout(() => {
      const docContent = document.querySelector(".theme-doc-markdown");
      if (docContent instanceof HTMLElement) {
        setContentElement(docContent);
        if (!displayContent) {
          setDisplayContent(docContent.innerHTML);
        }
      }
    }, 100);

    return () => clearTimeout(timer);
  }, [displayContent]);

  // Store original content for fallback
  const [originalContent, setOriginalContent] = useState<string | null>(null);

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

  // Get original content for toolbar
  const getOriginalContent = () => {
    const docContent = document.querySelector(".theme-doc-markdown");
    if (docContent instanceof HTMLElement) {
      return docContent.innerHTML;
    }
    return "";
  };

  return (
    <>
      {/* Chapter Toolbar for translation/personalization */}
      <div style={{ marginBottom: "1rem" }}>
        <ChapterToolbar
          sourcePath={sourcePath}
          content={displayContent || getOriginalContent()}
          onContentChange={handleContentChange}
        />
      </div>

      {/* Original DocItem Layout */}
      <OriginalLayout {...props} />
    </>
  );
}
