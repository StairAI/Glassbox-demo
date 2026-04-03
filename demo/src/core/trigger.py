#!/usr/bin/env python3
"""
Trigger Abstraction: Unified interface for agent inputs

All agent inputs are triggers - lightweight references to data.
Triggers can reference data stored in different locations:
- NewsTrigger: Full data on Walrus, metadata on SUI
- PriceTrigger: Data already on SUI (from oracle)
- SignalTrigger: Agent outputs (also on SUI)

This provides a unified interface for agents to consume data regardless of
where the actual data is stored.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class Trigger(ABC):
    """
    Base class for all agent triggers.

    A trigger is a lightweight reference to data that can trigger agent execution.
    The actual data may be stored on Walrus, on SUI blockchain, or elsewhere.

    All agents receive List[Trigger] as input, providing a unified interface.
    """

    trigger_type: str           # "news", "price", "signal"
    timestamp: datetime
    object_id: str              # SUI object ID where trigger metadata is stored
    producer: str               # Who created this trigger

    @abstractmethod
    def fetch_full_data(self) -> Dict[str, Any]:
        """
        Fetch the full data referenced by this trigger.

        This is the key abstraction: regardless of where data is stored,
        agents can fetch it through this unified interface.
        """
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert trigger to dictionary."""
        return {
            "trigger_type": self.trigger_type,
            "timestamp": self.timestamp.isoformat(),
            "object_id": self.object_id,
            "producer": self.producer
        }


@dataclass
class NewsTrigger(Trigger):
    """
    Trigger for news data.

    Full data is stored on Walrus (cost-efficient for large data).
    Only metadata is stored on SUI blockchain.

    Architecture:
        SUI: {blob_id, hash, size} (< 500 bytes)
        Walrus: {full articles} (4KB+)
    """

    walrus_blob_id: str         # Reference to Walrus storage
    data_hash: str              # SHA-256 for integrity verification
    size_bytes: int             # Size of full data
    articles_count: int         # Number of articles (preview info)

    def __init__(
        self,
        object_id: str,
        walrus_blob_id: str,
        data_hash: str,
        size_bytes: int,
        articles_count: int,
        timestamp: datetime,
        producer: str = "news_pipeline"
    ):
        super().__init__(
            trigger_type="news",
            timestamp=timestamp,
            object_id=object_id,
            producer=producer
        )
        self.walrus_blob_id = walrus_blob_id
        self.data_hash = data_hash
        self.size_bytes = size_bytes
        self.articles_count = articles_count

    def fetch_full_data(self, walrus_client=None) -> Dict[str, Any]:
        """
        Fetch full news data from Walrus.

        Args:
            walrus_client: Optional WalrusClient to use. If None, creates a new one.

        Returns:
            Dict with structure:
            {
                "articles": [...],
                "fetch_timestamp": "...",
                "total_count": 5
            }
        """
        from src.storage.walrus_client import WalrusClient, WalrusHelper
        import os

        if walrus_client is None:
            # Create client based on environment config
            walrus_enabled = os.getenv("WALRUS_ENABLED", "false").lower() == "true"
            client = WalrusClient(
                publisher_url=os.getenv("WALRUS_PUBLISHER_URL"),
                aggregator_url=os.getenv("WALRUS_AGGREGATOR_URL"),
                simulated=not walrus_enabled
            )
        else:
            client = walrus_client

        try:
            # Fetch from Walrus
            data = WalrusHelper.fetch_json(client, self.walrus_blob_id)

            # Verify integrity
            import hashlib
            computed_hash = hashlib.sha256(
                json.dumps(data, sort_keys=True).encode()
            ).hexdigest()

            if computed_hash != self.data_hash:
                raise ValueError(
                    f"Data integrity check failed! "
                    f"Expected hash: {self.data_hash}, "
                    f"Computed hash: {computed_hash}"
                )

            return data

        except Exception as e:
            raise RuntimeError(f"Failed to fetch news data from Walrus: {e}") from e

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        base = super().to_dict()
        base.update({
            "walrus_blob_id": self.walrus_blob_id,
            "data_hash": self.data_hash[:16] + "...",  # Truncate for display
            "size_bytes": self.size_bytes,
            "articles_count": self.articles_count
        })
        return base


