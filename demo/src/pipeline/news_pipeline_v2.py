#!/usr/bin/env python3
"""
NewsPipeline V2: Improved ETL with per-article storage

CHANGES FROM V1:
- One API call fetches multiple articles
- Each article stored as separate Walrus blob
- Database deduplication (skip already processed articles)
- Individual SUI triggers per article
- Better tracking and logging

ARCHITECTURE:
1. Fetch articles list (one API call)
2. Check DB for already processed articles (deduplication)
3. Store each NEW article as separate Walrus blob
4. Create individual SUI trigger per article
5. Record all in ActivityDB
"""

from typing import List, Optional, Dict, Set
from datetime import datetime
import hashlib
import json

from src.data_clients.cryptopanic_client import CryptoPanicClient
from src.data_sources.cryptopanic_source import CryptoPanicSource
from src.blockchain.sui_publisher import OnChainPublisher
from src.core.trigger import NewsTrigger
from src.storage.activity_db import ActivityDB


class NewsPipelineV2:
    """
    Improved News ETL Pipeline with per-article Walrus storage.

    Key improvements:
    - Single API call to fetch all articles
    - Each article gets its own Walrus blob
    - Database deduplication prevents reprocessing
    - Individual SUI triggers for granular tracking

    Example:
        pipeline = NewsPipelineV2(
            api_token="YOUR_TOKEN",
            publisher=OnChainPublisher(),
            db=ActivityDB()
        )
        triggers = pipeline.fetch_and_publish(currencies=["BTC"], limit=20)
        # Returns list of NewsTrigger instances (one per article)
    """

    def __init__(
        self,
        api_token: Optional[str] = None,
        publisher: Optional[OnChainPublisher] = None,
        db: Optional[ActivityDB] = None,
        owner_address: Optional[str] = None,
        auto_register_account: bool = True
    ):
        """
        Initialize news pipeline V2.

        Args:
            api_token: CryptoPanic API token
            publisher: OnChainPublisher instance (with Walrus support)
            db: ActivityDB for tracking and deduplication
            owner_address: Optional owner address (passed to publisher if provided)
            auto_register_account: Auto-register owner address in mocked_accounts table
        """
        self.client = CryptoPanicClient(auth_token=api_token) if api_token else None
        self.source = CryptoPanicSource(api_token=api_token) if api_token else None
        self.publisher = publisher
        self.db = db
        self.owner_address = owner_address

        # Auto-register mocked account if enabled
        if auto_register_account and self.db and self.owner_address:
            self._register_account()

    def _register_account(self):
        """Register owner address as a mocked account in the database."""
        try:
            self.db.register_mocked_account(
                account_address=self.owner_address,
                project_name="news_pipeline_v2",
                description="News pipeline owner address for data indexing",
                metadata={"pipeline_type": "news", "version": "v2"}
            )
        except Exception as e:
            print(f"  ⚠ Warning: Could not register mocked account: {e}")

    def fetch_and_publish(
        self,
        currencies: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[NewsTrigger]:
        """
        Fetch news articles and publish each as separate Walrus blob.

        Flow:
        1. Single API call to fetch articles
        2. Deduplicate against database
        3. Store each NEW article as separate Walrus blob
        4. Create individual SUI trigger per article
        5. Record everything in database

        Args:
            currencies: List of currency symbols (e.g., ["BTC", "ETH"])
            limit: Maximum number of articles to fetch from API

        Returns:
            List of NewsTrigger instances (one per NEW article)
        """
        print(f"\n{'='*80}")
        print("NEWS PIPELINE V2: Starting ETL Process")
        print(f"{'='*80}")

        # Step 1: EXTRACT - Single API call
        print(f"\n[1/4] EXTRACT: Fetching from CryptoPanic API")
        print(f"  Currencies: {currencies}")
        print(f"  Limit: {limit}")

        start_time = datetime.now()
        articles = self.source.fetch_news(currencies=currencies, limit=limit)
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)

        print(f"  ✓ Fetched {len(articles)} articles in {duration_ms}ms")

        # Log API call
        if self.db:
            self.db.log_api_call(
                api_name="cryptopanic",
                endpoint="/posts/",
                method="GET",
                request_params={"currencies": currencies, "limit": limit},
                response_status=200,
                response_data={"count": len(articles)},
                error_message=None,
                duration_ms=duration_ms
            )

        # Step 2: DEDUPLICATION - Check database for existing articles
        print(f"\n[2/4] DEDUPLICATION: Checking for existing articles")

        new_articles = self._filter_new_articles(articles)
        skipped_count = len(articles) - len(new_articles)

        print(f"  ✓ New articles: {len(new_articles)}")
        print(f"  ✓ Skipped (already processed): {skipped_count}")

        if len(new_articles) == 0:
            print(f"\n  ℹ No new articles to process")
            return []

        # Step 3: TRANSFORM & LOAD - Process each article individually
        print(f"\n[3/4] TRANSFORM & LOAD: Publishing {len(new_articles)} articles")

        triggers = []

        for i, article in enumerate(new_articles, 1):
            print(f"\n  [{i}/{len(new_articles)}] Processing: {article.title[:60]}...")

            try:
                trigger = self._publish_single_article(article, currencies)
                triggers.append(trigger)
                print(f"      ✓ Published - Trigger: {trigger.object_id[:16]}...")

            except Exception as e:
                print(f"      ✗ Failed: {e}")
                continue

        # Step 4: SUMMARY
        print(f"\n[4/4] SUMMARY")
        print(f"  ✓ Successfully published: {len(triggers)} articles")
        print(f"  ✓ Total Walrus blobs created: {len(triggers)}")
        print(f"  ✓ Total SUI triggers created: {len(triggers)}")

        print(f"\n{'='*80}")
        print("NEWS PIPELINE V2: ETL Complete")
        print(f"{'='*80}\n")

        return triggers

    def _filter_new_articles(self, articles) -> List:
        """
        Filter out articles that have already been processed.

        Uses database to check if article URL already exists.

        Args:
            articles: List of NewsArticle objects

        Returns:
            List of articles that haven't been processed yet
        """
        if not self.db:
            return articles  # No DB, process all

        new_articles = []

        for article in articles:
            # Check if article URL already exists in database
            # We use URL as unique identifier
            existing = self.db.get_article_by_url(article.url)

            if existing is None:
                new_articles.append(article)

        return new_articles

    def _publish_single_article(
        self,
        article,
        currencies: Optional[List[str]] = None
    ) -> NewsTrigger:
        """
        Publish a single article to Walrus and SUI.

        Steps:
        1. Transform article to storage format
        2. Store on Walrus (get blob_id)
        3. Create SUI trigger
        4. Record in database

        Args:
            article: NewsArticle object
            currencies: Currency context for metadata

        Returns:
            NewsTrigger instance
        """
        # Transform to storage format
        article_data = {
            "title": article.title,
            "source": article.source,
            "published_at": article.published_at.isoformat(),
            "url": article.url,
            "currencies": currencies or [],
            "raw_data": article.raw_data,
            "processed_at": datetime.now().isoformat()
        }

        # Generate article ID (hash of URL)
        article_id = self._generate_article_id(article.url)

        # Publish to Walrus + SUI via OnChainPublisher
        # Note: OnChainPublisher.publish_news_trigger expects batch format
        # We wrap single article in the expected structure
        news_data = {
            "articles": [article_data],
            "fetch_timestamp": datetime.now().isoformat(),
            "total_count": 1
        }

        trigger = self.publisher.publish_news_trigger(
            news_data=news_data,
            producer="news_pipeline_v2"
        )

        # Record article in database
        if self.db:
            # Store in news_articles table
            self.db.store_news_article(
                article_id=article_id,
                source=article.source,
                title=article.title,
                url=article.url,
                published_at=article.published_at.isoformat(),
                tokens=",".join(currencies) if currencies else None,
                raw_data=article.raw_data
            )

            # Log Walrus operation
            self.db.log_walrus_operation(
                operation_type="store",
                blob_id=trigger.walrus_blob_id,
                data_hash=trigger.data_hash,
                size_bytes=trigger.size_bytes,
                content_type="application/json",
                metadata={"article_id": article_id, "title": article.title[:100]},
                success=True,
                error_message=None
            )

            # Log SUI transaction
            self.db.log_sui_transaction(
                transaction_type="create_trigger",
                transaction_digest=None,  # Would be real tx hash in production
                object_id=trigger.object_id,
                sender="news_pipeline_v2",
                gas_used=0,  # Simulated
                status="success",
                metadata={
                    "trigger_type": "news",
                    "article_count": 1,
                    "walrus_blob_id": trigger.walrus_blob_id
                },
                error_message=None
            )

        return trigger

    def _generate_article_id(self, url: str) -> str:
        """
        Generate unique article ID from URL.

        Args:
            url: Article URL

        Returns:
            Hash-based article ID
        """
        return hashlib.sha256(url.encode()).hexdigest()

    def get_statistics(self) -> Dict:
        """
        Get pipeline statistics from database.

        Returns:
            Dict with stats about processed articles, API calls, etc.
        """
        if not self.db:
            return {"error": "No database configured"}

        stats = self.db.get_stats()

        return {
            "total_articles_processed": stats.get("news_articles", 0),
            "total_api_calls": stats.get("api_calls", 0),
            "total_walrus_operations": stats.get("walrus_operations", 0),
            "total_sui_transactions": stats.get("sui_transactions", 0)
        }


