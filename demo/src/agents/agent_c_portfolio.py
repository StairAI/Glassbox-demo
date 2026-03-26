"""
Agent C: Portfolio Management Agent

Consumes BTC and SUI price predictions from Agent B and SUI predictor.
Determines optimal portfolio allocation across BTC/SUI/USDC.
Executes rebalancing transactions on SUI blockchain (mock).
RAID scoring based on portfolio performance (Sharpe ratio, returns, drawdown).

Signal Output Format:
{
    "agent_id": "agent_c",
    "timestamp": "2024-...",
    "portfolio_value": float,
    "btc_allocation_pct": float,
    "sui_allocation_pct": float,
    "usdc_allocation_pct": float,
    "rebalance_actions": [{"asset": "BTC", "action": "BUY", "amount_usd": float}, ...],
    "transaction_hash": str,        # SUI blockchain transaction
    "raid_score": 0.0 to 1.0,       # Current RAID score
    "sharpe_ratio": float
}
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import json

# Handle imports for both standalone and package usage
try:
    from ..state.state_machine import create_agent_c_state_machine
    from ..scoring.portfolio_tracker import PortfolioTracker
    from ..data_sources.price_fetcher import PriceFetcher
    from ..data_sources.sui_predictor_mock import SUIPredictorMock
    from ..data_sources.sui_integration import MockSUIBlockchain
except (ImportError, ValueError):
    # Standalone execution or being imported from runner
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from state.state_machine import create_agent_c_state_machine
    from scoring.portfolio_tracker import PortfolioTracker
    from data_sources.price_fetcher import PriceFetcher
    from data_sources.sui_predictor_mock import SUIPredictorMock
    from data_sources.sui_integration import MockSUIBlockchain


class AgentC:
    """
    Portfolio Management Agent

    Manages BTC/SUI/USDC portfolio allocation based on price predictions.
    Submits rebalancing transactions to SUI blockchain.
    Tracks portfolio performance via RAID scoring.
    """

    def __init__(
        self,
        agent_id: str = "agent_c",
        initial_portfolio_value: float = 100000,
        price_fetcher: Optional[PriceFetcher] = None,
        sui_blockchain: Optional[MockSUIBlockchain] = None,
        output_dir: Optional[Path] = None
    ):
        """
        Initialize Agent C

        Args:
            agent_id: Agent identifier
            initial_portfolio_value: Starting portfolio value in USD
            price_fetcher: Price data source (shared across agents)
            sui_blockchain: SUI blockchain instance (shared)
            output_dir: Directory to store signals
        """
        self.agent_id = agent_id

        if output_dir is None:
            output_dir = Path(__file__).parent.parent.parent / "output" / "signals"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # State machine
        self.state = create_agent_c_state_machine(agent_id)

        # Price fetcher (shared resource)
        self.price_fetcher = price_fetcher if price_fetcher else PriceFetcher()

        # SUI predictor (mock)
        self.sui_predictor = SUIPredictorMock(accuracy_bias=0.7)

        # SUI blockchain
        self.sui_blockchain = sui_blockchain if sui_blockchain else MockSUIBlockchain()

        # Register agent on blockchain
        self.sui_address = self.sui_blockchain.register_agent(agent_id)

        # Portfolio tracker (RAID scoring)
        self.tracker = PortfolioTracker(agent_id, initial_portfolio_value)

        # Current portfolio allocation
        self.portfolio = {
            "btc_allocation_pct": 40.0,  # Start with 40% BTC
            "sui_allocation_pct": 30.0,  # 30% SUI
            "usdc_allocation_pct": 30.0,  # 30% USDC (stablecoin)
            "total_value_usd": initial_portfolio_value
        }

        # Signal history
        self.signal_history = []

        # Record initial snapshot
        self.tracker.record_snapshot(
            portfolio_value=initial_portfolio_value,
            btc_allocation_pct=40.0,
            sui_allocation_pct=30.0,
            usdc_allocation_pct=30.0
        )

        print(f"[{self.agent_id}] Agent C initialized")
        print(f"[{self.agent_id}] SUI address: {self.sui_address[:16]}...")
        print(f"[{self.agent_id}] Initial portfolio: ${initial_portfolio_value:,.0f} "
              f"(BTC: 40%, SUI: 30%, USDC: 30%)")

    def consume_prediction_signals(self, btc_prediction: Dict, sentiment_signal: Dict):
        """
        Consume BTC prediction from Agent B and sentiment from Agent A

        Args:
            btc_prediction: BTC prediction signal from Agent B
            sentiment_signal: Sentiment signal (for SUI prediction)
        """
        self.state.transition("ANALYZING", "Processing BTC and SUI predictions")

        # Store predictions in state metadata
        self.state.update_metadata("btc_predicted_change", btc_prediction["predicted_change_pct"])
        self.state.update_metadata("btc_confidence", btc_prediction["confidence"])

        # Get SUI prediction
        current_prices = self.price_fetcher.fetch_prices()
        sui_prediction = self.sui_predictor.predict_sui_price(
            current_price=current_prices["sui"]["price"],
            sentiment=sentiment_signal["overall_sentiment"]
        )

        self.state.update_metadata("sui_predicted_change", sui_prediction["expected_change_pct"])
        self.state.update_metadata("sui_confidence", sui_prediction["confidence"])

    def calculate_optimal_allocation(
        self,
        btc_prediction: Dict,
        sui_prediction: Dict,
        sentiment_signal: Dict
    ) -> Dict:
        """
        Determine optimal portfolio allocation based on predictions

        Args:
            btc_prediction: BTC prediction from Agent B
            sui_prediction: SUI prediction from mock predictor
            sentiment_signal: Sentiment signal

        Returns:
            dict: New allocation percentages
        """
        self.state.transition("ALLOCATING", "Calculating optimal portfolio allocation")

        # Simple allocation strategy based on predicted returns and confidence
        # In production, this would use modern portfolio theory (MPT), Black-Litterman, etc.

        btc_expected_return = btc_prediction["predicted_change_pct"] * btc_prediction["confidence"]
        sui_expected_return = sui_prediction["expected_change_pct"] * sui_prediction["confidence"]

        # Risk adjustment (higher volatility = lower allocation)
        current_prices = self.price_fetcher.fetch_prices()
        btc_volatility = current_prices["btc"]["volatility"]
        sui_volatility = current_prices["sui"]["volatility"]

        # Risk-adjusted expected returns
        btc_score = btc_expected_return / (1 + btc_volatility)
        sui_score = sui_expected_return / (1 + sui_volatility)

        # Normalize scores to [0, 1] range (assuming max score ~10)
        btc_score = max(0, min(10, btc_score + 5)) / 10
        sui_score = max(0, min(10, sui_score + 5)) / 10

        # Total risk assets allocation (leave minimum 15% in USDC for stability)
        min_usdc_pct = 15.0
        max_risk_pct = 100.0 - min_usdc_pct

        # Allocate risk budget between BTC and SUI
        total_score = btc_score + sui_score
        if total_score > 0:
            btc_allocation_pct = (btc_score / total_score) * max_risk_pct
            sui_allocation_pct = (sui_score / total_score) * max_risk_pct
        else:
            # No conviction, equal weight
            btc_allocation_pct = max_risk_pct / 2
            sui_allocation_pct = max_risk_pct / 2

        usdc_allocation_pct = 100.0 - btc_allocation_pct - sui_allocation_pct

        # Apply allocation bounds (min 10%, max 60% per asset for diversification)
        btc_allocation_pct = max(10.0, min(60.0, btc_allocation_pct))
        sui_allocation_pct = max(10.0, min(60.0, sui_allocation_pct))
        usdc_allocation_pct = 100.0 - btc_allocation_pct - sui_allocation_pct

        allocation = {
            "btc_allocation_pct": round(btc_allocation_pct, 1),
            "sui_allocation_pct": round(sui_allocation_pct, 1),
            "usdc_allocation_pct": round(usdc_allocation_pct, 1),
            "btc_score": btc_score,
            "sui_score": sui_score
        }

        self.state.update_metadata("btc_allocation_pct", allocation["btc_allocation_pct"])
        self.state.update_metadata("sui_allocation_pct", allocation["sui_allocation_pct"])

        return allocation

    def execute_rebalancing(self, new_allocation: Dict) -> Dict:
        """
        Execute portfolio rebalancing to reach target allocation

        Args:
            new_allocation: Target allocation percentages

        Returns:
            dict: Rebalancing actions and transaction info
        """
        self.state.transition("REBALANCING", "Executing portfolio rebalancing on SUI chain")

        current_value = self.portfolio["total_value_usd"]

        # Calculate rebalancing actions
        actions = []

        for asset in ["btc", "sui", "usdc"]:
            current_pct = self.portfolio[f"{asset}_allocation_pct"]
            target_pct = new_allocation[f"{asset}_allocation_pct"]
            diff_pct = target_pct - current_pct

            if abs(diff_pct) > 1.0:  # Only rebalance if difference > 1%
                amount_usd = (diff_pct / 100) * current_value
                action = "BUY" if amount_usd > 0 else "SELL"

                actions.append({
                    "asset": asset.upper(),
                    "action": action,
                    "amount_usd": round(abs(amount_usd), 2),
                    "from_pct": round(current_pct, 1),
                    "to_pct": round(target_pct, 1)
                })

        # Submit rebalancing transaction to SUI blockchain
        if actions:
            # Simulate gas cost (mock blockchain charges small fee)
            gas_cost_usd = 0.1 * len(actions)  # $0.10 per action

            tx_hash = self.sui_blockchain.submit_portfolio_rebalance(
                agent_name=self.agent_id,
                actions=actions,
                portfolio_value=current_value - gas_cost_usd
            )

            # Update portfolio
            self.portfolio.update(new_allocation)
            self.portfolio["total_value_usd"] = current_value - gas_cost_usd

            # Record rebalance in tracker
            self.tracker.record_rebalance(
                actions=actions,
                portfolio_value_before=current_value,
                portfolio_value_after=current_value - gas_cost_usd,
                transaction_hash=tx_hash
            )

            print(f"[{self.agent_id}] Rebalanced portfolio: {len(actions)} actions, "
                  f"gas: ${gas_cost_usd:.2f}, tx: {tx_hash[:16]}...")

        else:
            tx_hash = None
            print(f"[{self.agent_id}] No rebalancing needed (allocations within 1% tolerance)")

        return {
            "actions": actions,
            "transaction_hash": tx_hash,
            "gas_cost_usd": gas_cost_usd if actions else 0.0
        }

    def update_portfolio_performance(self):
        """
        Update portfolio value based on current prices

        In production, this tracks actual on-chain portfolio positions.
        For demo, we simulate based on price movements.
        """
        self.state.transition("TRACKING", "Updating portfolio performance")

        # Get current prices
        current_prices = self.price_fetcher.fetch_prices()
        btc_change = current_prices["btc"]["change_24h_pct"]
        sui_change = current_prices["sui"]["change_24h_pct"]

        # Calculate portfolio value change (simplified)
        btc_contribution = (self.portfolio["btc_allocation_pct"] / 100) * btc_change
        sui_contribution = (self.portfolio["sui_allocation_pct"] / 100) * sui_change
        usdc_contribution = 0.0  # Stablecoin doesn't change

        total_change_pct = btc_contribution + sui_contribution + usdc_contribution

        # Update portfolio value
        old_value = self.portfolio["total_value_usd"]
        new_value = old_value * (1 + total_change_pct / 100)
        self.portfolio["total_value_usd"] = new_value

        # Record snapshot
        self.tracker.record_snapshot(
            portfolio_value=new_value,
            btc_allocation_pct=self.portfolio["btc_allocation_pct"],
            sui_allocation_pct=self.portfolio["sui_allocation_pct"],
            usdc_allocation_pct=self.portfolio["usdc_allocation_pct"]
        )

        return {
            "old_value": old_value,
            "new_value": new_value,
            "change_pct": total_change_pct
        }

    def calculate_raid_score(self) -> Dict:
        """
        Calculate current RAID score based on portfolio performance

        Returns:
            dict: RAID score breakdown
        """
        raid_score = self.tracker.calculate_raid_score(lookback_hours=168)  # 7 days

        # Submit RAID score to SUI blockchain
        if raid_score["raid_score"] > 0:
            tx_hash = self.sui_blockchain.submit_raid_score(
                agent_name=self.agent_id,
                raid_score=raid_score["raid_score"],
                metrics={
                    "sharpe_ratio": raid_score["sharpe_ratio"],
                    "total_return_pct": raid_score["total_return_pct"],
                    "max_drawdown_pct": raid_score["max_drawdown_pct"],
                    "win_rate": raid_score["win_rate"]
                }
            )

            print(f"[{self.agent_id}] RAID score {raid_score['raid_score']:.3f} stored on-chain: {tx_hash[:16]}...")

        self.state.update_metadata("raid_score", raid_score["raid_score"])
        self.state.update_metadata("sharpe_ratio", raid_score["sharpe_ratio"])

        return raid_score

    def publish_signal(self, allocation: Dict, rebalance_info: Dict, raid_score: Dict):
        """
        Publish portfolio management signal

        Args:
            allocation: Portfolio allocation
            rebalance_info: Rebalancing actions and transaction
            raid_score: RAID score breakdown
        """
        self.state.transition("PUBLISHING", "Publishing portfolio management signal")

        signal = {
            "agent_id": self.agent_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "portfolio_value": round(self.portfolio["total_value_usd"], 2),
            "btc_allocation_pct": allocation["btc_allocation_pct"],
            "sui_allocation_pct": allocation["sui_allocation_pct"],
            "usdc_allocation_pct": allocation["usdc_allocation_pct"],
            "rebalance_actions": rebalance_info["actions"],
            "transaction_hash": rebalance_info["transaction_hash"],
            "sui_address": self.sui_address[:16] + "...",
            "raid_score": raid_score["raid_score"],
            "raid_metrics": {
                "sharpe_ratio": raid_score["sharpe_ratio"],
                "total_return_pct": raid_score["total_return_pct"],
                "max_drawdown_pct": raid_score["max_drawdown_pct"],
                "win_rate": raid_score["win_rate"]
            }
        }

        # Write to JSONL file
        signal_file = self.output_dir / f"{self.agent_id}_signals.jsonl"

        with open(signal_file, 'a') as f:
            f.write(json.dumps(signal) + "\n")

        print(f"[{self.agent_id}] Published signal: Portfolio ${signal['portfolio_value']:,.0f} | "
              f"BTC: {signal['btc_allocation_pct']}% | SUI: {signal['sui_allocation_pct']}% | "
              f"USDC: {signal['usdc_allocation_pct']}% | RAID: {signal['raid_score']:.3f}")

        # Store in history
        self.signal_history.append(signal)
        if len(self.signal_history) > 50:
            self.signal_history = self.signal_history[-50:]

        # Return to MONITORING state
        self.state.transition("MONITORING", "Signal published, monitoring for next cycle")

    def run_cycle(self, btc_prediction: Dict, sentiment_signal: Dict) -> Dict:
        """
        Execute one full portfolio management cycle

        Args:
            btc_prediction: BTC prediction from Agent B
            sentiment_signal: Sentiment signal from Agent A (for SUI prediction)

        Returns:
            dict: Published portfolio signal
        """
        # MONITORING → ANALYZING
        self.consume_prediction_signals(btc_prediction, sentiment_signal)

        # Get SUI prediction
        current_prices = self.price_fetcher.fetch_prices()
        sui_prediction = self.sui_predictor.predict_sui_price(
            current_price=current_prices["sui"]["price"],
            sentiment=sentiment_signal["overall_sentiment"]
        )

        # ANALYZING → ALLOCATING
        new_allocation = self.calculate_optimal_allocation(
            btc_prediction, sui_prediction, sentiment_signal
        )

        # ALLOCATING → REBALANCING
        rebalance_info = self.execute_rebalancing(new_allocation)

        # REBALANCING → TRACKING
        performance = self.update_portfolio_performance()

        # TRACKING → PUBLISHING
        raid_score = self.calculate_raid_score()

        # PUBLISHING → MONITORING
        self.publish_signal(new_allocation, rebalance_info, raid_score)

        # Force blockchain block creation
        self.sui_blockchain.force_create_block()

        return self.signal_history[-1]

    def get_latest_signal(self) -> Optional[Dict]:
        """Get most recent portfolio signal"""
        return self.signal_history[-1] if self.signal_history else None

    def get_signal_history(self, limit: int = 10) -> List[Dict]:
        """Get recent portfolio signals"""
        return self.signal_history[-limit:]


if __name__ == "__main__":
    # Test Agent C
    print("\nAgent C: Portfolio Management Agent - Test Output\n")
    print("=" * 80)

    # Initialize with shared resources
    price_fetcher = PriceFetcher(initial_btc_price=70000, initial_sui_price=2.5)
    sui_blockchain = MockSUIBlockchain()
    agent_c = AgentC(
        initial_portfolio_value=100000,
        price_fetcher=price_fetcher,
        sui_blockchain=sui_blockchain
    )

    # Simulate signals from Agent A and Agent B
    test_scenarios = [
        {
            "sentiment": {
                "agent_id": "agent_a",
                "overall_sentiment": 0.5,
                "sentiment_volatility": 0.2,
                "sentiment_trend": "RISING"
            },
            "btc_prediction": {
                "agent_id": "agent_b",
                "predicted_change_pct": 3.5,
                "confidence": 0.75
            }
        },
        {
            "sentiment": {
                "agent_id": "agent_a",
                "overall_sentiment": -0.3,
                "sentiment_volatility": 0.4,
                "sentiment_trend": "FALLING"
            },
            "btc_prediction": {
                "agent_id": "agent_b",
                "predicted_change_pct": -2.1,
                "confidence": 0.68
            }
        }
    ]

    print("\n1. Running portfolio management cycles...\n")

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"--- Cycle {i}: Sentiment {scenario['sentiment']['overall_sentiment']:+.2f}, "
              f"BTC prediction {scenario['btc_prediction']['predicted_change_pct']:+.2f}% ---")

        # Run full cycle
        signal = agent_c.run_cycle(
            btc_prediction=scenario["btc_prediction"],
            sentiment_signal=scenario["sentiment"]
        )

        print(f"Portfolio Value: ${signal['portfolio_value']:,.0f}")
        print(f"Allocations: BTC {signal['btc_allocation_pct']}% | "
              f"SUI {signal['sui_allocation_pct']}% | USDC {signal['usdc_allocation_pct']}%")
        print(f"Rebalance Actions: {len(signal['rebalance_actions'])}")
        print(f"RAID Score: {signal['raid_score']:.3f}")
        print()

    print("-" * 80)

    print("\n2. Latest RAID Score Breakdown:")
    latest_raid = agent_c.tracker.get_latest_raid_score()
    if latest_raid:
        print(f"  Overall RAID: {latest_raid['raid_score']:.3f}")
        print(f"  ├─ Sharpe Ratio: {latest_raid['sharpe_ratio']:.2f}")
        print(f"  ├─ Total Return: {latest_raid['total_return_pct']:+.2f}%")
        print(f"  ├─ Max Drawdown: {latest_raid['max_drawdown_pct']:.2f}%")
        print(f"  └─ Win Rate: {latest_raid['win_rate']:.1%}")

    print("\n3. SUI Blockchain Status:")
    blockchain_status = sui_blockchain.get_blockchain_status()
    print(f"  Current Block: {blockchain_status['current_block']:,}")
    print(f"  Total Transactions: {blockchain_status['total_transactions']}")
    print(f"  Agent C Address: {agent_c.sui_address}")

    print("\n4. Current State Machine Status:")
    print(agent_c.state.get_state_description())

    print("\n" + "=" * 80)
    print("Test completed successfully!")
    print(f"Signals saved to: {agent_c.output_dir}")
