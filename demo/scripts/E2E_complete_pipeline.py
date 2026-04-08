#!/usr/bin/env python3
"""
Complete End-to-End Pipeline: All Three Agents (A, B, C)

This script runs the complete Glass Box Protocol pipeline in a single execution:
1. Fetches news data from CryptoPanic
2. Runs Agent A (sentiment analysis) on each news article
3. Fetches BTC price from CoinGecko
4. Runs Agent B (investment prediction) with price data
5. Runs Agent C (portfolio management) with price + Agent B prediction

All signals are registered with a SINGLE owner address for clean signal tracking.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv('config/.env')

import os
import json
import hashlib
from datetime import datetime
from src.data_sources.cryptopanic_source import CryptoPanicSource
from src.data_sources.coingecko_source import CoinGeckoSource
from src.agents.agent_a_sentiment import AgentASentiment
from src.agents.agent_b_investment import AgentBInvestment
from src.agents.agent_c_portfolio import AgentCPortfolio
from src.reasoning_ledger.reasoning_ledger_sdk import ReasoningLedger
from src.storage.walrus_client import WalrusClient
from src.blockchain.sui_publisher import OnChainPublisher
from src.demo.signal_registry import SignalRegistry


def main():
    print("=" * 80)
    print("COMPLETE END-TO-END PIPELINE: AGENTS A, B, C")
    print("=" * 80)
    print()

    # ========================================================================
    # SETUP: Initialize all components with SINGLE owner
    # ========================================================================
    print("[Setup] Initializing components...")

    # Create SINGLE owner address for entire pipeline (FIXED across all runs)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    owner_address = "0xDEMO_PIPELINE_OWNER"  # Fixed address for unified indexing

    # Walrus client
    walrus_publisher = os.getenv("WALRUS_PUBLISHER_URL", "https://publisher.walrus-testnet.walrus.space")
    walrus_aggregator = os.getenv("WALRUS_AGGREGATOR_URL", "https://aggregator.walrus-testnet.walrus.space")
    walrus_enabled = os.getenv("WALRUS_ENABLED", "false").lower() == "true"

    walrus_client = WalrusClient(
        publisher_url=walrus_publisher,
        aggregator_url=walrus_aggregator,
        simulated=not walrus_enabled
    )

    # Publisher (shared by all agents)
    publisher = OnChainPublisher(
        walrus_client=walrus_client,
        owner_address=owner_address,
        simulated=True
    )

    # Reasoning ledger (shared by all agents)
    reasoning_ledger = ReasoningLedger(walrus_client=walrus_client)

    # Signal registry (shared)
    registry = SignalRegistry(registry_path="data/signal_registry.json")

    # Data sources
    cryptopanic_token = os.getenv("CRYPTOPANIC_API_TOKEN")
    news_source = CryptoPanicSource(api_token=cryptopanic_token)

    coingecko_api_key = os.getenv("COINGECKO_API_KEY")
    price_source = CoinGeckoSource(api_key=coingecko_api_key)

    print(f"  ✓ Owner: {owner_address}")
    print(f"  ✓ Walrus mode: {'Real' if walrus_enabled else 'Simulated'}")
    print(f"  ✓ CoinGecko: {'Pro' if coingecko_api_key else 'Free'} tier")
    print()

    # ========================================================================
    # Register Agent Definitions in Database
    # ========================================================================
    print("[Setup] Registering agent definitions...")

    registry.db.insert_agent({
        'agent_id': 'agent_a_sentiment',
        'agent_name': 'Agent A - Sentiment Analysis',
        'agent_version': '1.0-production',
        'agent_type': 'sentiment',
        'description': 'Analyzes sentiment from news articles and generates sentiment scores'
    })

    registry.db.insert_agent({
        'agent_id': 'agent_b_investment',
        'agent_name': 'Agent B - Investment Prediction',
        'agent_version': '1.0-production',
        'agent_type': 'investment',
        'description': 'Makes investment predictions based on price data and market conditions'
    })

    registry.db.insert_agent({
        'agent_id': 'agent_c_portfolio',
        'agent_name': 'Agent C - Portfolio Management',
        'agent_version': '1.0-production',
        'agent_type': 'portfolio',
        'description': 'Manages portfolio allocation based on price signals and investment predictions'
    })

    print(f"  ✓ Registered 3 agent definitions")
    print()

    # ========================================================================
    # STEP 1: Fetch News Data
    # ========================================================================
    print("=" * 80)
    print("STEP 1: FETCH NEWS DATA")
    print("=" * 80)
    print()

    print("[1.1] Fetching BTC news from CryptoPanic...")
    btc_articles = news_source.fetch_news(currencies=["BTC"], limit=5)
    print(f"  ✓ Fetched {len(btc_articles)} BTC articles")

    all_articles = btc_articles
    print(f"  ✓ Total: {len(all_articles)} articles")
    print()

    # Publish each article as NewsSignal
    news_signals = []
    print("[1.3] Publishing NewsSignals to Walrus...")
    for i, article in enumerate(all_articles, 1):
        article_dict = article.to_dict()
        news_signal = publisher.publish_news_signal(
            news_data=article_dict,
            producer=f"E2E-Pipeline-{timestamp.split('_')[1]}_news_pipeline"
        )

        # Register signal and capture signal_id
        signal_id = registry.register_signal({
            "signal_type": "news",
            "walrus_blob_id": news_signal.walrus_blob_id,
            "data_hash": news_signal.data_hash,
            "size_bytes": news_signal.size_bytes,
            "articles_count": 1,
            "producer": f"E2E-Pipeline-{timestamp.split('_')[1]}_news_pipeline",
            "owner": owner_address,
            "timestamp": datetime.now().isoformat()
        })

        # Set signal_id on NewsSignal object for traceability
        news_signal.signal_id = signal_id

        news_signals.append(news_signal)

        if i % 5 == 0:
            print(f"  ✓ Published {i}/{len(all_articles)} articles...")

    print(f"  ✓ All {len(news_signals)} NewsSignals published and registered")
    print()

    # ========================================================================
    # STEP 2: Run Agent A (Sentiment Analysis)
    # ========================================================================
    print("=" * 80)
    print("STEP 2: RUN AGENT A - SENTIMENT ANALYSIS")
    print("=" * 80)
    print()

    print("[2.1] Initializing Agent A...")
    agent_a = AgentASentiment(
        reasoning_ledger=reasoning_ledger,
        walrus_client=walrus_client,
        agent_version="1.0-production"
    )
    print()

    agent_a_outputs = []
    print("[2.2] Processing articles through Agent A...")
    for i, news_signal in enumerate(news_signals, 1):
        print(f"  Processing article {i}/{len(news_signals)}...")

        agent_a_output = agent_a.run(
            signals=[news_signal],
            store_reasoning=True
        )

        # Register Agent A's output signal
        output_signal_id = registry.register_signal({
            "signal_type": "insight",
            "insight_type": "a",
            "walrus_blob_id": agent_a_output.walrus_blob_id,
            "data_hash": agent_a_output.data_hash,
            "size_bytes": agent_a_output.size_bytes,
            "confidence": agent_a_output.confidence,
            "producer": "agent_a_sentiment",
            "walrus_trace_id": agent_a_output.walrus_trace_id,
            "owner": owner_address,
            "timestamp": datetime.now().isoformat()
        })

        # Set signal_id on InsightSignal for traceability
        agent_a_output.signal_id = output_signal_id

        # Register agent execution with database signal_ids
        registry.register_agent_execution(
            agent_id="agent_a_sentiment",
            agent_version="1.0-production",
            execution_id=agent_a_output.object_id,
            input_signal_ids=[news_signal.signal_id],  # Use database signal_id, not Walrus blob ID
            output_signal_id=output_signal_id,
            confidence=agent_a_output.confidence,
            execution_time_ms=None,
            walrus_trace_id=agent_a_output.walrus_trace_id,
            success=True
        )

        # Register reasoning trace
        trace_data_str = json.dumps({
            "agent_id": "agent_a_sentiment",
            "walrus_blob_id": agent_a_output.walrus_blob_id
        }, sort_keys=True)
        trace_hash = hashlib.sha256(trace_data_str.encode()).hexdigest()

        registry.register_reasoning_trace(
            walrus_trace_id=agent_a_output.walrus_trace_id,
            signal_id=output_signal_id,
            agent_id="agent_a_sentiment",
            agent_version="1.0-production",
            step_count=0,  # Will be populated from Walrus if needed
            data_hash=trace_hash,
            size_bytes=len(trace_data_str.encode()),
            execution_time_ms=None,
            confidence=agent_a_output.confidence,
            llm_provider=None,
            llm_model=None
        )

        agent_a_outputs.append(agent_a_output)

    print(f"  ✓ Agent A processed {len(agent_a_outputs)} articles")
    print()

    # ========================================================================
    # STEP 3: Fetch BTC Price and Run Agent B
    # ========================================================================
    print("=" * 80)
    print("STEP 3: FETCH BTC PRICE & RUN AGENT B")
    print("=" * 80)
    print()

    print("[3.1] Fetching current BTC price from CoinGecko...")
    btc_price_data = price_source.get_price("BTC")
    print(f"  ✓ BTC Price: ${btc_price_data.price_usd:,.2f}")
    print(f"  ✓ 24h Change: {btc_price_data.price_change_24h:+.2f}%")
    print()

    print("[3.2] Publishing PriceSignal...")
    price_dict = btc_price_data.to_dict()
    price_signal = publisher.publish_price_signal(
        price_data=price_dict,
        producer="coingecko_price_pipeline"
    )

    price_signal_id = registry.register_signal({
        "signal_type": "price",
        "walrus_blob_id": price_signal.walrus_blob_id,
        "data_hash": price_signal.data_hash,
        "size_bytes": price_signal.size_bytes,
        "symbol": price_signal.symbol,
        "price_usd": price_signal.price_usd,
        "producer": "coingecko_price_pipeline",
        "owner": owner_address,
        "timestamp": datetime.now().isoformat()
    })

    # Set signal_id on PriceSignal for traceability
    price_signal.signal_id = price_signal_id

    print(f"  ✓ PriceSignal registered: {price_signal.object_id} (DB: {price_signal_id})")
    print()

    print("[3.3] Initializing Agent B...")
    agent_b = AgentBInvestment(
        reasoning_ledger=reasoning_ledger,
        walrus_client=walrus_client,
        agent_version="1.0-production"
    )
    print()

    print("[3.4] Running Agent B with PriceSignal...")
    agent_b_output = agent_b.run(
        signals=[price_signal],
        store_reasoning=True
    )

    print(f"  ✓ Agent B Output:")
    print(f"    Insight Type:     {agent_b_output.insight_type}")
    print(f"    Confidence:       {agent_b_output.confidence:.2f}")
    print(f"    Walrus Blob:      {agent_b_output.walrus_blob_id}")
    print(f"    Reasoning Trace:  {agent_b_output.walrus_trace_id}")
    print()

    print("[3.5] Registering Agent B's InsightSignal...")
    agent_b_signal_id = registry.register_signal({
        "signal_type": "insight",
        "walrus_blob_id": agent_b_output.walrus_blob_id,
        "data_hash": agent_b_output.data_hash,
        "size_bytes": agent_b_output.size_bytes,
        "insight_type": "investment",
        "confidence": agent_b_output.confidence,
        "producer": "agent_b_investment",
        "owner": owner_address,
        "timestamp": datetime.now().isoformat(),
        "walrus_trace_id": agent_b_output.walrus_trace_id
    })

    # Set signal_id on InsightSignal for traceability
    agent_b_output.signal_id = agent_b_signal_id

    # Register Agent B execution with database signal_ids
    registry.register_agent_execution(
        agent_id="agent_b_investment",
        agent_version="1.0-production",
        execution_id=agent_b_output.object_id,
        input_signal_ids=[price_signal.signal_id],  # Use database signal_id
        output_signal_id=agent_b_signal_id,
        confidence=agent_b_output.confidence,
        execution_time_ms=None,
        walrus_trace_id=agent_b_output.walrus_trace_id,
        success=True
    )

    # Register Agent B reasoning trace
    trace_data_str = json.dumps({
        "agent_id": "agent_b_investment",
        "walrus_blob_id": agent_b_output.walrus_blob_id
    }, sort_keys=True)
    trace_hash = hashlib.sha256(trace_data_str.encode()).hexdigest()

    registry.register_reasoning_trace(
        walrus_trace_id=agent_b_output.walrus_trace_id,
        signal_id=agent_b_signal_id,
        agent_id="agent_b_investment",
        agent_version="1.0-production",
        step_count=0,
        data_hash=trace_hash,
        size_bytes=len(trace_data_str.encode()),
        execution_time_ms=None,
        confidence=agent_b_output.confidence,
        llm_provider=None,
        llm_model=None
    )

    print(f"  ✓ Registered signal_{agent_b_output.object_id[-6:]}")
    print()

    # ========================================================================
    # STEP 4: Run Agent C (Portfolio Management)
    # ========================================================================
    print("=" * 80)
    print("STEP 4: RUN AGENT C - PORTFOLIO MANAGEMENT")
    print("=" * 80)
    print()

    print("[4.1] Initializing Agent C...")
    agent_c = AgentCPortfolio(
        reasoning_ledger=reasoning_ledger,
        walrus_client=walrus_client,
        initial_portfolio_value=100000.0,
        agent_version="1.0-production"
    )
    print()

    print("[4.2] Running Agent C with PriceSignal + Agent B prediction...")
    agent_c_output = agent_c.run(
        signals=[price_signal, agent_b_output],
        store_reasoning=True
    )

    print(f"  ✓ Agent C Output:")
    print(f"    Insight Type:     {agent_c_output.insight_type}")
    print(f"    Confidence:       {agent_c_output.confidence:.2f}")
    print(f"    Walrus Blob:      {agent_c_output.walrus_blob_id}")
    print(f"    Reasoning Trace:  {agent_c_output.walrus_trace_id}")
    print()

    print("[4.3] Registering Agent C's InsightSignal...")
    agent_c_signal_id = registry.register_signal({
        "signal_type": "insight",
        "walrus_blob_id": agent_c_output.walrus_blob_id,
        "data_hash": agent_c_output.data_hash,
        "size_bytes": agent_c_output.size_bytes,
        "insight_type": "portfolio",
        "confidence": agent_c_output.confidence,
        "producer": "agent_c_portfolio",
        "owner": owner_address,
        "timestamp": datetime.now().isoformat(),
        "walrus_trace_id": agent_c_output.walrus_trace_id
    })

    # Set signal_id on InsightSignal for traceability
    agent_c_output.signal_id = agent_c_signal_id

    # Register Agent C execution with database signal_ids
    registry.register_agent_execution(
        agent_id="agent_c_portfolio",
        agent_version="1.0-production",
        execution_id=agent_c_output.object_id,
        input_signal_ids=[price_signal.signal_id, agent_b_output.signal_id],  # Use database signal_ids
        output_signal_id=agent_c_signal_id,
        confidence=agent_c_output.confidence,
        execution_time_ms=None,
        walrus_trace_id=agent_c_output.walrus_trace_id,
        success=True
    )

    # Register Agent C reasoning trace
    trace_data_str = json.dumps({
        "agent_id": "agent_c_portfolio",
        "walrus_blob_id": agent_c_output.walrus_blob_id
    }, sort_keys=True)
    trace_hash = hashlib.sha256(trace_data_str.encode()).hexdigest()

    registry.register_reasoning_trace(
        walrus_trace_id=agent_c_output.walrus_trace_id,
        signal_id=agent_c_signal_id,
        agent_id="agent_c_portfolio",
        agent_version="1.0-production",
        step_count=0,
        data_hash=trace_hash,
        size_bytes=len(trace_data_str.encode()),
        execution_time_ms=None,
        confidence=agent_c_output.confidence,
        llm_provider=None,
        llm_model=None
    )

    print(f"  ✓ Registered signal_{agent_c_output.object_id[-6:]}")
    print()

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"✅ Successfully executed complete pipeline with SINGLE owner")
    print()
    print(f"Owner Address: {owner_address}")
    print()
    print("Signals Published:")
    print(f"  • NewsSignals:           {len(news_signals)} (5 BTC articles)")
    print(f"  • Agent A Insights:      {len(agent_a_outputs)} (sentiment analysis)")
    print(f"  • PriceSignal (BTC):     1 (${btc_price_data.price_usd:,.2f})")
    print(f"  • Agent B Insight:       1 (investment prediction)")
    print(f"  • Agent C Insight:       1 (portfolio decision)")
    print(f"  • TOTAL:                 {len(news_signals) + len(agent_a_outputs) + 3}")
    print()
    print("All signals are now visible on the Glass Box Explorer frontend!")
    print(f"Open http://localhost:8080 to view them.")
    print(f"Filter by owner: {owner_address}")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
