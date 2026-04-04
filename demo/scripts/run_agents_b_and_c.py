#!/usr/bin/env python3
"""
Run Agent B and Agent C End-to-End

This script:
1. Fetches a real BTC price from CoinGecko and publishes as PriceSignal
2. Runs Agent B to generate BTC price prediction from PriceSignal
3. Runs Agent C to generate portfolio allocation from Agent B's prediction + PriceSignal

All signals are registered and will be visible on the frontend.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv('config/.env')

import os
from datetime import datetime
from src.data_sources.coingecko_source import CoinGeckoSource
from src.agents.agent_b_investment import AgentBInvestment
from src.agents.agent_c_portfolio import AgentCPortfolio
from src.reasoning_ledger.reasoning_ledger_sdk import ReasoningLedger
from src.storage.walrus_client import WalrusClient
from src.blockchain.sui_publisher import OnChainPublisher
from src.demo.signal_registry import SignalRegistry


def main():
    print("=" * 80)
    print("RUNNING AGENTS B & C END-TO-END")
    print("=" * 80)
    print()

    # Initialize components
    print("[Setup] Initializing components...")

    # Walrus client
    walrus_publisher = os.getenv("WALRUS_PUBLISHER_URL", "https://publisher.walrus-testnet.walrus.space")
    walrus_aggregator = os.getenv("WALRUS_AGGREGATOR_URL", "https://aggregator.walrus-testnet.walrus.space")
    walrus_enabled = os.getenv("WALRUS_ENABLED", "false").lower() == "true"

    walrus_client = WalrusClient(
        publisher_url=walrus_publisher,
        aggregator_url=walrus_aggregator,
        simulated=not walrus_enabled
    )

    # Publisher
    owner_address = f"0xAGENTS_BC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    publisher = OnChainPublisher(
        walrus_client=walrus_client,
        owner_address=owner_address,
        simulated=True
    )

    # Reasoning ledger
    reasoning_ledger = ReasoningLedger(walrus_client=walrus_client)

    # Signal registry
    registry = SignalRegistry(registry_path="data/signal_registry.json")

    # CoinGecko source
    coingecko_api_key = os.getenv("COINGECKO_API_KEY")
    price_source = CoinGeckoSource(api_key=coingecko_api_key)

    print(f"  ✓ Walrus mode: {'Real' if walrus_enabled else 'Simulated'}")
    print(f"  ✓ Owner: {owner_address}")
    print(f"  ✓ CoinGecko: {'Pro' if coingecko_api_key else 'Free'} tier")
    print()

    # ========================================================================
    # STEP 1: Fetch BTC Price and Publish PriceSignal
    # ========================================================================
    print("=" * 80)
    print("STEP 1: FETCH BTC PRICE FROM COINGECKO")
    print("=" * 80)
    print()

    print("[1.1] Fetching current BTC price...")
    btc_price_data = price_source.get_price("BTC")

    print(f"  ✓ Symbol:        {btc_price_data.symbol}")
    print(f"  ✓ Price (USD):   ${btc_price_data.price_usd:,.2f}")
    print(f"  ✓ 24h Change:    {btc_price_data.price_change_24h:+.2f}%")
    print(f"  ✓ 24h Volume:    ${btc_price_data.volume_24h:,.0f}")
    print(f"  ✓ Market Cap:    ${btc_price_data.market_cap:,.0f}")
    print()

    print("[1.2] Publishing PriceSignal to Walrus + SUI...")
    price_dict = btc_price_data.to_dict()
    price_signal = publisher.publish_price_signal(
        price_data=price_dict,
        producer="coingecko_price_pipeline"
    )

    print(f"  ✓ Signal ID:     {price_signal.object_id}")
    print(f"  ✓ Walrus Blob:   {price_signal.walrus_blob_id}")
    print()

    print("[1.3] Registering PriceSignal...")
    registry.register_signal({
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
    print(f"  ✓ Registered signal_{price_signal.object_id[-6:]}")
    print()

    # ========================================================================
    # STEP 2: Run Agent B (Investment Prediction)
    # ========================================================================
    print("=" * 80)
    print("STEP 2: RUN AGENT B - BTC PRICE PREDICTION")
    print("=" * 80)
    print()

    print("[2.1] Initializing Agent B...")
    agent_b = AgentBInvestment(
        reasoning_ledger=reasoning_ledger,
        walrus_client=walrus_client,
        agent_version="1.0-production"
    )
    print()

    print("[2.2] Running Agent B with PriceSignal...")
    agent_b_output = agent_b.run(
        signals=[price_signal],
        store_reasoning=True
    )

    print()
    print("  Agent B Output:")
    print(f"    Insight Type:     {agent_b_output.insight_type}")
    print(f"    Confidence:       {agent_b_output.confidence:.2f}")
    print(f"    Walrus Blob:      {agent_b_output.walrus_blob_id}")
    print(f"    Reasoning Trace:  {agent_b_output.walrus_trace_id}")
    print()

    print("[2.3] Registering Agent B's InsightSignal...")
    registry.register_signal({
        "signal_type": "insight",
        "walrus_blob_id": agent_b_output.walrus_blob_id,
        "data_hash": agent_b_output.data_hash,
        "size_bytes": agent_b_output.size_bytes,
        "insight_type": "investment",
        "confidence": agent_b_output.confidence,
        "producer": "agent_b_investment",
        "owner": owner_address,
        "timestamp": datetime.now().isoformat()
    })
    print(f"  ✓ Registered signal_{agent_b_output.object_id[-6:]}")
    print()

    # ========================================================================
    # STEP 3: Run Agent C (Portfolio Management)
    # ========================================================================
    print("=" * 80)
    print("STEP 3: RUN AGENT C - PORTFOLIO ALLOCATION")
    print("=" * 80)
    print()

    print("[3.1] Initializing Agent C...")
    agent_c = AgentCPortfolio(
        reasoning_ledger=reasoning_ledger,
        walrus_client=walrus_client,
        initial_portfolio_value=100000.0,
        agent_version="1.0-production"
    )
    print()

    print("[3.2] Running Agent C with PriceSignal + Agent B prediction...")
    agent_c_output = agent_c.run(
        signals=[price_signal, agent_b_output],
        store_reasoning=True
    )

    print()
    print("  Agent C Output:")
    print(f"    Insight Type:     {agent_c_output.insight_type}")
    print(f"    Confidence:       {agent_c_output.confidence:.2f}")
    print(f"    Walrus Blob:      {agent_c_output.walrus_blob_id}")
    print(f"    Reasoning Trace:  {agent_c_output.walrus_trace_id}")
    print()

    print("[3.3] Registering Agent C's InsightSignal...")
    registry.register_signal({
        "signal_type": "insight",
        "walrus_blob_id": agent_c_output.walrus_blob_id,
        "data_hash": agent_c_output.data_hash,
        "size_bytes": agent_c_output.size_bytes,
        "insight_type": "portfolio",
        "confidence": agent_c_output.confidence,
        "producer": "agent_c_portfolio",
        "owner": owner_address,
        "timestamp": datetime.now().isoformat()
    })
    print(f"  ✓ Registered signal_{agent_c_output.object_id[-6:]}")
    print()

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"✅ Successfully executed Agent B and Agent C")
    print()
    print("Signals Published:")
    print(f"  1. PriceSignal (BTC)        - ${btc_price_data.price_usd:,.2f}")
    print(f"  2. InsightSignal (Agent B)  - Investment prediction")
    print(f"  3. InsightSignal (Agent C)  - Portfolio allocation")
    print()
    print("All signals are now visible on the Glass Box Explorer frontend!")
    print(f"Open http://localhost:8080 to view them.")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
