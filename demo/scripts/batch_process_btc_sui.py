#!/usr/bin/env python3
"""
Batch Processing Script - BTC & SUI News Analysis

This script:
1. Extracts 100 news posts for BTC and SUI using existing NewsPipeline
2. Feeds data to SUI blockchain via OnChainPublisher
3. Agent A reads the data and outputs sentiment signals to SUI

Leverages existing modules:
- NewsPipeline (news extraction)
- OnChainPublisher (Walrus + SUI publishing)
- AgentA (sentiment analysis)
- TriggerRegistry (trigger tracking)
"""

import os
import sys
import time
from typing import List, Dict
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.pipeline.news_pipeline import NewsPipeline
from src.blockchain.sui_publisher import OnChainPublisher
from src.storage.walrus_client import WalrusClient
from src.agents.agent_a_sentiment import AgentA
from src.demo.trigger_registry import TriggerRegistry
from src.storage.activity_db import ActivityDB
from dotenv import load_dotenv


def fetch_batch_news(
    pipeline: NewsPipeline,
    db: ActivityDB,
    token: str,
    target_count: int = 100
) -> List[Dict]:
    """
    Fetch batch of news articles for a token using CryptoPanic API.

    Args:
        pipeline: NewsPipeline instance
        db: ActivityDB for logging
        token: Token symbol (BTC or SUI)
        target_count: Target number of articles

    Returns:
        List of article dictionaries
    """
    print(f"\n{'=' * 80}")
    print(f"FETCHING NEWS FOR {token}")
    print(f"{'=' * 80}")
    print(f"Target: {target_count} articles")

    all_articles = []
    page = 1
    max_pages = 10  # API limit

    while len(all_articles) < target_count and page <= max_pages:
        print(f"\n  [Page {page}] Fetching...", end=" ")

        start_time = time.time()

        try:
            # Use existing pipeline's source to fetch news
            articles = pipeline.source.fetch_news(
                currencies=[token],
                limit=min(20, target_count - len(all_articles))  # CryptoPanic returns ~20 per page
            )

            duration_ms = (time.time() - start_time) * 1000

            if articles:
                # Convert article objects to dicts
                for article in articles:
                    all_articles.append({
                        "title": article.title,
                        "source": article.source,
                        "published_at": article.published_at.isoformat(),
                        "url": article.url,
                        "raw_data": article.raw_data
                    })

                print(f"✓ {len(articles)} articles (total: {len(all_articles)})")

                # Log to database
                db.log_api_call(
                    api_name="CryptoPanic",
                    endpoint="/api/v1/posts/",
                    method="GET",
                    request_params={"currencies": token, "page": page},
                    response_status=200,
                    response_data={"count": len(articles)},
                    duration_ms=duration_ms
                )

                # Store articles in database
                for article in articles:
                    db.store_news_article(
                        article_id=str(article.raw_data.get('id', f"{token}_{len(all_articles)}")),
                        source="CryptoPanic",
                        title=article.title,
                        url=article.url,
                        published_at=article.published_at.isoformat(),
                        tokens=[token],
                        raw_data=article.raw_data
                    )
            else:
                print("No more articles available")
                break

            # Be respectful to API - rate limiting
            time.sleep(2)
            page += 1

        except Exception as e:
            print(f"✗ Error: {e}")
            db.log_api_call(
                api_name="CryptoPanic",
                endpoint="/api/v1/posts/",
                method="GET",
                request_params={"currencies": token, "page": page},
                error_message=str(e),
                duration_ms=(time.time() - start_time) * 1000
            )
            break

    print(f"\n✓ Total extracted: {len(all_articles)} articles for {token}")
    return all_articles


