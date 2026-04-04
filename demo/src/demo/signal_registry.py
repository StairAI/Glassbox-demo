#!/usr/bin/env python3
"""
SignalRegistry: Centralized signal storage for demo

In production, this would be replaced by SUI smart contracts.
For demo, we use a local JSON file to store signal metadata.

This allows us to test the complete flow without deploying smart contracts.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class SignalRegistry:
    """
    Centralized signal registry for demo purposes.

    Stores signal metadata in a local JSON file.
    In production, this would be replaced by SUI blockchain smart contracts.

    Example:
        registry = SignalRegistry()

        # Register a news signal
        signal_id = registry.register_signal({
            "signal_type": "news",
            "walrus_blob_id": "xyz123...",
            "data_hash": "abc...",
            "size_bytes": 4096,
            "articles_count": 5
        })

        # Get all news signals
        news_signals = registry.get_signals(signal_type="news")

        # Get specific signal
        signal = registry.get_signal(signal_id)
    """

    def __init__(self, registry_path: str = "data/signal_registry.json"):
        """
        Initialize signal registry.

        Args:
            registry_path: Path to JSON file for storing signals
        """
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize empty registry if doesn't exist
        if not self.registry_path.exists():
            self._save_registry([])

    def register_signal(self, signal_data: Dict[str, Any]) -> str:
        """
        Register a new signal and return its ID.

        Args:
            signal_data: Signal metadata dict

        Returns:
            signal_id: Unique signal identifier
        """
        signals = self._load_registry()

        # Generate unique ID
        signal_id = f"signal_{len(signals):06d}"
        signal_data["signal_id"] = signal_id
        signal_data["registered_at"] = datetime.now().isoformat()

        signals.append(signal_data)
        self._save_registry(signals)

        print(f"[SignalRegistry] ✓ Registered {signal_data.get('signal_type', 'unknown')} signal: {signal_id}")

        return signal_id

    def get_signals(
        self,
        signal_type: Optional[str] = None,
        producer: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get signals with optional filtering.

        Args:
            signal_type: Filter by type ("news", "price", "insight")
            producer: Filter by producer ("news_pipeline", "agent_a", etc.)
            limit: Maximum number of signals to return

        Returns:
            List of signal metadata dicts
        """
        signals = self._load_registry()

        # Apply filters
        if signal_type:
            signals = [t for t in signals if t.get("signal_type") == signal_type]

        if producer:
            signals = [t for t in signals if t.get("producer") == producer]

        # Sort by registration time (newest first)
        signals = sorted(
            signals,
            key=lambda t: t.get("registered_at", ""),
            reverse=True
        )

        # Apply limit
        if limit:
            signals = signals[:limit]

        return signals

    def get_signal(self, signal_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific signal by ID.

        Args:
            signal_id: Signal identifier

        Returns:
            Signal metadata dict or None if not found
        """
        signals = self._load_registry()

        for signal in signals:
            if signal.get("signal_id") == signal_id:
                return signal

        return None

    def count_signals(self, signal_type: Optional[str] = None) -> int:
        """
        Count signals, optionally filtered by type.

        Args:
            signal_type: Optional filter by type

        Returns:
            Number of signals
        """
        return len(self.get_signals(signal_type=signal_type))

    def clear_registry(self):
        """Clear all signals from registry (for testing)."""
        self._save_registry([])
        print("[SignalRegistry] ✓ Registry cleared")

    # === Private Methods ===

    def _load_registry(self) -> List[Dict[str, Any]]:
        """Load signals from JSON file."""
        try:
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_registry(self, signals: List[Dict[str, Any]]):
        """Save signals to JSON file."""
        with open(self.registry_path, 'w') as f:
            json.dump(signals, f, indent=2)


# === Helper Functions ===

def create_news_signal_entry(
    signal_id: str,
    walrus_blob_id: str,
    data_hash: str,
    size_bytes: int,
    articles_count: int,
    producer: str = "news_pipeline"
) -> Dict[str, Any]:
    """
    Create a news signal entry for registry.

    Args:
        signal_id: Signal ID from registry
        walrus_blob_id: Walrus blob ID
        data_hash: SHA-256 hash
        size_bytes: Data size
        articles_count: Number of articles
        producer: Producer identifier

    Returns:
        Signal entry dict
    """
    return {
        "signal_id": signal_id,
        "signal_type": "news",
        "walrus_blob_id": walrus_blob_id,
        "data_hash": data_hash,
        "size_bytes": size_bytes,
        "articles_count": articles_count,
        "producer": producer,
        "timestamp": datetime.now().isoformat()
    }


def create_price_signal_entry(
    signal_id: str,
    symbol: str,
    price_usd: float,
    oracle_source: str,
    confidence: Optional[float] = None,
    producer: str = "sui_price_pipeline"
) -> Dict[str, Any]:
    """
    Create a price signal entry for registry.

    Args:
        signal_id: Signal ID from registry
        symbol: Asset symbol
        price_usd: Price in USD
        oracle_source: Oracle name
        confidence: Oracle confidence
        producer: Producer identifier

    Returns:
        Signal entry dict
    """
    return {
        "signal_id": signal_id,
        "signal_type": "price",
        "symbol": symbol,
        "price_usd": price_usd,
        "oracle_source": oracle_source,
        "confidence": confidence,
        "producer": producer,
        "timestamp": datetime.now().isoformat()
    }
