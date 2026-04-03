"""
Data API Clients

Pure API wrappers for external data sources.
No abstraction layer - each client handles its specific API.
Returns raw JSON responses without transformation.
"""

from .coingecko_client import (
    CoinGeckoClient,
    CoinGeckoAPIError,
    CoinGeckoRateLimitError,
)

from .cryptopanic_client import (
    CryptoPanicClient,
    CryptoPanicAPIError,
    CryptoPanicRateLimitError,
    CryptoPanicAuthError,
)

__all__ = [
    # CoinGecko
    "CoinGeckoClient",
    "CoinGeckoAPIError",
    "CoinGeckoRateLimitError",
    # CryptoPanic
    "CryptoPanicClient",
    "CryptoPanicAPIError",
    "CryptoPanicRateLimitError",
    "CryptoPanicAuthError",
]
