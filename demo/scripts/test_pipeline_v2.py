#!/usr/bin/env python3
"""
Test NewsPipeline V2 - Per-article storage with deduplication

This script demonstrates the improved pipeline:
1. Fetch 20 articles in one API call
2. Deduplicate against database
3. Store each NEW article as separate Walrus blob
4. Create individual SUI triggers
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.pipeline.news_pipeline_v2 import NewsPipelineV2
from src.blockchain.sui_publisher import OnChainPublisher
from src.storage.walrus_client import WalrusClient
from src.storage.activity_db import ActivityDB
from src.demo.trigger_registry import TriggerRegistry
from dotenv import load_dotenv

def main():
    """Test NewsPipeline V2."""

    # Load environment
    load_dotenv('config/.env')

    print("=" * 80)
    print("NEWS PIPELINE V2 TEST")
    print("=" * 80)
    print()

    # API Key
    api_key = "1faf4af4f599defbd358148d7edbce39c9da3dcb"

    # Get configurable owner address from environment
    owner_address = os.getenv("SUI_OWNER_ADDRESS")
    if owner_address:
        print(f"  ℹ Using custom owner address: {owner_address}")
    else:
        print(f"  ℹ No custom owner address set (will use default)")

    # Initialize components
    print("\nInitializing components...")

    # Walrus client
    walrus_enabled = os.getenv("WALRUS_ENABLED", "false").lower() == "true"
    if walrus_enabled:
        walrus_client = WalrusClient(
            publisher_url=os.getenv("WALRUS_PUBLISHER_URL"),
            aggregator_url=os.getenv("WALRUS_AGGREGATOR_URL"),
            simulated=False
        )
        print(f"  ✓ Walrus: Real testnet")
    else:
        walrus_client = WalrusClient(simulated=True)
        print(f"  ✓ Walrus: Simulated mode")

    # Database
    db = ActivityDB(db_path="data/activity.db")
    print(f"  ✓ Database: data/activity.db")

    # Trigger registry
    registry = TriggerRegistry(registry_path="data/trigger_registry.json")
    print(f"  ✓ Registry: data/trigger_registry.json")

    # Publisher (with configurable owner)
    publisher = OnChainPublisher(
        walrus_client=walrus_client,
        owner_address=owner_address,  # Pass owner address from env
        simulated=True  # For demo, we simulate SUI transactions
    )
    if owner_address:
        print(f"  ✓ Publisher initialized with custom owner: {owner_address[:16]}...")
    else:
        print(f"  ✓ Publisher initialized with default owner")

    # Pipeline V2 (with configurable owner)
    pipeline = NewsPipelineV2(
        api_token=api_key,
        publisher=publisher,
        db=db,
        owner_address=owner_address  # Pass owner address to pipeline
    )
    print(f"  ✓ Pipeline V2 ready")

    print()

    # Test 1: Fetch BTC articles
    print("=" * 80)
    print("TEST 1: Fetch BTC articles (limit 20)")
    print("=" * 80)

    triggers_btc = pipeline.fetch_and_publish(
        currencies=["BTC"],
        limit=20
    )

    print(f"\n✓ BTC Processing complete:")
    print(f"  - New articles published: {len(triggers_btc)}")
    if triggers_btc:
        print(f"  - First trigger ID: {triggers_btc[0].object_id[:32]}...")
        print(f"  - First Walrus blob: {triggers_btc[0].walrus_blob_id[:32]}...")

    # Test 2: Fetch SUI articles
    print("\n" + "=" * 80)
    print("TEST 2: Fetch SUI articles (limit 20)")
    print("=" * 80)

    triggers_sui = pipeline.fetch_and_publish(
        currencies=["SUI"],
        limit=20
    )

    print(f"\n✓ SUI Processing complete:")
    print(f"  - New articles published: {len(triggers_sui)}")
    if triggers_sui:
        print(f"  - First trigger ID: {triggers_sui[0].object_id[:32]}...")
        print(f"  - First Walrus blob: {triggers_sui[0].walrus_blob_id[:32]}...")

    # Test 3: Run again to test deduplication
    print("\n" + "=" * 80)
    print("TEST 3: Re-fetch BTC articles (should skip duplicates)")
    print("=" * 80)

    triggers_btc_2 = pipeline.fetch_and_publish(
        currencies=["BTC"],
        limit=20
    )

    print(f"\n✓ BTC Re-fetch complete:")
    print(f"  - New articles published: {len(triggers_btc_2)}")
    print(f"  - Expected: 0 (all should be deduplicated)")

    # Display statistics
    print("\n" + "=" * 80)
    print("FINAL STATISTICS")
    print("=" * 80)

    stats = pipeline.get_statistics()
    print(f"\n  Total articles in DB: {stats['total_articles_processed']}")
    print(f"  Total API calls: {stats['total_api_calls']}")
    print(f"  Total Walrus operations: {stats['total_walrus_operations']}")
    print(f"  Total SUI transactions: {stats['total_sui_transactions']}")

    # Trigger registry summary
    print(f"\n  Trigger Registry:")
    news_triggers = registry.get_triggers(trigger_type="news")
    print(f"    - News triggers: {len(news_triggers)}")

    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print()

    # Show sample article from database
    print("Sample articles from database:")
    articles = db.get_news_articles(limit=3)
    for i, article in enumerate(articles, 1):
        print(f"\n  {i}. {article['title'][:80]}")
        print(f"     Source: {article['source']}")
        print(f"     URL: {article['url'][:60]}...")
        print(f"     Published: {article['published_at']}")

    print()


if __name__ == "__main__":
    main()
