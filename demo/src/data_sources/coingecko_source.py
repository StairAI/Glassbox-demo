"""
CoinGecko Price Source

Transforms CoinGecko API responses into unified PriceSource format.
Uses CoinGeckoClient for all API communication.
"""

from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal
import logging

from ..abstract import (
    PriceSource,
    PriceData,
    PriceSourceError,
    RateLimitError,
    SymbolNotFoundError,
    HistoricalDataNotAvailableError,
)
from ..data_clients import CoinGeckoClient, CoinGeckoAPIError, CoinGeckoRateLimitError

logger = logging.getLogger(__name__)


class CoinGeckoSource(PriceSource):
    """
    CoinGecko price source implementation.

    Transforms CoinGecko API data into standardized PriceData format.
    Handles caching, rate limiting, and error transformation.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize CoinGecko price source.

        Args:
            api_key: Optional API key for pro tier (not required for free tier)
        """
        super().__init__(api_key)
        self._source_name = "coingecko"
        self._client = CoinGeckoClient(api_key=api_key)

    def get_price(self, symbol: str, vs_currency: str = "usd", **kwargs) -> PriceData:
        """Get current price for a single asset."""
        # Check cache first
        cached = self.get_cached_price(symbol)
        if cached:
            logger.debug(f"Using cached price for {symbol}")
            return cached

        # Get price using client
        try:
            coin_id = self._client.symbol_to_id(symbol)
            response = self._client.get_simple_price(
                ids=[coin_id],
                vs_currencies=vs_currency,
                **kwargs
            )

            if coin_id not in response:
                raise SymbolNotFoundError(self._source_name, symbol)

            # Transform response to PriceData
            price_data = self._transform_simple_price(symbol, response[coin_id], vs_currency)

            # Cache the result
            self.set_cached_price(symbol, price_data)

            logger.info(f"Fetched price for {symbol}: ${price_data.price_usd}")
            return price_data

        except CoinGeckoRateLimitError as e:
            raise RateLimitError(self._source_name, retry_after=60) from e
        except CoinGeckoAPIError as e:
            raise PriceSourceError(self._source_name, str(e), original_error=e)

    def get_prices(self, symbols: List[str], vs_currency: str = "usd", **kwargs) -> Dict[str, PriceData]:
        """Get current prices for multiple assets."""
        try:
            # Convert symbols to CoinGecko IDs
            coin_ids = [self._client.symbol_to_id(symbol) for symbol in symbols]

            # Fetch prices from API
            response = self._client.get_simple_price(
                ids=coin_ids,
                vs_currencies=vs_currency,
                **kwargs
            )

            # Transform responses to PriceData
            prices = {}
            for symbol, coin_id in zip(symbols, coin_ids):
                if coin_id in response:
                    price_data = self._transform_simple_price(symbol, response[coin_id], vs_currency)
                    prices[symbol] = price_data
                    self.set_cached_price(symbol, price_data)
                else:
                    logger.warning(f"Price data not found for {symbol} ({coin_id})")

            logger.info(f"Fetched prices for {len(prices)} assets from CoinGecko")
            return prices

        except CoinGeckoRateLimitError as e:
            raise RateLimitError(self._source_name, retry_after=60) from e
        except CoinGeckoAPIError as e:
            raise PriceSourceError(self._source_name, str(e), original_error=e)

    def get_historical_price(self, symbol: str, date: datetime, vs_currency: str = "usd", **kwargs) -> PriceData:
        """Get historical price for a specific date."""
        try:
            coin_id = self._client.symbol_to_id(symbol)
            date_str = date.strftime("%d-%m-%Y")

            # Fetch historical data from API
            response = self._client.get_coin_history(coin_id, date_str)

            # Check if market data exists
            if "market_data" not in response or vs_currency not in response["market_data"]["current_price"]:
                raise HistoricalDataNotAvailableError(self._source_name, symbol, date)

            # Transform response to PriceData
            price_data = self._transform_historical_price(symbol, response, vs_currency, date)

            logger.info(f"Fetched historical price for {symbol} on {date.date()}: ${price_data.price_usd}")
            return price_data

        except CoinGeckoRateLimitError as e:
            raise RateLimitError(self._source_name, retry_after=60) from e
        except CoinGeckoAPIError as e:
            if "not found" in str(e).lower():
                raise HistoricalDataNotAvailableError(self._source_name, symbol, date) from e
            raise PriceSourceError(self._source_name, str(e), original_error=e)

    def _transform_simple_price(self, symbol: str, data: Dict, vs_currency: str) -> PriceData:
        """
        Transform CoinGecko simple price response to PriceData.

        Args:
            symbol: Original symbol (e.g., "BTC")
            data: CoinGecko API response for single coin
            vs_currency: Target currency (e.g., "usd")

        Returns:
            PriceData object
        """
        price_usd = Decimal(str(data[vs_currency]))

        price_change_24h = None
        if f"{vs_currency}_24h_change" in data:
            price_change_24h = Decimal(str(data[f"{vs_currency}_24h_change"]))

        volume_24h = None
        if f"{vs_currency}_24h_vol" in data:
            volume_24h = Decimal(str(data[f"{vs_currency}_24h_vol"]))

        market_cap = None
        if f"{vs_currency}_market_cap" in data:
            market_cap = Decimal(str(data[f"{vs_currency}_market_cap"]))

        return PriceData(
            source=self._source_name,
            symbol=symbol,
            price_usd=price_usd,
            timestamp=datetime.now(),
            price_change_24h=price_change_24h,
            volume_24h=volume_24h,
            market_cap=market_cap,
            raw_data=data,
        )

    def _transform_historical_price(self, symbol: str, data: Dict, vs_currency: str, date: datetime) -> PriceData:
        """
        Transform CoinGecko historical response to PriceData.

        Args:
            symbol: Original symbol (e.g., "BTC")
            data: CoinGecko API historical response
            vs_currency: Target currency (e.g., "usd")
            date: Date of historical data

        Returns:
            PriceData object
        """
        market_data = data["market_data"]
        price_usd = Decimal(str(market_data["current_price"][vs_currency]))

        market_cap = None
        if "market_cap" in market_data and vs_currency in market_data["market_cap"]:
            market_cap = Decimal(str(market_data["market_cap"][vs_currency]))

        volume_24h = None
        if "total_volume" in market_data and vs_currency in market_data["total_volume"]:
            volume_24h = Decimal(str(market_data["total_volume"][vs_currency]))

        return PriceData(
            source=self._source_name,
            symbol=symbol,
            price_usd=price_usd,
            timestamp=datetime.combine(date.date(), datetime.min.time()),
            market_cap=market_cap,
            volume_24h=volume_24h,
            raw_data=data,
        )

    def is_available(self) -> bool:
        """Check if CoinGecko API is available."""
        return self._client.ping()

    def get_rate_limit_info(self) -> Optional[Dict]:
        """Get rate limit information."""
        return self._client.get_rate_limit_info()

    def normalize_symbol(self, symbol: str) -> str:
        """Normalize symbol to standard format."""
        return symbol.upper()

    def test_connection(self) -> bool:
        """Test connection to CoinGecko API."""
        return self.is_available()
