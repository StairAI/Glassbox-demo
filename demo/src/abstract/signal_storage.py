#!/usr/bin/env python3
"""
Signal Storage Implementations

Concrete implementations of SignalStorage interface for different backends:
- FileBasedSignalStorage: JSON file storage (simple, for demo)
- DatabaseSignalStorage: SQLite/PostgreSQL storage (production)
- BlockchainSignalRegistry: Query signals from SUI blockchain
"""

import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from src.abstract.pipeline import SignalStorage
from src.abstract import Signal, create_signal_from_onchain


class FileBasedSignalStorage(SignalStorage):
    """
    File-based signal storage using JSON.

    Simple implementation for demo/development. Stores signals in a JSON file.
    Not suitable for production (no concurrent access control, scalability issues).
    """

    def __init__(self, storage_path: str = "data/signal_registry.json"):
        """
        Initialize file-based storage.

        Args:
            storage_path: Path to JSON file for storing signals
        """
        self.storage_path = storage_path
        self._ensure_storage_exists()

    def _ensure_storage_exists(self):
        """Create storage file if it doesn't exist."""
        storage_file = Path(self.storage_path)
        storage_file.parent.mkdir(parents=True, exist_ok=True)

        if not storage_file.exists():
            with open(storage_file, 'w') as f:
                json.dump({"signals": []}, f)

    def _read_storage(self) -> Dict[str, Any]:
        """Read entire storage file."""
        with open(self.storage_path, 'r') as f:
            return json.load(f)

    def _write_storage(self, data: Dict[str, Any]):
        """Write entire storage file."""
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)

    def store(self, signal: Signal) -> bool:
        """Store a signal."""
        try:
            data = self._read_storage()

            # Convert signal to storable format
            signal_dict = {
                "signal_id": signal.object_id,
                "signal_type": signal.signal_type,
                "timestamp": signal.timestamp.isoformat(),
                "object_id": signal.object_id,
                "producer": signal.producer,
                "stored_at": datetime.now().isoformat()
            }

            # Add type-specific fields
            if signal.signal_type == "news":
                signal_dict.update({
                    "walrus_blob_id": signal.walrus_blob_id,
                    "data_hash": signal.data_hash,
                    "size_bytes": signal.size_bytes,
                    "articles_count": signal.articles_count
                })
            elif signal.signal_type == "price":
                signal_dict.update({
                    "symbol": signal.symbol,
                    "price_usd": signal.price_usd,
                    "oracle_source": signal.oracle_source,
                    "confidence": signal.confidence
                })
            elif signal.signal_type == "insight":
                signal_dict.update({
                    "insight_type": signal.insight_type,
                    "signal_value": signal.signal_value,
                    "confidence": signal.confidence,
                    "walrus_trace_id": signal.walrus_trace_id
                })

            # Append to signals list
            data["signals"].append(signal_dict)

            # Write back
            self._write_storage(data)

            return True

        except Exception as e:
            print(f"Error storing signal: {e}")
            return False

    def get(self, signal_id: str) -> Optional[Signal]:
        """Retrieve a signal by ID."""
        data = self._read_storage()

        for signal_dict in data["signals"]:
            if signal_dict.get("signal_id") == signal_id:
                return create_signal_from_onchain(signal_dict)

        return None

    def list(
        self,
        signal_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Signal]:
        """List signals with filtering."""
        data = self._read_storage()
        signals = data["signals"]

        # Filter by type if specified
        if signal_type:
            signals = [
                t for t in signals
                if t.get("signal_type") == signal_type
            ]

        # Sort by timestamp (newest first)
        signals.sort(
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )

        # Apply pagination
        signals = signals[offset:offset + limit]

        # Convert to Signal objects
        return [
            create_signal_from_onchain(t)
            for t in signals
        ]

    def delete(self, signal_id: str) -> bool:
        """Delete a signal."""
        try:
            data = self._read_storage()
            original_count = len(data["signals"])

            data["signals"] = [
                t for t in data["signals"]
                if t.get("signal_id") != signal_id
            ]

            self._write_storage(data)

            return len(data["signals"]) < original_count

        except Exception as e:
            print(f"Error deleting signal: {e}")
            return False

    def count(self, signal_type: Optional[str] = None) -> int:
        """Count signals."""
        data = self._read_storage()
        signals = data["signals"]

        if signal_type:
            signals = [
                t for t in signals
                if t.get("signal_type") == signal_type
            ]

        return len(signals)

    def clear(self, signal_type: Optional[str] = None) -> int:
        """
        Clear all signals (or filtered by type).

        Args:
            signal_type: Optional filter by type

        Returns:
            Number of signals deleted
        """
        data = self._read_storage()
        original_count = len(data["signals"])

        if signal_type:
            data["signals"] = [
                t for t in data["signals"]
                if t.get("signal_type") != signal_type
            ]
        else:
            data["signals"] = []

        self._write_storage(data)

        return original_count - len(data["signals"])


