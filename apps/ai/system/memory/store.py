"""
Memory Store
============

Persistent storage for AI state, decisions, and learning data.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class MemoryType(str, Enum):
    """Types of memory entries"""

    DECISION = "decision"
    ACTION = "action"
    PATTERN = "pattern"
    STATE = "state"
    ALERT = "alert"
    LEARNING = "learning"


@dataclass
class MemoryEntry:
    """Single memory entry"""

    entry_id: str
    memory_type: MemoryType
    key: str
    value: dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
    tags: list[str] = field(default_factory=list)

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "memory_type": self.memory_type.value,
            "key": self.key,
            "value": self.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryEntry":
        return cls(
            entry_id=data["entry_id"],
            memory_type=MemoryType(data["memory_type"]),
            key=data["key"],
            value=data["value"],
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=(
                datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None
            ),
            tags=data.get("tags", []),
        )


class MemoryStore:
    """
    Persistent memory store for AI system.

    Stores:
    - Decision history
    - Action outcomes
    - Learned patterns
    - Worker states
    - Alert history

    Uses file-based storage initially, can be extended to use
    PostgreSQL or Redis for production.
    """

    _instance: "MemoryStore | None" = None

    def __new__(cls, storage_path: str | None = None) -> "MemoryStore":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, storage_path: str | None = None):
        if self._initialized:
            return

        self._storage_path = Path(storage_path or "data/ai_memory")
        self._storage_path.mkdir(parents=True, exist_ok=True)

        self._entries: dict[str, MemoryEntry] = {}
        self._by_type: dict[MemoryType, list[str]] = {t: [] for t in MemoryType}
        self._by_key: dict[str, list[str]] = {}

        self._load_from_disk()
        self._initialized = True

        logger.info(f"🧠 Memory Store initialized ({len(self._entries)} entries loaded)")

    def _get_file_path(self, memory_type: MemoryType) -> Path:
        return self._storage_path / f"{memory_type.value}.json"

    def _load_from_disk(self):
        """Load all memory from disk"""
        for memory_type in MemoryType:
            file_path = self._get_file_path(memory_type)
            if file_path.exists():
                try:
                    with open(file_path) as f:
                        data = json.load(f)

                    for entry_data in data:
                        entry = MemoryEntry.from_dict(entry_data)
                        if not entry.is_expired():
                            self._entries[entry.entry_id] = entry
                            self._by_type[memory_type].append(entry.entry_id)

                            if entry.key not in self._by_key:
                                self._by_key[entry.key] = []
                            self._by_key[entry.key].append(entry.entry_id)

                    logger.debug(f"Loaded {len(data)} {memory_type.value} entries")
                except Exception as e:
                    logger.error(f"Failed to load {memory_type.value}: {e}")

    def _save_to_disk(self, memory_type: MemoryType):
        """Save memory type to disk"""
        file_path = self._get_file_path(memory_type)

        entries = [
            self._entries[entry_id].to_dict()
            for entry_id in self._by_type[memory_type]
            if entry_id in self._entries
        ]

        try:
            with open(file_path, "w") as f:
                json.dump(entries, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save {memory_type.value}: {e}")

    def store(
        self,
        memory_type: MemoryType,
        key: str,
        value: dict[str, Any],
        ttl_hours: int | None = None,
        tags: list[str] | None = None,
    ) -> MemoryEntry:
        """
        Store a memory entry.

        Args:
            memory_type: Type of memory
            key: Identifier key
            value: Data to store
            ttl_hours: Time-to-live in hours (None = forever)
            tags: Optional tags for filtering

        Returns:
            Created MemoryEntry
        """
        entry_id = f"{memory_type.value}_{datetime.utcnow().timestamp()}"

        entry = MemoryEntry(
            entry_id=entry_id,
            memory_type=memory_type,
            key=key,
            value=value,
            expires_at=(datetime.utcnow() + timedelta(hours=ttl_hours) if ttl_hours else None),
            tags=tags or [],
        )

        self._entries[entry_id] = entry
        self._by_type[memory_type].append(entry_id)

        if key not in self._by_key:
            self._by_key[key] = []
        self._by_key[key].append(entry_id)

        # Persist to disk
        self._save_to_disk(memory_type)

        return entry

    def get(self, entry_id: str) -> MemoryEntry | None:
        """Get entry by ID"""
        entry = self._entries.get(entry_id)
        if entry and entry.is_expired():
            self._remove_entry(entry_id)
            return None
        return entry

    def get_by_key(self, key: str) -> list[MemoryEntry]:
        """Get all entries with a key"""
        entry_ids = self._by_key.get(key, [])
        entries = []

        for entry_id in entry_ids:
            entry = self.get(entry_id)
            if entry:
                entries.append(entry)

        return entries

    def get_by_type(
        self,
        memory_type: MemoryType,
        limit: int = 100,
        since: datetime | None = None,
    ) -> list[MemoryEntry]:
        """Get entries by type"""
        entry_ids = self._by_type.get(memory_type, [])
        entries = []

        for entry_id in reversed(entry_ids[-limit * 2 :]):  # Check more for expiry
            entry = self.get(entry_id)
            if entry:
                if since and entry.created_at < since:
                    continue
                entries.append(entry)
                if len(entries) >= limit:
                    break

        return entries

    def search(
        self,
        memory_type: MemoryType | None = None,
        tags: list[str] | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[MemoryEntry]:
        """Search entries with filters"""
        results = []

        if memory_type:
            entry_ids = self._by_type.get(memory_type, [])
        else:
            entry_ids = list(self._entries.keys())

        for entry_id in reversed(entry_ids):
            entry = self.get(entry_id)
            if not entry:
                continue

            if since and entry.created_at < since:
                continue

            if tags and not any(t in entry.tags for t in tags):
                continue

            results.append(entry)
            if len(results) >= limit:
                break

        return results

    def _remove_entry(self, entry_id: str):
        """Remove an entry"""
        entry = self._entries.pop(entry_id, None)
        if entry:
            if entry_id in self._by_type.get(entry.memory_type, []):
                self._by_type[entry.memory_type].remove(entry_id)
            if entry_id in self._by_key.get(entry.key, []):
                self._by_key[entry.key].remove(entry_id)

    def cleanup_expired(self) -> int:
        """Remove all expired entries"""
        expired_ids = [entry_id for entry_id, entry in self._entries.items() if entry.is_expired()]

        for entry_id in expired_ids:
            self._remove_entry(entry_id)

        # Save all types that had removals
        for memory_type in MemoryType:
            self._save_to_disk(memory_type)

        return len(expired_ids)

    def get_stats(self) -> dict[str, Any]:
        """Get memory store statistics"""
        stats = {
            "total_entries": len(self._entries),
            "by_type": {},
            "storage_path": str(self._storage_path),
        }

        for memory_type in MemoryType:
            count = len(self._by_type.get(memory_type, []))
            if count > 0:
                stats["by_type"][memory_type.value] = count

        return stats


# Convenience functions
def get_memory_store() -> MemoryStore:
    """Get the global memory store instance"""
    return MemoryStore()


def store_decision(
    decision_id: str,
    decision_data: dict[str, Any],
    ttl_hours: int = 720,  # 30 days
) -> MemoryEntry:
    """Store a decision in memory"""
    store = get_memory_store()
    return store.store(
        memory_type=MemoryType.DECISION,
        key=decision_id,
        value=decision_data,
        ttl_hours=ttl_hours,
        tags=["decision", decision_data.get("decision_type", "unknown")],
    )


def store_action(
    action_id: str,
    action_data: dict[str, Any],
    ttl_hours: int = 720,
) -> MemoryEntry:
    """Store an action in memory"""
    store = get_memory_store()
    return store.store(
        memory_type=MemoryType.ACTION,
        key=action_id,
        value=action_data,
        ttl_hours=ttl_hours,
        tags=["action", action_data.get("action_type", "unknown")],
    )


def get_recent_decisions(limit: int = 50) -> list[MemoryEntry]:
    """Get recent decisions"""
    store = get_memory_store()
    return store.get_by_type(MemoryType.DECISION, limit=limit)


def get_recent_actions(limit: int = 50) -> list[MemoryEntry]:
    """Get recent actions"""
    store = get_memory_store()
    return store.get_by_type(MemoryType.ACTION, limit=limit)
