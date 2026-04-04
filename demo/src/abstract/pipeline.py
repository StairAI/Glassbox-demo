#!/usr/bin/env python3
"""
Abstract Pipeline Interface

All pipelines in the Glass Box Protocol should implement this interface.
Pipelines are ETL (Extract, Transform, Load) processes that:
1. Extract data from external sources
2. Transform data into standardized format
3. Generate Signals and store them

Key principles:
- Pipelines are NOT agents (no reasoning, no LLM)
- Pipelines output Signals (references to data)
- Signals are stored in a SignalStorage implementation
- Downstream agents consume Signals
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from .signal import Signal


class Pipeline(ABC):
    """
    Abstract base class for all data pipelines.

    A pipeline is responsible for:
    1. Extracting data from external sources (APIs, oracles, etc.)
    2. Transforming data into standardized format
    3. Creating Signals and storing them

    Pipelines are pure ETL - no reasoning, no LLM calls.
    """

    def __init__(
        self,
        name: str,
        signal_storage: Optional['SignalStorage'] = None
    ):
        """
        Initialize pipeline.

        Args:
            name: Pipeline name (e.g., "news_pipeline", "price_pipeline")
            signal_storage: Storage backend for signals
        """
        self.name = name
        self.signal_storage = signal_storage
        self._last_run: Optional[datetime] = None
        self._run_count: int = 0

    @abstractmethod
    def extract(self, **kwargs) -> Any:
        """
        EXTRACT: Fetch data from external sources.

        This method should:
        - Call external APIs
        - Fetch from oracles
        - Query databases
        - etc.

        Returns:
            Raw data from source (format varies by pipeline)
        """
        pass

    @abstractmethod
    def transform(self, raw_data: Any) -> Dict[str, Any]:
        """
        TRANSFORM: Convert raw data to standardized format.

        This method should:
        - Parse API responses
        - Validate data
        - Apply transformations
        - Prepare for storage

        Args:
            raw_data: Raw data from extract()

        Returns:
            Transformed data ready for storage
        """
        pass

    @abstractmethod
    def load(self, transformed_data: Dict[str, Any]) -> Signal:
        """
        LOAD: Create Signal and store it.

        This method should:
        - Store data in appropriate storage (Walrus, SUI, etc.)
        - Create Signal object with references
        - Store Signal in SignalStorage

        Args:
            transformed_data: Data from transform()

        Returns:
            Signal object (reference to stored data)
        """
        pass

    def run(self, **kwargs) -> Signal:
        """
        Run the complete ETL pipeline.

        This is the main entry point that orchestrates:
        1. Extract
        2. Transform
        3. Load

        Args:
            **kwargs: Pipeline-specific parameters

        Returns:
            Signal object

        Raises:
            PipelineError: If any step fails
        """
        try:
            print(f"\n{'='*80}")
            print(f"{self.name.upper()}: Starting ETL Process")
            print(f"{'='*80}")

            # Step 1: Extract
            print(f"\n[1/3] EXTRACT: Fetching from source")
            raw_data = self.extract(**kwargs)
            print(f"  ✓ Data extracted successfully")

            # Step 2: Transform
            print(f"\n[2/3] TRANSFORM: Converting to standard format")
            transformed_data = self.transform(raw_data)
            print(f"  ✓ Data transformed successfully")

            # Step 3: Load
            print(f"\n[3/3] LOAD: Creating and storing signal")
            signal = self.load(transformed_data)
            print(f"  ✓ Signal created: {signal.object_id[:16]}...")

            # Store signal if storage is configured
            if self.signal_storage:
                self.signal_storage.store(signal)
                print(f"  ✓ Signal stored in registry")

            # Update stats
            self._last_run = datetime.now()
            self._run_count += 1

            print(f"\n{'='*80}")
            print(f"{self.name.upper()}: ETL Complete")
            print(f"{'='*80}\n")

            return signal

        except Exception as e:
            raise PipelineError(
                pipeline=self.name,
                message=f"Pipeline execution failed: {str(e)}",
                original_error=e
            ) from e

    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline execution statistics."""
        return {
            "name": self.name,
            "last_run": self._last_run.isoformat() if self._last_run else None,
            "run_count": self._run_count
        }

    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate pipeline configuration.

        Returns:
            True if pipeline is properly configured
        """
        pass


class ScheduledPipeline(Pipeline):
    """
    Pipeline that can run on a schedule.

    Extends Pipeline with scheduling capabilities.
    """

    def __init__(
        self,
        name: str,
        signal_storage: Optional['SignalStorage'] = None,
        interval_seconds: int = 300
    ):
        """
        Initialize scheduled pipeline.

        Args:
            name: Pipeline name
            signal_storage: Storage backend for signals
            interval_seconds: Run interval in seconds (default: 5 minutes)
        """
        super().__init__(name, signal_storage)
        self.interval_seconds = interval_seconds
        self._is_running = False

    def run_once(self, **kwargs) -> Signal:
        """Run pipeline once (wrapper for run())."""
        return self.run(**kwargs)

    def run_periodic(self, **kwargs):
        """
        Run pipeline periodically.

        This method will run the pipeline at specified intervals
        until stopped by user (Ctrl+C) or error.

        Args:
            **kwargs: Pipeline-specific parameters
        """
        import time

        self._is_running = True
        print(f"\n🔄 Starting periodic pipeline: {self.name}")
        print(f"   Interval: {self.interval_seconds}s")
        print(f"   Press Ctrl+C to stop\n")

        while self._is_running:
            try:
                signal = self.run_once(**kwargs)
                print(f"\n⏰ Next run in {self.interval_seconds} seconds...")
                time.sleep(self.interval_seconds)

            except KeyboardInterrupt:
                print(f"\n\n⏹️  Pipeline stopped by user")
                self._is_running = False
                break

            except Exception as e:
                print(f"\n❌ Error in pipeline: {e}")
                print(f"   Retrying in {self.interval_seconds} seconds...")
                time.sleep(self.interval_seconds)

    def stop(self):
        """Stop periodic execution."""
        self._is_running = False


class SignalStorage(ABC):
    """
    Abstract interface for signal storage.

    This provides a consistent interface for storing and retrieving signals,
    regardless of the backend (file, database, blockchain registry, etc.)
    """

    @abstractmethod
    def store(self, signal: Signal) -> bool:
        """
        Store a signal.

        Args:
            signal: Signal to store

        Returns:
            True if stored successfully
        """
        pass

    @abstractmethod
    def get(self, signal_id: str) -> Optional[Signal]:
        """
        Retrieve a signal by ID.

        Args:
            signal_id: Signal object ID

        Returns:
            Signal if found, None otherwise
        """
        pass

    @abstractmethod
    def list(
        self,
        signal_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Signal]:
        """
        List signals with optional filtering.

        Args:
            signal_type: Filter by type ("news", "price", "insight")
            limit: Maximum number to return
            offset: Pagination offset

        Returns:
            List of Signals
        """
        pass

    @abstractmethod
    def delete(self, signal_id: str) -> bool:
        """
        Delete a signal.

        Args:
            signal_id: Signal object ID

        Returns:
            True if deleted successfully
        """
        pass

    @abstractmethod
    def count(self, signal_type: Optional[str] = None) -> int:
        """
        Count signals.

        Args:
            signal_type: Optional filter by type

        Returns:
            Number of signals
        """
        pass


# === Exceptions ===

class PipelineError(Exception):
    """Base exception for pipeline errors."""

    def __init__(
        self,
        pipeline: str,
        message: str,
        original_error: Optional[Exception] = None
    ):
        self.pipeline = pipeline
        self.message = message
        self.original_error = original_error
        super().__init__(f"[{pipeline}] {message}")


class ExtractError(PipelineError):
    """Exception raised during data extraction."""
    pass


class TransformError(PipelineError):
    """Exception raised during data transformation."""
    pass


class LoadError(PipelineError):
    """Exception raised during data loading."""
    pass
