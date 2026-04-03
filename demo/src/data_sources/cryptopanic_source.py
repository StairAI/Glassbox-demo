"""
CryptoPanic News Source

Transforms CryptoPanic API responses into unified NewsSource format.
Uses CryptoPanicClient for all API communication.
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging

from ..abstract import (
    NewsSource,
    NewsArticle,
    NewsSourceError,
    RateLimitError,
    AuthenticationError,
)
from ..data_clients import (
    CryptoPanicClient,
    CryptoPanicAPIError,
    CryptoPanicRateLimitError,
    CryptoPanicAuthError,
)

logger = logging.getLogger(__name__)


class CryptoPanicSource(NewsSource):
    """
    CryptoPanic news source implementation.

    Transforms CryptoPanic API data into standardized NewsArticle format.
    Handles v2 API limitations and error transformation.
    """

    def __init__(self, api_token: str):
        """
        Initialize CryptoPanic news source.

        Args:
            api_token: CryptoPanic API authentication token
        """
        super().__init__(api_token)
        self._source_name = "cryptopanic"
        self._client = CryptoPanicClient(auth_token=api_token)

    def fetch_news(
        self,
        currencies: Optional[List[str]] = None,
        limit: int = 100,
        filter_type: Optional[str] = None,
        **kwargs
    ) -> List[NewsArticle]:
        """
        Fetch news from CryptoPanic with pagination support.

        Args:
            currencies: List of currency symbols (e.g., ["BTC", "SUI"])
            limit: Maximum articles to return (default: 100)
            filter_type: Filter type - "rising", "hot", "bullish", "bearish", "important", "lol"
            **kwargs: Additional parameters (public, kind, regions, etc.)

        Returns:
            List of NewsArticle objects

        Raises:
            AuthenticationError: If API token is invalid
            RateLimitError: If rate limit exceeded
            NewsSourceError: For other API errors

        Note:
            The API returns ~20 results per page. To fetch 100 articles,
            this method will automatically follow the 'next' pagination URLs.
        """
        try:
            articles = []
            page = 1
            max_pages = 10  # Safety limit to prevent infinite loops

            # Initial fetch
            response = self._client.get_posts(
                currencies=currencies,
                filter_type=filter_type,
                **kwargs
            )

            # Validate response structure
            if not self.validate_response(response):
                raise NewsSourceError(
                    self._source_name,
                    "Invalid API response structure - missing 'results' field"
                )

            # Process first page
            results = response.get("results", [])
            logger.debug(f"Page {page}: Got {len(results)} results from API")

            for item in results:
                if len(articles) >= limit:
                    break
                try:
                    article = self._transform_post(item)
                    articles.append(article)
                except Exception as e:
                    logger.warning(f"Failed to transform post: {e}")
                    logger.debug(f"Problematic post data: {item}")
                    continue

            # Follow pagination if we need more articles
            next_url = response.get("next")

            while next_url and len(articles) < limit and page < max_pages:
                page += 1
                logger.debug(f"Fetching page {page} via pagination...")

                # Fetch next page
                response = self._client.get_posts_from_url(next_url)

                if not self.validate_response(response):
                    logger.warning("Invalid response structure in pagination, stopping")
                    break

                results = response.get("results", [])
                logger.debug(f"Page {page}: Got {len(results)} results from API")

                for item in results:
                    if len(articles) >= limit:
                        break
                    try:
                        article = self._transform_post(item)
                        articles.append(article)
                    except Exception as e:
                        logger.warning(f"Failed to transform post: {e}")
                        continue

                # Get next page URL
                next_url = response.get("next")

            logger.info(f"Fetched {len(articles)} articles from CryptoPanic ({page} pages)")
            return articles

        except CryptoPanicAuthError as e:
            raise AuthenticationError(self._source_name) from e
        except CryptoPanicRateLimitError as e:
            raise RateLimitError(self._source_name) from e
        except CryptoPanicAPIError as e:
            raise NewsSourceError(self._source_name, str(e), original_error=e)

    def _transform_post(self, post: Dict) -> NewsArticle:
        """
        Transform CryptoPanic API post to NewsArticle.

        Args:
            post: Single post from CryptoPanic API response

        Returns:
            NewsArticle object

        Notes:
            v2 Developer API has limited fields compared to v1:
            - No 'url' field (we generate placeholder)
            - No 'currencies' field in response (even when filtered)
            - No 'votes' field
            - No 'domain' or 'source' fields
        """
        # Parse published date
        published_str = post.get("published_at") or post.get("created_at")
        if published_str:
            # CryptoPanic format: "2026-03-27T10:00:00Z"
            published_at = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
        else:
            published_at = datetime.now()

        # Extract title (required)
        title = post.get("title", "Untitled")

        # Generate URL (v2 API doesn't provide URLs)
        # Use title-based placeholder for compatibility
        url = post.get("url", f"cryptopanic://{title}")

        # Extract optional fields (may not exist in v2 API)
        description = post.get("description")
        kind = post.get("kind")  # "news", "media", "blog"

        # Extract currencies if available (v2 often doesn't include this)
        currencies = None
        if "currencies" in post and post["currencies"]:
            if isinstance(post["currencies"], list):
                currencies = [c.get("code") if isinstance(c, dict) else c for c in post["currencies"]]

        # Extract domain if available
        domain = None
        if "domain" in post:
            domain = post["domain"]
        elif "source" in post and isinstance(post["source"], dict):
            domain = post["source"].get("domain")

        # Extract votes if available (not in v2 Developer API)
        votes = None
        if "votes" in post and isinstance(post["votes"], dict):
            votes = {
                "negative": post["votes"].get("negative", 0),
                "positive": post["votes"].get("positive", 0),
                "important": post["votes"].get("important", 0),
                "liked": post["votes"].get("liked", 0),
                "disliked": post["votes"].get("disliked", 0),
                "lol": post["votes"].get("lol", 0),
                "toxic": post["votes"].get("toxic", 0),
                "saved": post["votes"].get("saved", 0),
            }

        return NewsArticle(
            source=self._source_name,
            url=url,
            title=title,
            published_at=published_at,
            domain=domain,
            currencies=currencies,
            kind=kind,
            sentiment=None,  # CryptoPanic doesn't provide sentiment scores
            votes=votes,
            raw_data=post,
        )

    def is_available(self) -> bool:
        """Check if CryptoPanic API is available."""
        return self._client.ping()

    def validate_response(self, response_data: Dict) -> bool:
        """
        Validate CryptoPanic API response structure.

        Args:
            response_data: Raw API response

        Returns:
            True if valid structure, False otherwise
        """
        return isinstance(response_data, dict) and "results" in response_data

    def get_rate_limit_info(self) -> Optional[Dict]:
        """Get rate limit information."""
        return self._client.get_rate_limit_info()
