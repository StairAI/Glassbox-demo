"""
Portfolio Tracker - Agent C RAID Scoring

Tracks Agent C's portfolio performance and calculates RAID score based on:
- Sharpe Ratio (risk-adjusted returns)
- Total returns
- Maximum drawdown
- Win rate (profitable rebalances)
"""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional


class PortfolioTracker:
    """
    Track Agent C's portfolio performance and calculate RAID score

    RAID Score Components:
    - Sharpe Ratio (40%): Risk-adjusted return metric
    - Total Return (30%): Absolute portfolio gain/loss percentage
    - Max Drawdown (20%): Largest peak-to-trough decline (lower = better)
    - Win Rate (10%): Percentage of profitable rebalances
    """

    def __init__(self, agent_id: str = "agent_c", initial_portfolio_value: float = 100000, storage_dir: Optional[Path] = None):
        """
        Initialize portfolio tracker

        Args:
            agent_id: Agent identifier
            initial_portfolio_value: Starting portfolio value in USD
            storage_dir: Directory to store portfolio history
        """
        self.agent_id = agent_id
        self.initial_value = initial_portfolio_value
        self.current_value = initial_portfolio_value

        if storage_dir is None:
            storage_dir = Path(__file__).parent.parent.parent / "output" / "scoring"
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Portfolio snapshots over time
        self.snapshots = []

        # Rebalancing actions history
        self.rebalances = []

        # RAID score history
        self.raid_scores = []

        # Performance metrics
        self.peak_value = initial_portfolio_value  # For drawdown calculation

        # Load persisted data
        self._load_data()

    def record_snapshot(
        self,
        portfolio_value: float,
        btc_allocation_pct: float,
        sui_allocation_pct: float,
        usdc_allocation_pct: float,
        metadata: Optional[Dict] = None
    ):
        """
        Record portfolio snapshot

        Args:
            portfolio_value: Total portfolio value in USD
            btc_allocation_pct: BTC allocation percentage (0-100)
            sui_allocation_pct: SUI allocation percentage (0-100)
            usdc_allocation_pct: USDC allocation percentage (0-100)
            metadata: Additional context
        """
        snapshot = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "portfolio_value": portfolio_value,
            "btc_allocation_pct": btc_allocation_pct,
            "sui_allocation_pct": sui_allocation_pct,
            "usdc_allocation_pct": usdc_allocation_pct,
            "total_return_pct": ((portfolio_value - self.initial_value) / self.initial_value) * 100,
            "metadata": metadata or {}
        }

        self.snapshots.append(snapshot)
        self.current_value = portfolio_value

        # Update peak for drawdown calculation
        if portfolio_value > self.peak_value:
            self.peak_value = portfolio_value

        self._save_data()

    def record_rebalance(
        self,
        actions: List[Dict],
        portfolio_value_before: float,
        portfolio_value_after: float,
        transaction_hash: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Record a rebalancing action

        Args:
            actions: List of actions [{"asset": "BTC", "action": "BUY", "amount_usd": 5000}, ...]
            portfolio_value_before: Value before rebalance
            portfolio_value_after: Value after rebalance (including gas costs)
            transaction_hash: SUI blockchain transaction hash
            metadata: Additional context
        """
        rebalance = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actions": actions,
            "value_before": portfolio_value_before,
            "value_after": portfolio_value_after,
            "gas_cost_usd": portfolio_value_before - portfolio_value_after,  # Simplified
            "transaction_hash": transaction_hash,
            "profitable": None,  # To be determined after time passes
            "metadata": metadata or {}
        }

        self.rebalances.append(rebalance)
        self._save_data()

        print(f"[{self.agent_id}] Recorded rebalance: {len(actions)} actions, "
              f"value: ${portfolio_value_after:,.2f}")

    def mark_rebalance_outcome(self, rebalance_index: int, profitable: bool):
        """
        Mark whether a rebalance was profitable

        Args:
            rebalance_index: Index in rebalances list
            profitable: True if rebalance led to profit
        """
        if 0 <= rebalance_index < len(self.rebalances):
            self.rebalances[rebalance_index]["profitable"] = profitable
            self._save_data()

    def calculate_raid_score(self, lookback_hours: int = 168) -> Dict:
        """
        Calculate RAID score based on recent portfolio performance

        Args:
            lookback_hours: Hours of history to consider (default: 7 days)

        Returns:
            dict: RAID score and component metrics
        """
        # Filter snapshots within lookback window
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)

        recent_snapshots = [
            s for s in self.snapshots
            if datetime.fromisoformat(s["timestamp"]) > cutoff_time
        ]

        if len(recent_snapshots) < 2:
            return {
                "raid_score": 0.5,  # Neutral score with insufficient data
                "sharpe_ratio_score": 0.5,
                "return_score": 0.5,
                "drawdown_score": 0.5,
                "win_rate_score": 0.5,
                "sharpe_ratio": 0.0,
                "total_return_pct": 0.0,
                "max_drawdown_pct": 0.0,
                "win_rate": 0.0,
                "total_snapshots": len(self.snapshots),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        # Calculate metrics

        # 1. Sharpe Ratio (risk-adjusted returns)
        returns = []
        for i in range(1, len(recent_snapshots)):
            prev_value = recent_snapshots[i-1]["portfolio_value"]
            curr_value = recent_snapshots[i]["portfolio_value"]
            returns.append((curr_value - prev_value) / prev_value)

        if returns:
            avg_return = sum(returns) / len(returns)
            if len(returns) > 1:
                variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
                std_dev = variance ** 0.5
            else:
                std_dev = 0.001  # Avoid division by zero

            # Annualized Sharpe ratio (assuming hourly snapshots)
            risk_free_rate = 0.04 / (365 * 24)  # 4% annual risk-free rate
            sharpe_ratio = (avg_return - risk_free_rate) / std_dev if std_dev > 0 else 0.0
        else:
            sharpe_ratio = 0.0

        # Sharpe score: 1.0 for Sharpe >= 2.0, 0.0 for Sharpe <= 0
        sharpe_ratio_score = max(0.0, min(1.0, sharpe_ratio / 2.0))

        # 2. Total Return
        first_value = recent_snapshots[0]["portfolio_value"]
        last_value = recent_snapshots[-1]["portfolio_value"]
        total_return_pct = ((last_value - first_value) / first_value) * 100

        # Return score: 1.0 for +20% return, 0.0 for -20% return, 0.5 for 0%
        return_score = max(0.0, min(1.0, 0.5 + (total_return_pct / 40.0)))

        # 3. Maximum Drawdown
        peak = recent_snapshots[0]["portfolio_value"]
        max_drawdown_pct = 0.0

        for snapshot in recent_snapshots:
            value = snapshot["portfolio_value"]
            if value > peak:
                peak = value
            drawdown_pct = ((peak - value) / peak) * 100
            if drawdown_pct > max_drawdown_pct:
                max_drawdown_pct = drawdown_pct

        # Drawdown score: 1.0 for 0% drawdown, 0.0 for 30%+ drawdown
        drawdown_score = max(0.0, min(1.0, 1.0 - (max_drawdown_pct / 30.0)))

        # 4. Win Rate (for recent rebalances)
        recent_rebalances = [
            r for r in self.rebalances
            if datetime.fromisoformat(r["timestamp"]) > cutoff_time and r["profitable"] is not None
        ]

        if recent_rebalances:
            wins = sum(1 for r in recent_rebalances if r["profitable"])
            win_rate = wins / len(recent_rebalances)
            win_rate_score = win_rate
        else:
            win_rate = 0.5
            win_rate_score = 0.5

        # Combined RAID score (weighted average)
        raid_score = (
            sharpe_ratio_score * 0.40 +
            return_score * 0.30 +
            drawdown_score * 0.20 +
            win_rate_score * 0.10
        )

        result = {
            "raid_score": round(raid_score, 3),
            "sharpe_ratio_score": round(sharpe_ratio_score, 3),
            "return_score": round(return_score, 3),
            "drawdown_score": round(drawdown_score, 3),
            "win_rate_score": round(win_rate_score, 3),
            "sharpe_ratio": round(sharpe_ratio, 3),
            "total_return_pct": round(total_return_pct, 2),
            "max_drawdown_pct": round(max_drawdown_pct, 2),
            "win_rate": round(win_rate, 3),
            "total_snapshots": len(self.snapshots),
            "total_rebalances": len(self.rebalances),
            "current_value": self.current_value,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # Store RAID score history
        self.raid_scores.append(result)
        self._save_data()

        return result

    def get_snapshot_history(self, limit: int = 20) -> List[Dict]:
        """Get recent portfolio snapshots"""
        return self.snapshots[-limit:]

    def get_rebalance_history(self, limit: int = 10) -> List[Dict]:
        """Get recent rebalances"""
        return self.rebalances[-limit:]

    def get_raid_score_history(self, limit: int = 10) -> List[Dict]:
        """Get recent RAID scores"""
        return self.raid_scores[-limit:]

    def get_latest_raid_score(self) -> Optional[Dict]:
        """Get most recent RAID score"""
        return self.raid_scores[-1] if self.raid_scores else None

    def _save_data(self):
        """Persist portfolio data to disk"""
        data_file = self.storage_dir / f"{self.agent_id}_portfolio.json"

        data = {
            "agent_id": self.agent_id,
            "initial_value": self.initial_value,
            "current_value": self.current_value,
            "peak_value": self.peak_value,
            "snapshots": self.snapshots[-200:],      # Keep last 200
            "rebalances": self.rebalances[-50:],     # Keep last 50
            "raid_scores": self.raid_scores[-50:]    # Keep last 50
        }

        with open(data_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _load_data(self):
        """Load persisted portfolio data"""
        data_file = self.storage_dir / f"{self.agent_id}_portfolio.json"

        if not data_file.exists():
            return

        try:
            with open(data_file, 'r') as f:
                data = json.load(f)

            self.initial_value = data.get("initial_value", self.initial_value)
            self.current_value = data.get("current_value", self.current_value)
            self.peak_value = data.get("peak_value", self.peak_value)
            self.snapshots = data.get("snapshots", [])
            self.rebalances = data.get("rebalances", [])
            self.raid_scores = data.get("raid_scores", [])

            print(f"[{self.agent_id}] Loaded {len(self.snapshots)} snapshots, "
                  f"{len(self.rebalances)} rebalances, {len(self.raid_scores)} RAID scores")

        except Exception as e:
            print(f"[{self.agent_id}] Warning: Could not load data: {e}")


if __name__ == "__main__":
    # Test portfolio tracker
    print("\nPortfolio Tracker - Test Output\n")
    print("=" * 80)

    tracker = PortfolioTracker(initial_portfolio_value=100000)

    print("\n1. Recording initial snapshot...")
    tracker.record_snapshot(
        portfolio_value=100000,
        btc_allocation_pct=40,
        sui_allocation_pct=30,
        usdc_allocation_pct=30
    )

    print("\n2. Simulating portfolio performance over time...")
    import random
    values = [100000]
    for i in range(10):
        # Simulate portfolio growth with volatility
        change = random.gauss(0.02, 0.05)  # 2% avg growth, 5% volatility
        new_value = values[-1] * (1 + change)
        values.append(new_value)

        # Allocations shift slightly
        btc_pct = 40 + random.gauss(0, 5)
        sui_pct = 30 + random.gauss(0, 5)
        usdc_pct = 100 - btc_pct - sui_pct

        tracker.record_snapshot(
            portfolio_value=new_value,
            btc_allocation_pct=btc_pct,
            sui_allocation_pct=sui_pct,
            usdc_allocation_pct=usdc_pct
        )

    print(f"  Final value: ${tracker.current_value:,.2f}")

    print("\n3. Recording rebalance actions...")
    tracker.record_rebalance(
        actions=[
            {"asset": "BTC", "action": "BUY", "amount_usd": 5000},
            {"asset": "USDC", "action": "SELL", "amount_usd": -5000}
        ],
        portfolio_value_before=values[-1],
        portfolio_value_after=values[-1] - 10,  # Gas cost
        transaction_hash="0x1234abcd"
    )

    # Mark rebalance as profitable
    tracker.mark_rebalance_outcome(0, profitable=True)

    print("\n4. Calculating RAID score...")
    raid_score = tracker.calculate_raid_score()

    print(f"\nRAID Score Report:")
    print(f"  Overall RAID Score: {raid_score['raid_score']:.3f}")
    print(f"  ├─ Sharpe Ratio Score: {raid_score['sharpe_ratio_score']:.3f} (Sharpe: {raid_score['sharpe_ratio']:.2f})")
    print(f"  ├─ Return Score: {raid_score['return_score']:.3f} (Return: {raid_score['total_return_pct']:+.2f}%)")
    print(f"  ├─ Drawdown Score: {raid_score['drawdown_score']:.3f} (Max DD: {raid_score['max_drawdown_pct']:.2f}%)")
    print(f"  └─ Win Rate Score: {raid_score['win_rate_score']:.3f} (Win Rate: {raid_score['win_rate']:.1%})")
    print(f"\n  Total Snapshots: {raid_score['total_snapshots']}")
    print(f"  Total Rebalances: {raid_score['total_rebalances']}")
    print(f"  Current Portfolio Value: ${raid_score['current_value']:,.2f}")

    print("\n5. Portfolio Snapshot History (last 5):")
    for snapshot in tracker.get_snapshot_history(limit=5):
        print(f"  [{snapshot['timestamp'][:19]}] ${snapshot['portfolio_value']:,.2f} | "
              f"BTC: {snapshot['btc_allocation_pct']:.1f}% | "
              f"SUI: {snapshot['sui_allocation_pct']:.1f}% | "
              f"USDC: {snapshot['usdc_allocation_pct']:.1f}% | "
              f"Total Return: {snapshot['total_return_pct']:+.2f}%")

    print("\n" + "=" * 80)
    print("Test completed successfully!")
    print(f"Data saved to: {tracker.storage_dir}")
