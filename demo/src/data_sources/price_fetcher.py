"""
BTC/SUI Price Simulator
Simulates realistic crypto price movements with volatility
"""

import random
import math
from datetime import datetime, timezone, timedelta
from typing import Dict, List


class PriceFetcher:
    """Simulate BTC and SUI price movements"""

    def __init__(self, initial_btc_price: float = 70000, initial_sui_price: float = 2.5):
        """
        Initialize price simulator

        Args:
            initial_btc_price: Starting BTC price in USD
            initial_sui_price: Starting SUI price in USD
        """
        self.btc_price = initial_btc_price
        self.sui_price = initial_sui_price

        # Price history (for charts and analysis)
        self.btc_history = []
        self.sui_history = []

        self.start_time = datetime.now(timezone.utc)

        # Volatility parameters
        self.btc_volatility = 0.03  # 3% daily volatility
        self.sui_volatility = 0.06  # 6% daily volatility (higher for smaller cap)

        # Trend bias (can be influenced by sentiment)
        self.btc_trend_bias = 0.0  # -1.0 (bearish) to +1.0 (bullish)
        self.sui_trend_bias = 0.0

    def fetch_prices(self) -> Dict:
        """
        Fetch current BTC and SUI prices

        Returns:
            dict: {
                "btc": {"price": float, "change_24h_pct": float},
                "sui": {"price": float, "change_24h_pct": float},
                "timestamp": str
            }
        """
        # Simulate price movement
        self._update_prices()

        # Calculate 24h changes
        btc_change_24h = self._calculate_24h_change(self.btc_history, self.btc_price)
        sui_change_24h = self._calculate_24h_change(self.sui_history, self.sui_price)

        return {
            "btc": {
                "price": round(self.btc_price, 2),
                "change_24h_pct": round(btc_change_24h, 2),
                "volatility": self.btc_volatility,
                "trend_bias": self.btc_trend_bias
            },
            "sui": {
                "price": round(self.sui_price, 4),  # More decimals for lower price
                "change_24h_pct": round(sui_change_24h, 2),
                "volatility": self.sui_volatility,
                "trend_bias": self.sui_trend_bias
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def _update_prices(self):
        """Update prices with realistic random walk"""
        timestamp = datetime.now(timezone.utc)

        # BTC price update
        btc_random_return = random.gauss(0, self.btc_volatility / math.sqrt(365 * 24))
        btc_trend_influence = self.btc_trend_bias * self.btc_volatility / math.sqrt(365 * 24)
        btc_total_return = btc_random_return + btc_trend_influence

        self.btc_price *= (1 + btc_total_return)
        self.btc_price = max(30000, min(150000, self.btc_price))  # Floor/ceiling

        self.btc_history.append({
            "timestamp": timestamp,
            "price": self.btc_price
        })

        # SUI price update (correlated with BTC but more volatile)
        correlation = 0.7  # 70% correlation with BTC (less than ETH)
        sui_correlated_component = btc_total_return * correlation
        sui_independent_component = random.gauss(0, self.sui_volatility / math.sqrt(365 * 24)) * (1 - correlation)
        sui_trend_influence = self.sui_trend_bias * self.sui_volatility / math.sqrt(365 * 24)
        sui_total_return = sui_correlated_component + sui_independent_component + sui_trend_influence

        self.sui_price *= (1 + sui_total_return)
        self.sui_price = max(0.5, min(10.0, self.sui_price))  # Floor/ceiling

        self.sui_history.append({
            "timestamp": timestamp,
            "price": self.sui_price
        })

        # Keep only last 24 hours of history
        cutoff_time = timestamp - timedelta(hours=24)
        self.btc_history = [h for h in self.btc_history if h["timestamp"] > cutoff_time]
        self.sui_history = [h for h in self.sui_history if h["timestamp"] > cutoff_time]

    def _calculate_24h_change(self, history: List[Dict], current_price: float) -> float:
        """Calculate 24-hour price change percentage"""
        if not history:
            return 0.0

        oldest_price = history[0]["price"]
        change_pct = ((current_price - oldest_price) / oldest_price) * 100
        return change_pct

    def set_sentiment_influence(self, btc_sentiment: float, sui_sentiment: float):
        """
        Allow sentiment to influence price trends

        Args:
            btc_sentiment: -1.0 to +1.0 (bearish to bullish)
            sui_sentiment: -1.0 to +1.0 (bearish to bullish)
        """
        # Sentiment gradually shifts trend bias
        self.btc_trend_bias = 0.7 * self.btc_trend_bias + 0.3 * btc_sentiment
        self.sui_trend_bias = 0.7 * self.sui_trend_bias + 0.3 * sui_sentiment

        # Clamp to [-1, 1]
        self.btc_trend_bias = max(-1.0, min(1.0, self.btc_trend_bias))
        self.sui_trend_bias = max(-1.0, min(1.0, self.sui_trend_bias))

    def get_price_at_time(self, asset: str, hours_ago: int) -> float:
        """
        Get historical price from N hours ago

        Args:
            asset: "BTC" or "SUI"
            hours_ago: How many hours in the past

        Returns:
            float: Price at that time (or current if not available)
        """
        history = self.btc_history if asset == "BTC" else self.sui_history
        current_price = self.btc_price if asset == "BTC" else self.sui_price

        if not history or hours_ago <= 0:
            return current_price

        target_time = datetime.now(timezone.utc) - timedelta(hours=hours_ago)

        # Find closest historical price
        closest = None
        min_diff = float('inf')

        for record in history:
            diff = abs((record["timestamp"] - target_time).total_seconds())
            if diff < min_diff:
                min_diff = diff
                closest = record

        return closest["price"] if closest else current_price


if __name__ == "__main__":
    # Test the price fetcher
    print("\nPrice Fetcher - Test Output\n")
    print("=" * 80)

    fetcher = PriceFetcher(initial_btc_price=70000, initial_sui_price=2.5)

    print("\nSimulating 10 price updates...\n")

    for i in range(10):
        # Simulate some sentiment influence
        if i == 5:
            print("  [Applying bullish sentiment influence...]\n")
            fetcher.set_sentiment_influence(btc_sentiment=0.7, sui_sentiment=0.5)

        prices = fetcher.fetch_prices()

        print(f"Update {i+1}:")
        print(f"  BTC: ${prices['btc']['price']:,.2f} ({prices['btc']['change_24h_pct']:+.2f}%)")
        print(f"  SUI: ${prices['sui']['price']:.4f} ({prices['sui']['change_24h_pct']:+.2f}%)")
        print(f"  Time: {prices['timestamp']}")
        print()

    print("=" * 80)
    print("Test completed successfully!")
