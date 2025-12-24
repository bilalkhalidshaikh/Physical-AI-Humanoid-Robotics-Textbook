#!/usr/bin/env python3
"""Document ingestion script for Physical AI Book RAG.

Ingests markdown documents from docs/ into Qdrant vector database
with OpenAI embeddings.

Usage:
    python scripts/ingest.py                    # Full ingestion
    python scripts/ingest.py --incremental      # Only new/modified files
    python scripts/ingest.py --dry-run          # Preview without ingesting
    python scripts/ingest.py --clear            # Clear collection and re-ingest
"""

import argparse
import hashlib
import os
import sys
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from qdrant_client.http.models import Distance, VectorParams, PointStruct

# Add scripts directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chunking import DocumentChunk, process_file
from file_tracker import FileTracker, find_markdown_files

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "physical_ai_book")

EMBEDDING_MODEL = "text-embedding-004"
EMBEDDING_DIMENSIONS = 768  # Gemini text-embedding-004 dimensions

# Chunking configuration
MAX_TOKENS = 512
OVERLAP_TOKENS = 50

# Batch sizes
EMBEDDING_BATCH_SIZE = 100
UPSERT_BATCH_SIZE = 100


def get_openai_client() -> OpenAI:
    """Get OpenAI client."""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    return OpenAI(api_key=OPENAI_API_KEY)


def get_qdrant_client() -> QdrantClient:
    """Get Qdrant client."""
    if not QDRANT_URL:
        raise ValueError("QDRANT_URL environment variable is required")

    return QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
    )


def setup_collection(client: QdrantClient, recreate: bool = False) -> None:
    """Set up Qdrant collection with proper configuration."""
    collections = client.get_collections().collections
    exists = any(c.name == QDRANT_COLLECTION for c in collections)

    if exists and recreate:
        print(f"🗑️  Deleting existing collection: {QDRANT_COLLECTION}")
        client.delete_collection(QDRANT_COLLECTION)
        exists = False

    if not exists:
        print(f"📦 Creating collection: {QDRANT_COLLECTION}")
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=EMBEDDING_DIMENSIONS,
                distance=Distance.COSINE,
            ),
        )

        # Create payload indexes
        client.create_payload_index(
            collection_name=QDRANT_COLLECTION,
            field_name="source_file",
            field_schema=qdrant_models.PayloadSchemaType.KEYWORD,
        )
        client.create_payload_index(
            collection_name=QDRANT_COLLECTION,
            field_name="file_hash",
            field_schema=qdrant_models.PayloadSchemaType.KEYWORD,
        )
        client.create_payload_index(
            collection_name=QDRANT_COLLECTION,
            field_name="module",
            field_schema=qdrant_models.PayloadSchemaType.KEYWORD,
        )

        print("✅ Collection created with indexes")
    else:
        print(f"✅ Collection exists: {QDRANT_COLLECTION}")


def generate_embeddings(
    openai_client: OpenAI, texts: List[str]
) -> List[List[float]]:
    """Generate embeddings for a batch of texts."""
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )
    return [item.embedding for item in response.data]


def delete_file_vectors(
    qdrant_client: QdrantClient, source_file: str, file_hash: Optional[str] = None
) -> int:
    """Delete vectors for a specific file."""
    filter_conditions = [
        qdrant_models.FieldCondition(
            key="source_file",
            match=qdrant_models.MatchValue(value=source_file),
        )
    ]

    if file_hash:
        filter_conditions.append(
            qdrant_models.FieldCondition(
                key="file_hash",
                match=qdrant_models.MatchValue(value=file_hash),
            )
        )

    # Get count before deletion
    result = qdrant_client.scroll(
        collection_name=QDRANT_COLLECTION,
        scroll_filter=qdrant_models.Filter(must=filter_conditions),
        limit=1,
        with_payload=False,
        with_vectors=False,
    )

    # Delete matching points
    qdrant_client.delete(
        collection_name=QDRANT_COLLECTION,
        points_selector=qdrant_models.FilterSelector(
            filter=qdrant_models.Filter(must=filter_conditions)
        ),
    )

    return len(result[0]) if result[0] else 0


def ingest_chunks(
    qdrant_client: QdrantClient,
    openai_client: OpenAI,
    chunks: List[DocumentChunk],
    file_hash: str,
) -> int:
    """Ingest document chunks into Qdrant."""
    if not chunks:
        return 0

    points = []

    # Process in batches
    for i in range(0, len(chunks), EMBEDDING_BATCH_SIZE):
        batch = chunks[i : i + EMBEDDING_BATCH_SIZE]
        texts = [chunk.text for chunk in batch]

        # Generate embeddings
        embeddings = generate_embeddings(openai_client, texts)

        # Create points
        for chunk, embedding in zip(batch, embeddings):
            point_id = str(uuid4())
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "text": chunk.text,
                        "source_file": chunk.source_file,
                        "section": chunk.section,
                        "chunk_position": chunk.chunk_position,
                        "file_hash": file_hash,
                        "chapter": chunk.chapter,
                        "module": chunk.module,
                        "has_code": chunk.has_code,
                        "word_count": chunk.word_count,
                    },
                )
            )

    # Upsert in batches
    for i in range(0, len(points), UPSERT_BATCH_SIZE):
        batch = points[i : i + UPSERT_BATCH_SIZE]
        qdrant_client.upsert(collection_name=QDRANT_COLLECTION, points=batch)

    return len(points)