class BlockchainSignalRegistry(SignalStorage):
    """
    Blockchain-based signal registry.

    Queries signals directly from SUI blockchain.
    This is a read-only view - signals are published by OnChainPublisher.
    """

    def __init__(self, sui_client=None):
        """
        Initialize blockchain registry.

        Args:
            sui_client: SUI client for querying blockchain
        """
        self.sui_client = sui_client

    def store(self, signal: Signal) -> bool:
        """
        Cannot store directly to blockchain through registry.

        Signals must be published via OnChainPublisher.
        This method is a no-op.
        """
        print("⚠️  BlockchainSignalRegistry is read-only")
        print("   Use OnChainPublisher to publish signals to blockchain")
        return False

    def get(self, signal_id: str) -> Optional[Signal]:
        """Retrieve a signal from blockchain."""
        if not self.sui_client:
            raise ValueError("SUI client not configured")

        # Query SUI blockchain for signal object
        # Implementation depends on SUI SDK
        raise NotImplementedError("Blockchain query not yet implemented")

    def list(
        self,
        signal_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Signal]:
        """List signals from blockchain."""
        if not self.sui_client:
            raise ValueError("SUI client not configured")

        # Query SUI blockchain for signal objects
        # Implementation depends on SUI SDK
        raise NotImplementedError("Blockchain query not yet implemented")

    def delete(self, signal_id: str) -> bool:
        """Cannot delete from blockchain."""
        print("⚠️  Cannot delete from blockchain (immutable)")
        return False

    def count(self, signal_type: Optional[str] = None) -> int:
        """Count signals on blockchain."""
        if not self.sui_client:
            raise ValueError("SUI client not configured")

        # Query SUI blockchain
        raise NotImplementedError("Blockchain query not yet implemented")


class HybridSignalStorage(SignalStorage):
    """
    Hybrid storage combining file cache and blockchain.

    Writes to both file cache (fast queries) and blockchain (permanent record).
    Reads from cache first, falls back to blockchain if needed.
    """

    def __init__(
        self,
        file_storage: FileBasedSignalStorage,
        blockchain_registry: Optional[BlockchainSignalRegistry] = None
    ):
        """
        Initialize hybrid storage.

        Args:
            file_storage: File-based cache
            blockchain_registry: Optional blockchain registry
        """
        self.file_storage = file_storage
        self.blockchain_registry = blockchain_registry

    def store(self, signal: Signal) -> bool:
        """Store in file cache (blockchain publishing handled separately)."""
        return self.file_storage.store(signal)

    def get(self, signal_id: str) -> Optional[Signal]:
        """Get from file cache first, fallback to blockchain."""
        # Try file cache first
        signal = self.file_storage.get(signal_id)
        if signal:
            return signal

        # Fallback to blockchain if configured
        if self.blockchain_registry:
            return self.blockchain_registry.get(signal_id)

        return None

    def list(
        self,
        signal_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Signal]:
        """List from file cache."""
        return self.file_storage.list(signal_type, limit, offset)

    def delete(self, signal_id: str) -> bool:
        """Delete from file cache."""
        return self.file_storage.delete(signal_id)

    def count(self, signal_type: Optional[str] = None) -> int:
        """Count from file cache."""
        return self.file_storage.count(signal_type)


# === Factory Functions ===

def create_signal_storage(
    storage_type: str = "file",
    **kwargs
) -> SignalStorage:
    """
    Factory function to create appropriate signal storage.

    Args:
        storage_type: "file", "blockchain", or "hybrid"
        **kwargs: Storage-specific parameters

    Returns:
        SignalStorage implementation
    """
    if storage_type == "file":
        storage_path = kwargs.get("storage_path", "data/signal_registry.json")
        return FileBasedSignalStorage(storage_path)

    elif storage_type == "blockchain":
        sui_client = kwargs.get("sui_client")
        return BlockchainSignalRegistry(sui_client)

    elif storage_type == "hybrid":
        file_storage = FileBasedSignalStorage(
            kwargs.get("storage_path", "data/signal_registry.json")
        )
        blockchain_registry = BlockchainSignalRegistry(
            kwargs.get("sui_client")
        )
        return HybridSignalStorage(file_storage, blockchain_registry)

    else:
        raise ValueError(f"Unknown storage type: {storage_type}")
