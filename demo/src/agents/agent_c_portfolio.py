#!/usr/bin/env python3
"""
Agent C: Portfolio Management Agent

This agent demonstrates the complete Glass Box Protocol tool architecture:

**Input:**
- Signals from Agent B (BTC price predictions)
- PriceSignal for BTC (same signal used by Agent B - REUSED from Walrus)

**Tools (all explicitly logged in reasoning trace):**
1. get_portfolio() - Fetch current portfolio state from Walrus storage
2. get_sui_price() - Fetch real-time SUI price from CoinGecko

**Note:** BTC price is consumed from PriceSignal (same signal used by Agent B), not via tool call.

**Processing:**
1. Fetches current portfolio holdings from Walrus
2. Analyzes Agent B's BTC price predictions
3. Fetches BTC price from PriceSignal (reused from Agent B)
4. Fetches current SUI price from CoinGecko
5. Calculates optimal portfolio allocation (BTC, SUI, USDC)
6. Generates rebalancing recommendations

**Output:**
- InsightSignal with portfolio allocation recommendations
- All tool calls recorded in reasoning trace for transparency

This agent extends the abstract Agent base class and demonstrates
the Glass Box Protocol's signal reuse pattern.
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from src.abstract import Agent, Signal, InsightSignal
from src.reasoning_ledger.reasoning_ledger_sdk import ReasoningLedger
from src.storage.walrus_client import WalrusClient
from src.data_sources.coingecko_source import CoinGeckoSource


class AgentCPortfolio(Agent):
    """
    Agent C: Portfolio Management Agent

    Extends the abstract Agent base class to provide:
    - Standardized signal input/output
    - Automatic reasoning trace recording
    - Tool-based SUI price fetching with explicit logging
    - Portfolio allocation and rebalancing logic
    """

    def __init__(
        self,
        reasoning_ledger: Optional[ReasoningLedger] = None,
        walrus_client: Optional[WalrusClient] = None,
        initial_portfolio_value: float = 100000.0,
        agent_version: str = "1.0"
    ):
        """
        Initialize Agent C.

        Args:
            reasoning_ledger: ReasoningLedger for storing reasoning traces
            walrus_client: WalrusClient for fetching signal data
            initial_portfolio_value: Starting portfolio value in USD
            agent_version: Agent version for traceability
        """
        # Initialize parent Agent class
        super().__init__(
            agent_id="agent_c_portfolio",
            agent_version=agent_version,
            reasoning_ledger=reasoning_ledger
        )

        # Agent-specific configuration
        self.walrus_client = walrus_client
        self.initial_portfolio_value = initial_portfolio_value

        # Initialize CoinGecko price source (tool for fetching SUI price)
        coingecko_api_key = os.getenv("COINGECKO_API_KEY")
        self.price_source = CoinGeckoSource(api_key=coingecko_api_key)

        # Initialize portfolio state (simplified - in production would use SQLite)
        self.portfolio_state = {
            "total_value_usd": initial_portfolio_value,
            "allocations": {
                "BTC": 0.50,  # 50% BTC
                "SUI": 0.30,  # 30% SUI
                "USDC": 0.20  # 20% USDC (stable)
            },
            "holdings": {
                "BTC": 0.0,
                "SUI": 0.0,
                "USDC": initial_portfolio_value * 0.20
            }
        }

        print(f"  ✓ Portfolio initialized: ${initial_portfolio_value:,.2f}")
        print(f"  ✓ Initial allocations: BTC={self.portfolio_state['allocations']['BTC']:.0%}, "
              f"SUI={self.portfolio_state['allocations']['SUI']:.0%}, "
              f"USDC={self.portfolio_state['allocations']['USDC']:.0%}")

    # ==================================================================================
    # TOOLS: External API and Storage Operations
    # ==================================================================================

    def get_sui_price(self) -> Dict[str, Any]:
        """
        Tool: Fetch real-time SUI price from CoinGecko.

        This is an explicit tool that will be logged in the reasoning trace.

        Returns:
            Dict with SUI price data
        """
        try:
            price_data = self.price_source.get_price("SUI")

            result = {
                "symbol": "SUI",
                "price_usd": float(price_data.price_usd),
                "price_change_24h": float(price_data.price_change_24h) if price_data.price_change_24h else None,
                "volume_24h": float(price_data.volume_24h) if price_data.volume_24h else None,
                "market_cap": float(price_data.market_cap) if price_data.market_cap else None,
                "source": "coingecko",
                "timestamp": price_data.timestamp.isoformat()
            }

            # Record this tool call in reasoning trace
            self.record_tool_call(
                tool_name="get_sui_price",
                tool_input={"symbol": "SUI", "source": "coingecko"},
                tool_output=result,
                tool_description="Fetch real-time SUI price from CoinGecko API",
                success=True
            )

            return result

        except Exception as e:
            # Record failed tool call
            self.record_tool_call(
                tool_name="get_sui_price",
                tool_input={"symbol": "SUI", "source": "coingecko"},
                tool_output={"error": str(e)},
                tool_description="Fetch real-time SUI price from CoinGecko API",
                success=False
            )
            raise

    def get_portfolio(self) -> Dict[str, Any]:
        """
        Tool: Fetch current portfolio state from Walrus.

        This retrieves the portfolio JSON blob from Walrus storage.
        In production, this would fetch from the latest Walrus blob ID.
        For now, we use the in-memory portfolio state but simulate Walrus fetch.

        Returns:
            Dict with portfolio holdings and allocations
        """
        try:
            # In production: fetch from Walrus using blob_id
            # portfolio_json = self.walrus_client.get_blob(self.portfolio_blob_id)
            # portfolio_data = json.loads(portfolio_json)

            # For now: use in-memory state (simulating Walrus fetch)
            portfolio_data = self.portfolio_state.copy()

            result = {
                "total_value_usd": portfolio_data["total_value_usd"],
                "allocations": portfolio_data["allocations"],
                "holdings": portfolio_data["holdings"],
                "last_updated": datetime.now().isoformat()
            }

            # Record this tool call in reasoning trace
            self.record_tool_call(
                tool_name="get_portfolio",
                tool_input={"source": "walrus_storage"},
                tool_output=result,
                tool_description="Fetch current portfolio state from Walrus storage",
                success=True
            )

            return result

        except Exception as e:
            # Record failed tool call
            self.record_tool_call(
                tool_name="get_portfolio",
                tool_input={"source": "walrus_storage"},
                tool_output={"error": str(e)},
                tool_description="Fetch current portfolio state from Walrus storage",
                success=False
            )
            raise

    # ==================================================================================
    # CORE INTERFACE - Required by abstract Agent
    # ==================================================================================

    def process_signals(self, signals: List[Signal]) -> Dict[str, Any]:
        """
        Process price prediction signals and generate portfolio allocation.

        This is the core reasoning logic called by Agent.run().

        Uses multiple tools:
        1. get_portfolio() - Fetch current portfolio state from Walrus
        2. get_sui_price() - Fetch current SUI price from CoinGecko

        Args:
            signals: List of input signals (InsightSignals with BTC predictions + PriceSignal for BTC)

        Returns:
            Dict with portfolio allocation recommendations
        """
        # Step 1: Fetch current portfolio state from Walrus (TOOL CALL)
        print("  Fetching current portfolio state (tool call)...")
        portfolio = self.get_portfolio()
        print(f"    ✓ Portfolio value: ${portfolio['total_value_usd']:,.2f}")

        # Step 2: Fetch BTC prediction from Agent B and BTC price from signals
        btc_prediction = None
        btc_price_data = None

        from src.abstract import PriceSignal

        for signal in signals:
            if isinstance(signal, InsightSignal):
                # Fetch prediction data from Walrus
                insight_data = signal.fetch_full_data(walrus_client=self.walrus_client)
                if insight_data.get("insight_type") == "price_prediction" or \
                   insight_data.get("insight_type") == "investment":
                    btc_prediction = insight_data.get("signal_value", {}).get("prediction", insight_data.get("signal_value"))

            elif isinstance(signal, PriceSignal):
                # Fetch BTC price data from Walrus (same signal consumed by Agent B)
                price_signal_data = signal.fetch_full_data(walrus_client=self.walrus_client)
                if price_signal_data.get("symbol") == "BTC":
                    btc_price_data = price_signal_data
                    print(f"  ✓ BTC price from signal: ${btc_price_data['price_usd']:,.2f}")

        self.record_step(
            step_name="fetch_signals",
            description="Fetched BTC price prediction from Agent B and BTC price from PriceSignal",
            input_data={"signal_count": len(signals)},
            output_data={
                "has_btc_prediction": btc_prediction is not None,
                "has_btc_price": btc_price_data is not None
            }
        )

        # Validate we have BTC price
        if not btc_price_data:
            raise ValueError("Missing BTC PriceSignal - cannot calculate portfolio allocation without current BTC price")

        # Step 3: Fetch real-time SUI price using tool (TOOL CALL)
        print("  Fetching real-time SUI price (tool call)...")
        sui_price_data = self.get_sui_price()
        print(f"    ✓ SUI price: ${sui_price_data['price_usd']:,.4f}")

        # Step 4: Calculate optimal portfolio allocation
        allocation = self._calculate_allocation(
            btc_prediction=btc_prediction,
            btc_price_data=btc_price_data,
            sui_price_data=sui_price_data,
            current_portfolio=portfolio
        )

        self.record_step(
            step_name="calculate_allocation",
            description="Calculated optimal portfolio allocation",
            input_data={
                "btc_prediction": btc_prediction,
                "btc_price": btc_price_data['price_usd'],
                "sui_price": sui_price_data['price_usd'],
                "portfolio_value": portfolio['total_value_usd']
            },
            output_data=allocation,
            confidence=allocation.get("confidence", 0.75)
        )

        # Return output in format expected by Agent base class
        return {
            "portfolio_allocation": allocation,
            "confidence": allocation.get("confidence", 0.75),
            "btc_price": btc_price_data['price_usd'],
            "sui_price": sui_price_data['price_usd'],
            "portfolio_value": portfolio['total_value_usd'],
            "rebalancing_needed": allocation.get("rebalancing_needed", True)
        }

    # ==================================================================================
    # OPTIONAL HOOKS - Override for custom behavior
    # ==================================================================================

    def validate_input(self, signals: List[Signal]) -> bool:
        """
        Validate that we have at least one signal.

        Args:
            signals: Input signals

        Returns:
            True if valid, False otherwise
        """
        if not signals:
            print("  WARNING: No input signals provided")
            return False

        return True

    def before_process(self, signals: List[Signal]) -> None:
        """
        Hook called before processing.

        Use this for initialization, logging, etc.
        """
        print(f"  Current portfolio value: ${self.portfolio_state['total_value_usd']:,.2f}")
        print(f"  Current allocations: "
              f"BTC={self.portfolio_state['allocations']['BTC']:.0%}, "
              f"SUI={self.portfolio_state['allocations']['SUI']:.0%}, "
              f"USDC={self.portfolio_state['allocations']['USDC']:.0%}")

    # ==================================================================================
    # PORTFOLIO ALLOCATION LOGIC
    # ==================================================================================

    def _calculate_allocation(
        self,
        btc_prediction: Optional[Dict],
        btc_price_data: Dict,
        sui_price_data: Dict,
        current_portfolio: Dict
    ) -> Dict[str, Any]:
        """
        Calculate optimal portfolio allocation based on predictions and risk parameters.

        Args:
            btc_prediction: BTC price prediction from Agent B
            btc_price_data: Current BTC price data from CoinGecko
            sui_price_data: Current SUI price data from CoinGecko
            current_portfolio: Current portfolio state from Walrus

        Returns:
            Dict with portfolio allocation and rebalancing actions
        """
        # Get current allocations from portfolio
        current_alloc = current_portfolio['allocations'].copy()

        # Default target allocations (conservative)
        target_alloc = {
            "BTC": 0.50,
            "SUI": 0.30,
            "USDC": 0.20
        }

        # Adjust based on BTC prediction if available
        if btc_prediction:
            direction = btc_prediction.get("direction", "NEUTRAL")
            confidence = btc_prediction.get("prediction_confidence", 0.5)
            expected_return = btc_prediction.get("expected_return_pct", 0.0)

            # Increase BTC allocation if bullish and high confidence
            if direction == "BULLISH" and confidence > 0.7:
                target_alloc["BTC"] = min(0.70, 0.50 + (confidence - 0.7) * 0.5)  # Up to 70%
                target_alloc["SUI"] = 0.20
                target_alloc["USDC"] = 1.0 - target_alloc["BTC"] - target_alloc["SUI"]

            # Decrease BTC allocation if bearish and high confidence
            elif direction == "BEARISH" and confidence > 0.7:
                target_alloc["BTC"] = max(0.30, 0.50 - (confidence - 0.7) * 0.4)  # Down to 30%
                target_alloc["USDC"] = 0.40  # More stable assets
                target_alloc["SUI"] = 1.0 - target_alloc["BTC"] - target_alloc["USDC"]

        # Check SUI momentum and adjust
        sui_change_24h = sui_price_data.get("price_change_24h", 0)
        if sui_change_24h and sui_change_24h > 5:  # Strong positive momentum
            # Slightly increase SUI allocation
            target_alloc["SUI"] = min(0.40, target_alloc["SUI"] + 0.05)
            target_alloc["BTC"] = target_alloc["BTC"] - 0.05
        elif sui_change_24h and sui_change_24h < -5:  # Strong negative momentum
            # Slightly decrease SUI allocation
            target_alloc["SUI"] = max(0.20, target_alloc["SUI"] - 0.05)
            target_alloc["USDC"] = target_alloc["USDC"] + 0.05

        # Normalize to ensure sum = 1.0
        total = sum(target_alloc.values())
        target_alloc = {k: v/total for k, v in target_alloc.items()}

        # Calculate rebalancing actions
        portfolio_value = current_portfolio['total_value_usd']
        actions = []

        for asset in ["BTC", "SUI", "USDC"]:
            current_pct = current_alloc[asset]
            target_pct = target_alloc[asset]
            diff_pct = target_pct - current_pct

            # Only rebalance if difference > 2%
            if abs(diff_pct) > 0.02:
                rebalance_amount = portfolio_value * diff_pct

                action = "BUY" if diff_pct > 0 else "SELL"
                if abs(diff_pct) < 0.02:
                    action = "HOLD"

                actions.append({
                    "asset": asset,
                    "action": action,
                    "current_allocation_pct": round(current_pct * 100, 2),
                    "target_allocation_pct": round(target_pct * 100, 2),
                    "rebalance_amount_usd": round(rebalance_amount, 2)
                })
            else:
                actions.append({
                    "asset": asset,
                    "action": "HOLD",
                    "current_allocation_pct": round(current_pct * 100, 2),
                    "target_allocation_pct": round(target_pct * 100, 2),
                    "rebalance_amount_usd": 0.0
                })

        # Calculate portfolio metrics
        expected_return_24h = 0.0
        if btc_prediction:
            expected_return_24h = btc_prediction.get("expected_return_pct", 0) * target_alloc["BTC"]

        # Add SUI expected return (simple momentum)
        if sui_change_24h:
            expected_return_24h += (sui_change_24h * 0.5) * target_alloc["SUI"]  # 50% momentum continuation

        portfolio_metrics = {
            "expected_return_24h_pct": round(expected_return_24h, 2),
            "risk_score": self._calculate_risk_score(target_alloc),
            "diversification_score": self._calculate_diversification(target_alloc)
        }

        return {
            "signal_type": "portfolio_allocation",
            "actions": actions,
            "target_allocations": {k: round(v * 100, 2) for k, v in target_alloc.items()},
            "portfolio_metrics": portfolio_metrics,
            "total_value_usd": portfolio_value,
            "rebalancing_needed": any(a["action"] != "HOLD" for a in actions),
            "confidence": 0.75,  # Portfolio management confidence
            "timestamp": datetime.now().isoformat()
        }

    def _calculate_risk_score(self, allocations: Dict[str, float]) -> float:
        """
        Calculate portfolio risk score (0.0 = low risk, 1.0 = high risk).

        Higher crypto allocation = higher risk
        """
        crypto_allocation = allocations.get("BTC", 0) + allocations.get("SUI", 0)
        return round(crypto_allocation * 0.8, 2)  # Scale to 0-0.8 range

    def _calculate_diversification(self, allocations: Dict[str, float]) -> float:
        """
        Calculate diversification score (0.0 = not diversified, 1.0 = well diversified).

        Using Herfindahl–Hirschman Index (HHI) inverted.
        """
        hhi = sum(allocation ** 2 for allocation in allocations.values())
        diversification = 1.0 - (hhi - 1/len(allocations)) / (1 - 1/len(allocations))
        return round(diversification, 2)