def publish_news_to_sui(
    publisher: OnChainPublisher,
    registry: TriggerRegistry,
    db: ActivityDB,
    token: str,
    articles: List[Dict]
) -> str:
    """
    Publish news data to SUI blockchain via Walrus + OnChainPublisher.

    Args:
        publisher: OnChainPublisher instance
        registry: TriggerRegistry for tracking
        db: ActivityDB for logging
        token: Token symbol
        articles: List of articles

    Returns:
        Trigger ID
    """
    print(f"\n{'=' * 80}")
    print(f"PUBLISHING {token} NEWS TO SUI")
    print(f"{'=' * 80}")

    # Prepare news data
    news_data = {
        "articles": articles,
        "fetch_timestamp": datetime.utcnow().isoformat(),
        "total_count": len(articles)
    }

    print(f"  Articles: {len(articles)}")
    print(f"  Data size: {len(str(news_data)):,} bytes")

    # Publish using existing OnChainPublisher
    trigger = publisher.publish_news_trigger(
        news_data=news_data,
        producer=f"batch_processor_{token.lower()}"
    )

    # Log to database
    db.log_walrus_operation(
        operation_type="store",
        blob_id=trigger.walrus_blob_id,
        size_bytes=trigger.size_bytes,
        metadata={"token": token, "article_count": len(articles)},
        success=True
    )

    db.log_sui_transaction(
        transaction_type="publish_news_trigger",
        object_id=trigger.object_id,
        metadata={
            "token": token,
            "walrus_blob_id": trigger.walrus_blob_id,
            "article_count": len(articles)
        },
        status="success"
    )

    # Register trigger
    trigger_id = registry.register_trigger({
        "trigger_type": "news",
        "object_id": trigger.object_id,
        "walrus_blob_id": trigger.walrus_blob_id,
        "data_hash": trigger.data_hash,  # Add data_hash for verification
        "articles_count": trigger.articles_count,
        "size_bytes": trigger.size_bytes,
        "producer": f"batch_processor_{token.lower()}",
        "timestamp": trigger.timestamp.isoformat() if hasattr(trigger.timestamp, 'isoformat') else trigger.timestamp
    })

    print(f"\n✓ Published to SUI")
    print(f"  Trigger ID: {trigger_id}")
    print(f"  Walrus Blob: {trigger.walrus_blob_id[:32]}...")
    print(f"  SUI Object: {trigger.object_id[:32]}...")

    return trigger_id


def process_with_agent_a(
    agent: AgentA,
    db: ActivityDB,
    token: str
) -> None:
    """
    Process news triggers with Agent A to generate sentiment signals.

    Args:
        agent: AgentA instance
        db: ActivityDB for logging
        token: Token being processed
    """
    print(f"\n{'=' * 80}")
    print(f"AGENT A: PROCESSING {token} NEWS")
    print(f"{'=' * 80}")

    start_time = time.time()

    # Run Agent A (processes all unprocessed news triggers)
    signal_triggers = agent.run(max_triggers=1)

    processing_time_ms = (time.time() - start_time) * 1000

    if signal_triggers:
        signal = signal_triggers[0]

        print(f"\n✓ Sentiment Signal Generated")
        print(f"\n  Sentiment Scores:")

        # Display token sentiments
        if "tokens" in signal.signal_value:
            for token_data in signal.signal_value["tokens"]:
                print(f"    {token_data['target_token']}: {token_data['target_token_sentiment']:.2f} (confidence: {token_data['confidence']:.2f})")
                if 'reasoning' in token_data and token_data['reasoning']:
                    print(f"      → {token_data['reasoning'][:100]}...")

        print(f"\n  Overall Confidence: {signal.confidence:.2f}")
        print(f"  Producer: {signal.producer}")
        print(f"  Reasoning Trace: {signal.walrus_trace_id[:32] if signal.walrus_trace_id else 'N/A'}...")

        # Log processing to database
        db.log_trigger_processing(
            trigger_id=signal.object_id,
            trigger_type="signal",
            agent_id="agent_a_sentiment",
            output_data=signal.signal_value,
            confidence=signal.confidence,
            reasoning_blob_id=signal.walrus_trace_id,
            processing_time_ms=processing_time_ms,
            success=True
        )

        # Log signal publication to SUI
        db.log_sui_transaction(
            transaction_type="publish_sentiment_signal",
            object_id=signal.object_id,
            metadata={
                "token": token,
                "confidence": signal.confidence,
                "reasoning_blob_id": signal.walrus_trace_id
            },
            status="success"
        )

        print(f"\n✓ Signal published to SUI")
        print(f"  Signal Object ID: {signal.object_id[:32]}...")

    else:
        print("\n✗ No signals generated (no unprocessed triggers)")