@dataclass
class PriceTrigger(Trigger):
    """
    Trigger for price data from on-chain oracles.

    Data is already on SUI blockchain (posted by oracles like Pyth/Switchboard).
    No need for Walrus - data is small and already on-chain.

    Architecture:
        SUI: {symbol, price, oracle_source} (< 200 bytes)
    """

    symbol: str                 # "BTC", "ETH", "SUI"
    price_usd: float            # Current price in USD
    oracle_source: str          # "pyth", "switchboard", "custom"
    confidence: Optional[float] = None  # Oracle confidence interval

    def __init__(
        self,
        object_id: str,
        symbol: str,
        price_usd: float,
        oracle_source: str,
        timestamp: datetime,
        confidence: Optional[float] = None,
        producer: str = "sui_price_pipeline"
    ):
        super().__init__(
            trigger_type="price",
            timestamp=timestamp,
            object_id=object_id,
            producer=producer
        )
        self.symbol = symbol
        self.price_usd = price_usd
        self.oracle_source = oracle_source
        self.confidence = confidence

    def fetch_full_data(self) -> Dict[str, Any]:
        """
        Fetch price data.

        Price data is already in the trigger (small enough to store on-chain).
        No need to fetch from external storage.

        Returns:
            Dict with price information
        """
        return {
            "symbol": self.symbol,
            "price_usd": self.price_usd,
            "oracle_source": self.oracle_source,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat()
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        base = super().to_dict()
        base.update({
            "symbol": self.symbol,
            "price_usd": self.price_usd,
            "oracle_source": self.oracle_source,
            "confidence": self.confidence
        })
        return base


@dataclass
class SignalTrigger(Trigger):
    """
    Trigger for signals from other agents.

    Agent outputs (like sentiment signals or investment signals) are stored on-chain.
    These can trigger downstream agents.

    Architecture:
        SUI: {signal_type, value, confidence} (< 500 bytes)
        Walrus: {reasoning_trace} (if needed for transparency)
    """

    signal_type: str            # "sentiment", "investment", "portfolio"
    signal_value: Dict[str, Any]  # The actual signal data
    confidence: float           # Agent's confidence in this signal
    walrus_trace_id: Optional[str] = None  # Reasoning trace on Walrus

    def __init__(
        self,
        object_id: str,
        signal_type: str,
        signal_value: Dict[str, Any],
        confidence: float,
        timestamp: datetime,
        producer: str,
        walrus_trace_id: Optional[str] = None
    ):
        super().__init__(
            trigger_type="signal",
            timestamp=timestamp,
            object_id=object_id,
            producer=producer
        )
        self.signal_type = signal_type
        self.signal_value = signal_value
        self.confidence = confidence
        self.walrus_trace_id = walrus_trace_id

    def fetch_full_data(self) -> Dict[str, Any]:
        """
        Fetch signal data.

        Signal data is stored on-chain. Optionally fetch reasoning trace from Walrus.

        Returns:
            Dict with signal and reasoning trace
        """
        data = {
            "signal_type": self.signal_type,
            "signal_value": self.signal_value,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "producer": self.producer
        }

        # Optionally fetch reasoning trace
        if self.walrus_trace_id:
            from src.storage.walrus_client import WalrusClient, WalrusHelper

            client = WalrusClient(simulated=True)
            try:
                trace = WalrusHelper.fetch_json(client, self.walrus_trace_id)
                data["reasoning_trace"] = trace
            except Exception as e:
                data["reasoning_trace_error"] = str(e)

        return data

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        base = super().to_dict()
        base.update({
            "signal_type": self.signal_type,
            "signal_value": self.signal_value,
            "confidence": self.confidence,
            "walrus_trace_id": self.walrus_trace_id[:16] + "..." if self.walrus_trace_id else None
        })
        return base


# === Helper Functions ===

def create_trigger_from_onchain(trigger_data: Dict[str, Any]) -> Trigger:
    """
    Factory function to create Trigger from on-chain data.

    This would be used by agents to parse triggers from SUI blockchain.

    Args:
        trigger_data: Raw data from SUI object

    Returns:
        Appropriate Trigger subclass instance
    """
    trigger_type = trigger_data.get("trigger_type")

    if trigger_type == "news":
        return NewsTrigger(
            object_id=trigger_data["object_id"],
            walrus_blob_id=trigger_data["walrus_blob_id"],
            data_hash=trigger_data["data_hash"],
            size_bytes=trigger_data["size_bytes"],
            articles_count=trigger_data["articles_count"],
            timestamp=datetime.fromisoformat(trigger_data["timestamp"]),
            producer=trigger_data.get("producer", "unknown")
        )

    elif trigger_type == "price":
        return PriceTrigger(
            object_id=trigger_data["object_id"],
            symbol=trigger_data["symbol"],
            price_usd=trigger_data["price_usd"],
            oracle_source=trigger_data["oracle_source"],
            timestamp=datetime.fromisoformat(trigger_data["timestamp"]),
            confidence=trigger_data.get("confidence"),
            producer=trigger_data.get("producer", "unknown")
        )

    elif trigger_type == "signal":
        return SignalTrigger(
            object_id=trigger_data["object_id"],
            signal_type=trigger_data["signal_type"],
            signal_value=trigger_data["signal_value"],
            confidence=trigger_data["confidence"],
            timestamp=datetime.fromisoformat(trigger_data["timestamp"]),
            producer=trigger_data["producer"],
            walrus_trace_id=trigger_data.get("walrus_trace_id")
        )

    else:
        raise ValueError(f"Unknown trigger type: {trigger_type}")
