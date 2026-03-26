"""
Agent A: Sentiment Digestion Agent

Consumes news headlines and extracts sentiment metrics for downstream agents.
NO RAID scoring - this is a baseline data processing agent.

Signal Output Format:
{
    "agent_id": "agent_a",
    "timestamp": "2024-...",
    "overall_sentiment": 0.0 to 1.0,      # Aggregate sentiment score
    "sentiment_volatility": 0.0 to 1.0,   # How much sentiment is fluctuating
    "news_volume": int,                   # Number of articles processed
    "bullish_ratio": 0.0 to 1.0,          # Percentage of bullish articles
    "sentiment_trend": "RISING" | "FALLING" | "STABLE",
    "key_topics": ["topic1", "topic2"]    # Main themes in news
}
"""

import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import json

# Handle imports for both standalone and package usage
try:
    from ..state.state_machine import create_agent_a_state_machine
except (ImportError, ValueError):
    # Standalone execution or being imported from runner
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from state.state_machine import create_agent_a_state_machine


class NewsSimulator:
    """Simulate Bitcoin/crypto news headlines with varying sentiment"""

    NEWS_TEMPLATES = {
        "bullish": [
            "Bitcoin ETF sees record inflows of ${amount}M in single day",
            "Major institution announces ${amount}M Bitcoin investment",
            "Bitcoin adoption surges as {count} new countries embrace crypto",
            "Bitcoin lightning network transactions surge {pct}% year-over-year",
            "Bitcoin mining difficulty reaches all-time high, signaling network strength",
            "Bitcoin on-chain metrics show strongest accumulation since {year}",
            "Payment giant {company} integrates Bitcoin for {count}M users",
            "Bitcoin hash rate hits new record high",
            "Analyst predicts Bitcoin to reach ${price}K by end of {year}",
            "Bitcoin correlation with traditional markets hits multi-year low"
        ],
        "bearish": [
            "Bitcoin price drops {pct}% amid regulatory concerns",
            "Major exchange reports ${amount}M in Bitcoin outflows",
            "Analyst warns of potential Bitcoin correction to ${price}K",
            "Bitcoin faces resistance at ${price}K level",
            "Regulatory pressure mounts as {country} considers crypto restrictions",
            "Bitcoin dominance falls to {pct}% as altcoins gain traction",
            "Whale wallet moves ${amount}M in Bitcoin to exchange",
            "Bitcoin futures show increased short interest",
            "Crypto winter fears resurface as Bitcoin struggles",
            "Technical indicators suggest Bitcoin overbought at current levels"
        ],
        "neutral": [
            "Bitcoin holds steady despite mixed macroeconomic signals",
            "Bitcoin trading volume remains flat week-over-week",
            "Analysts divided on Bitcoin's short-term direction",
            "Bitcoin consolidates between ${low}K and ${high}K",
            "Bitcoin market awaits key economic data releases",
            "Mixed signals from Bitcoin on-chain metrics",
            "Bitcoin volatility index reaches {year} average",
            "Institutional Bitcoin holdings remain unchanged this quarter",
            "Bitcoin price action mirrors previous consolidation phases",
            "Crypto market sentiment remains neutral amid uncertainty"
        ]
    }

    def generate_headline(self, sentiment_bias: Optional[str] = None) -> Dict:
        """
        Generate a realistic news headline with sentiment

        Args:
            sentiment_bias: "bullish", "bearish", "neutral", or None for random

        Returns:
            dict: {"headline": str, "sentiment": float, "category": str}
        """
        if sentiment_bias is None:
            sentiment_bias = random.choice(["bullish", "bearish", "neutral"])

        template = random.choice(self.NEWS_TEMPLATES[sentiment_bias])

        # Fill in template variables
        headline = template
        headline = re.sub(r'\{amount\}', str(random.randint(100, 1000)), headline)
        headline = re.sub(r'\{count\}', str(random.randint(10, 500)), headline)
        headline = re.sub(r'\{pct\}', str(random.randint(5, 300)), headline)
        headline = re.sub(r'\{price\}', str(random.randint(40, 100)), headline)
        headline = re.sub(r'\{year\}', str(random.randint(2020, 2024)), headline)
        headline = re.sub(r'\{country\}', random.choice(["China", "India", "US", "EU"]), headline)
        headline = re.sub(r'\{company\}', random.choice(["Visa", "PayPal", "Square", "Mastercard"]), headline)
        headline = re.sub(r'\{low\}', str(random.randint(60, 70)), headline)
        headline = re.sub(r'\{high\}', str(random.randint(71, 80)), headline)

        # Assign sentiment score
        if sentiment_bias == "bullish":
            sentiment = random.uniform(0.4, 0.9)
        elif sentiment_bias == "bearish":
            sentiment = random.uniform(-0.9, -0.4)
        else:  # neutral
            sentiment = random.uniform(-0.3, 0.3)

        return {
            "headline": headline,
            "sentiment": round(sentiment, 2),
            "category": sentiment_bias,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


class AgentA:
    """
    Sentiment Digestion Agent

    Processes news headlines and outputs structured sentiment signals
    """

    def __init__(self, agent_id: str = "agent_a", output_dir: Optional[Path] = None):
        """
        Initialize Agent A

        Args:
            agent_id: Agent identifier
            output_dir: Directory to store signals
        """
        self.agent_id = agent_id

        if output_dir is None:
            output_dir = Path(__file__).parent.parent.parent / "output" / "signals"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # State machine
        self.state = create_agent_a_state_machine(agent_id)

        # News simulator
        self.news_sim = NewsSimulator()

        # News buffer
        self.news_buffer = []
        self.max_buffer_size = 20

        # Sentiment history (for trend detection)
        self.sentiment_history = []

        print(f"[{self.agent_id}] Agent A initialized")

    def collect_news(self, count: int = 5, sentiment_bias: Optional[str] = None):
        """
        Collect news headlines

        Args:
            count: Number of headlines to collect
            sentiment_bias: Optional bias ("bullish", "bearish", "neutral")
        """
        self.state.transition("COLLECTING", f"Collecting {count} news articles")

        for _ in range(count):
            headline_data = self.news_sim.generate_headline(sentiment_bias)
            self.news_buffer.append(headline_data)

        # Keep buffer size limited
        if len(self.news_buffer) > self.max_buffer_size:
            self.news_buffer = self.news_buffer[-self.max_buffer_size:]

        self.state.update_metadata("news_count", len(self.news_buffer))

    def analyze_sentiment(self) -> Dict:
        """
        Analyze sentiment from news buffer

        Returns:
            dict: Sentiment signal
        """
        self.state.transition("ANALYZING", f"Analyzing {len(self.news_buffer)} articles")

        if not self.news_buffer:
            # No news to analyze
            return self._create_neutral_signal()

        # Calculate sentiment metrics

        # 1. Overall sentiment (average)
        sentiments = [article["sentiment"] for article in self.news_buffer]
        overall_sentiment = sum(sentiments) / len(sentiments)

        # 2. Sentiment volatility (standard deviation)
        if len(sentiments) > 1:
            mean_sentiment = overall_sentiment
            variance = sum((s - mean_sentiment) ** 2 for s in sentiments) / len(sentiments)
            sentiment_volatility = variance ** 0.5
        else:
            sentiment_volatility = 0.0

        # Normalize volatility to [0, 1] range (assuming max volatility ~1.0)
        sentiment_volatility = min(sentiment_volatility, 1.0)

        # 3. News volume
        news_volume = len(self.news_buffer)

        # 4. Bullish ratio
        bullish_count = sum(1 for article in self.news_buffer if article["sentiment"] > 0.2)
        bullish_ratio = bullish_count / len(self.news_buffer)

        # 5. Sentiment trend (compare recent vs older articles)
        if len(self.news_buffer) >= 4:
            recent_avg = sum(sentiments[-2:]) / 2
            older_avg = sum(sentiments[:2]) / 2
            diff = recent_avg - older_avg

            if diff > 0.15:
                sentiment_trend = "RISING"
            elif diff < -0.15:
                sentiment_trend = "FALLING"
            else:
                sentiment_trend = "STABLE"
        else:
            sentiment_trend = "STABLE"

        # 6. Key topics (extract from categories)
        categories = [article["category"] for article in self.news_buffer]
        category_counts = {}
        for cat in categories:
            category_counts[cat] = category_counts.get(cat, 0) + 1

        key_topics = sorted(category_counts.keys(), key=lambda k: category_counts[k], reverse=True)[:3]

        # Create signal
        signal = {
            "agent_id": self.agent_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_sentiment": round(overall_sentiment, 2),
            "sentiment_volatility": round(sentiment_volatility, 2),
            "news_volume": news_volume,
            "bullish_ratio": round(bullish_ratio, 2),
            "sentiment_trend": sentiment_trend,
            "key_topics": key_topics
        }

        # Store in history
        self.sentiment_history.append(signal)
        if len(self.sentiment_history) > 50:
            self.sentiment_history = self.sentiment_history[-50:]

        self.state.update_metadata("overall_sentiment", overall_sentiment)
        self.state.update_metadata("sentiment_trend", sentiment_trend)

        return signal

    def publish_signal(self, signal: Dict):
        """
        Publish sentiment signal to file

        Args:
            signal: Sentiment signal dictionary
        """
        self.state.transition("PUBLISHING", "Publishing sentiment signal")

        # Write to JSONL file
        signal_file = self.output_dir / f"{self.agent_id}_signals.jsonl"

        with open(signal_file, 'a') as f:
            f.write(json.dumps(signal) + "\n")

        print(f"[{self.agent_id}] Published signal: sentiment={signal['overall_sentiment']:+.2f}, "
              f"trend={signal['sentiment_trend']}, volume={signal['news_volume']}")

        # Return to IDLE state
        self.state.transition("IDLE", "Signal published, returning to idle")

    def run_cycle(self, news_count: int = 5, sentiment_bias: Optional[str] = None) -> Dict:
        """
        Execute one full sentiment analysis cycle

        Args:
            news_count: Number of news articles to collect
            sentiment_bias: Optional sentiment bias for simulation

        Returns:
            dict: Published sentiment signal
        """
        # IDLE → COLLECTING
        self.collect_news(count=news_count, sentiment_bias=sentiment_bias)

        # COLLECTING → ANALYZING
        signal = self.analyze_sentiment()

        # ANALYZING → PUBLISHING → IDLE
        self.publish_signal(signal)

        return signal

    def get_latest_signal(self) -> Optional[Dict]:
        """Get most recent sentiment signal"""
        return self.sentiment_history[-1] if self.sentiment_history else None

    def get_signal_history(self, limit: int = 10) -> List[Dict]:
        """Get recent sentiment signals"""
        return self.sentiment_history[-limit:]

    def _create_neutral_signal(self) -> Dict:
        """Create neutral signal when no news available"""
        return {
            "agent_id": self.agent_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_sentiment": 0.0,
            "sentiment_volatility": 0.0,
            "news_volume": 0,
            "bullish_ratio": 0.5,
            "sentiment_trend": "STABLE",
            "key_topics": []
        }


if __name__ == "__main__":
    # Test Agent A
    print("\nAgent A: Sentiment Digestion Agent - Test Output\n")
    print("=" * 80)

    agent = AgentA()

    print("\n1. Running neutral sentiment cycle...")
    signal1 = agent.run_cycle(news_count=5, sentiment_bias=None)
    print(f"\nSignal Output:")
    print(json.dumps(signal1, indent=2))

    print("\n" + "-" * 80)

    print("\n2. Running bullish sentiment cycle...")
    signal2 = agent.run_cycle(news_count=7, sentiment_bias="bullish")
    print(f"\nSignal Output:")
    print(json.dumps(signal2, indent=2))

    print("\n" + "-" * 80)

    print("\n3. Running bearish sentiment cycle...")
    signal3 = agent.run_cycle(news_count=6, sentiment_bias="bearish")
    print(f"\nSignal Output:")
    print(json.dumps(signal3, indent=2))

    print("\n" + "-" * 80)

    print("\n4. Signal History:")
    for i, sig in enumerate(agent.get_signal_history(), 1):
        print(f"  [{i}] Sentiment: {sig['overall_sentiment']:+.2f} | "
              f"Trend: {sig['sentiment_trend']:8s} | "
              f"Bullish Ratio: {sig['bullish_ratio']:.1%} | "
              f"Volume: {sig['news_volume']}")

    print("\n5. Current State Machine Status:")
    print(agent.state.get_state_description())

    print("\n" + "=" * 80)
    print("Test completed successfully!")
    print(f"Signals saved to: {agent.output_dir}")
