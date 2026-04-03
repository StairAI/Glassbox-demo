"""
Abstract base class for news data sources.

This allows integration with multiple news APIs (CryptoPanic, NewsAPI, Twitter, etc.)
while maintaining a consistent interface.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class NewsArticle:
    """Standardized news article structure."""

    # Required fields
    source: str              # Source name (e.g., "cryptopanic", "newsapi")
    url: str                 # Unique URL
    title: str               # Article title
    published_at: datetime   # Publication timestamp

    # Optional fields
    domain: Optional[str] = None          # Source domain (e.g., "coindesk.com")
    currencies: Optional[List[str]] = None # Related currencies (e.g., ["BTC", "ETH"])
    kind: Optional[str] = None            # Article type (e.g., "news", "media")
    sentiment: Optional[str] = None       # Sentiment label if provided by API
    votes: Optional[Dict] = None          # Vote counts (positive, negative, etc.)

    # Metadata
    raw_data: Optional[Dict] = None       # Full raw response from API
    fetched_at: Optional[datetime] = None # When we fetched it

    def __post_init__(self):
        """Ensure fetched_at is set."""
        if self.fetched_at is None:
            self.fetched_at = datetime.now()

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            "source": self.source,
            "url": self.url,
            "title": self.title,
            "published_at": self.published_at.isoformat(),
            "domain": self.domain,
            "currencies": self.currencies,
            "kind": self.kind,
            "sentiment": self.sentiment,
            "votes": self.votes,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
        }


class NewsSource(ABC):
    """
    Abstract base class for news data sources.

    All news providers (CryptoPanic, NewsAPI, Twitter, etc.) should implement this interface.
    """

    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize news source.

        Args:
            api_token: API authentication token (if required)
        """
        self.api_token = api_token
        self._source_name = self.__class__.__name__.lower().replace("source", "")

    @property
    def source_name(self) -> str:
        """Return the name of this news source."""
        return self._source_name

    @abstractmethod
    def fetch_news(
        self,
        currencies: Optional[List[str]] = None,
        limit: int = 100,
        filter_type: Optional[str] = None,
        **kwargs
    ) -> List[NewsArticle]:
        """
        Fetch news articles from the source.

        Args:
            currencies: List of currency symbols to filter (e.g., ["BTC", "SUI"])
            limit: Maximum number of articles to fetch
            filter_type: Source-specific filter (e.g., "hot", "trending", "rising")
            **kwargs: Additional source-specific parameters

        Returns:
            List of NewsArticle objects

        Raises:
            NewsSourceError: If API request fails
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the news source is available and configured.

        Returns:
            True if source can be used, False otherwise
        """
        pass

    def get_rate_limit_info(self) -> Optional[Dict]:
        """
        Get rate limit information (if available).

        Returns:
            Dict with rate limit info or None
        """
        return None

    def validate_response(self, response_data: Dict) -> bool:
        """
        Validate API response structure.

        Args:
            response_data: Raw API response

        Returns:
            True if valid, False otherwise
        """
        return True


class NewsSourceError(Exception):
    """Exception raised when news source encounters an error."""

    def __init__(self, source: str, message: str, original_error: Optional[Exception] = None):
        self.source = source
        self.message = message
        self.original_error = original_error
        super().__init__(f"[{source}] {message}")


class RateLimitError(NewsSourceError):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, source: str, retry_after: Optional[int] = None):
        message = "Rate limit exceeded"
        if retry_after:
            message += f" (retry after {retry_after} seconds)"
        super().__init__(source, message)
        self.retry_after = retry_after


class AuthenticationError(NewsSourceError):
    """Exception raised when authentication fails."""

    def __init__(self, source: str):
        super().__init__(source, "Authentication failed - check API token")
