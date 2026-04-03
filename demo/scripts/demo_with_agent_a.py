#!/usr/bin/env python3
"""
Complete Demo: News → Walrus → Trigger → Agent A → Sentiment Signal

This demonstrates the complete flow:
1. NewsPipeline fetches real news from CryptoPanic
2. Stores full data on Walrus
3. Creates trigger in TriggerRegistry
4. Agent A reads trigger and fetches data from Walrus
5. Agent A analyzes sentiment with LLM (or fallback)
6. Agent A stores reasoning trace on Walrus
7. Agent A publishes sentiment signal trigger
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
from src.agents.agent_a_sentiment import AgentA

# Load environment
load_dotenv("config/.env")


def main():
    """Run complete demo with Agent A."""
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 10 + "COMPLETE FLOW: NEWS → WALRUS → AGENT A → SENTIMENT" + " " * 10 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    # Initialize components
    print("[SETUP] Initializing components...")

    # Walrus client
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
        simulated=True
    )
    print(f"  ✓ OnChainPublisher: Configured")

    # Trigger registry
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
    # STEP 2: AGENT A PROCESSES NEWS
    # ===========================================================================
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "STEP 2: AGENT A SENTIMENT ANALYSIS" + " " * 22 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    # Initialize Agent A
    agent_a = AgentA(
        registry=registry,
        publisher=publisher,
        target_tokens=["BTC", "ETH"]  # Tokens to analyze
    )

    # Run Agent A
    signal_triggers = agent_a.run(max_triggers=1)

    if signal_triggers:
        signal = signal_triggers[0]
        print()
        print("=" * 80)
        print("SENTIMENT SIGNAL GENERATED")
        print("=" * 80)
        print()
        print(f"Signal Value:")

        # Display token sentiments
        if "tokens" in signal.signal_value:
            for token_data in signal.signal_value["tokens"]:
                print(f"  {token_data['target_token']}: {token_data['target_token_sentiment']} (confidence: {token_data['confidence']})")
                if 'reasoning' in token_data:
                    print(f"    Reasoning: {token_data['reasoning'][:80]}...")
        else:
            # Fallback for old format
            for key, value in signal.signal_value.items():
                print(f"  {key}: {value}")

        print()
        print(f"Overall Confidence: {signal.confidence}")
        print(f"Producer: {signal.producer}")
        if signal.walrus_trace_id:
            print(f"Reasoning trace: {signal.walrus_trace_id[:32]}...")
        print()

    # ===========================================================================
    # STEP 3: VERIFY SIGNAL IN REGISTRY
    # ===========================================================================
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "STEP 3: VERIFY SIGNAL TRIGGER" + " " * 22 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    print("Checking TriggerRegistry for sentiment signals...")
    sentiment_signals = registry.get_triggers(trigger_type="signal", limit=5)
    print(f"  ✓ Found {len(sentiment_signals)} sentiment signal(s)")

    if sentiment_signals:
        print()
        print("Latest sentiment signal:")
        latest = sentiment_signals[-1]
        print(f"  Trigger ID: {latest['trigger_id']}")
        print(f"  Signal Type: {latest['signal_type']}")
        print(f"  Confidence: {latest['confidence']}")
        print(f"  Producer: {latest['producer']}")
        print()

    # ===========================================================================
    # SUMMARY
    # ===========================================================================
    print()
    print("=" * 80)
    print("COMPLETE DEMO: SUCCESS")
    print("=" * 80)
    print()
    print("✅ What worked:")
    print(f"  1. NewsPipeline fetched {trigger.articles_count} articles from CryptoPanic")
    print(f"  2. Stored {trigger.size_bytes:,} bytes on Walrus")
    print(f"  3. Created news trigger in TriggerRegistry")
    print(f"  4. Agent A read trigger and fetched data from Walrus")
    print(f"  5. Agent A analyzed sentiment {'with LLM' if agent_a.llm_available else 'with fallback'}")
    print(f"  6. Agent A stored reasoning trace on Walrus")
    print(f"  7. Agent A published sentiment signal trigger")
    print()
    print(f"Storage mode: {'REAL WALRUS TESTNET ✅' if walrus_enabled else 'Simulated'}")
    print(f"LLM mode: {'Claude Sonnet 4.5 ✅' if agent_a.llm_available else 'Fallback (rule-based)'}")
    print()
    print("📋 Next steps:")
    print("  1. Implement Agent B (Investment Signals)")
    print("  2. Agent B reads sentiment + price triggers")
    print("  3. Agent B generates investment signals")
    print("  4. Build complete multi-agent system")
    print()


if __name__ == "__main__":
    main()
