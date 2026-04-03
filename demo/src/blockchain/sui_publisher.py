#!/usr/bin/env python3
"""
OnChainPublisher: Publishes triggers to SUI blockchain.

Updated architecture:
- Large data (news) → Walrus storage + metadata on SUI
- Small data (prices) → Direct storage on SUI
- All data exposed as Triggers for agents
"""

import json
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime

from src.storage.walrus_client import WalrusClient, WalrusHelper
from src.core.trigger import NewsTrigger, PriceTrigger, SignalTrigger


class OnChainPublisher:
    """
    Publishes triggers to SUI blockchain.

    Uses hybrid storage strategy:
    - Large data (> 1KB) → Walrus (cheap) + metadata on SUI
    - Small data (< 1KB) → Direct storage on SUI

    All published data is exposed as Triggers for agent consumption.

    Example:
        publisher = OnChainPublisher(
            walrus_client=walrus_client,
            sui_client=sui_client,
            simulated=True
        )

        # Publish news (large data → Walrus)
        trigger = publisher.publish_news_trigger(news_data, "news_pipeline")

        # Publish price (small data → SUI)
        trigger = publisher.publish_price_trigger("BTC", 66434.0, "pyth")
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

    # === News Triggers ===

    def publish_news_trigger(
        self,
        news_data: Dict[str, Any],
        producer: str = "news_pipeline"
    ) -> NewsTrigger:
        """
        Publish news trigger.

        News data is large (4KB+), so:
        1. Store full data on Walrus
        2. Store metadata + blob_id on SUI
        3. Return NewsTrigger

        Args:
            news_data: Full news data dict
            producer: Pipeline identifier

        Returns:
            NewsTrigger instance
        """
        print(f"\n[OnChainPublisher] Publishing News Trigger")

        # Step 1: Store full data on Walrus
        print(f"  [1/3] Storing full data on Walrus...")
        blob_id = WalrusHelper.store_json(self.walrus_client, news_data)
        data_json = json.dumps(news_data, sort_keys=True)
        data_hash = hashlib.sha256(data_json.encode()).hexdigest()
        size_bytes = len(data_json)

        print(f"    ✓ Walrus blob ID: {blob_id[:16]}...")
        print(f"    ✓ Data hash: {data_hash[:16]}...")
        print(f"    ✓ Size: {size_bytes:,} bytes")

        # Step 2: Create trigger metadata (lightweight!)
        print(f"  [2/3] Creating trigger metadata...")
        trigger_metadata = {
            "trigger_type": "news",
            "walrus_blob_id": blob_id,
            "data_hash": data_hash,
            "size_bytes": size_bytes,
            "articles_count": len(news_data.get("articles", [])),
            "timestamp": int(datetime.now().timestamp()),
            "producer": producer,
            "owner": self.owner_address or "default"  # Configurable owner
        }

        metadata_size = len(json.dumps(trigger_metadata))
        print(f"    ✓ Metadata size: {metadata_size} bytes (< 500 bytes)")

        # Step 3: Publish metadata to SUI
        print(f"  [3/3] Publishing metadata to SUI...")
        object_id = self._publish_trigger_to_sui(trigger_metadata)
        print(f"    ✓ SUI object ID: {object_id}")

        # Create and return trigger
        trigger = NewsTrigger(
            object_id=object_id,
            walrus_blob_id=blob_id,
            data_hash=data_hash,
            size_bytes=size_bytes,
            articles_count=trigger_metadata["articles_count"],
            timestamp=datetime.fromtimestamp(trigger_metadata["timestamp"]),
            producer=producer
        )

        print(f"  ✓ News trigger published successfully\n")
        return trigger

    # === Price Triggers ===

    def publish_price_trigger(
        self,
        symbol: str,
        price_usd: float,
        oracle_source: str,
        confidence: Optional[float] = None,
        producer: str = "sui_price_pipeline"
    ) -> PriceTrigger:
        """
        Publish price trigger.

        Price data is small (< 200 bytes), so:
        1. Store directly on SUI (no Walrus needed)
        2. Return PriceTrigger

        Args:
            symbol: Asset symbol (e.g., "BTC")
            price_usd: Price in USD
            oracle_source: Oracle name (e.g., "pyth")
            confidence: Oracle confidence (optional)
            producer: Pipeline identifier

        Returns:
            PriceTrigger instance
        """
        print(f"\n[OnChainPublisher] Publishing Price Trigger")

        # Create trigger data (small enough for on-chain)
        print(f"  [1/2] Creating trigger data...")
        trigger_data = {
            "trigger_type": "price",
            "symbol": symbol,
            "price_usd": price_usd,
            "oracle_source": oracle_source,
            "confidence": confidence,
            "timestamp": int(datetime.now().timestamp()),
            "producer": producer,
            "owner": self.owner_address or "default"  # Configurable owner
        }

        data_size = len(json.dumps(trigger_data))
        print(f"    ✓ Symbol: {symbol}")
        print(f"    ✓ Price: ${price_usd:,.2f}")
        print(f"    ✓ Oracle: {oracle_source}")
        print(f"    ✓ Data size: {data_size} bytes (< 1KB, no Walrus needed)")

        # Publish to SUI
        print(f"  [2/2] Publishing to SUI...")
        object_id = self._publish_trigger_to_sui(trigger_data)
        print(f"    ✓ SUI object ID: {object_id}")

        # Create and return trigger
        trigger = PriceTrigger(
            object_id=object_id,
            symbol=symbol,
            price_usd=price_usd,
            oracle_source=oracle_source,
            timestamp=datetime.fromtimestamp(trigger_data["timestamp"]),
            confidence=confidence,
            producer=producer
        )

        print(f"  ✓ Price trigger published successfully\n")
        return trigger

    # === Signal Triggers ===

    def publish_signal_trigger(
        self,
        signal_type: str,
        signal_value: Dict[str, Any],
        confidence: float,
        producer: str,
        reasoning_trace: Optional[Dict[str, Any]] = None
    ) -> SignalTrigger:
        """
        Publish signal trigger (agent output).

        Signals are stored on SUI, reasoning traces on Walrus.

        Args:
            signal_type: Type of signal (e.g., "sentiment", "investment")
            signal_value: Signal data
            confidence: Agent's confidence
            producer: Agent identifier
            reasoning_trace: Optional reasoning trace (stored on Walrus)

        Returns:
            SignalTrigger instance
        """
        print(f"\n[OnChainPublisher] Publishing Signal Trigger")

        # Store reasoning trace on Walrus (if provided)
        walrus_trace_id = None
        if reasoning_trace:
            print(f"  [1/3] Storing reasoning trace on Walrus...")
            walrus_trace_id = WalrusHelper.store_json(self.walrus_client, reasoning_trace)
            print(f"    ✓ Trace ID: {walrus_trace_id[:16]}...")

        # Create trigger data
        print(f"  [2/3] Creating signal trigger...")
        trigger_data = {
            "trigger_type": "signal",
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
        object_id = self._publish_trigger_to_sui(trigger_data)
        print(f"    ✓ SUI object ID: {object_id}")

        # Create and return trigger
        trigger = SignalTrigger(
            object_id=object_id,
            signal_type=signal_type,
            signal_value=signal_value,
            confidence=confidence,
            timestamp=datetime.fromtimestamp(trigger_data["timestamp"]),
            producer=producer,
            walrus_trace_id=walrus_trace_id
        )

        print(f"  ✓ Signal trigger published successfully\n")
        return trigger

    # === Private Methods ===

    def _publish_trigger_to_sui(self, trigger_data: Dict[str, Any]) -> str:
        """
        Publish trigger metadata to SUI blockchain.

        Args:
            trigger_data: Trigger metadata dict

        Returns:
            object_id: SUI object ID
        """
        if self.simulated:
            return self._simulate_sui_publish(trigger_data)
        else:
            return self._real_sui_publish(trigger_data)

    def _simulate_sui_publish(self, trigger_data: Dict[str, Any]) -> str:
        """Simulate SUI publication for demo."""
        # Generate mock object ID from trigger data
        data_str = json.dumps(trigger_data, sort_keys=True)
        object_hash = hashlib.sha256(data_str.encode()).hexdigest()
        mock_object_id = f"0x{object_hash[:40]}"

        return mock_object_id

    def _real_sui_publish(self, trigger_data: Dict[str, Any]) -> str:
        """
        Publish to real SUI blockchain.

        This would use pysui SDK to create and execute transactions.

        Pseudocode:
            from pysui import SyncTransaction

            txn = SyncTransaction(client=self.sui_client)

            if trigger_data["trigger_type"] == "news":
                txn.move_call(
                    target=f"{self.package_id}::trigger::publish_news_trigger",
                    arguments=[...],
                )
            elif trigger_data["trigger_type"] == "price":
                txn.move_call(
                    target=f"{self.package_id}::trigger::publish_price_trigger",
                    arguments=[...],
                )

            result = txn.execute(gas_budget=10_000_000)
            return result.digest
        """
        raise NotImplementedError(
            "Real SUI publishing requires pysui SDK and deployed smart contract. "
            "Use simulated=True for demo purposes."
        )


class TriggerEventEmitter:
    """
    Emits lightweight SUI events when triggers are created.

    These events allow agents to watch for new triggers without
    constantly polling the blockchain.
    """

    def __init__(self, client=None, package_id: Optional[str] = None, simulated: bool = True):
        self.client = client
        self.package_id = package_id
        self.simulated = simulated

    def emit_trigger_event(
        self,
        trigger_type: str,
        object_id: str,
        preview_data: Dict[str, Any]
    ) -> str:
        """
        Emit event when trigger is created.

        Args:
            trigger_type: "news", "price", "signal"
            object_id: SUI object ID of trigger
            preview_data: Small preview data for filtering

        Returns:
            Event ID
        """
        if self.simulated:
            print(f"  [Event] TriggerCreated: type={trigger_type}, object={object_id[:16]}...")
            return f"event_{object_id[:16]}"

        # Real implementation would emit SUI event
        raise NotImplementedError("Real event emission requires pysui SDK")