def main():
    """Run batch processing for BTC and SUI."""
    print("\n" + "=" * 80)
    print("BATCH PROCESSING: BTC & SUI NEWS → SENTIMENT ANALYSIS")
    print("=" * 80)

    # Load environment
    load_dotenv('config/.env')

    # Initialize database
    print("\n[1/6] Initializing database...")
    db = ActivityDB(db_path="data/activity.db")
    print(f"  ✓ Database ready")

    # Initialize components
    print("\n[2/6] Initializing components...")

    walrus_client = WalrusClient()
    publisher = OnChainPublisher(walrus_client=walrus_client)
    registry = TriggerRegistry()

    api_token = os.getenv("CRYPTOPANIC_API_TOKEN")
    pipeline = NewsPipeline(api_token=api_token, publisher=publisher)

    # Initialize Agent A for both BTC and SUI
    agent_a = AgentA(
        registry=registry,
        publisher=publisher,
        target_tokens=["BTC", "SUI"]  # Analyze both tokens
    )

    print(f"  ✓ Components initialized")
    print(f"    - Walrus: {'✓ Real Testnet' if not walrus_client.simulated else '✗ Simulated'}")
    print(f"    - Agent A LLM: {'✓ Claude 4.5' if agent_a.llm_available else '✗ Fallback'}")

    # ================================================================================
    # PART 1: BTC Processing
    # ================================================================================

    print("\n" + "=" * 80)
    print("PART 1: BTC PROCESSING")
    print("=" * 80)

    # Fetch BTC news
    print("\n[3/6] Fetching BTC news (target: 100 articles)...")
    btc_articles = fetch_batch_news(pipeline, db, "BTC", target_count=100)

    # Publish to SUI
    print("\n[4/6] Publishing BTC news to SUI...")
    btc_trigger_id = publish_news_to_sui(publisher, registry, db, "BTC", btc_articles)

    # Process with Agent A
    print("\n[5/6] Processing BTC with Agent A...")
    process_with_agent_a(agent_a, db, "BTC")

    # ================================================================================
    # PART 2: SUI Processing
    # ================================================================================

    print("\n" + "=" * 80)
    print("PART 2: SUI PROCESSING")
    print("=" * 80)

    # Fetch SUI news
    print("\n[3/6] Fetching SUI news (target: 100 articles)...")
    sui_articles = fetch_batch_news(pipeline, db, "SUI", target_count=100)

    # Publish to SUI
    print("\n[4/6] Publishing SUI news to SUI...")
    sui_trigger_id = publish_news_to_sui(publisher, registry, db, "SUI", sui_articles)

    # Process with Agent A
    print("\n[5/6] Processing SUI with Agent A...")
    process_with_agent_a(agent_a, db, "SUI")

    # ================================================================================
    # SUMMARY
    # ================================================================================

    print("\n" + "=" * 80)
    print("BATCH PROCESSING COMPLETE")
    print("=" * 80)

    # Database statistics
    stats = db.get_stats()
    print(f"\nDatabase Statistics:")
    print(f"  API Calls: {stats['api_calls']}")
    print(f"  News Articles: {stats['news_articles']}")
    print(f"  Walrus Operations: {stats['walrus_operations']}")
    print(f"  SUI Transactions: {stats['sui_transactions']}")
    print(f"  Trigger Processing: {stats['trigger_processing']}")

    print(f"\nProcessing Summary:")
    print(f"  BTC Articles: {len(btc_articles)}")
    print(f"  SUI Articles: {len(sui_articles)}")
    print(f"  Total Articles: {len(btc_articles) + len(sui_articles)}")

    print(f"\nTrigger Registry:")
    news_triggers = registry.get_triggers(trigger_type="news")
    signal_triggers = registry.get_triggers(trigger_type="signal")
    print(f"  News Triggers: {len(news_triggers)}")
    print(f"  Signal Triggers: {len(signal_triggers)}")

    print(f"\n✓ Complete end-to-end flow:")
    print(f"  1. Extracted news from CryptoPanic API")
    print(f"  2. Stored articles in local database")
    print(f"  3. Published news data to Walrus (decentralized storage)")
    print(f"  4. Created triggers on SUI blockchain")
    print(f"  5. Agent A read triggers from SUI")
    print(f"  6. Agent A fetched full data from Walrus")
    print(f"  7. Agent A analyzed sentiment")
    print(f"  8. Agent A published signals back to SUI")
    print(f"  9. All activities logged in database")

    print(f"\n📊 View database: sqlite3 data/activity.db")
    print(f"📋 View triggers: cat data/trigger_registry.json")
    print()

    db.close()


if __name__ == "__main__":
    main()
