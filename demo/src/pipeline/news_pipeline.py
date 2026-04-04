#!/usr/bin/env python3
"""
NewsPipeline: ETL pipeline for news data with Walrus storage

SIMPLIFIED ARCHITECTURE:
- All news data → Walrus (full storage)
- Only metadata + blob_id → SUI
- Returns NewsSignal for agents

This is NOT an agent - just pure ETL (Extract, Transform, Load).
"""

from typing import List, Optional
from datetime import datetime

from src.data_clients.cryptopanic_client import CryptoPanicClient
from src.data_sources.cryptopanic_source import CryptoPanicSource
from src.blockchain.sui_publisher import OnChainPublisher
from src.abstract import NewsSignal


class NewsPipeline:
    """
    News ETL Pipeline with Walrus storage.

    Simplified flow:
    1. Fetch news from CryptoPanic API
    2. Transform to standardized format
    3. Store ALL data on Walrus (cheap!)
    4. Publish metadata + blob_id to SUI
    5. Return NewsSignal

    No LLM, no reasoning - just data movement.

    Example:
        pipeline = NewsPipeline(
            api_token="YOUR_TOKEN",
            publisher=OnChainPublisher()
        )
        signal = pipeline.fetch_and_publish(currencies=["BTC"], limit=5)
    """

    def __init__(
        self,
        api_token: Optional[str] = None,
        publisher: Optional[OnChainPublisher] = None
    ):
        """
        Initialize news pipeline.

        Args:
            api_token: CryptoPanic API token (optional if using with publisher only)
            publisher: OnChainPublisher instance (with Walrus support)
        """
        # Layer 1: API Client (raw HTTP requests)
        self.client = CryptoPanicClient(auth_token=api_token) if api_token else None

        # Layer 2: Data Source (transformation to dataclasses)
        self.source = CryptoPanicSource(api_token=api_token) if api_token else None

        # Layer 3: On-chain publisher (with Walrus)
        self.publisher = publisher

    def fetch_and_publish(
        self,
        currencies: Optional[List[str]] = None,
        limit: int = 20
    ) -> NewsSignal:
        """
        Fetch news from API and publish to Walrus + SUI.

        This is the complete ETL flow:
        1. EXTRACT: Fetch from CryptoPanic API
        2. TRANSFORM: Convert to standardized format
        3. LOAD: Store on Walrus + metadata on SUI

        Args:
            currencies: List of currency symbols (e.g., ["BTC", "ETH"])
            limit: Maximum number of articles to fetch

        Returns:
            NewsSignal instance (reference to data on Walrus + SUI)
        """
        print(f"\n{'='*80}")
        print("NEWS PIPELINE: Starting ETL Process")
        print(f"{'='*80}")

        # Step 1: EXTRACT - Fetch from API
        print(f"\n[1/3] EXTRACT: Fetching from CryptoPanic API")
        print(f"  Currencies: {currencies}")
        print(f"  Limit: {limit}")

        articles = self.source.fetch_news(currencies=currencies, limit=limit)
        print(f"  ✓ Fetched {len(articles)} articles")

        # Step 2: TRANSFORM - Convert to storage format
        print(f"\n[2/3] TRANSFORM: Converting to storage format")

        news_data = self._transform_for_storage(articles)
        print(f"  ✓ Prepared {len(news_data['articles'])} articles")
        print(f"  ✓ Data size: {len(str(news_data)):,} bytes")

        # Step 3: LOAD - Publish to Walrus + SUI
        # OnChainPublisher handles:
        # - Storing full data on Walrus
        # - Publishing metadata to SUI
        # - Returning NewsSignal
        print(f"\n[3/3] LOAD: Publishing to Walrus + SUI")

        signal = self.publisher.publish_news_signal(
            news_data=news_data,
            producer="news_pipeline"
        )

        print(f"{'='*80}")
        print("NEWS PIPELINE: ETL Complete")
        print(f"{'='*80}")
        print(f"✓ News signal published: {signal.object_id[:16]}...")
        print(f"✓ Walrus blob: {signal.walrus_blob_id[:16]}...")
        print(f"✓ Articles count: {signal.articles_count}")
        print(f"✓ Size: {signal.size_bytes:,} bytes")
        print()

        return signal

    def _transform_for_storage(self, articles) -> dict:
        """
        Transform articles for Walrus storage.

        This is pure data transformation - no reasoning, no LLM.
        Just converts NewsArticle objects to serializable dicts.
        """
        articles_data = []

        for article in articles:
            articles_data.append({
                "title": article.title,
                "source": article.source,
                "published_at": article.published_at.isoformat(),
                "url": article.url,
                "raw_data": article.raw_data
            })

        return {
            "articles": articles_data,
            "fetch_timestamp": datetime.now().isoformat(),
            "total_count": len(articles_data)
        }


class NewsScheduler:
    """
    Scheduler for periodic news fetching.

    Runs news pipeline on schedule (e.g., every 5 minutes).

    Example:
        scheduler = NewsScheduler(pipeline=news_pipeline)
        scheduler.run_periodic(interval_seconds=300)  # Every 5 minutes
    """

    def __init__(self, pipeline: NewsPipeline):
        self.pipeline = pipeline

    def run_once(self, currencies: Optional[List[str]] = None) -> NewsSignal:
        """Run pipeline once."""
        return self.pipeline.fetch_and_publish(currencies=currencies)

    def run_periodic(self, currencies: Optional[List[str]] = None, interval_seconds: int = 300):
        """
        Run pipeline periodically.

        In production, this would use a proper scheduler like APScheduler.
        """
        import time

        print(f"Starting periodic news fetching (every {interval_seconds}s)")

        while True:
            try:
                self.run_once(currencies=currencies)
                print(f"Sleeping for {interval_seconds} seconds...")
                time.sleep(interval_seconds)
            except KeyboardInterrupt:
                print("\nScheduler stopped by user")
                break
            except Exception as e:
                print(f"Error in scheduler: {e}")
                time.sleep(interval_seconds)
