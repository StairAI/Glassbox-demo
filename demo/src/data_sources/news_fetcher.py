"""
Bitcoin News Fetcher
Generates mock Bitcoin-related news for demo purposes
"""

import random
from datetime import datetime, timezone
from typing import Dict


class NewsFetcher:
    """Fetches Bitcoin-related news (mock implementation)"""

    def __init__(self):
        self.bullish_templates = [
            "Bitcoin surges past ${price}k as institutional adoption accelerates",
            "Major bank announces Bitcoin custody services, market rallies",
            "Bitcoin network hash rate hits all-time high, signaling strength",
            "El Salvador doubles down on Bitcoin strategy with new purchases",
            "Bitcoin ETF sees record inflows of $500M in single day",
            "MicroStrategy acquires additional {amount} BTC for treasury",
            "Bitcoin lightning network transactions surge 300% year-over-year",
            "Bitcoin dominance rises to {dom}% as altcoins struggle",
            "Institutional investors allocate {pct}% of portfolio to Bitcoin",
            "Bitcoin breaks through key resistance at ${price}k with strong momentum"
        ]

        self.bearish_templates = [
            "Bitcoin drops below ${price}k amid regulatory concerns",
            "SEC increases scrutiny on cryptocurrency exchanges",
            "Major exchange reports security breach, Bitcoin falls",
            "China reaffirms cryptocurrency ban, market tumbles",
            "Bitcoin mining difficulty adjustment raises energy concerns",
            "Large wallet moves {amount} BTC to exchange, sell pressure expected",
            "Bitcoin funding rates turn negative as shorts increase",
            "Regulatory uncertainty weighs on Bitcoin sentiment",
            "Bitcoin correlation with tech stocks increases amid market volatility",
            "Bitcoin fails to hold ${price}k support level"
        ]

        self.neutral_templates = [
            "Bitcoin trades sideways at ${price}k as market awaits direction",
            "Bitcoin volatility reaches lowest level in 6 months",
            "Analysts divided on Bitcoin's next major move",
            "Bitcoin holds steady despite mixed macroeconomic signals",
            "Bitcoin consolidates in tight range between ${low}k-${high}k",
            "Bitcoin market participants remain cautious ahead of Fed decision",
            "Bitcoin trading volume remains subdued during holiday period",
            "Bitcoin miners continue operations despite thin margins",
            "Bitcoin on-chain metrics show mixed signals",
            "Bitcoin market cap maintains $1.3T valuation"
        ]

        self.news_counter = 0

    def fetch(self) -> Dict:
        """
        Fetch a random Bitcoin news headline

        Returns:
            dict: {
                "headline": str,
                "timestamp": str (ISO format),
                "source": str,
                "expected_sentiment": str  # For testing
            }
        """
        self.news_counter += 1

        # 40% bullish, 40% bearish, 20% neutral
        rand = random.random()
        if rand < 0.4:
            template = random.choice(self.bullish_templates)
            expected_sentiment = "bullish"
        elif rand < 0.8:
            template = random.choice(self.bearish_templates)
            expected_sentiment = "bearish"
        else:
            template = random.choice(self.neutral_templates)
            expected_sentiment = "neutral"

        # Generate random values for template placeholders
        price = random.randint(60, 80)
        amount = random.randint(500, 5000)
        dom = random.randint(45, 55)
        pct = random.randint(1, 5)
        low = price - 2
        high = price + 2

        headline = template.format(
            price=price,
            amount=amount,
            dom=dom,
            pct=pct,
            low=low,
            high=high
        )

        return {
            "headline": headline,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "mock_news_api",
            "expected_sentiment": expected_sentiment,
            "news_id": f"news_{self.news_counter:04d}"
        }

    def fetch_batch(self, count: int = 5) -> list:
        """Fetch multiple news items"""
        return [self.fetch() for _ in range(count)]


if __name__ == "__main__":
    # Test the news fetcher
    fetcher = NewsFetcher()

    print("Bitcoin News Fetcher - Test Output\n")
    print("=" * 80)

    for i in range(10):
        news = fetcher.fetch()
        print(f"\n[{i+1}] {news['headline']}")
        print(f"    Expected: {news['expected_sentiment'].upper()}")
        print(f"    Time: {news['timestamp']}")
