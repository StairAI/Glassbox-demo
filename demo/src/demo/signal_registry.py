#!/usr/bin/env python3
"""
SignalRegistry: Centralized signal storage for demo

In production, this would be replaced by SUI smart contracts.
For demo, we use a SQLite database to store signal metadata.

This allows us to test the complete flow without deploying smart contracts.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import database module
from src.storage.database import GlassBoxDatabase


class SignalRegistry:
    """
    Centralized signal registry for demo purposes.

    Stores signal metadata in SQLite database.
    In production, this would be replaced by SUI blockchain smart contracts.

    Example:
        registry = SignalRegistry()

        # Register a news signal
        signal_id = registry.register_signal({
            "signal_type": "news",
            "walrus_blob_id": "xyz123...",
            "data_hash": "abc...",
            "size_bytes": 4096,
            "articles_count": 5,
            "producer": "news_pipeline",
            "owner": "0x123...",
            "timestamp": "2026-04-05T12:00:00"
        })

        # Get all news signals
        news_signals = registry.get_signals(signal_type="news")

        # Get specific signal
        signal = registry.get_signal(signal_id)
    """

    def __init__(self, registry_path: str = "data/signal_registry.json", db_path: Optional[str] = None):
        """
        Initialize signal registry.

        Args:
            registry_path: DEPRECATED - kept for backwards compatibility.
                          Now uses SQLite database at data/glassbox.db
            db_path: Optional absolute path to database file. If not provided,
                    uses relative path "data/glassbox.db"
        """
        # Use database instead of JSON file
        if db_path is None:
            db_path = "data/glassbox.db"

        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self.db = GlassBoxDatabase(db_path=db_path)

    def register_signal(self, signal_data: Dict[str, Any]) -> str:
        """
        Register a new signal and return its ID.

        Args:
            signal_data: Signal metadata dict

        Returns:
            signal_id: Unique signal identifier
        """
        # Generate unique ID based on current count
        current_count = self.db.count_signals()
        signal_id = f"signal_{current_count:06d}"
        signal_data["signal_id"] = signal_id

        # Ensure timestamp is set
        if "timestamp" not in signal_data:
            signal_data["timestamp"] = datetime.now().isoformat()

        # Insert into database
        self.db.insert_signal(signal_data)

        print(f"[SignalRegistry] ✓ Registered {signal_data.get('signal_type', 'unknown')} signal: {signal_id}")

        return signal_id

    def get_signals(
        self,
        signal_type: Optional[str] = None,
        producer: Optional[str] = None,
        owner: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get signals with optional filtering.

        Args:
            signal_type: Filter by type ("news", "price", "insight")
            producer: Filter by producer ("news_pipeline", "agent_a", etc.)
            owner: Filter by owner address
            limit: Maximum number of signals to return

        Returns:
            List of signal metadata dicts
        """
        # Query database
        signals = self.db.get_signals(
            signal_type=signal_type,
            producer=producer,
            owner=owner,
            limit=limit if limit else 10000
        )

        return signals

    def get_signal(self, signal_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific signal by ID.

        Args:
            signal_id: Signal identifier

        Returns:
            Signal metadata dict or None if not found
        """
        return self.db.get_signal_by_id(signal_id)

    def count_signals(self, signal_type: Optional[str] = None, producer: Optional[str] = None) -> int:
        """
        Count signals, optionally filtered by type.

        Args:
            signal_type: Optional filter by type
            producer: Optional filter by producer

        Returns:
            Number of signals
        """
        return self.db.count_signals(signal_type=signal_type, producer=producer)

    def clear_registry(self):
        """Clear all signals from registry (for testing)."""
        # Delete database file and recreate
        self.db.close()
        db_path = Path("data/glassbox.db")
        if db_path.exists():
            db_path.unlink()

        self.db = GlassBoxDatabase(db_path="data/glassbox.db")
        print("[SignalRegistry] ✓ Registry cleared")

    def get_unique_owners(self) -> List[Dict[str, Any]]:
        """
        Get list of unique owner addresses from signals.

        Returns:
            List of owner dicts with address and signal count
        """
        return self.db.get_unique_owners()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.

        Returns:
            Dictionary with counts and metrics
        """
        return self.db.get_stats()

    def register_agent_execution(
        self,
        agent_id: str,
        agent_version: str,
        execution_id: str,
        input_signal_ids: List[str],
        output_signal_id: Optional[str] = None,
        confidence: Optional[float] = None,
        execution_time_ms: Optional[float] = None,
        walrus_trace_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> int:
        """
        Register an agent execution in the database.

        Args:
            agent_id: Agent identifier (e.g., "agent_a_sentiment")
            agent_version: Agent version
            execution_id: Unique execution ID
            input_signal_ids: List of input signal IDs
            output_signal_id: Output signal ID (if produced)
            confidence: Execution confidence score
            execution_time_ms: Execution time in milliseconds
            walrus_trace_id: Walrus blob ID for reasoning trace
            success: Whether execution succeeded
            error_message: Error message if failed

        Returns:
            Row ID of inserted execution
        """
        execution_data = {
            "agent_id": agent_id,
            "agent_version": agent_version,
            "execution_id": execution_id,
            "input_signal_ids": input_signal_ids,
            "output_signal_id": output_signal_id,
            "confidence": confidence,
            "execution_time_ms": execution_time_ms,
            "walrus_trace_id": walrus_trace_id,
            "success": success,
            "error_message": error_message,
            "executed_at": datetime.now().isoformat()
        }

        row_id = self.db.insert_agent_execution(execution_data)
        print(f"[SignalRegistry] ✓ Registered agent execution: {agent_id} → {execution_id[:12]}...")
        return row_id

    def register_reasoning_trace(
        self,
        walrus_trace_id: str,
        signal_id: str,
        agent_id: str,
        agent_version: str,
        step_count: int,
        data_hash: str,
        size_bytes: int,
        execution_time_ms: Optional[float] = None,
        confidence: Optional[float] = None,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None
    ) -> int:
        """
        Register a reasoning trace in the database.

        Args:
            walrus_trace_id: Walrus blob ID for the trace
            signal_id: Associated signal ID
            agent_id: Agent that produced the trace
            agent_version: Agent version
            step_count: Number of reasoning steps
            data_hash: SHA-256 hash of trace data
            size_bytes: Size of trace data
            execution_time_ms: Execution time
            confidence: Overall confidence
            llm_provider: LLM provider if used
            llm_model: LLM model if used

        Returns:
            Row ID of inserted trace
        """
        trace_data = {
            "walrus_trace_id": walrus_trace_id,
            "signal_id": signal_id,
            "agent_id": agent_id,
            "agent_version": agent_version,
            "step_count": step_count,
            "data_hash": data_hash,
            "size_bytes": size_bytes,
            "execution_time_ms": execution_time_ms,
            "confidence": confidence,
            "llm_provider": llm_provider,
            "llm_model": llm_model
        }

        row_id = self.db.insert_reasoning_trace(trace_data)
        print(f"[SignalRegistry] ✓ Registered reasoning trace: {walrus_trace_id[:16]}... → {signal_id}")
        return row_id

    def register_mocked_account(self, address: str, name: str, description: Optional[str] = None) -> str:
        """
        Register a mocked wallet account.

        Args:
            address: Wallet address
            name: Display name
            description: Optional description

        Returns:
            address
        """
        self.db.insert_mocked_account(address, name, description)
        print(f"[SignalRegistry] ✓ Registered mocked account: {address} ({name})")
        return address

    def get_mocked_accounts(self) -> List[Dict[str, Any]]:
        """
        Get all mocked accounts.

        Returns:
            List of mocked account dicts
        """
        return self.db.get_mocked_accounts()


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