def compute_file_hash(file_path: str) -> str:
    """Compute MD5 hash of file contents."""
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def ingest_file(
    qdrant_client: QdrantClient,
    openai_client: OpenAI,
    file_path: str,
    tracker: FileTracker,
    base_path: str = "docs",
) -> int:
    """Ingest a single file into Qdrant."""
    file_hash = compute_file_hash(file_path)

    # Get relative path for source_file
    rel_path = file_path.replace("\\", "/")
    if base_path in rel_path:
        rel_path = rel_path.split(base_path + "/")[-1]

    # Delete existing vectors for this file
    delete_file_vectors(qdrant_client, rel_path)

    # Process file into chunks
    chunks = process_file(
        file_path,
        base_path=base_path,
        max_tokens=MAX_TOKENS,
        overlap_tokens=OVERLAP_TOKENS,
    )

    if not chunks:
        print(f"  ⚠️  No chunks generated for {rel_path}")
        return 0

    # Ingest chunks
    count = ingest_chunks(qdrant_client, openai_client, chunks, file_hash)

    # Update tracker
    tracker.mark_ingested(file_path, count, file_hash)

    return count


def run_ingestion(
    docs_path: str = "docs",
    incremental: bool = False,
    dry_run: bool = False,
    clear: bool = False,
) -> None:
    """Run the ingestion process."""
    print("🚀 Starting document ingestion...")
    print(f"   Collection: {QDRANT_COLLECTION}")
    print(f"   Incremental: {incremental}")
    print(f"   Dry run: {dry_run}")
    print()

    # Initialize clients
    qdrant_client = get_qdrant_client()
    openai_client = get_openai_client()
    tracker = FileTracker()

    # Setup collection
    if not dry_run:
        setup_collection(qdrant_client, recreate=clear)

    # Find all markdown files
    all_files = find_markdown_files(docs_path)
    print(f"📚 Found {len(all_files)} markdown files")

    # Determine files to process
    if incremental:
        categorized = tracker.get_files_to_process(all_files)
        files_to_process = categorized["new"] + categorized["modified"]
        deleted_files = categorized["deleted"]

        print(f"   New files: {len(categorized['new'])}")
        print(f"   Modified: {len(categorized['modified'])}")
        print(f"   Deleted: {len(deleted_files)}")
        print(f"   Unchanged: {len(categorized['unchanged'])}")

        # Handle deleted files
        if deleted_files and not dry_run:
            print("\n🗑️  Removing deleted files from index...")
            for file_path in deleted_files:
                delete_file_vectors(qdrant_client, file_path)
                tracker.mark_deleted(file_path)
                print(f"   Removed: {file_path}")
    else:
        files_to_process = all_files

    if not files_to_process:
        print("\n✅ No files to process")
        return

    print(f"\n📝 Processing {len(files_to_process)} files...")

    if dry_run:
        print("\n🔍 Dry run - would process:")
        for file_path in files_to_process:
            chunks = process_file(file_path, base_path=docs_path)
            rel_path = file_path.replace("\\", "/").split(docs_path + "/")[-1]
            print(f"   {rel_path}: {len(chunks)} chunks")
        return

    # Process files
    total_chunks = 0
    success_count = 0
    error_count = 0

    for i, file_path in enumerate(files_to_process, 1):
        rel_path = file_path.replace("\\", "/").split(docs_path + "/")[-1]

        try:
            print(f"[{i}/{len(files_to_process)}] {rel_path}...", end=" ")
            chunks = ingest_file(
                qdrant_client, openai_client, file_path, tracker, docs_path
            )
            print(f"✓ {chunks} chunks")
            total_chunks += chunks
            success_count += 1
        except Exception as e:
            print(f"✗ Error: {e}")
            error_count += 1

    # Summary
    print("\n" + "=" * 50)
    print("📊 Ingestion Summary")
    print("=" * 50)
    print(f"   Files processed: {success_count}")
    print(f"   Files failed: {error_count}")
    print(f"   Total chunks: {total_chunks}")

    # Get collection stats
    try:
        collection_info = qdrant_client.get_collection(QDRANT_COLLECTION)
        print(f"   Vectors in collection: {collection_info.points_count}")
    except Exception:
        pass

    print("\n✅ Ingestion complete!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Ingest documents into Qdrant for RAG"
    )
    parser.add_argument(
        "--docs-path",
        default="docs",
        help="Path to docs directory (default: docs)",
    )
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Only process new/modified files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without actually ingesting",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear collection before ingesting",
    )

    args = parser.parse_args()

    try:
        run_ingestion(
            docs_path=args.docs_path,
            incremental=args.incremental,
            dry_run=args.dry_run,
            clear=args.clear,
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  Ingestion interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
