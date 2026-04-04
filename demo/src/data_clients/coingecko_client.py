"""
CoinGecko API Client

Pure API wrapper for CoinGecko v3 API.
No data transformation - just handles HTTP requests and returns raw JSON.

API Documentation: https://www.coingecko.com/en/api/documentation
"""

import requests
from typing import Dict, List, Optional
import logging
import time

logger = logging.getLogger(__name__)


class CoinGeckoAPIError(Exception):
    """Base exception for CoinGecko API errors."""
    pass


class CoinGeckoRateLimitError(CoinGeckoAPIError):
    """Raised when rate limit is exceeded."""
    pass


class CoinGeckoClient:
    """
    CoinGecko API v3 Client.

    Handles all HTTP communication with CoinGecko API.
    Returns raw JSON responses without transformation.

    Supports both free and Pro tiers:
    - Free tier: https://api.coingecko.com/api/v3 (15 requests/min)
    - Pro tier: https://pro-api.coingecko.com/api/v3 (higher rate limits)
    """

    FREE_BASE_URL = "https://api.coingecko.com/api/v3"
    PRO_BASE_URL = "https://pro-api.coingecko.com/api/v3"

    # Symbol to CoinGecko ID mapping
    SYMBOL_TO_ID = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SUI": "sui",
        "USDC": "usd-coin",
        "USDT": "tether",
        "SOL": "solana",
        "BNB": "binancecoin",
        "ADA": "cardano",
        "XRP": "ripple",
        "DOT": "polkadot",
    }

    def __init__(self, api_key: Optional[str] = None, min_request_interval: float = 4.0):
        """
        Initialize CoinGecko API client.

        Args:
            api_key: Optional API key for pro tier (not required for free tier)
            min_request_interval: Minimum seconds between requests (default: 4.0 for 15/min)
        """
        self.api_key = api_key
        self._last_request_time = 0
        self._min_request_interval = min_request_interval

        # Use Pro API URL if API key is provided
        self.base_url = self.PRO_BASE_URL if api_key else self.FREE_BASE_URL
        logger.info(f"CoinGecko client initialized with {'Pro' if api_key else 'Free'} tier")

    def get_simple_price(
        self,
        ids: List[str],
        vs_currencies: str = "usd",
        include_24hr_change: bool = True,
        include_24hr_vol: bool = True,
        include_market_cap: bool = True,
        **kwargs
    ) -> Dict:
        """
        Get current price of cryptocurrencies.

        Args:
            ids: List of CoinGecko coin IDs (e.g., ["bitcoin", "ethereum"])
            vs_currencies: Target currency (default: "usd")
            include_24hr_change: Include 24h price change
            include_24hr_vol: Include 24h volume
            include_market_cap: Include market cap
            **kwargs: Additional query parameters

        Returns:
            Raw JSON response dict with structure:
            {
                "bitcoin": {
                    "usd": float,
                    "usd_24h_change": float,
                    "usd_24h_vol": float,
                    "usd_market_cap": float
                },
                ...
            }

        Raises:
            CoinGeckoRateLimitError: If rate limit exceeded
            CoinGeckoAPIError: For other API errors
        """
        # Rate limiting
        self._wait_for_rate_limit()

        # Build parameters
        params = {
            "ids": ",".join(ids),
            "vs_currencies": vs_currencies,
            "include_24hr_change": "true" if include_24hr_change else "false",
            "include_24hr_vol": "true" if include_24hr_vol else "false",
            "include_market_cap": "true" if include_market_cap else "false",
        }

        # Add API key if available
        if self.api_key:
            params["x_cg_pro_api_key"] = self.api_key

        # Add any additional kwargs
        params.update(kwargs)

        # Make request
        try:
            response = requests.get(
                f"{self.base_url}/simple/price",
                params=params,
                timeout=30
            )

            logger.debug(f"CoinGecko API request: {response.url}")
            logger.debug(f"Status: {response.status_code}")

            # Handle errors
            if response.status_code == 429:
                raise CoinGeckoRateLimitError(
                    "Rate limit exceeded. Free tier: 15 requests/minute. "
                    "Wait 60 seconds or upgrade to pro tier."
                )

            if response.status_code == 404:
                raise CoinGeckoAPIError(
                    f"Coin IDs not found: {ids}"
                )

            if response.status_code != 200:
                raise CoinGeckoAPIError(
                    f"API request failed with status {response.status_code}: {response.text}"
                )

            # Parse and return JSON
            data = response.json()
            logger.debug(f"Received price data for {len(data)} coins")

            return data

        except requests.Timeout:
            raise CoinGeckoAPIError("Request timeout - CoinGecko API not responding")

        except requests.RequestException as e:
            raise CoinGeckoAPIError(f"Network error: {str(e)}") from e

    def get_coin_history(
        self,
        coin_id: str,
        date: str,
        localization: bool = False
    ) -> Dict:
        """
        Get historical data for a coin on a specific date.

        Args:
            coin_id: CoinGecko coin ID (e.g., "bitcoin")
            date: Date in DD-MM-YYYY format (e.g., "21-03-2026")
            localization: Include localized languages

        Returns:
            Raw JSON response dict with structure:
            {
                "id": str,
                "symbol": str,
                "name": str,
                "market_data": {
                    "current_price": {"usd": float, ...},
                    "market_cap": {"usd": float, ...},
                    "total_volume": {"usd": float, ...}
                },
                ...
            }

        Raises:
            CoinGeckoRateLimitError: If rate limit exceeded
            CoinGeckoAPIError: For other API errors
        """
        # Rate limiting
        self._wait_for_rate_limit()

        # Build parameters
        params = {
            "date": date,
            "localization": "true" if localization else "false"
        }

        # Add API key if available
        if self.api_key:
            params["x_cg_pro_api_key"] = self.api_key

        # Make request
        try:
            response = requests.get(
                f"{self.base_url}/coins/{coin_id}/history",
                params=params,
                timeout=30
            )

            logger.debug(f"CoinGecko history request: {coin_id} on {date}")
            logger.debug(f"Status: {response.status_code}")

            # Handle errors
            if response.status_code == 429:
                raise CoinGeckoRateLimitError("Rate limit exceeded")

            if response.status_code == 404:
                raise CoinGeckoAPIError(
                    f"Historical data not found for {coin_id} on {date}"
                )

            if response.status_code != 200:
                raise CoinGeckoAPIError(
                    f"API request failed with status {response.status_code}: {response.text}"
                )

            # Parse and return JSON
            data = response.json()
            logger.debug(f"Received historical data for {coin_id}")

            return data

        except requests.Timeout:
            raise CoinGeckoAPIError("Request timeout - CoinGecko API not responding")

        except requests.RequestException as e:
            raise CoinGeckoAPIError(f"Network error: {str(e)}") from e

    def ping(self) -> bool:
        """
        Test if API is accessible.

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/ping", timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def symbol_to_id(self, symbol: str) -> str:
        """
        Convert symbol to CoinGecko coin ID.

        Args:
            symbol: Cryptocurrency symbol (e.g., "BTC", "ETH")

        Returns:
            CoinGecko coin ID (e.g., "bitcoin", "ethereum")
        """
        symbol_upper = symbol.upper()
        return self.SYMBOL_TO_ID.get(symbol_upper, symbol.lower())

    def _wait_for_rate_limit(self):
        """Wait if necessary to respect rate limits."""
        now = time.time()
        elapsed = now - self._last_request_time

        if elapsed < self._min_request_interval:
            wait_time = self._min_request_interval - elapsed
            logger.debug(f"Rate limiting: waiting {wait_time:.2f} seconds")
            time.sleep(wait_time)

        self._last_request_time = time.time()

    def get_rate_limit_info(self) -> Dict:
        """
        Get rate limit information.

        Returns:
            Dict with rate limit info:
            {
                "limit": int,
                "period": str,
                "min_interval_seconds": float,
                "tier": str
            }
        """
        return {
            "limit": 15,
            "period": "minute",
            "min_interval_seconds": self._min_request_interval,
            "tier": "pro" if self.api_key else "free"
        }
