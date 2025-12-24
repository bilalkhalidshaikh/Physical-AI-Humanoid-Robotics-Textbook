"""Document chunking utilities for RAG ingestion.

Implements markdown-aware chunking with header splitting
to preserve document structure.
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Iterator
import tiktoken


@dataclass
class DocumentChunk:
    """A chunk of document text with metadata."""

    text: str
    source_file: str
    section: Optional[str]
    chunk_position: int
    chapter: Optional[str]
    module: Optional[str]
    has_code: bool
    word_count: int


def count_tokens(text: str, model: str = "text-embedding-3-small") -> int:
    """Count tokens in text using tiktoken."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def detect_module(file_path: str) -> Optional[str]:
    """Detect module from file path."""
    path_lower = file_path.lower()

    if "ros2" in path_lower or "ros-2" in path_lower:
        return "ros2"
    elif "gazebo" in path_lower:
        return "gazebo"
    elif "isaac" in path_lower:
        return "isaac_sim"
    elif "vla" in path_lower or "vision-language" in path_lower:
        return "vla"
    elif "manipulation" in path_lower:
        return "manipulation"
    elif "navigation" in path_lower:
        return "navigation"

    return None


def detect_chapter(file_path: str) -> Optional[str]:
    """Extract chapter name from file path."""
    # Look for module-X-name or chapter-X patterns
    match = re.search(r"(module-\d+-[\w-]+|chapter-\d+)", file_path, re.IGNORECASE)
    if match:
        return match.group(1)

    # Try to get parent directory name
    parts = file_path.replace("\\", "/").split("/")
    for part in reversed(parts[:-1]):  # Exclude filename
        if part and part != "docs":
            return part

    return None


def has_code_blocks(text: str) -> bool:
    """Check if text contains code blocks."""
    return "```" in text or bool(re.search(r"^\s{4,}\S", text, re.MULTILINE))


def split_by_headers(content: str) -> List[tuple]:
    """Split markdown content by headers, preserving hierarchy.

    Returns list of (header, content) tuples.
    """
    # Match markdown headers (# to ####)
    header_pattern = re.compile(r"^(#{1,4})\s+(.+)$", re.MULTILINE)

    sections = []
    last_end = 0
    current_header = None

    for match in header_pattern.finditer(content):
        # Save previous section
        if last_end > 0 or match.start() > 0:
            section_text = content[last_end : match.start()].strip()
            if section_text:
                sections.append((current_header, section_text))

        current_header = match.group(2).strip()
        last_end = match.end()

    # Don't forget the last section
    remaining = content[last_end:].strip()
    if remaining:
        sections.append((current_header, remaining))

    return sections


def chunk_text(
    text: str,
    max_tokens: int = 512,
    overlap_tokens: int = 50,
) -> List[str]:
    """Split text into chunks with token-based sizing and overlap.

    Args:
        text: Text to chunk
        max_tokens: Maximum tokens per chunk (default 512)
        overlap_tokens: Token overlap between chunks (default 50)

    Returns:
        List of text chunks
    """
    if not text.strip():
        return []

    # If text fits in one chunk, return as-is
    if count_tokens(text) <= max_tokens:
        return [text]

    chunks = []
    paragraphs = text.split("\n\n")

    current_chunk = []
    current_tokens = 0

    for para in paragraphs:
        para_tokens = count_tokens(para)

        # If single paragraph exceeds max, split it further
        if para_tokens > max_tokens:
            # Save current chunk if any
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = []
                current_tokens = 0

            # Split large paragraph by sentences
            sentences = re.split(r"(?<=[.!?])\s+", para)
            for sentence in sentences:
                sent_tokens = count_tokens(sentence)
                if current_tokens + sent_tokens > max_tokens:
                    if current_chunk:
                        chunks.append("\n\n".join(current_chunk))
                    current_chunk = [sentence]
                    current_tokens = sent_tokens
                else:
                    current_chunk.append(sentence)
                    current_tokens += sent_tokens
        # Normal case: add paragraph to current chunk
        elif current_tokens + para_tokens > max_tokens:
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))

            # Start new chunk with overlap from previous
            if chunks and overlap_tokens > 0:
                # Get last few tokens worth of text for overlap
                overlap_text = get_overlap_text(chunks[-1], overlap_tokens)
                if overlap_text:
                    current_chunk = [overlap_text, para]
                    current_tokens = count_tokens(overlap_text) + para_tokens
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk = [para]
                current_tokens = para_tokens
        else:
            current_chunk.append(para)
            current_tokens += para_tokens

    # Add final chunk
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks


def get_overlap_text(text: str, target_tokens: int) -> str:
    """Get the last N tokens worth of text for overlap."""
    words = text.split()
    overlap_words = []
    token_count = 0

    for word in reversed(words):
        word_tokens = count_tokens(word)
        if token_count + word_tokens > target_tokens:
            break
        overlap_words.insert(0, word)
        token_count += word_tokens

    return " ".join(overlap_words)


def chunk_markdown_document(
    content: str,
    source_file: str,
    max_tokens: int = 512,
    overlap_tokens: int = 50,
) -> Iterator[DocumentChunk]:
    """Chunk a markdown document preserving structure.

    Args:
        content: Markdown content
        source_file: Source file path
        max_tokens: Max tokens per chunk
        overlap_tokens: Overlap between chunks

    Yields:
        DocumentChunk objects
    """
    module = detect_module(source_file)
    chapter = detect_chapter(source_file)

    # Split by headers first
    sections = split_by_headers(content)

    chunk_position = 0

    for section_header, section_content in sections:
        # Chunk each section
        text_chunks = chunk_text(section_content, max_tokens, overlap_tokens)

        for chunk_text_content in text_chunks:
            # Prepend section header to first chunk of section
            if chunk_position == 0 or text_chunks.index(chunk_text_content) == 0:
                if section_header:
                    full_text = f"## {section_header}\n\n{chunk_text_content}"
                else:
                    full_text = chunk_text_content
            else:
                full_text = chunk_text_content

            yield DocumentChunk(
                text=full_text,
                source_file=source_file,
                section=section_header,
                chunk_position=chunk_position,
                chapter=chapter,
                module=module,
                has_code=has_code_blocks(chunk_text_content),
                word_count=len(chunk_text_content.split()),
            )

            chunk_position += 1


def process_file(
    file_path: str,
    base_path: str = "docs",
    max_tokens: int = 512,
    overlap_tokens: int = 50,
) -> List[DocumentChunk]:
    """Process a single markdown file into chunks.

    Args:
        file_path: Path to markdown file
        base_path: Base path to strip from source_file
        max_tokens: Max tokens per chunk
        overlap_tokens: Overlap between chunks

    Returns:
        List of DocumentChunk objects
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Create relative source path
    rel_path = file_path.replace("\\", "/")
    if base_path in rel_path:
        rel_path = rel_path.split(base_path + "/")[-1]

    return list(
        chunk_markdown_document(
            content=content,
            source_file=rel_path,
            max_tokens=max_tokens,
            overlap_tokens=overlap_tokens,
        )
    )
