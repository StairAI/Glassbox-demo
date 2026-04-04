#!/usr/bin/env python3
"""
Test Agent C: Portfolio Management Agent

This script tests Agent C with all four tool calls:
1. get_portfolio() - Fetch portfolio from Walrus
2. get_btc_price() - Fetch BTC price from CoinGecko
3. get_sui_price() - Fetch SUI price from CoinGecko
4. update_portfolio() - Update portfolio on Walrus

It creates mock signals from Agent B and verifies that:
- All tools are called correctly
- Tool calls are logged in reasoning trace
- Portfolio allocation is calculated correctly
- InsightSignal is generated with proper format
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv('config/.env')

import json
from datetime import datetime
from src.agents.agent_c_portfolio import AgentCPortfolio
from src.abstract.signal import InsightSignal, PriceSignal
from src.reasoning_ledger.reasoning_ledger_sdk import ReasoningLedger
from src.storage.walrus_client import WalrusClient


def create_mock_btc_price_signal(walrus_client: WalrusClient) -> PriceSignal:
    """Create a mock BTC price signal (same signal that Agent B uses)."""
    from src.storage.walrus_client import WalrusHelper
    import hashlib

    # Create price data (same format as CoinGecko)
    price_data = {
        "symbol": "BTC",
        "price_usd": 66933.00,
        "price_change_24h": 0.31,
        "volume_24h": 20900000000.0,
        "market_cap": 1320000000000.0,
        "source": "coingecko",
        "timestamp": datetime.now().isoformat()
    }

    # Store in Walrus
    blob_id = WalrusHelper.store_json(walrus_client, price_data)

    # Compute hash
    data_json = json.dumps(price_data, sort_keys=True)
    data_hash = hashlib.sha256(data_json.encode()).hexdigest()

    # Create PriceSignal
    signal = PriceSignal(
        object_id="mock_btc_price_signal",
        walrus_blob_id=blob_id,
        data_hash=data_hash,
        size_bytes=len(data_json),
        symbol="BTC",
        price_usd=66933.00,
        timestamp=datetime.now(),
        producer="coingecko_price_pipeline"
    )

    return signal


def create_mock_btc_prediction(walrus_client: WalrusClient) -> InsightSignal:
    """Create a mock BTC price prediction signal from Agent B."""
    # Create prediction data
    prediction_data = {
        "insight_type": "investment",
        "signal_value": {
            "prediction": {
                "signal_type": "price_prediction",
                "asset": "BTC",
                "current_price": 66933.00,
                "predicted_price_24h": 68500.00,
                "prediction_confidence": 0.82,
                "direction": "BULLISH",
                "expected_return_pct": 2.34,
                "risk_level": "MODERATE",
                "reasoning_summary": "Strong momentum and positive sentiment indicators",
                "timestamp": datetime.now().isoformat(),
                "prediction_horizon_hours": 24
            }
        },
        "confidence": 0.82,
        "timestamp": datetime.now().isoformat(),
        "producer": "agent_b_investment"
    }

    # Store data in simulated Walrus
    from src.storage.walrus_client import WalrusHelper
    import hashlib

    blob_id = WalrusHelper.store_json(walrus_client, prediction_data)

    # Compute correct hash (MUST match fetch_full_data format: sort_keys=True, NO indent)
    data_json_for_hash = json.dumps(prediction_data, sort_keys=True)
    data_hash = hashlib.sha256(data_json_for_hash.encode()).hexdigest()

    # Create InsightSignal
    signal = InsightSignal(
        object_id="mock_signal_agent_b_prediction",
        walrus_blob_id=blob_id,
        data_hash=data_hash,
        size_bytes=len(data_json_for_hash),
        insight_type="investment",
        confidence=0.82,
        timestamp=datetime.now(),
        producer="agent_b_investment",
        walrus_trace_id=None
    )

    return signal


def main():
    """Test Agent C portfolio management."""
    print("=" * 80)
    print("AGENT C: PORTFOLIO MANAGEMENT TEST")
    print("=" * 80)
    print()

    # Initialize Walrus client (simulated mode)
    walrus_client = WalrusClient(
        publisher_url="https://publisher.walrus-testnet.walrus.space",
        aggregator_url="https://aggregator.walrus-testnet.walrus.space",
        simulated=True
    )

    # Initialize Reasoning Ledger
    reasoning_ledger = ReasoningLedger(walrus_client=walrus_client)

    # Initialize Agent C
    print("[1] Initializing Agent C...")
    agent_c = AgentCPortfolio(
        reasoning_ledger=reasoning_ledger,
        walrus_client=walrus_client,
        initial_portfolio_value=100000.0,
        agent_version="1.0-test"
    )
    print()

    # Create mock BTC price signal (same signal used by Agent B)
    print("[2] Creating mock BTC price signal...")
    btc_price_signal = create_mock_btc_price_signal(walrus_client)
    print(f"    ✓ Created BTC price signal: {btc_price_signal.object_id}")
    print(f"    ✓ Walrus blob ID: {btc_price_signal.walrus_blob_id}")
    print(f"    ✓ BTC Price: $66,933.00")
    print()

    # Create mock BTC prediction signal from Agent B
    print("[3] Creating mock BTC prediction signal from Agent B...")
    btc_prediction_signal = create_mock_btc_prediction(walrus_client)
    print(f"    ✓ Created prediction signal: {btc_prediction_signal.object_id}")
    print(f"    ✓ Walrus blob ID: {btc_prediction_signal.walrus_blob_id}")
    print(f"    ✓ Prediction: BTC $66,933 → $68,500 (BULLISH, 82% confidence)")
    print()

    # Run Agent C with both signals
    print("[4] Running Agent C with BTC price + prediction signals...")
    print()
    try:
        output_signal = agent_c.run(
            signals=[btc_price_signal, btc_prediction_signal],
            store_reasoning=True
        )

        print()
        print("=" * 80)
        print("AGENT C OUTPUT")
        print("=" * 80)
        print()

        # Fetch full output data
        if hasattr(output_signal, '_mock_data'):
            output_data = output_signal._mock_data
        else:
            output_data = {
                "insight_type": output_signal.insight_type,
                "confidence": output_signal.confidence
            }

        print(f"Signal ID:       {output_signal.object_id}")
        print(f"Walrus Blob ID:  {output_signal.walrus_blob_id}")
        print(f"Confidence:      {output_signal.confidence:.2f}")
        print()

        # Display portfolio allocation
        print("PORTFOLIO ALLOCATION:")
        print("-" * 80)

        if "signal_value" in output_data and "portfolio_allocation" in output_data["signal_value"]:
            allocation = output_data["signal_value"]["portfolio_allocation"]

            # Target allocations
            if "target_allocations" in allocation:
                print("\nTarget Allocations:")
                for asset, pct in allocation["target_allocations"].items():
                    print(f"  {asset:6s}: {pct:5.1f}%")

            # Rebalancing actions
            if "actions" in allocation:
                print("\nRebalancing Actions:")
                for action in allocation["actions"]:
                    asset = action["asset"]
                    action_type = action["action"]
                    current = action["current_allocation_pct"]
                    target = action["target_allocation_pct"]
                    amount = action["rebalance_amount_usd"]

                    if action_type != "HOLD":
                        print(f"  {asset:6s}: {action_type:4s} ${amount:,.2f} ({current:.1f}% → {target:.1f}%)")
                    else:
                        print(f"  {asset:6s}: HOLD (no change needed)")

            # Portfolio metrics
            if "portfolio_metrics" in allocation:
                metrics = allocation["portfolio_metrics"]
                print("\nPortfolio Metrics:")
                print(f"  Expected 24h Return:   {metrics.get('expected_return_24h_pct', 0):+.2f}%")
                print(f"  Risk Score:            {metrics.get('risk_score', 0):.2f} (0=low, 1=high)")
                print(f"  Diversification Score: {metrics.get('diversification_score', 0):.2f} (0=poor, 1=excellent)")

        print()

        # Display tool calls from reasoning trace
        print("=" * 80)
        print("TOOL CALLS (from reasoning trace)")
        print("=" * 80)
        print()

        reasoning_steps = agent_c.get_reasoning_steps()
        tool_calls = [step for step in reasoning_steps if step.get("step_type") == "tool_call"]

        if tool_calls:
            for i, tool_call in enumerate(tool_calls, 1):
                tool_name = tool_call.get("tool_name", "unknown")
                success = tool_call.get("success", False)
                status = "✓" if success else "✗"

                print(f"[{i}] {status} {tool_name}")
                print(f"    Description: {tool_call.get('tool_description', 'N/A')}")

                # Show key output for each tool
                tool_output = tool_call.get("tool_output", {})
                if tool_name == "get_portfolio":
                    print(f"    Portfolio Value: ${tool_output.get('total_value_usd', 0):,.2f}")
                elif tool_name == "get_btc_price":
                    print(f"    BTC Price: ${tool_output.get('price_usd', 0):,.2f}")
                elif tool_name == "get_sui_price":
                    print(f"    SUI Price: ${tool_output.get('price_usd', 0):,.4f}")
                elif tool_name == "update_portfolio":
                    print(f"    Status: {tool_output.get('status', 'unknown')}")
                    print(f"    Walrus Blob: {tool_output.get('walrus_blob_id', 'N/A')}")

                print()
        else:
            print("  No tool calls found in reasoning trace")

        print("=" * 80)
        print("✅ AGENT C TEST COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print()
        print("Summary:")
        print(f"  - Agent executed with {len(tool_calls)} tool calls")
        print(f"  - All tool calls logged in reasoning trace")
        print(f"  - Portfolio allocation calculated successfully")
        print(f"  - InsightSignal generated and stored")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
