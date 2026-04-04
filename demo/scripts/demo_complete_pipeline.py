#!/usr/bin/env python3
"""
Complete Pipeline Demo: News → Walrus → Signal → Agent A

This demonstrates:
1. NewsPipeline fetches real news from CryptoPanic
2. Stores full data on Walrus (real testnet!)
3. Creates signal in SignalRegistry
4. Agent A reads signal and fetches data from Walrus
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
from src.demo.signal_registry import SignalRegistry
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
        simulated=True  # For demo, we use SignalRegistry instead of real smart contracts
    )
    print(f"  ✓ OnChainPublisher: Configured")

    # Signal registry (replaces smart contracts for demo)
    registry = SignalRegistry()
    print(f"  ✓ SignalRegistry: Ready")
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
    signal = news_pipeline.fetch_and_publish(
        currencies=["BTC", "ETH"],
        limit=5
    )

    # Register signal in registry
    print("Registering signal...")
    signal_id = registry.register_signal({
        "signal_type": "news",
        "walrus_blob_id": signal.walrus_blob_id,
        "data_hash": signal.data_hash,
        "size_bytes": signal.size_bytes,
        "articles_count": signal.articles_count,
        "timestamp": signal.timestamp.isoformat(),
        "producer": "news_pipeline"
    })
    print(f"  ✓ Signal registered: {signal_id}")
    print()

    # ===========================================================================
    # STEP 2: AGENT A READS TRIGGER
    # ===========================================================================
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "STEP 2: AGENT A READS TRIGGER" + " " * 23 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    print("Agent A checking for new signals...")

    # Agent reads signals from registry
    news_signals = registry.get_signals(signal_type="news", limit=1)

    if not news_signals:
        print("  No signals found")
        return

    latest_signal = news_signals[0]
    print(f"  ✓ Found signal: {latest_signal['signal_id']}")
    print(f"  ✓ Walrus blob: {latest_signal['walrus_blob_id'][:32]}...")
    print(f"  ✓ Articles count: {latest_signal['articles_count']}")
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

    # Create signal object from registry data
    from src.abstract import NewsSignal
    from datetime import datetime

    signal_obj = NewsSignal(
        object_id=latest_signal['signal_id'],
        walrus_blob_id=latest_signal['walrus_blob_id'],
        data_hash=latest_signal['data_hash'],
        size_bytes=latest_signal['size_bytes'],
        articles_count=latest_signal['articles_count'],
        timestamp=datetime.fromisoformat(latest_signal['timestamp']),
        producer=latest_signal['producer']
    )

    # Fetch full data (this will get from Walrus!)
    news_data = signal_obj.fetch_full_data()

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
    print("  4. Publish sentiment signal signal")
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
    print(f"  1. NewsPipeline fetched {signal.articles_count} articles from CryptoPanic")
    print(f"  2. Stored {signal.size_bytes:,} bytes on Walrus testnet")
    print(f"  3. Created signal in SignalRegistry")
    print(f"  4. Agent A read signal and fetched data from Walrus")
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
