"""File tracking for incremental ingestion.

Tracks file hashes to detect new/modified files
for efficient re-ingestion.
"""

import hashlib
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class FileRecord:
    """Record of a tracked file."""

    path: str
    hash: str
    last_modified: str
    chunk_count: int
    ingested_at: str


class FileTracker:
    """Tracks file states for incremental ingestion."""

    def __init__(self, tracker_file: str = ".ingestion_tracker.json"):
        self.tracker_file = tracker_file
        self.records: Dict[str, FileRecord] = {}
        self._load()

    def _load(self) -> None:
        """Load tracker state from file."""
        if os.path.exists(self.tracker_file):
            try:
                with open(self.tracker_file, "r") as f:
                    data = json.load(f)
                    self.records = {
                        path: FileRecord(**record)
                        for path, record in data.get("files", {}).items()
                    }
            except (json.JSONDecodeError, KeyError):
                self.records = {}

    def _save(self) -> None:
        """Save tracker state to file."""
        data = {
            "version": "1.0",
            "updated_at": datetime.now().isoformat(),
            "files": {path: asdict(record) for path, record in self.records.items()},
        }
        with open(self.tracker_file, "w") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def compute_hash(file_path: str) -> str:
        """Compute MD5 hash of file contents."""
        hasher = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def is_modified(self, file_path: str) -> bool:
        """Check if file has been modified since last ingestion."""
        rel_path = self._normalize_path(file_path)

        if rel_path not in self.records:
            return True

        current_hash = self.compute_hash(file_path)
        return current_hash != self.records[rel_path].hash

    def get_new_files(self, file_paths: List[str]) -> List[str]:
        """Get files that are new (not in tracker)."""
        new_files = []
        for path in file_paths:
            rel_path = self._normalize_path(path)
            if rel_path not in self.records:
                new_files.append(path)
        return new_files

    def get_modified_files(self, file_paths: List[str]) -> List[str]:
        """Get files that have been modified since last ingestion."""
        modified = []
        for path in file_paths:
            rel_path = self._normalize_path(path)
            if rel_path in self.records and self.is_modified(path):
                modified.append(path)
        return modified

    def get_deleted_files(self, current_files: List[str]) -> List[str]:
        """Get files that were tracked but no longer exist."""
        current_set = {self._normalize_path(p) for p in current_files}
        tracked_set = set(self.records.keys())
        return list(tracked_set - current_set)

    def get_files_to_process(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """Get categorized files that need processing.

        Returns dict with keys: 'new', 'modified', 'deleted', 'unchanged'
        """
        new_files = []
        modified_files = []
        unchanged_files = []

        for path in file_paths:
            rel_path = self._normalize_path(path)
            if rel_path not in self.records:
                new_files.append(path)
            elif self.is_modified(path):
                modified_files.append(path)
            else:
                unchanged_files.append(path)

        deleted_files = self.get_deleted_files(file_paths)

        return {
            "new": new_files,
            "modified": modified_files,
            "deleted": deleted_files,
            "unchanged": unchanged_files,
        }

    def mark_ingested(
        self, file_path: str, chunk_count: int, file_hash: Optional[str] = None
    ) -> None:
        """Mark a file as successfully ingested."""
        rel_path = self._normalize_path(file_path)
        now = datetime.now().isoformat()

        self.records[rel_path] = FileRecord(
            path=rel_path,
            hash=file_hash or self.compute_hash(file_path),
            last_modified=datetime.fromtimestamp(
                os.path.getmtime(file_path)
            ).isoformat(),
            chunk_count=chunk_count,
            ingested_at=now,
        )
        self._save()

    def mark_deleted(self, file_path: str) -> None:
        """Remove a file from tracking."""
        rel_path = self._normalize_path(file_path)
        if rel_path in self.records:
            del self.records[rel_path]
            self._save()

    def get_record(self, file_path: str) -> Optional[FileRecord]:
        """Get the record for a file."""
        rel_path = self._normalize_path(file_path)
        return self.records.get(rel_path)

    def get_all_records(self) -> Dict[str, FileRecord]:
        """Get all tracked file records."""
        return self.records.copy()

    def get_stats(self) -> Dict:
        """Get tracker statistics."""
        total_chunks = sum(r.chunk_count for r in self.records.values())
        return {
            "total_files": len(self.records),
            "total_chunks": total_chunks,
            "tracker_file": self.tracker_file,
        }

    def clear(self) -> None:
        """Clear all tracking data."""
        self.records = {}
        self._save()

    def _normalize_path(self, path: str) -> str:
        """Normalize path for consistent tracking."""
        # Convert to forward slashes and make relative
        normalized = path.replace("\\", "/")

        # Remove common prefixes
        for prefix in ["docs/", "./docs/", "."]:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix) :]
                break

        return normalized.lstrip("/")


def find_markdown_files(
    directory: str, extensions: Set[str] = {".md", ".mdx"}
) -> List[str]:
    """Find all markdown files in a directory recursively."""
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                files.append(os.path.join(root, filename))
    return files
