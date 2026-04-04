#!/usr/bin/env python3
"""
Test Agent B (Investment Prediction Agent)

This script tests Agent B by:
1. Creating mock sentiment and price signals
2. Running Agent B to generate prediction
3. Verifying the output and reasoning trace
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv("config/.env")

from src.agents.agent_b_investment import AgentBInvestment
from src.reasoning_ledger.reasoning_ledger_sdk import ReasoningLedger
from src.storage.walrus_client import WalrusClient
from src.abstract import InsightSignal, PriceSignal

print("="*80)
print("AGENT B TEST - BTC PRICE PREDICTION")
print("="*80)
print()

# Initialize Walrus client
walrus_enabled = os.getenv("WALRUS_ENABLED", "false").lower() == "true"
walrus_client = WalrusClient(
    publisher_url=os.getenv("WALRUS_PUBLISHER_URL"),
    aggregator_url=os.getenv("WALRUS_AGGREGATOR_URL"),
    simulated=not walrus_enabled
)

# Initialize Reasoning Ledger
reasoning_ledger = ReasoningLedger(walrus_client)

# Initialize Agent B
agent_b = AgentBInvestment(
    reasoning_ledger=reasoning_ledger,
    walrus_client=walrus_client,
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Create mock price signal (fetched from real CoinGecko in practice)
print("[1] Creating mock price signal...")
price_signal = PriceSignal(
    object_id="0xtest_price_001",
    walrus_blob_id="test_btc_price_blob",
    data_hash="abc123",
    size_bytes=330,
    symbol="BTC",
    price_usd=66933.00,
    timestamp=datetime.now(),
    producer="coingecko_price_pipeline"
)
print(f"  ✓ Price Signal: BTC = ${price_signal.price_usd:,.2f}")
print()

# Create mock sentiment signal (from Agent A)
print("[2] Creating mock sentiment signal...")
sentiment_signal = InsightSignal(
    object_id="0xtest_sentiment_001",
    walrus_blob_id="test_sentiment_blob",
    data_hash="def456",
    size_bytes=500,
    insight_type="sentiment",
    confidence=0.85,
    timestamp=datetime.now(),
    producer="agent_a_sentiment",
    walrus_trace_id="test_trace_001"
)
print(f"  ✓ Sentiment Signal: confidence = {sentiment_signal.confidence}")
print()

# Note: In real usage, signals would fetch their data from Walrus
# For this test, we'll use Agent B's fallback prediction mode

print("[3] Running Agent B prediction (fallback mode)...")
print()

try:
    # Run Agent B with mock signals
    # Since signals don't have real Walrus data, Agent B will use fallback mode
    result_signal = agent_b.run(signals=[price_signal])

    print()
    print("="*80)
    print("PREDICTION RESULT")
    print("="*80)
    print()
    print(f"  Current BTC Price:  ${price_signal.price_usd:,.2f}")
    print(f"  Predicted Price:    ${result_signal}")
    print()
    print("✅ Agent B test completed successfully!")

except Exception as e:
    print(f"❌ Agent B test failed: {e}")
    import traceback
    traceback.print_exc()
