"""
Abstract base class for price data sources.

This allows integration with multiple price APIs (CoinGecko, CoinMarketCap, Binance, etc.)
while maintaining a consistent interface.
"""

from abc import abstractmethod
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from decimal import Decimal

from .data_source import DataSource, DataSourceError


@dataclass
class PriceData:
    """Standardized price data structure."""

    # Required fields
    source: str              # Source name (e.g., "coingecko", "binance")
    symbol: str              # Asset symbol (e.g., "BTC", "SUI")
    price_usd: Decimal       # Price in USD
    timestamp: datetime      # Price timestamp

    # Optional fields
    price_change_24h: Optional[Decimal] = None     # 24h price change (%)
    volume_24h: Optional[Decimal] = None           # 24h trading volume
    market_cap: Optional[Decimal] = None           # Market capitalization
    high_24h: Optional[Decimal] = None             # 24h high
    low_24h: Optional[Decimal] = None              # 24h low

    # Additional pricing
    price_btc: Optional[Decimal] = None            # Price in BTC
    price_eth: Optional[Decimal] = None            # Price in ETH

    # Metadata
    raw_data: Optional[Dict] = None                # Full raw response
    fetched_at: Optional[datetime] = None          # When we fetched it

    def __post_init__(self):
        """Ensure fetched_at is set and convert to Decimal."""
        if self.fetched_at is None:
            self.fetched_at = datetime.now()

        # Ensure price is Decimal
        if not isinstance(self.price_usd, Decimal):
            self.price_usd = Decimal(str(self.price_usd))

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            "source": self.source,
            "symbol": self.symbol,
            "price_usd": float(self.price_usd),
            "timestamp": self.timestamp.isoformat(),
            "price_change_24h": float(self.price_change_24h) if self.price_change_24h else None,
            "volume_24h": float(self.volume_24h) if self.volume_24h else None,
            "market_cap": float(self.market_cap) if self.market_cap else None,
            "high_24h": float(self.high_24h) if self.high_24h else None,
            "low_24h": float(self.low_24h) if self.low_24h else None,
            "price_btc": float(self.price_btc) if self.price_btc else None,
            "price_eth": float(self.price_eth) if self.price_eth else None,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
        }


class PriceSource(DataSource):
    """
    Abstract base class for price data sources.

    All price providers (CoinGecko, CoinMarketCap, Binance, etc.) should implement this interface.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize price source.

        Args:
            api_key: API authentication key (if required)
        """
        super().__init__(credentials=api_key)
        self.api_key = api_key  # Keep for backward compatibility
        self._cache: Dict[str, PriceData] = {}
        self._cache_duration = 60  # seconds

    @abstractmethod
    def get_price(
        self,
        symbol: str,
        vs_currency: str = "usd",
        **kwargs
    ) -> PriceData:
        """
        Get current price for a single asset.

        Args:
            symbol: Asset symbol (e.g., "BTC", "SUI")
            vs_currency: Quote currency (default: "usd")
            **kwargs: Additional source-specific parameters

        Returns:
            PriceData object

        Raises:
            PriceSourceError: If API request fails
        """
        pass

    @abstractmethod
    def get_prices(
        self,
        symbols: List[str],
        vs_currency: str = "usd",
        **kwargs
    ) -> Dict[str, PriceData]:
        """
        Get current prices for multiple assets.

        Args:
            symbols: List of asset symbols (e.g., ["BTC", "SUI"])
            vs_currency: Quote currency (default: "usd")
            **kwargs: Additional source-specific parameters

        Returns:
            Dict mapping symbol to PriceData

        Raises:
            PriceSourceError: If API request fails
        """
        pass

    @abstractmethod
    def get_historical_price(
        self,
        symbol: str,
        date: datetime,
        vs_currency: str = "usd",
        **kwargs
    ) -> PriceData:
        """
        Get historical price for a specific date.

        Args:
            symbol: Asset symbol
            date: Date for historical price
            vs_currency: Quote currency (default: "usd")
            **kwargs: Additional source-specific parameters

        Returns:
            PriceData object

        Raises:
            PriceSourceError: If API request fails or date not available
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the price source is available and configured.

        Returns:
            True if source can be used, False otherwise
        """
        pass

    def get_cached_price(self, symbol: str) -> Optional[PriceData]:
        """
        Get cached price if available and not expired.

        Args:
            symbol: Asset symbol

        Returns:
            Cached PriceData or None
        """
        if symbol in self._cache:
            cached = self._cache[symbol]
            age = (datetime.now() - cached.fetched_at).total_seconds()
            if age < self._cache_duration:
                return cached
        return None

    def set_cached_price(self, symbol: str, price_data: PriceData):
        """
        Cache price data.

        Args:
            symbol: Asset symbol
            price_data: PriceData to cache
        """
        self._cache[symbol] = price_data

    def clear_cache(self):
        """Clear all cached prices."""
        self._cache.clear()

    def get_rate_limit_info(self) -> Optional[Dict]:
        """
        Get rate limit information (if available).

        Returns:
            Dict with rate limit info or None
        """
        return None

    def normalize_symbol(self, symbol: str) -> str:
        """
        Normalize symbol to source-specific format.

        Args:
            symbol: Input symbol (e.g., "BTC", "bitcoin")

        Returns:
            Normalized symbol for this source
        """
        return symbol.upper()


class PriceSourceError(DataSourceError):
    """Exception raised when price source encounters an error."""

    def __init__(self, source: str, message: str, original_error: Optional[Exception] = None):
        super().__init__(source, message)
        self.original_error = original_error


class RateLimitError(PriceSourceError):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, source: str, retry_after: Optional[int] = None):
        message = "Rate limit exceeded"
        if retry_after:
            message += f" (retry after {retry_after} seconds)"
        super().__init__(source, message)
        self.retry_after = retry_after


class SymbolNotFoundError(PriceSourceError):
    """Exception raised when symbol is not found."""

    def __init__(self, source: str, symbol: str):
        super().__init__(source, f"Symbol not found: {symbol}")
        self.symbol = symbol


class HistoricalDataNotAvailableError(PriceSourceError):
    """Exception raised when historical data is not available for the requested date."""

    def __init__(self, source: str, symbol: str, date: datetime):
        super().__init__(source, f"Historical data not available for {symbol} on {date.date()}")
        self.symbol = symbol
        self.date = date
