#!/usr/bin/env python3
"""
Complete Demo: Data Pipeline Architecture (Corrected)

This demonstrates the corrected architecture where:
- Data Pipelines (NOT agents) fetch from off-chain and publish to on-chain
- Real Agents read from on-chain and perform LLM reasoning

Flow:
1. NewsPipeline fetches news → publishes to SUI blockchain
2. PricePipeline fetches prices → publishes to SUI blockchain
3. Agent A reads from on-chain → performs sentiment analysis (LLM)
4. Agent B reads from on-chain → generates investment signals (LLM)

Key Distinction:
- Pipelines: No LLM, no reasoning, pure ETL
- Agents: LLM-powered reasoning with Walrus traces
"""

import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline.news_pipeline import NewsPipeline
from src.pipeline.price_pipeline import PricePipeline
from src.blockchain.sui_publisher import OnChainPublisher, OnChainEventEmitter
from dotenv import load_dotenv

# Load environment
load_dotenv("config/.env")


def main():
    """Run complete pipeline architecture demo."""
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "DATA PIPELINE ARCHITECTURE (CORRECTED)" + " " * 16 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    print("Architecture Overview:")
    print("-" * 80)
    print("1. Data Pipelines (NOT agents):")
    print("   - NewsPipeline: Fetch news → Publish to SUI")
    print("   - PricePipeline: Fetch prices → Publish to SUI")
    print("   - No LLM, no reasoning, pure ETL")
    print()
    print("2. Real Agents (with LLM reasoning):")
    print("   - Agent A: Read news from SUI → Sentiment analysis (LLM)")
    print("   - Agent B: Read sentiment + prices → Investment signals (LLM)")
    print("   - Reasoning traces stored on Walrus")
    print()
    print("=" * 80)
    print()

    # Initialize blockchain components (simulated mode)
    print("[SETUP] Initializing blockchain components (simulated mode)")
    publisher = OnChainPublisher(simulated=True)
    event_emitter = OnChainEventEmitter(simulated=True)
    print("✓ OnChainPublisher ready")
    print("✓ OnChainEventEmitter ready")
    print()

    # ===========================================================================
    # PART 1: NEWS PIPELINE (NOT AN AGENT)
    # ===========================================================================
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "PART 1: NEWS PIPELINE (NOT AN AGENT)" + " " * 21 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    api_token = os.getenv("CRYPTOPANIC_API_TOKEN")
    if not api_token:
        print("❌ CRYPTOPANIC_API_TOKEN not found in .env")
        return

    # Initialize News Pipeline
    news_pipeline = NewsPipeline(
        api_token=api_token,
        publisher=publisher,
        event_emitter=event_emitter
    )

    # Run pipeline: Fetch news and publish to blockchain
    news_object_id = news_pipeline.fetch_and_publish(
        currencies=["BTC", "ETH"],
        limit=5
    )

    print(f"\n✓ News data published to blockchain")
    print(f"✓ Object ID: {news_object_id}")
    print()

    # ===========================================================================
    # PART 2: PRICE PIPELINE (NOT AN AGENT)
    # ===========================================================================
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 19 + "PART 2: PRICE PIPELINE (NOT AN AGENT)" + " " * 20 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    # Initialize Price Pipeline
    price_pipeline = PricePipeline(
        api_key=None,  # Free tier
        publisher=publisher,
        event_emitter=event_emitter
    )

    # Run pipeline: Fetch prices and publish to blockchain
    price_object_id = price_pipeline.fetch_and_publish(
        symbols=["BTC", "ETH", "SUI"]
    )

    print(f"\n✓ Price data published to blockchain")
    print(f"✓ Object ID: {price_object_id}")
    print()

    # ===========================================================================
    # PART 3: AGENT A - SENTIMENT ANALYSIS (REAL AGENT WITH LLM)
    # ===========================================================================
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "PART 3: AGENT A - SENTIMENT ANALYSIS (REAL AGENT)" + " " * 12 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    print("NOTE: This would be a real agent with LLM reasoning")
    print()
    print("Agent A Flow:")
    print("1. Detect 'news_available' event from blockchain")
    print(f"2. Fetch full news data from SUI (Object ID: {news_object_id})")
    print("3. Use LLM to analyze sentiment:")
    print("   - Prompt: 'Analyze sentiment of these Bitcoin and Ethereum articles'")
    print("   - LLM processes articles and generates sentiment scores")
    print("4. Store reasoning trace on Walrus:")
    print("   - Input: News articles (from blockchain)")
    print("   - LLM Prompt: Full prompt sent to LLM")
    print("   - LLM Response: Complete reasoning chain")
    print("   - Output: Sentiment signals")
    print("5. Publish sentiment signals back to blockchain")
    print()
    print("Simulated Output:")
    print("  ✓ Sentiment Analysis Complete")
    print("  ✓ BTC: Bullish (0.72)")
    print("  ✓ ETH: Neutral (0.45)")
    print("  ✓ Reasoning trace stored on Walrus: blob_id_abc123...")
    print("  ✓ Sentiment signals published to SUI: 0xdef456...")
    print()

    # ===========================================================================
    # PART 4: AGENT B - INVESTMENT SIGNALS (REAL AGENT WITH LLM)
    # ===========================================================================
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 12 + "PART 4: AGENT B - INVESTMENT SIGNALS (REAL AGENT)" + " " * 13 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    print("NOTE: This would be a real agent with LLM reasoning")
    print()
    print("Agent B Flow:")
    print("1. Detect 'sentiment_available' and 'price_updated' events")
    print("2. Fetch data from blockchain:")
    print("   - Sentiment signals from Agent A")
    print(f"   - Price data (Object ID: {price_object_id})")
    print("3. Use LLM to generate investment signals:")
    print("   - Prompt: 'Given bullish sentiment and price of $X, generate signal'")
    print("   - LLM analyzes combined data and generates recommendations")
    print("4. Store reasoning trace on Walrus:")
    print("   - Input: Sentiment signals + Price data")
    print("   - LLM Reasoning: Analysis of market conditions")
    print("   - Output: Investment signals (BUY/SELL/HOLD)")
    print("5. Publish investment signals to blockchain")
    print()
    print("Simulated Output:")
    print("  ✓ Investment Signal Generated")
    print("  ✓ BTC: STRONG BUY (confidence: 0.85)")
    print("  ✓ ETH: HOLD (confidence: 0.60)")
    print("  ✓ Reasoning trace stored on Walrus: blob_id_xyz789...")
    print("  ✓ Signals published to SUI: 0xghi012...")
    print()

    # ===========================================================================
    # SUMMARY
    # ===========================================================================
    print()
    print("=" * 80)
    print("ARCHITECTURE SUMMARY")
    print("=" * 80)
    print()
    print("Data Flow:")
    print("  Off-Chain APIs → Pipelines → SUI Blockchain → Agents (LLM) → Output")
    print()
    print("Key Distinction:")
    print()
    print("  Pipelines (NOT Agents):")
    print("    ✓ Pure ETL (Extract, Transform, Load)")
    print("    ✓ No LLM, no reasoning")
    print("    ✓ Just move data: API → Blockchain")
    print("    ✓ Producer Type: 'pipeline'")
    print()
    print("  Real Agents:")
    print("    ✓ LLM-powered reasoning")
    print("    ✓ Read from blockchain (not APIs)")
    print("    ✓ Reasoning traces on Walrus")
    print("    ✓ Producer Type: 'agent'")
    print()
    print("Data Storage:")
    print("  • Raw Data: SUI blockchain (via RawDataObject)")
    print("  • Reasoning Traces: Walrus DA (immutable)")
    print("  • RAID Scores: SUI smart contracts (queryable)")
    print()
    print("Benefits:")
    print("  ✓ Clear separation: pipelines vs agents")
    print("  ✓ All agent inputs come from blockchain (verifiable)")
    print("  ✓ Complete reasoning transparency (Walrus traces)")
    print("  ✓ Data lineage tracking (on-chain)")
    print()
    print("Next Steps:")
    print("  1. Implement Agent A with LLM reasoning")
    print("  2. Implement Agent B with LLM reasoning")
    print("  3. Deploy Move contracts to SUI testnet")
    print("  4. Integrate Walrus SDK for reasoning storage")
    print()


if __name__ == "__main__":
    main()
