"""
Abstract base classes for data sources.

This module provides abstract interfaces for news and price data sources,
allowing easy integration with multiple APIs while maintaining consistent interfaces.
"""

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

__all__ = [
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
]
