#!/usr/bin/env python3
"""
Signal Abstraction: Unified interface for all data in the system

IMPORTANT: Everything is a Signal. There is no separate "Signal" class.

Signals are lightweight references to data that can activate agents.

UNIFIED WALRUS ARCHITECTURE:
All signals use the same storage pattern:
- SUI Blockchain: Metadata only (walrus_blob_id, data_hash, object_id)
- Walrus Storage: Full data (articles, prices, insights, reasoning traces)

Signal Types:
- NewsSignal: News articles → Full data on Walrus
- PriceSignal: Price data → Full data on Walrus
- InsightSignal: Agent outputs → Signal data + reasoning trace on Walrus

"Signal" is just a signal_type="insight", not a separate concept.
Agent outputs are signals that can signal downstream agents.

This provides a unified interface for all data regardless of source or size.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class Signal(ABC):
    """
    Base class for all agent signals.

    A signal is a lightweight reference to data that can signal agent execution.
    The actual data may be stored on Walrus, on SUI blockchain, or elsewhere.

    All agents receive List[Signal] as input, providing a unified interface.
    """

    signal_type: str           # "news", "price", "insight"
    timestamp: datetime
    object_id: str              # SUI object ID where signal metadata is stored
    producer: str               # Who created this signal

    @abstractmethod
    def fetch_full_data(self) -> Dict[str, Any]:
        """
        Fetch the full data referenced by this signal.

        This is the key abstraction: regardless of where data is stored,
        agents can fetch it through this unified interface.
        """
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert signal to dictionary."""
        return {
            "signal_type": self.signal_type,
            "timestamp": self.timestamp.isoformat(),
            "object_id": self.object_id,
            "producer": self.producer
        }


