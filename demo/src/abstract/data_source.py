#!/usr/bin/env python3
"""
Abstract base class for all data sources in the Glass Box Protocol.

This provides a unified parent interface for all external data sources:
- NewsSource: News APIs (CryptoPanic, NewsAPI, etc.)
- PriceSource: Price oracles (CoinGecko, Pyth, etc.)

All data sources provide:
1. A standardized initialization pattern
2. Availability checking
3. Error handling
4. Source identification
"""

from abc import ABC, abstractmethod
from typing import Optional


class DataSource(ABC):
    """
    Abstract base class for all data sources.

    All external data sources (news, price, social, etc.) should extend this class.
    This provides a common interface for initialization, availability checking, and error handling.
    """

    def __init__(self, credentials: Optional[str] = None, **kwargs):
        """
        Initialize data source.

        Args:
            credentials: API key/token for authentication (if required)
            **kwargs: Additional source-specific configuration
        """
        self.credentials = credentials
        self._source_name = self.__class__.__name__.lower().replace("source", "")
        self._config = kwargs

    @property
    def source_name(self) -> str:
        """Return the name of this data source."""
        return self._source_name

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this data source is available and configured correctly.

        Returns:
            True if source is available, False otherwise
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test connection to the data source.

        Returns:
            True if connection successful, False otherwise
        """
        pass

    def __repr__(self) -> str:
        """String representation of data source."""
        return f"{self.__class__.__name__}(source={self.source_name})"


class DataSourceError(Exception):
    """Base exception for data source errors."""

    def __init__(self, source: str, message: str):
        """
        Initialize data source error.

        Args:
            source: Name of the data source
            message: Error message
        """
        self.source = source
        self.message = message
        super().__init__(f"[{source}] {message}")
