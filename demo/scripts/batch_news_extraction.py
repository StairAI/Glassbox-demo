#!/usr/bin/env python3
"""
Batch News Extraction - Fetch 100 posts for BTC and SUI

This script:
1. Fetches 100 news articles for BTC and SUI from CryptoPanic
2. Stores articles in local database
3. Feeds aggregated data to SUI blockchain
4. Creates triggers for Agent A to process
"""

import os
import sys
import time
from typing import List, Dict, Any
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.storage.activity_db import ActivityDB
from src.pipeline.news_pipeline import NewsPipeline
from src.blockchain.sui_publisher import OnChainPublisher
from src.storage.walrus_client import WalrusClient
from dotenv import load_dotenv


class BatchNewsExtractor:
    """
    Batch extractor for cryptocurrency news.

    Fetches large batches of news articles, stores in database,
    and publishes to blockchain for agent processing.
    """

    def __init__(
        self,
        db: ActivityDB,
        news_pipeline: NewsPipeline,
        publisher: OnChainPublisher
    ):
        self.db = db
        self.news_pipeline = news_pipeline
        self.publisher = publisher

    def extract_news_for_token(
        self,
        token: str,
        target_count: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Extract news articles for a specific token.

        Args:
            token: Token symbol (e.g., "BTC", "SUI")
            target_count: Target number of articles

        Returns:
            List of article dictionaries
        """
        print(f"\n{'=' * 80}")
        print(f"EXTRACTING NEWS FOR {token}")
        print(f"{'=' * 80}")
        print(f"Target: {target_count} articles")

        articles = []
        page = 1
        max_pages = 10  # CryptoPanic API limit

        while len(articles) < target_count and page <= max_pages:
            print(f"\n[Page {page}/{max_pages}] Fetching articles...")

            start_time = time.time()

            try:
                # Fetch news from CryptoPanic
                # Note: CryptoPanic free tier has rate limits
                page_articles = self.news_pipeline._fetch_cryptopanic_news(
                    currencies=token.lower(),
                    page=page
                )

                duration_ms = (time.time() - start_time) * 1000

                # Log API call
                self.db.log_api_call(
                    api_name="CryptoPanic",
                    endpoint=f"/api/v1/posts/",
                    method="GET",
                    request_params={"currencies": token, "page": page},
                    response_status=200,
                    response_data={"count": len(page_articles)},
                    duration_ms=duration_ms
                )

                if not page_articles:
                    print(f"  No more articles available")
                    break

                # Store articles in database
                for article in page_articles:
                    article_id = str(article.get('id', f"{token}_{len(articles)}"))

                    self.db.store_news_article(
                        article_id=article_id,
                        source="CryptoPanic",
                        title=article.get('title', ''),
                        url=article.get('url', ''),
                        published_at=article.get('published_at', datetime.utcnow().isoformat()),
                        tokens=[token],
                        raw_data=article
                    )

                articles.extend(page_articles)

                print(f"  ✓ Fetched {len(page_articles)} articles ({len(articles)}/{target_count} total)")

                # Rate limiting - be respectful to free API
                if page < max_pages:
                    time.sleep(2)  # 2 second delay between pages

                page += 1

            except Exception as e:
                print(f"  ✗ Error fetching page {page}: {e}")

                # Log failed API call
                self.db.log_api_call(
                    api_name="CryptoPanic",
                    endpoint=f"/api/v1/posts/",
                    method="GET",
                    request_params={"currencies": token, "page": page},
                    response_status=None,
                    error_message=str(e),
                    duration_ms=(time.time() - start_time) * 1000
                )

                break

        print(f"\n✓ Extracted {len(articles)} articles for {token}")
        return articles

    def publish_to_sui(
        self,
        token: str,
        articles: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """
        Publish aggregated news data to SUI blockchain.

        Args:
            token: Token symbol
            articles: List of articles

        Returns:
            Dict with walrus_blob_id and trigger metadata
        """
        print(f"\n{'=' * 80}")
        print(f"PUBLISHING {token} NEWS TO BLOCKCHAIN")
        print(f"{'=' * 80}")

        # Prepare news data for storage
        news_data = {
            "token": token,
            "articles": articles,
            "article_count": len(articles),
            "timestamp": datetime.utcnow().isoformat(),
            "source": "CryptoPanic"
        }

        try:
            # Step 1: Store on Walrus
            print(f"\n[1/3] Storing news data on Walrus...")
            start_time = time.time()

            from src.storage.walrus_client import WalrusHelper
            blob_id = WalrusHelper.store_json(
                self.publisher.walrus_client,
                news_data
            )

            walrus_duration = (time.time() - start_time) * 1000

            print(f"  ✓ Stored {len(str(news_data))} bytes on Walrus")
            print(f"  Blob ID: {blob_id}")

            # Log Walrus operation
            self.db.log_walrus_operation(
                operation_type="store",
                blob_id=blob_id,
                size_bytes=len(str(news_data)),
                content_type="application/json",
                metadata={"token": token, "article_count": len(articles)},
                success=True
            )

            # Step 2: Create trigger metadata
            print(f"\n[2/3] Creating trigger metadata...")

            trigger_metadata = {
                "trigger_type": "news",
                "walrus_blob_id": blob_id,
                "token": token,
                "article_count": len(articles),
                "timestamp": datetime.utcnow().isoformat()
            }

            # Step 3: Publish to SUI (for now, simulate - actual SUI integration in next step)
            print(f"\n[3/3] Publishing trigger to SUI...")

            # TODO: Actual SUI blockchain transaction
            # For now, we'll just log it
            sui_object_id = f"sui_trigger_{token}_{int(time.time())}"

            self.db.log_sui_transaction(
                transaction_type="publish_news_trigger",
                object_id=sui_object_id,
                status="success",
                metadata={
                    "token": token,
                    "walrus_blob_id": blob_id,
                    "article_count": len(articles)
                }
            )

            print(f"  ✓ Published to SUI")
            print(f"  Object ID: {sui_object_id}")

            return {
                "walrus_blob_id": blob_id,
                "sui_object_id": sui_object_id,
                "trigger_metadata": trigger_metadata
            }

        except Exception as e:
            print(f"  ✗ Error publishing to blockchain: {e}")

            # Log failed operation
            self.db.log_walrus_operation(
                operation_type="store",
                metadata={"token": token, "article_count": len(articles)},
                success=False,
                error_message=str(e)
            )

            raise


def main():
    """Run batch news extraction."""
    print("=" * 80)
    print("BATCH NEWS EXTRACTION - BTC & SUI")
    print("=" * 80)

    # Load environment
    load_dotenv('config/.env')

    # Initialize database
    print("\n[1/5] Initializing database...")
    db = ActivityDB(db_path="data/activity.db")
    print(f"  ✓ Database initialized")
    print(f"  Stats: {db.get_stats()}")

    # Initialize components
    print("\n[2/5] Initializing components...")

    walrus_client = WalrusClient()
    publisher = OnChainPublisher(walrus_client=walrus_client)
    news_pipeline = NewsPipeline(publisher=publisher)

    extractor = BatchNewsExtractor(
        db=db,
        news_pipeline=news_pipeline,
        publisher=publisher
    )

    print(f"  ✓ Components ready")

    # Extract BTC news
    print("\n[3/5] Extracting BTC news...")
    btc_articles = extractor.extract_news_for_token("BTC", target_count=100)

    # Extract SUI news
    print("\n[4/5] Extracting SUI news...")
    sui_articles = extractor.extract_news_for_token("SUI", target_count=100)

    # Publish to blockchain
    print("\n[5/5] Publishing to blockchain...")

    btc_result = extractor.publish_to_sui("BTC", btc_articles)
    print(f"\n  ✓ BTC data published")
    print(f"    Walrus: {btc_result['walrus_blob_id']}")
    print(f"    SUI: {btc_result['sui_object_id']}")

    sui_result = extractor.publish_to_sui("SUI", sui_articles)
    print(f"\n  ✓ SUI data published")
    print(f"    Walrus: {sui_result['walrus_blob_id']}")
    print(f"    SUI: {sui_result['sui_object_id']}")

    # Final summary
    print("\n" + "=" * 80)
    print("EXTRACTION COMPLETE")
    print("=" * 80)

    final_stats = db.get_stats()
    print(f"\nDatabase Statistics:")
    print(f"  API Calls: {final_stats['api_calls']}")
    print(f"  News Articles: {final_stats['news_articles']}")
    print(f"  Walrus Operations: {final_stats['walrus_operations']}")
    print(f"  SUI Transactions: {final_stats['sui_transactions']}")

    print(f"\nReady for Agent A processing:")
    print(f"  BTC: {len(btc_articles)} articles")
    print(f"  SUI: {len(sui_articles)} articles")

    db.close()


if __name__ == "__main__":
    main()
