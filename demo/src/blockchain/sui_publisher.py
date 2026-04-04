#!/usr/bin/env python3
"""
OnChainPublisher: Publishes signals to SUI blockchain.

Updated architecture:
- Large data (news) → Walrus storage + metadata on SUI
- Small data (prices) → Direct storage on SUI
- All data exposed as Signals for agents
"""

import json
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime

from src.storage.walrus_client import WalrusClient, WalrusHelper
from src.abstract import NewsSignal, PriceSignal, InsightSignal


class OnChainPublisher:
    """
    Publishes signals to SUI blockchain.

    Uses hybrid storage strategy:
    - Large data (> 1KB) → Walrus (cheap) + metadata on SUI
    - Small data (< 1KB) → Direct storage on SUI

    All published data is exposed as Signals for agent consumption.

    Example:
        publisher = OnChainPublisher(
            walrus_client=walrus_client,
            sui_client=sui_client,
            simulated=True
        )

        # Publish news (large data → Walrus)
        signal = publisher.publish_news_signal(news_data, "news_pipeline")

        # Publish price (small data → SUI)
        signal = publisher.publish_price_signal("BTC", 66434.0, "pyth")
    """

    def __init__(
        self,
        walrus_client: Optional[WalrusClient] = None,
        sui_client=None,  # pysui.SuiClient
        package_id: Optional[str] = None,
        owner_address: Optional[str] = None,
        simulated: bool = True
    ):
        """
        Initialize OnChainPublisher.

        Args:
            walrus_client: WalrusClient for large data storage
            sui_client: pysui SuiClient for blockchain operations
            package_id: Deployed package ID on SUI
            owner_address: Configurable owner address for published objects
                          If None, uses the transaction signer address
            simulated: If True, simulate operations (for demo/testing)
        """
        self.walrus_client = walrus_client or WalrusClient(simulated=True)
        self.sui_client = sui_client
        self.package_id = package_id
        self.owner_address = owner_address  # Configurable owner
        self.simulated = simulated

        # Size threshold for Walrus vs SUI storage
        self.walrus_threshold_bytes = 1024  # 1KB

        if not simulated and (not sui_client or not package_id):
            raise ValueError("sui_client and package_id required when simulated=False")

    # === News Signals ===

    def publish_news_signal(
        self,
        news_data: Dict[str, Any],
        producer: str = "news_pipeline"
    ) -> NewsSignal:
        """
        Publish news signal.

        News data is large (4KB+), so:
        1. Store full data on Walrus
        2. Store metadata + blob_id on SUI
        3. Return NewsSignal

        Args:
            news_data: Full news data dict
            producer: Pipeline identifier

        Returns:
            NewsSignal instance
        """
        print(f"\n[OnChainPublisher] Publishing News Signal")

        # Step 1: Store full data on Walrus
        print(f"  [1/3] Storing full data on Walrus...")
        blob_id = WalrusHelper.store_json(self.walrus_client, news_data)
        # IMPORTANT: Hash must match WalrusHelper.store_json format (sort_keys=True, indent=2)
        data_json = json.dumps(news_data, sort_keys=True, indent=2)
        data_hash = hashlib.sha256(data_json.encode()).hexdigest()
        size_bytes = len(data_json)

        print(f"    ✓ Walrus blob ID: {blob_id[:16]}...")
        print(f"    ✓ Data hash: {data_hash[:16]}...")
        print(f"    ✓ Size: {size_bytes:,} bytes")

        # Step 2: Create signal metadata (lightweight!)
        print(f"  [2/3] Creating signal metadata...")
        signal_metadata = {
            "signal_type": "news",
            "walrus_blob_id": blob_id,
            "data_hash": data_hash,
            "size_bytes": size_bytes,
            "articles_count": len(news_data.get("articles", [])),
            "timestamp": int(datetime.now().timestamp()),
            "producer": producer,
            "owner": self.owner_address or "default"  # Configurable owner
        }

        metadata_size = len(json.dumps(signal_metadata))
        print(f"    ✓ Metadata size: {metadata_size} bytes (< 500 bytes)")

        # Step 3: Publish metadata to SUI
        print(f"  [3/3] Publishing metadata to SUI...")
        object_id = self._publish_signal_to_sui(signal_metadata)
        print(f"    ✓ SUI object ID: {object_id}")

        # Create and return signal
        signal = NewsSignal(
            object_id=object_id,
            walrus_blob_id=blob_id,
            data_hash=data_hash,
            size_bytes=size_bytes,
            articles_count=signal_metadata["articles_count"],
            timestamp=datetime.fromtimestamp(signal_metadata["timestamp"]),
            producer=producer
        )

        print(f"  ✓ News signal published successfully\n")
        return signal

    # === Price Signals ===

    def publish_price_signal(
        self,
        price_data: Dict[str, Any],
        producer: str = "coingecko_price_pipeline"
    ) -> PriceSignal:
        """
        Publish price signal.

        UNIFIED WALRUS ARCHITECTURE:
        All signals use the same pattern:
        1. Store full data on Walrus
        2. Store metadata + blob_id on SUI
        3. Return PriceSignal

        Args:
            price_data: Full price data dict from PriceData.to_dict()
                Expected keys: source, symbol, price_usd, timestamp, etc.
            producer: Pipeline identifier

        Returns:
            PriceSignal instance
        """
        print(f"\n[OnChainPublisher] Publishing Price Signal")

        # Step 1: Store full data on Walrus
        print(f"  [1/3] Storing full data on Walrus...")
        blob_id = WalrusHelper.store_json(self.walrus_client, price_data)
        # IMPORTANT: Hash must match WalrusHelper.store_json format (sort_keys=True, indent=2)
        data_json = json.dumps(price_data, sort_keys=True, indent=2)
        data_hash = hashlib.sha256(data_json.encode()).hexdigest()
        size_bytes = len(data_json)

        print(f"    ✓ Walrus blob ID: {blob_id[:16]}...")
        print(f"    ✓ Data hash: {data_hash[:16]}...")
        print(f"    ✓ Size: {size_bytes:,} bytes")

        # Step 2: Create signal metadata (lightweight!)
        print(f"  [2/3] Creating signal metadata...")
        signal_metadata = {
            "signal_type": "price",
            "walrus_blob_id": blob_id,
            "data_hash": data_hash,
            "size_bytes": size_bytes,
            "symbol": price_data["symbol"],
            "price_usd": price_data["price_usd"],
            "timestamp": int(datetime.now().timestamp()),
            "producer": producer,
            "owner": self.owner_address or "default"  # Configurable owner
        }

        metadata_size = len(json.dumps(signal_metadata))
        print(f"    ✓ Symbol: {price_data['symbol']}")
        print(f"    ✓ Price: ${price_data['price_usd']:,.2f}")
        print(f"    ✓ Metadata size: {metadata_size} bytes (< 500 bytes)")

        # Step 3: Publish metadata to SUI
        print(f"  [3/3] Publishing metadata to SUI...")
        object_id = self._publish_signal_to_sui(signal_metadata)
        print(f"    ✓ SUI object ID: {object_id}")

        # Create and return signal
        signal = PriceSignal(
            object_id=object_id,
            walrus_blob_id=blob_id,
            data_hash=data_hash,
            size_bytes=size_bytes,
            symbol=signal_metadata["symbol"],
            price_usd=signal_metadata["price_usd"],
            timestamp=datetime.fromtimestamp(signal_metadata["timestamp"]),
            producer=producer
        )

        print(f"  ✓ Price signal published successfully\n")
        return signal

    # === Signal Signals ===

    def publish_signal_signal(
        self,
        signal_type: str,
        signal_value: Dict[str, Any],
        confidence: float,
        producer: str,
        reasoning_trace: Optional[Dict[str, Any]] = None
    ) -> InsightSignal:
        """
        Publish signal signal (agent output).

        Signals are stored on SUI, reasoning traces on Walrus.

        Args:
            signal_type: Type of signal (e.g., "sentiment", "investment")
            signal_value: Signal data
            confidence: Agent's confidence
            producer: Agent identifier
            reasoning_trace: Optional reasoning trace (stored on Walrus)

        Returns:
            InsightSignal instance
        """
        print(f"\n[OnChainPublisher] Publishing Signal Signal")

        # Store reasoning trace on Walrus (if provided)
        walrus_trace_id = None
        if reasoning_trace:
            print(f"  [1/3] Storing reasoning trace on Walrus...")
            walrus_trace_id = WalrusHelper.store_json(self.walrus_client, reasoning_trace)
            print(f"    ✓ Trace ID: {walrus_trace_id[:16]}...")

        # Create signal data
        print(f"  [2/3] Creating signal signal...")
        signal_data = {
            "signal_type": "insight",
            "signal_type": signal_type,
            "signal_value": signal_value,
            "confidence": confidence,
            "walrus_trace_id": walrus_trace_id,
            "timestamp": int(datetime.now().timestamp()),
            "producer": producer,
            "owner": self.owner_address or "default"  # Configurable owner
        }

        # Publish to SUI
        print(f"  [3/3] Publishing to SUI...")
        object_id = self._publish_signal_to_sui(signal_data)
        print(f"    ✓ SUI object ID: {object_id}")

        # Create and return signal
        signal = InsightSignal(
            object_id=object_id,
            signal_type=signal_type,
            signal_value=signal_value,
            confidence=confidence,
            timestamp=datetime.fromtimestamp(signal_data["timestamp"]),
            producer=producer,
            walrus_trace_id=walrus_trace_id
        )

        print(f"  ✓ Signal signal published successfully\n")
        return signal

    # === Private Methods ===

    def _publish_signal_to_sui(self, signal_data: Dict[str, Any]) -> str:
        """
        Publish signal metadata to SUI blockchain.

        Args:
            signal_data: Signal metadata dict

        Returns:
            object_id: SUI object ID
        """
        if self.simulated:
            return self._simulate_sui_publish(signal_data)
        else:
            return self._real_sui_publish(signal_data)

    def _simulate_sui_publish(self, signal_data: Dict[str, Any]) -> str:
        """Simulate SUI publication for demo."""
        # Generate mock object ID from signal data
        data_str = json.dumps(signal_data, sort_keys=True)
        object_hash = hashlib.sha256(data_str.encode()).hexdigest()
        mock_object_id = f"0x{object_hash[:40]}"

        return mock_object_id

    def _real_sui_publish(self, signal_data: Dict[str, Any]) -> str:
        """
        Publish to real SUI blockchain.

        This would use pysui SDK to create and execute transactions.

        Pseudocode:
            from pysui import SyncTransaction

            txn = SyncTransaction(client=self.sui_client)

            if signal_data["signal_type"] == "news":
                txn.move_call(
                    target=f"{self.package_id}::signal::publish_news_signal",
                    arguments=[...],
                )
            elif signal_data["signal_type"] == "price":
                txn.move_call(
                    target=f"{self.package_id}::signal::publish_price_signal",
                    arguments=[...],
                )

            result = txn.execute(gas_budget=10_000_000)
            return result.digest
        """
        raise NotImplementedError(
            "Real SUI publishing requires pysui SDK and deployed smart contract. "
            "Use simulated=True for demo purposes."
        )


class SignalEventEmitter:
    """
    Emits lightweight SUI events when signals are created.

    These events allow agents to watch for new signals without
    constantly polling the blockchain.
    """

    def __init__(self, client=None, package_id: Optional[str] = None, simulated: bool = True):
        self.client = client
        self.package_id = package_id
        self.simulated = simulated

    def emit_signal_event(
        self,
        signal_type: str,
        object_id: str,
        preview_data: Dict[str, Any]
    ) -> str:
        """
        Emit event when signal is created.

        Args:
            signal_type: "news", "price", "insight"
            object_id: SUI object ID of signal
            preview_data: Small preview data for filtering

        Returns:
            Event ID
        """
        if self.simulated:
            print(f"  [Event] SignalCreated: type={signal_type}, object={object_id[:16]}...")
            return f"event_{object_id[:16]}"

        # Real implementation would emit SUI event
        raise NotImplementedError("Real event emission requires pysui SDK")
