"""
Abstract base classes for Glass Box Protocol.

This module provides abstract interfaces for:
- Data sources (news, price)
- Signals (core data structures)
- Pipelines (ETL processes)
- Signal storage (file, blockchain, hybrid)

These abstractions ensure consistent interfaces across the system.
"""

from .data_source import (
    DataSource,
    DataSourceError,
)

from .news_source import (
    NewsSource,
    NewsArticle,
    NewsSourceError,
    RateLimitError,
    AuthenticationError,
)

from .price_source import (
    PriceSource,
    PriceData,
    PriceSourceError,
    SymbolNotFoundError,
    HistoricalDataNotAvailableError,
)

from .signal import (
    Signal,
    NewsSignal,
    PriceSignal,
    InsightSignal,
    create_signal_from_onchain,
)

from .pipeline import (
    Pipeline,
    ScheduledPipeline,
    SignalStorage,
    PipelineError,
    ExtractError,
    TransformError,
    LoadError,
)

from .signal_storage import (
    FileBasedSignalStorage,
    BlockchainSignalRegistry,
    HybridSignalStorage,
    create_signal_storage,
)

from .agent import (
    Agent,
    AgentError,
    SignalValidationError,
    ProcessingError,
)

__all__ = [
    # Data Source
    "DataSource",
    "DataSourceError",
    # News
    "NewsSource",
    "NewsArticle",
    "NewsSourceError",
    "RateLimitError",
    "AuthenticationError",
    # Price
    "PriceSource",
    "PriceData",
    "PriceSourceError",
    "SymbolNotFoundError",
    "HistoricalDataNotAvailableError",
    # Signals
    "Signal",
    "NewsSignal",
    "PriceSignal",
    "InsightSignal",
    "create_signal_from_onchain",
    # Pipeline
    "Pipeline",
    "ScheduledPipeline",
    "SignalStorage",
    "PipelineError",
    "ExtractError",
    "TransformError",
    "LoadError",
    # Signal Storage
    "FileBasedSignalStorage",
    "BlockchainSignalRegistry",
    "HybridSignalStorage",
    "create_signal_storage",
    # Agent
    "Agent",
    "AgentError",
    "SignalValidationError",
    "ProcessingError",
]