class NewsSchedulerV2:
    """
    Scheduler for periodic news fetching using V2 pipeline.

    Runs news pipeline on schedule with deduplication support.

    Example:
        scheduler = NewsSchedulerV2(pipeline=news_pipeline_v2)
        scheduler.run_periodic(currencies=["BTC", "SUI"], interval_seconds=300)
    """

    def __init__(self, pipeline: NewsPipelineV2):
        self.pipeline = pipeline

    def run_once(
        self,
        currencies: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[NewsTrigger]:
        """Run pipeline once."""
        return self.pipeline.fetch_and_publish(currencies=currencies, limit=limit)

    def run_periodic(
        self,
        currencies: Optional[List[str]] = None,
        limit: int = 20,
        interval_seconds: int = 300
    ):
        """
        Run pipeline periodically.

        Args:
            currencies: Currency filters
            limit: Max articles per fetch
            interval_seconds: Seconds between runs
        """
        import time

        print(f"Starting periodic news fetching V2 (every {interval_seconds}s)")
        print(f"Currencies: {currencies}")
        print(f"Limit: {limit}")

        iteration = 0

        while True:
            try:
                iteration += 1
                print(f"\n{'='*80}")
                print(f"Iteration {iteration}")
                print(f"{'='*80}")

                triggers = self.run_once(currencies=currencies, limit=limit)

                print(f"\nSleeping for {interval_seconds} seconds...")
                time.sleep(interval_seconds)

            except KeyboardInterrupt:
                print("\n\nScheduler stopped by user")
                break
            except Exception as e:
                print(f"\n✗ Error in scheduler: {e}")
                import traceback
                traceback.print_exc()
                print(f"\nRetrying in {interval_seconds} seconds...")
                time.sleep(interval_seconds)
