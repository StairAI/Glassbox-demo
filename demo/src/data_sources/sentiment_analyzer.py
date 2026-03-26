"""
Sentiment Analyzer for Bitcoin News
Simple keyword-based sentiment analysis
"""

import re
from typing import Dict, List


class SentimentAnalyzer:
    """Analyze news sentiment using keyword matching"""

    def __init__(self):
        # Bullish keywords with weights
        self.bullish_keywords = {
            'surge': 0.9,
            'surges': 0.9,
            'rally': 0.8,
            'rallies': 0.8,
            'breakout': 0.9,
            'adoption': 0.7,
            'bullish': 1.0,
            'strength': 0.6,
            'accelerate': 0.7,
            'accelerates': 0.7,
            'record': 0.8,
            'inflows': 0.7,
            'acquire': 0.6,
            'acquires': 0.6,
            'momentum': 0.7,
            'break': 0.6,
            'breaks': 0.6,
            'high': 0.5,
            'resistance': 0.4,
            'rise': 0.6,
            'rises': 0.6,
            'double': 0.7,
            'doubles': 0.7,
            'hit': 0.5,
            'hits': 0.5
        }

        # Bearish keywords with weights
        self.bearish_keywords = {
            'drop': -0.8,
            'drops': -0.8,
            'fall': -0.8,
            'falls': -0.8,
            'crash': -1.0,
            'dump': -0.9,
            'regulation': -0.6,
            'regulatory': -0.6,
            'ban': -1.0,
            'bearish': -1.0,
            'concern': -0.6,
            'concerns': -0.6,
            'scrutiny': -0.7,
            'breach': -0.8,
            'tumble': -0.9,
            'tumbles': -0.9,
            'pressure': -0.5,
            'negative': -0.7,
            'uncertainty': -0.6,
            'fail': -0.7,
            'fails': -0.7,
            'weigh': -0.5,
            'weighs': -0.5,
            'struggle': -0.6,
            'struggles': -0.6
        }

        # Neutral/context keywords
        self.neutral_keywords = {
            'trade', 'trades', 'trading', 'market', 'bitcoin', 'btc',
            'analyst', 'analysts', 'volatility', 'range', 'level',
            'hold', 'holds', 'steady', 'consolidate', 'consolidates'
        }

    def analyze(self, news: Dict) -> Dict:
        """
        Analyze sentiment of news headline

        Args:
            news: dict with 'headline' key

        Returns:
            dict: {
                "sentiment": float (-1.0 to +1.0),
                "confidence": float (0.0 to 1.0),
                "matched_keywords": list,
                "signal": str ("BULLISH", "BEARISH", "NEUTRAL")
            }
        """
        headline = news.get('headline', '').lower()

        # Tokenize (simple split)
        words = re.findall(r'\b\w+\b', headline)

        # Match keywords
        bullish_matches = []
        bearish_matches = []
        sentiment_score = 0.0

        for word in words:
            if word in self.bullish_keywords:
                weight = self.bullish_keywords[word]
                bullish_matches.append((word, weight))
                sentiment_score += weight
            elif word in self.bearish_keywords:
                weight = self.bearish_keywords[word]
                bearish_matches.append((word, weight))
                sentiment_score += weight

        # Normalize sentiment to [-1, 1]
        max_possible = 3.0  # Cap at 3 strong keywords
        sentiment = max(-1.0, min(1.0, sentiment_score / max_possible))

        # Calculate confidence based on keyword matches
        total_matches = len(bullish_matches) + len(bearish_matches)
        if total_matches == 0:
            confidence = 0.3  # Low confidence if no keywords matched
        elif total_matches == 1:
            confidence = 0.6  # Medium confidence for single keyword
        elif total_matches == 2:
            confidence = 0.8  # High confidence for two keywords
        else:
            confidence = 0.95  # Very high confidence for 3+ keywords

        # Determine discrete signal
        if sentiment > 0.3:
            signal = "BULLISH"
        elif sentiment < -0.3:
            signal = "BEARISH"
        else:
            signal = "NEUTRAL"

        return {
            "sentiment": round(sentiment, 3),
            "confidence": round(confidence, 3),
            "matched_keywords": {
                "bullish": bullish_matches,
                "bearish": bearish_matches
            },
            "signal": signal,
            "headline": news.get('headline', '')
        }

    def analyze_batch(self, news_list: List[Dict]) -> List[Dict]:
        """Analyze multiple news items"""
        return [self.analyze(news) for news in news_list]

    def calculate_aggregate_sentiment(self, analyses: List[Dict]) -> Dict:
        """
        Calculate aggregate sentiment from multiple analyses

        Args:
            analyses: list of analysis results

        Returns:
            dict: {
                "avg_sentiment": float,
                "avg_confidence": float,
                "signal": str,
                "trend": str ("RISING", "FALLING", "STABLE")
            }
        """
        if not analyses:
            return {
                "avg_sentiment": 0.0,
                "avg_confidence": 0.0,
                "signal": "NEUTRAL",
                "trend": "STABLE"
            }

        sentiments = [a['sentiment'] for a in analyses]
        confidences = [a['confidence'] for a in analyses]

        avg_sentiment = sum(sentiments) / len(sentiments)
        avg_confidence = sum(confidences) / len(confidences)

        # Determine trend (comparing first half to second half)
        if len(sentiments) >= 4:
            mid = len(sentiments) // 2
            first_half_avg = sum(sentiments[:mid]) / mid
            second_half_avg = sum(sentiments[mid:]) / (len(sentiments) - mid)

            if second_half_avg > first_half_avg + 0.1:
                trend = "RISING"
            elif second_half_avg < first_half_avg - 0.1:
                trend = "FALLING"
            else:
                trend = "STABLE"
        else:
            trend = "STABLE"

        # Aggregate signal
        if avg_sentiment > 0.3:
            signal = "BULLISH"
        elif avg_sentiment < -0.3:
            signal = "BEARISH"
        else:
            signal = "NEUTRAL"

        return {
            "avg_sentiment": round(avg_sentiment, 3),
            "avg_confidence": round(avg_confidence, 3),
            "signal": signal,
            "trend": trend,
            "num_items": len(analyses)
        }


if __name__ == "__main__":
    # Test the sentiment analyzer
    from news_fetcher import NewsFetcher

    fetcher = NewsFetcher()
    analyzer = SentimentAnalyzer()

    print("Sentiment Analyzer - Test Output\n")
    print("=" * 80)

    # Test with 10 news items
    analyses = []
    for i in range(10):
        news = fetcher.fetch()
        analysis = analyzer.analyze(news)

        print(f"\n[{i+1}] {news['headline']}")
        print(f"    Expected: {news['expected_sentiment'].upper()}")
        print(f"    Analysis: {analysis['signal']} (sentiment: {analysis['sentiment']:.2f}, confidence: {analysis['confidence']:.2f})")
        print(f"    Keywords: {len(analysis['matched_keywords']['bullish'])} bullish, {len(analysis['matched_keywords']['bearish'])} bearish")

        analyses.append(analysis)

    # Show aggregate
    print("\n" + "=" * 80)
    print("AGGREGATE SENTIMENT:")
    aggregate = analyzer.calculate_aggregate_sentiment(analyses)
    print(f"  Average: {aggregate['avg_sentiment']:.2f} ({aggregate['signal']})")
    print(f"  Confidence: {aggregate['avg_confidence']:.2f}")
    print(f"  Trend: {aggregate['trend']}")
