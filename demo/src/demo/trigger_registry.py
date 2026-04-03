#!/usr/bin/env python3
"""
TriggerRegistry: Centralized trigger storage for demo

In production, this would be replaced by SUI smart contracts.
For demo, we use a local JSON file to store trigger metadata.

This allows us to test the complete flow without deploying smart contracts.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class TriggerRegistry:
    """
    Centralized trigger registry for demo purposes.

    Stores trigger metadata in a local JSON file.
    In production, this would be replaced by SUI blockchain smart contracts.

    Example:
        registry = TriggerRegistry()

        # Register a news trigger
        trigger_id = registry.register_trigger({
            "trigger_type": "news",
            "walrus_blob_id": "xyz123...",
            "data_hash": "abc...",
            "size_bytes": 4096,
            "articles_count": 5
        })

        # Get all news triggers
        news_triggers = registry.get_triggers(trigger_type="news")

        # Get specific trigger
        trigger = registry.get_trigger(trigger_id)
    """

    def __init__(self, registry_path: str = "data/trigger_registry.json"):
        """
        Initialize trigger registry.

        Args:
            registry_path: Path to JSON file for storing triggers
        """
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize empty registry if doesn't exist
        if not self.registry_path.exists():
            self._save_registry([])

    def register_trigger(self, trigger_data: Dict[str, Any]) -> str:
        """
        Register a new trigger and return its ID.

        Args:
            trigger_data: Trigger metadata dict

        Returns:
            trigger_id: Unique trigger identifier
        """
        triggers = self._load_registry()

        # Generate unique ID
        trigger_id = f"trigger_{len(triggers):06d}"
        trigger_data["trigger_id"] = trigger_id
        trigger_data["registered_at"] = datetime.now().isoformat()

        triggers.append(trigger_data)
        self._save_registry(triggers)

        print(f"[TriggerRegistry] ✓ Registered {trigger_data.get('trigger_type', 'unknown')} trigger: {trigger_id}")

        return trigger_id

    def get_triggers(
        self,
        trigger_type: Optional[str] = None,
        producer: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get triggers with optional filtering.

        Args:
            trigger_type: Filter by type ("news", "price", "signal")
            producer: Filter by producer ("news_pipeline", "agent_a", etc.)
            limit: Maximum number of triggers to return

        Returns:
            List of trigger metadata dicts
        """
        triggers = self._load_registry()

        # Apply filters
        if trigger_type:
            triggers = [t for t in triggers if t.get("trigger_type") == trigger_type]

        if producer:
            triggers = [t for t in triggers if t.get("producer") == producer]

        # Sort by registration time (newest first)
        triggers = sorted(
            triggers,
            key=lambda t: t.get("registered_at", ""),
            reverse=True
        )

        # Apply limit
        if limit:
            triggers = triggers[:limit]

        return triggers

    def get_trigger(self, trigger_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific trigger by ID.

        Args:
            trigger_id: Trigger identifier

        Returns:
            Trigger metadata dict or None if not found
        """
        triggers = self._load_registry()

        for trigger in triggers:
            if trigger.get("trigger_id") == trigger_id:
                return trigger

        return None

    def count_triggers(self, trigger_type: Optional[str] = None) -> int:
        """
        Count triggers, optionally filtered by type.

        Args:
            trigger_type: Optional filter by type

        Returns:
            Number of triggers
        """
        return len(self.get_triggers(trigger_type=trigger_type))

    def clear_registry(self):
        """Clear all triggers from registry (for testing)."""
        self._save_registry([])
        print("[TriggerRegistry] ✓ Registry cleared")

    # === Private Methods ===

    def _load_registry(self) -> List[Dict[str, Any]]:
        """Load triggers from JSON file."""
        try:
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_registry(self, triggers: List[Dict[str, Any]]):
        """Save triggers to JSON file."""
        with open(self.registry_path, 'w') as f:
            json.dump(triggers, f, indent=2)


# === Helper Functions ===

def create_news_trigger_entry(
    trigger_id: str,
    walrus_blob_id: str,
    data_hash: str,
    size_bytes: int,
    articles_count: int,
    producer: str = "news_pipeline"
) -> Dict[str, Any]:
    """
    Create a news trigger entry for registry.

    Args:
        trigger_id: Trigger ID from registry
        walrus_blob_id: Walrus blob ID
        data_hash: SHA-256 hash
        size_bytes: Data size
        articles_count: Number of articles
        producer: Producer identifier

    Returns:
        Trigger entry dict
    """
    return {
        "trigger_id": trigger_id,
        "trigger_type": "news",
        "walrus_blob_id": walrus_blob_id,
        "data_hash": data_hash,
        "size_bytes": size_bytes,
        "articles_count": articles_count,
        "producer": producer,
        "timestamp": datetime.now().isoformat()
    }


def create_price_trigger_entry(
    trigger_id: str,
    symbol: str,
    price_usd: float,
    oracle_source: str,
    confidence: Optional[float] = None,
    producer: str = "sui_price_pipeline"
) -> Dict[str, Any]:
    """
    Create a price trigger entry for registry.

    Args:
        trigger_id: Trigger ID from registry
        symbol: Asset symbol
        price_usd: Price in USD
        oracle_source: Oracle name
        confidence: Oracle confidence
        producer: Producer identifier

    Returns:
        Trigger entry dict
    """
    return {
        "trigger_id": trigger_id,
        "trigger_type": "price",
        "symbol": symbol,
        "price_usd": price_usd,
        "oracle_source": oracle_source,
        "confidence": confidence,
        "producer": producer,
        "timestamp": datetime.now().isoformat()
    }