@dataclass
class NewsSignal(Signal):
    """
    Signal for news data.

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
            signal_type="news",
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
class PriceSignal(Signal):
    """
    Signal for price data from on-chain oracles.

    Unified architecture: All data stored on Walrus, metadata on SUI blockchain.

    Architecture:
        SUI: {walrus_blob_id, data_hash, symbol} (< 200 bytes)
        Walrus: {symbol, price_usd, oracle_source, confidence, historical_data} (all price data)
    """

    walrus_blob_id: str         # Reference to Walrus storage
    data_hash: str              # SHA-256 for integrity verification
    size_bytes: int             # Size of full data
    symbol: str                 # "BTC", "ETH", "SUI" (preview info)
    price_usd: float            # Current price (preview info)

    def __init__(
        self,
        object_id: str,
        walrus_blob_id: str,
        data_hash: str,
        size_bytes: int,
        symbol: str,
        price_usd: float,
        timestamp: datetime,
        producer: str = "sui_price_pipeline"
    ):
        super().__init__(
            signal_type="price",
            timestamp=timestamp,
            object_id=object_id,
            producer=producer
        )
        self.walrus_blob_id = walrus_blob_id
        self.data_hash = data_hash
        self.size_bytes = size_bytes
        self.symbol = symbol
        self.price_usd = price_usd

    def fetch_full_data(self, walrus_client=None) -> Dict[str, Any]:
        """
        Fetch full price data from Walrus.

        Args:
            walrus_client: Optional WalrusClient to use. If None, creates a new one.

        Returns:
            Dict with structure:
            {
                "symbol": "BTC",
                "price_usd": 45000.0,
                "oracle_source": "pyth",
                "confidence": 0.99,
                "timestamp": "...",
                "historical_data": [...]  # Optional
            }
        """
        from src.storage.walrus_client import WalrusClient, WalrusHelper
        import os

        if walrus_client is None:
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
            raise RuntimeError(f"Failed to fetch price data from Walrus: {e}") from e

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        base = super().to_dict()
        base.update({
            "walrus_blob_id": self.walrus_blob_id,
            "data_hash": self.data_hash[:16] + "...",  # Truncate for display
            "size_bytes": self.size_bytes,
            "symbol": self.symbol,
            "price_usd": self.price_usd
        })
        return base


@dataclass
class InsightSignal(Signal):
    """
    Signal for agent outputs (insights).

    NOTE: "Insight" is NOT a separate class - it's just a type of signal.
    Agent outputs are signals that can activate downstream agents.

    Examples:
    - Sentiment analysis results
    - Investment recommendations
    - Portfolio rebalancing decisions

    Unified architecture: All data stored on Walrus, metadata on SUI blockchain.

    Architecture:
        SUI: {walrus_blob_id, data_hash, insight_type, confidence} (< 300 bytes)
        Walrus: {insight_type, signal_value, confidence, reasoning_trace} (all insight data)
    """

    walrus_blob_id: str         # Reference to Walrus storage (signal data)
    data_hash: str              # SHA-256 for integrity verification
    size_bytes: int             # Size of full data
    insight_type: str           # "sentiment", "investment", "portfolio" (preview info)
    confidence: float           # Agent's confidence (preview info)
    walrus_trace_id: Optional[str] = None  # Reasoning trace on Walrus (separate blob)

    def __init__(
        self,
        object_id: str,
        walrus_blob_id: str,
        data_hash: str,
        size_bytes: int,
        insight_type: str,
        confidence: float,
        timestamp: datetime,
        producer: str,
        walrus_trace_id: Optional[str] = None
    ):
        super().__init__(
            signal_type="insight",
            timestamp=timestamp,
            object_id=object_id,
            producer=producer
        )
        self.walrus_blob_id = walrus_blob_id
        self.data_hash = data_hash
        self.size_bytes = size_bytes
        self.insight_type = insight_type
        self.confidence = confidence
        self.walrus_trace_id = walrus_trace_id

    def fetch_full_data(self, walrus_client=None) -> Dict[str, Any]:
        """
        Fetch full insight data from Walrus.

        Args:
            walrus_client: Optional WalrusClient to use. If None, creates a new one.

        Returns:
            Dict with structure:
            {
                "insight_type": "sentiment",
                "signal_value": {...},
                "confidence": 0.85,
                "timestamp": "...",
                "producer": "agent_a_sentiment",
                "reasoning_trace": {...}  # If walrus_trace_id is set
            }
        """
        from src.storage.walrus_client import WalrusClient, WalrusHelper
        import os

        if walrus_client is None:
            walrus_enabled = os.getenv("WALRUS_ENABLED", "false").lower() == "true"
            client = WalrusClient(
                publisher_url=os.getenv("WALRUS_PUBLISHER_URL"),
                aggregator_url=os.getenv("WALRUS_AGGREGATOR_URL"),
                simulated=not walrus_enabled
            )
        else:
            client = walrus_client

        try:
            # Fetch signal data from Walrus
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

            # Optionally fetch reasoning trace (separate blob)
            if self.walrus_trace_id:
                try:
                    trace = WalrusHelper.fetch_json(client, self.walrus_trace_id)
                    data["reasoning_trace"] = trace
                except Exception as e:
                    data["reasoning_trace_error"] = str(e)

            return data

        except Exception as e:
            raise RuntimeError(f"Failed to fetch insight data from Walrus: {e}") from e

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        base = super().to_dict()
        base.update({
            "walrus_blob_id": self.walrus_blob_id,
            "data_hash": self.data_hash[:16] + "...",  # Truncate for display
            "size_bytes": self.size_bytes,
            "insight_type": self.insight_type,
            "confidence": self.confidence,
            "walrus_trace_id": self.walrus_trace_id[:16] + "..." if self.walrus_trace_id else None
        })
        return base


# === Helper Functions ===

def create_signal_from_onchain(signal_data: Dict[str, Any]) -> Signal:
    """
    Factory function to create Signal from on-chain data.

    This would be used by agents to parse signals from SUI blockchain.

    IMPORTANT: All signals now use unified Walrus storage architecture.
    On-chain data only contains metadata + Walrus blob reference.

    Args:
        signal_data: Raw data from SUI object

    Returns:
        Appropriate Signal subclass instance
    """
    signal_type = signal_data.get("signal_type")

    if signal_type == "news":
        return NewsSignal(
            object_id=signal_data["object_id"],
            walrus_blob_id=signal_data["walrus_blob_id"],
            data_hash=signal_data["data_hash"],
            size_bytes=signal_data["size_bytes"],
            articles_count=signal_data["articles_count"],
            timestamp=datetime.fromisoformat(signal_data["timestamp"]),
            producer=signal_data.get("producer", "unknown")
        )

    elif signal_type == "price":
        return PriceSignal(
            object_id=signal_data["object_id"],
            walrus_blob_id=signal_data["walrus_blob_id"],
            data_hash=signal_data["data_hash"],
            size_bytes=signal_data["size_bytes"],
            symbol=signal_data["symbol"],
            price_usd=signal_data["price_usd"],
            timestamp=datetime.fromisoformat(signal_data["timestamp"]),
            producer=signal_data.get("producer", "unknown")
        )

    elif signal_type == "insight":
        return InsightSignal(
            object_id=signal_data["object_id"],
            walrus_blob_id=signal_data["walrus_blob_id"],
            data_hash=signal_data["data_hash"],
            size_bytes=signal_data["size_bytes"],
            insight_type=signal_data["insight_type"],
            confidence=signal_data["confidence"],
            timestamp=datetime.fromisoformat(signal_data["timestamp"]),
            producer=signal_data["producer"],
            walrus_trace_id=signal_data.get("walrus_trace_id")
        )

    else:
        raise ValueError(f"Unknown signal type: {signal_type}")
