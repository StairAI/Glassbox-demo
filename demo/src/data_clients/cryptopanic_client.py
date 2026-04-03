"""
CryptoPanic API Client

Pure API wrapper for CryptoPanic v2 Developer API.
No data transformation - just handles HTTP requests and returns raw JSON.

API Documentation: https://cryptopanic.com/developers/api/
"""

import requests
from typing import Dict, List, Optional, Any
import logging
import time

logger = logging.getLogger(__name__)


class CryptoPanicAPIError(Exception):
    """Base exception for CryptoPanic API errors."""
    pass


class CryptoPanicRateLimitError(CryptoPanicAPIError):
    """Raised when rate limit is exceeded."""
    pass


class CryptoPanicAuthError(CryptoPanicAPIError):
    """Raised when authentication fails."""
    pass


class CryptoPanicClient:
    """
    CryptoPanic API v2 Client.

    Handles all HTTP communication with CryptoPanic API.
    Returns raw JSON responses without transformation.
    """

    BASE_URL = "https://cryptopanic.com/api/developer/v2"

    def __init__(self, auth_token: str):
        """
        Initialize CryptoPanic API client.

        Args:
            auth_token: CryptoPanic API authentication token
        """
        self.auth_token = auth_token
        self._last_request_time = 0
        self._daily_request_count = 0
        self._daily_limit = 100

    def get_posts(
        self,
        currencies: Optional[List[str]] = None,
        filter_type: Optional[str] = None,
        kind: Optional[str] = None,
        public: Optional[bool] = None,
        regions: Optional[List[str]] = None,
        **kwargs
    ) -> Dict:
        """
        Fetch posts from CryptoPanic API.

        Args:
            currencies: List of currency codes (e.g., ["BTC", "SUI"])
            filter_type: Filter type - "rising", "hot", "bullish", "bearish", "important", "lol"
            kind: Post kind - "news", "media", "all"
            public: Use public mode (True) or private mode (False/None)
            regions: List of region codes
            **kwargs: Additional query parameters

        Returns:
            Raw JSON response dict with structure:
            {
                "next": str or None,
                "previous": str or None,
                "results": [
                    {
                        "title": str,
                        "description": str,
                        "published_at": str,
                        "created_at": str,
                        "kind": str
                    },
                    ...
                ]
            }

        Raises:
            CryptoPanicAuthError: If authentication fails
            CryptoPanicRateLimitError: If rate limit exceeded
            CryptoPanicAPIError: For other API errors
        """
        # Build query parameters
        params = {
            "auth_token": self.auth_token,
        }

        # Add optional parameters
        if currencies:
            params["currencies"] = ",".join(currencies)

        if filter_type:
            params["filter"] = filter_type

        if kind:
            params["kind"] = kind

        if public is not None:
            params["public"] = "true" if public else "false"

        if regions:
            params["regions"] = ",".join(regions)

        # Add any additional kwargs
        params.update(kwargs)

        # Make request
        try:
            response = requests.get(
                f"{self.BASE_URL}/posts/",
                params=params,
                timeout=30
            )

            # Track request count
            self._daily_request_count += 1
            self._last_request_time = time.time()

            # Log request
            logger.debug(f"CryptoPanic API request: {response.url}")
            logger.debug(f"Status: {response.status_code}")
            logger.debug(f"Daily requests: {self._daily_request_count}/{self._daily_limit}")

            # Handle errors
            if response.status_code == 401 or response.status_code == 403:
                raise CryptoPanicAuthError(
                    f"Authentication failed (status {response.status_code}). "
                    "Check your API token."
                )

            if response.status_code == 429:
                raise CryptoPanicRateLimitError(
                    f"Rate limit exceeded. Daily limit: {self._daily_limit} requests."
                )

            if response.status_code == 404:
                raise CryptoPanicAPIError(
                    "API endpoint not found. The API may have changed."
                )

            if response.status_code != 200:
                raise CryptoPanicAPIError(
                    f"API request failed with status {response.status_code}: {response.text}"
                )

            # Parse and return JSON
            data = response.json()
            logger.debug(f"Received {len(data.get('results', []))} results")

            return data

        except requests.Timeout:
            raise CryptoPanicAPIError("Request timeout - CryptoPanic API not responding")

        except requests.RequestException as e:
            raise CryptoPanicAPIError(f"Network error: {str(e)}") from e

    def get_posts_from_url(self, url: str) -> Dict:
        """
        Fetch posts from a specific URL (used for pagination).

        Args:
            url: Full URL to fetch (typically from 'next' field in response)

        Returns:
            Raw JSON response dict

        Raises:
            CryptoPanicAuthError: If authentication fails
            CryptoPanicRateLimitError: If rate limit exceeded
            CryptoPanicAPIError: For other API errors
        """
        try:
            response = requests.get(url, timeout=30)

            # Track request count
            self._daily_request_count += 1
            self._last_request_time = time.time()

            logger.debug(f"Pagination request: {url}")
            logger.debug(f"Status: {response.status_code}")
            logger.debug(f"Daily requests: {self._daily_request_count}/{self._daily_limit}")

            # Handle errors (same as get_posts)
            if response.status_code == 401 or response.status_code == 403:
                raise CryptoPanicAuthError(
                    f"Authentication failed (status {response.status_code}). "
                    "Check your API token."
                )

            if response.status_code == 429:
                raise CryptoPanicRateLimitError(
                    f"Rate limit exceeded. Daily limit: {self._daily_limit} requests."
                )

            if response.status_code == 404:
                raise CryptoPanicAPIError(
                    "API endpoint not found. The pagination URL may be invalid."
                )

            if response.status_code != 200:
                raise CryptoPanicAPIError(
                    f"API request failed with status {response.status_code}: {response.text}"
                )

            # Parse and return JSON
            data = response.json()
            logger.debug(f"Received {len(data.get('results', []))} results from pagination")

            return data

        except requests.Timeout:
            raise CryptoPanicAPIError("Request timeout - CryptoPanic API not responding")

        except requests.RequestException as e:
            raise CryptoPanicAPIError(f"Network error: {str(e)}") from e

    def ping(self) -> bool:
        """
        Test if API is accessible.

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/posts/",
                params={"auth_token": self.auth_token},
                timeout=10
            )
            # 200 = working, 429 = rate limited but working
            return response.status_code in [200, 429]
        except Exception:
            return False

    def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check for CryptoPanic API.

        Returns:
            Dict with health status:
            {
                "healthy": bool,
                "status_code": int or None,
                "response_time_ms": float or None,
                "error": str or None,
                "message": str,
                "timestamp": str
            }
        """
        import time
        from datetime import datetime

        result = {
            "healthy": False,
            "status_code": None,
            "response_time_ms": None,
            "error": None,
            "message": "",
            "timestamp": datetime.utcnow().isoformat()
        }

        try:
            start_time = time.time()
            response = requests.get(
                f"{self.BASE_URL}/posts/",
                params={"auth_token": self.auth_token, "public": "true"},
                timeout=10
            )
            response_time = (time.time() - start_time) * 1000  # Convert to ms

            result["status_code"] = response.status_code
            result["response_time_ms"] = round(response_time, 2)

            if response.status_code == 200:
                result["healthy"] = True
                result["message"] = f"API is healthy (response time: {result['response_time_ms']}ms)"

            elif response.status_code == 429:
                result["healthy"] = True
                result["message"] = "API is healthy but rate limited"

            elif response.status_code == 401:
                result["error"] = "Authentication failed"
                result["message"] = "Invalid API token"

            elif response.status_code == 502:
                result["error"] = "Bad Gateway"
                result["message"] = "CryptoPanic servers are down or experiencing issues"

            elif response.status_code == 503:
                result["error"] = "Service Unavailable"
                result["message"] = "CryptoPanic API is temporarily unavailable"

            else:
                result["error"] = f"HTTP {response.status_code}"
                result["message"] = f"API returned unexpected status: {response.status_code}"

        except requests.Timeout:
            result["error"] = "Timeout"
            result["message"] = "API request timed out (>10 seconds)"

        except requests.ConnectionError as e:
            result["error"] = "Connection Error"
            result["message"] = f"Could not connect to CryptoPanic API: {str(e)}"

        except Exception as e:
            result["error"] = type(e).__name__
            result["message"] = f"Unexpected error: {str(e)}"

        return result

    def get_rate_limit_info(self) -> Dict:
        """
        Get rate limit information.

        Returns:
            Dict with rate limit info:
            {
                "limit": int,
                "period": str,
                "requests_made": int,
                "source": str
            }
        """
        return {
            "limit": self._daily_limit,
            "period": "day",
            "requests_made": self._daily_request_count,
            "source": "client tracking"
        }

    def reset_daily_counter(self):
        """Reset daily request counter (call this daily)."""
        self._daily_request_count = 0
        logger.info("Daily request counter reset")
