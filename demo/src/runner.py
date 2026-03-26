"""
Multi-Agent Investment System - Orchestrator

Coordinates the full 3-agent pipeline:
1. Agent A: News → Sentiment Metrics (NO RAID scoring)
2. Agent B: Sentiment + Price → BTC Prediction (RAID scoring: accuracy)
3. Agent C: Predictions → Portfolio Allocation (RAID scoring: Sharpe ratio)

All agents submit signals to Glass Box Protocol and execute on SUI blockchain.
"""

import sys
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

# Handle imports
sys.path.insert(0, str(Path(__file__).parent))

from agents.agent_a_sentiment import AgentA
from agents.agent_b_investment import AgentB
from agents.agent_c_portfolio import AgentC
from data_sources.price_fetcher import PriceFetcher
from data_sources.sui_integration import MockSUIBlockchain
from visualization.dashboard import DashboardGenerator


class MultiAgentOrchestrator:
    """
    Orchestrates the 3-agent investment system

    Pipeline:
    News → [Agent A] → Sentiment Signal
                           ↓
               BTC Price → [Agent B] → Price Prediction → RAID Score
                           ↓
               SUI Mock  → [Agent C] → Portfolio Allocation → RAID Score
                           ↓
                      SUI Blockchain
    """

    def __init__(
        self,
        initial_portfolio_value: float = 100000,
        initial_btc_price: float = 70000,
        initial_sui_price: float = 2.5
    ):
        """
        Initialize multi-agent system

        Args:
            initial_portfolio_value: Starting portfolio value in USD
            initial_btc_price: Starting BTC price
            initial_sui_price: Starting SUI price
        """
        print("=" * 80)
        print("  MULTI-AGENT INVESTMENT SYSTEM")
        print("  Glass Box Protocol + SUI Blockchain Integration")
        print("=" * 80)
        print()

        # Shared resources
        self.price_fetcher = PriceFetcher(
            initial_btc_price=initial_btc_price,
            initial_sui_price=initial_sui_price
        )

        self.sui_blockchain = MockSUIBlockchain()

        # Initialize agents
        print("[SYSTEM] Initializing agents...")
        print()

        self.agent_a = AgentA(agent_id="agent_a")
        print()

        self.agent_b = AgentB(
            agent_id="agent_b",
            price_fetcher=self.price_fetcher
        )
        print()

        self.agent_c = AgentC(
            agent_id="agent_c",
            initial_portfolio_value=initial_portfolio_value,
            price_fetcher=self.price_fetcher,
            sui_blockchain=self.sui_blockchain
        )
        print()

        # Execution stats
        self.cycle_count = 0
        self.start_time = datetime.now(timezone.utc)

        print("[SYSTEM] All agents initialized successfully!")
        print()

    def run_single_cycle(
        self,
        news_count: int = 5,
        sentiment_bias: Optional[str] = None
    ):
        """
        Execute one full cycle through all agents

        Args:
            news_count: Number of news articles for Agent A
            sentiment_bias: Optional sentiment bias ("bullish", "bearish", "neutral")
        """
        self.cycle_count += 1

        print("=" * 80)
        print(f"  CYCLE {self.cycle_count}")
        print("=" * 80)
        print()

        # Step 1: Agent A - Sentiment Digestion
        print("--- Agent A: Sentiment Digestion ---")
        sentiment_signal = self.agent_a.run_cycle(
            news_count=news_count,
            sentiment_bias=sentiment_bias
        )
        print(f"Output: Sentiment {sentiment_signal['overall_sentiment']:+.2f} | "
              f"Trend: {sentiment_signal['sentiment_trend']} | "
              f"Volume: {sentiment_signal['news_volume']}")
        print()

        # Step 2: Agent B - Investment Suggestion
        print("--- Agent B: Investment Suggestion ---")
        btc_prediction = self.agent_b.run_cycle(sentiment_signal)
        print(f"Output: BTC ${btc_prediction['predicted_btc_price']:,.0f} "
              f"({btc_prediction['predicted_change_pct']:+.2f}%) | "
              f"Confidence: {btc_prediction['confidence']:.1%} | "
              f"RAID: {btc_prediction['raid_score']:.3f}")
        print()

        # Step 3: Agent C - Portfolio Management
        print("--- Agent C: Portfolio Management ---")
        portfolio_signal = self.agent_c.run_cycle(btc_prediction, sentiment_signal)
        print(f"Output: Portfolio ${portfolio_signal['portfolio_value']:,.0f} | "
              f"BTC: {portfolio_signal['btc_allocation_pct']}% | "
              f"SUI: {portfolio_signal['sui_allocation_pct']}% | "
              f"USDC: {portfolio_signal['usdc_allocation_pct']}% | "
              f"RAID: {portfolio_signal['raid_score']:.3f}")
        print()

        # Display cycle summary
        self._print_cycle_summary(sentiment_signal, btc_prediction, portfolio_signal)

    def run_multiple_cycles(
        self,
        num_cycles: int = 5,
        news_per_cycle: int = 5,
        sentiment_pattern: Optional[list] = None
    ):
        """
        Execute multiple cycles

        Args:
            num_cycles: Number of cycles to run
            news_per_cycle: News articles per cycle
            sentiment_pattern: List of sentiment biases (cycles through list)
        """
        print(f"[SYSTEM] Running {num_cycles} cycles...")
        print()

        for i in range(num_cycles):
            sentiment_bias = None
            if sentiment_pattern:
                sentiment_bias = sentiment_pattern[i % len(sentiment_pattern)]

            self.run_single_cycle(
                news_count=news_per_cycle,
                sentiment_bias=sentiment_bias
            )

            # Short pause between cycles (simulating time passing)
            if i < num_cycles - 1:
                time.sleep(0.5)

        # Final summary
        self._print_final_summary()

    def _print_cycle_summary(self, sentiment, prediction, portfolio):
        """Print summary after each cycle"""
        print("-" * 80)
        print("CYCLE SUMMARY:")
        print(f"  Sentiment: {sentiment['overall_sentiment']:+.2f} ({sentiment['sentiment_trend']})")
        print(f"  BTC Prediction: {prediction['predicted_change_pct']:+.2f}% "
              f"(Confidence: {prediction['confidence']:.1%}, RAID: {prediction['raid_score']:.3f})")
        print(f"  Portfolio: ${portfolio['portfolio_value']:,.0f} "
              f"(RAID: {portfolio['raid_score']:.3f})")
        print(f"  Rebalancing: {len(portfolio['rebalance_actions'])} actions")
        print("-" * 80)
        print()

    def _print_final_summary(self):
        """Print final summary after all cycles"""
        print("=" * 80)
        print("  FINAL SUMMARY")
        print("=" * 80)
        print()

        # Agent B performance
        print("--- Agent B (Investment Suggestion) Performance ---")
        agent_b_raid = self.agent_b.tracker.get_latest_raid_score()
        if agent_b_raid:
            print(f"  RAID Score: {agent_b_raid['raid_score']:.3f}")
            print(f"  ├─ Accuracy: {agent_b_raid['accuracy_score']:.3f} (MAE: {agent_b_raid['mae_pct']:.2f}%)")
            print(f"  ├─ Direction: {agent_b_raid['direction_score']:.3f} ({agent_b_raid['direction_accuracy']:.1%})")
            print(f"  └─ Consistency: {agent_b_raid['consistency_score']:.3f}")
            print(f"  Total Predictions: {agent_b_raid['total_predictions']} "
                  f"(Validated: {agent_b_raid['validated_predictions']})")
        print()

        # Agent C performance
        print("--- Agent C (Portfolio Management) Performance ---")
        agent_c_raid = self.agent_c.tracker.get_latest_raid_score()
        if agent_c_raid:
            print(f"  RAID Score: {agent_c_raid['raid_score']:.3f}")
            print(f"  ├─ Sharpe Ratio: {agent_c_raid['sharpe_ratio']:.2f}")
            print(f"  ├─ Total Return: {agent_c_raid['total_return_pct']:+.2f}%")
            print(f"  ├─ Max Drawdown: {agent_c_raid['max_drawdown_pct']:.2f}%")
            print(f"  └─ Win Rate: {agent_c_raid['win_rate']:.1%}")
            print(f"  Portfolio Value: ${agent_c_raid['current_value']:,.0f}")
            print(f"  Total Rebalances: {agent_c_raid['total_rebalances']}")
        print()

        # SUI blockchain status
        print("--- SUI Blockchain Status ---")
        blockchain_status = self.sui_blockchain.get_blockchain_status()
        print(f"  Current Block: {blockchain_status['current_block']:,}")
        print(f"  Total Transactions: {blockchain_status['total_transactions']}")
        print(f"  Registered Agents: {blockchain_status['registered_agents']}")
        print()

        for agent_name, agent_info in blockchain_status['agents'].items():
            raid = agent_info['raid_score'] if agent_info['raid_score'] else 'N/A'
            print(f"  {agent_name}: {agent_info['address']} | RAID: {raid}")
        print()

        # Execution stats
        elapsed_time = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        print(f"--- Execution Stats ---")
        print(f"  Total Cycles: {self.cycle_count}")
        print(f"  Execution Time: {elapsed_time:.2f}s")
        print(f"  Average Cycle Time: {elapsed_time/self.cycle_count:.2f}s")
        print()

        print("=" * 80)
        print("  SYSTEM COMPLETE")
        print("=" * 80)
        print()

        # Generate visualization dashboard
        print("Generating visualization dashboard...")
        try:
            dashboard = DashboardGenerator()
            dashboard.generate_dashboard()
            print()
        except Exception as e:
            print(f"Warning: Could not generate dashboard: {e}")
            print()


def main():
    """Main entry point"""
    # Initialize orchestrator
    orchestrator = MultiAgentOrchestrator(
        initial_portfolio_value=100000,
        initial_btc_price=70000,
        initial_sui_price=2.5
    )

    # Run multiple cycles with varying sentiment patterns
    sentiment_pattern = ["bullish", "bullish", "neutral", "bearish", "neutral"]

    orchestrator.run_multiple_cycles(
        num_cycles=5,
        news_per_cycle=6,
        sentiment_pattern=sentiment_pattern
    )


if __name__ == "__main__":
    main()
