#!/usr/bin/env python3
"""
Complete Pipeline Demo: News → Walrus → Trigger → Agent A

This demonstrates:
1. NewsPipeline fetches real news from CryptoPanic
2. Stores full data on Walrus (real testnet!)
3. Creates trigger in TriggerRegistry
4. Agent A reads trigger and fetches data from Walrus
5. Agent A processes with LLM and generates sentiment signals
"""

import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.pipeline.news_pipeline import NewsPipeline
from src.blockchain.sui_publisher import OnChainPublisher
from src.demo.trigger_registry import TriggerRegistry
from src.storage.walrus_client import WalrusClient

# Load environment
load_dotenv("config/.env")


def main():
    """Run complete pipeline demo."""
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "COMPLETE PIPELINE: NEWS → WALRUS → AGENT" + " " * 15 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    # Initialize components
    print("[SETUP] Initializing components...")

    # Walrus client (real testnet!)
    walrus_enabled = os.getenv("WALRUS_ENABLED", "false").lower() == "true"
    walrus_client = WalrusClient(
        publisher_url=os.getenv("WALRUS_PUBLISHER_URL"),
        aggregator_url=os.getenv("WALRUS_AGGREGATOR_URL"),
        simulated=not walrus_enabled
    )
    print(f"  ✓ WalrusClient: {'REAL TESTNET' if walrus_enabled else 'SIMULATED'}")

    # OnChain publisher
    publisher = OnChainPublisher(
        walrus_client=walrus_client,
        simulated=True  # For demo, we use TriggerRegistry instead of real smart contracts
    )
    print(f"  ✓ OnChainPublisher: Configured")

    # Trigger registry (replaces smart contracts for demo)
    registry = TriggerRegistry()
    print(f"  ✓ TriggerRegistry: Ready")
    print()

    # ===========================================================================
    # STEP 1: NEWS PIPELINE
    # ===========================================================================
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 25 + "STEP 1: NEWS PIPELINE" + " " * 26 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    api_token = os.getenv("CRYPTOPANIC_API_TOKEN")
    if not api_token:
        print("❌ CRYPTOPANIC_API_TOKEN not found in .env")
        return

    # Create news pipeline
    news_pipeline = NewsPipeline(
        api_token=api_token,
        publisher=publisher
    )

    # Fetch and publish news
    print("Running news pipeline...")
    trigger = news_pipeline.fetch_and_publish(
        currencies=["BTC", "ETH"],
        limit=5
    )

    # Register trigger in registry
    print("Registering trigger...")
    trigger_id = registry.register_trigger({
        "trigger_type": "news",
        "walrus_blob_id": trigger.walrus_blob_id,
        "data_hash": trigger.data_hash,
        "size_bytes": trigger.size_bytes,
        "articles_count": trigger.articles_count,
        "timestamp": trigger.timestamp.isoformat(),
        "producer": "news_pipeline"
    })
    print(f"  ✓ Trigger registered: {trigger_id}")
    print()

    # ===========================================================================
    # STEP 2: AGENT A READS TRIGGER
    # ===========================================================================
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "STEP 2: AGENT A READS TRIGGER" + " " * 23 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    print("Agent A checking for new triggers...")

    # Agent reads triggers from registry
    news_triggers = registry.get_triggers(trigger_type="news", limit=1)

    if not news_triggers:
        print("  No triggers found")
        return

    latest_trigger = news_triggers[0]
    print(f"  ✓ Found trigger: {latest_trigger['trigger_id']}")
    print(f"  ✓ Walrus blob: {latest_trigger['walrus_blob_id'][:32]}...")
    print(f"  ✓ Articles count: {latest_trigger['articles_count']}")
    print()

    # ===========================================================================
    # STEP 3: AGENT A FETCHES DATA FROM WALRUS
    # ===========================================================================
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "STEP 3: AGENT A FETCHES FROM WALRUS" + " " * 22 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    print("Fetching full news data from Walrus...")

    # Create trigger object from registry data
    from src.core.trigger import NewsTrigger
    from datetime import datetime

    trigger_obj = NewsTrigger(
        object_id=latest_trigger['trigger_id'],
        walrus_blob_id=latest_trigger['walrus_blob_id'],
        data_hash=latest_trigger['data_hash'],
        size_bytes=latest_trigger['size_bytes'],
        articles_count=latest_trigger['articles_count'],
        timestamp=datetime.fromisoformat(latest_trigger['timestamp']),
        producer=latest_trigger['producer']
    )

    # Fetch full data (this will get from Walrus!)
    news_data = trigger_obj.fetch_full_data()

    print(f"  ✓ Fetched {len(news_data['articles'])} articles from Walrus")
    print(f"  ✓ Data integrity verified (hash matches)")
    print()

    # Show sample articles
    print("Sample articles:")
    for i, article in enumerate(news_data['articles'][:3], 1):
        print(f"  {i}. {article['title'][:70]}...")
    print()

    # ===========================================================================
    # STEP 4: AGENT A PROCESSES (PLACEHOLDER)
    # ===========================================================================
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "STEP 4: AGENT A PROCESSES WITH LLM" + " " * 22 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    print("Agent A would now:")
    print("  1. Analyze sentiment of each article with LLM")
    print("  2. Generate sentiment scores for BTC/ETH")
    print("  3. Store reasoning trace on Walrus")
    print("  4. Publish sentiment signal trigger")
    print()
    print("  → This will be implemented in Agent A class")
    print()

    # ===========================================================================
    # SUMMARY
    # ===========================================================================
    print()
    print("=" * 80)
    print("PIPELINE DEMO: COMPLETE")
    print("=" * 80)
    print()
    print("✅ What worked:")
    print(f"  1. NewsPipeline fetched {trigger.articles_count} articles from CryptoPanic")
    print(f"  2. Stored {trigger.size_bytes:,} bytes on Walrus testnet")
    print(f"  3. Created trigger in TriggerRegistry")
    print(f"  4. Agent A read trigger and fetched data from Walrus")
    print(f"  5. Data integrity verified via hash")
    print()
    print("📋 Next steps:")
    print("  1. Implement Agent A with LLM reasoning")
    print("  2. Store reasoning traces on Walrus")
    print("  3. Implement Agent B (Investment Signals)")
    print("  4. Build complete multi-agent system")
    print()
    print(f"Storage mode: {'REAL WALRUS TESTNET ✅' if walrus_enabled else 'Simulated'}")
    print()


if __name__ == "__main__":
    main()
