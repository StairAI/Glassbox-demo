"""
Bitcoin Investment Agent
Main decision-making agent with Glass Box Protocol integration
"""

import random
from datetime import datetime, timezone
from typing import Dict, Optional
from state_machine import AgentState


class BitcoinAgent:
    """
    Bitcoin investment agent that analyzes news sentiment
    and generates trading signals with Glass Box reasoning traces
    """

    def __init__(self, agent_id: str, initial_btc_price: float = 70000):
        """
        Initialize Bitcoin agent

        Args:
            agent_id: Agent's RAID address
            initial_btc_price: Starting BTC price for demo
        """
        self.agent_id = agent_id
        self.btc_price = initial_btc_price
        self.state = AgentState()
        self.news_history = []
        self.signal_count = 0

        print(f"[Bitcoin Agent] Initialized with ID: {agent_id}")
        print(f"[Bitcoin Agent] Initial BTC price: ${self.btc_price:,.0f}")

    def process_news(self, news: Dict, sentiment_analysis: Dict) -> Optional[Dict]:
        """
        Process news item and generate signal if thresholds met

        Args:
            news: News item dict
            sentiment_analysis: Sentiment analysis result

        Returns:
            Signal dict if generated, None otherwise
        """
        # Add to news history
        self.news_history.append({
            "headline": news["headline"],
            "sentiment": sentiment_analysis["sentiment"],
            "confidence": sentiment_analysis["confidence"],
            "signal": sentiment_analysis["signal"],
            "timestamp": news["timestamp"]
        })

        # Update state machine
        self.state.update_from_news(news, sentiment_analysis, self.news_history)

        # Simulate BTC price movement (for demo)
        self._simulate_price_movement(sentiment_analysis["sentiment"])

        # Check if should generate signal
        if self.state.should_generate_signal():
            signal = self._generate_signal()
            self.state.add_signal_to_history(signal)
            return signal

        return None

    def _simulate_price_movement(self, sentiment: float):
        """
        Simulate BTC price movement based on sentiment

        In production, this would fetch real price from an API
        """
        # Random walk with sentiment bias
        base_change = random.uniform(-500, 500)
        sentiment_influence = sentiment * 1000
        price_change = base_change + sentiment_influence

        self.btc_price += price_change
        self.btc_price = max(50000, self.btc_price)  # Floor at $50k

    def _generate_signal(self) -> Dict:
        """
        Generate trading signal based on current state

        Returns:
            dict: {
                "signal_id": str,
                "asset": str,
                "direction": str (LONG/SHORT),
                "entry_price": float,
                "stop_loss": float,
                "take_profit": float,
                "position_size": str,
                "confidence": float,
                "timestamp": str
            }
        """
        self.signal_count += 1

        # Determine direction from sentiment
        if self.state.market_sentiment > 0:
            direction = "LONG"
            stop_loss_pct = 0.95  # -5%
            take_profit_pct = 1.08  # +8%
        else:
            direction = "SHORT"
            stop_loss_pct = 1.05  # +5%
            take_profit_pct = 0.92  # -8%

        entry_price = self.btc_price
        stop_loss = entry_price * stop_loss_pct
        take_profit = entry_price * take_profit_pct

        # Position sizing based on confidence
        if self.state.confidence > 0.9:
            position_size = "full position (100%)"
        elif self.state.confidence > 0.8:
            position_size = "large position (75%)"
        elif self.state.confidence > 0.7:
            position_size = "medium position (50%)"
        else:
            position_size = "small position (25%)"

        signal_id = f"sig_btc_{direction.lower()}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

        signal = {
            "signal_id": signal_id,
            "asset": "BTC",
            "direction": direction,
            "entry_price": round(entry_price, 2),
            "stop_loss": round(stop_loss, 2),
            "take_profit": round(take_profit, 2),
            "position_size": position_size,
            "confidence": round(self.state.confidence, 3),
            "risk_reward_ratio": round(abs(take_profit - entry_price) / abs(entry_price - stop_loss), 2),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        return signal

    def generate_reasoning_steps(self, news: Dict, sentiment_analysis: Dict, signal: Optional[Dict]) -> list:
        """
        Generate reasoning steps for Glass Box trace

        Args:
            news: News item
            sentiment_analysis: Sentiment analysis result
            signal: Generated signal (or None)

        Returns:
            list of (behavior, data, tool, params) tuples
        """
        steps = []

        # Step 1: Observing
        steps.append((
            "Observing",
            f"Ingested news: '{news['headline'][:80]}...' Sentiment: {sentiment_analysis['sentiment']:+.2f} ({sentiment_analysis['signal']})",
            None,
            None
        ))

        # Step 2: Planning
        planning_text = f"""Multi-step analysis:
1. Update news stream with new item (total: {len(self.news_history)} items)
2. Calculate rolling average sentiment (last 5 items)
3. Determine sentiment trend (RISING/FALLING/STABLE)
4. Calculate confidence score from keyword matches
5. Check execution criteria (|sentiment| > 0.5 AND confidence > 0.7)
6. Generate position sizing based on confidence level"""

        steps.append(("Planning", planning_text, None, None))

        # Step 3: Reasoning
        sentiment_direction = "bullish" if self.state.market_sentiment > 0 else "bearish" if self.state.market_sentiment < 0 else "neutral"

        reasoning_text = f"""Market analysis:
- Rolling average sentiment: {self.state.market_sentiment:+.2f} ({sentiment_direction.upper()})
- Current confidence: {self.state.confidence:.2f}
- Sentiment trend: {self.state.sentiment_trend}
- Latest news signal: {sentiment_analysis['signal']}

Risk assessment:
- Current BTC price: ${self.btc_price:,.0f}
- News stream consistency: {len([h for h in self.news_history[-5:] if h['signal'] == sentiment_analysis['signal']])} of 5 aligned

Decision logic:
- Threshold check: |{self.state.market_sentiment:.2f}| > 0.5? {abs(self.state.market_sentiment) > 0.5}
- Confidence check: {self.state.confidence:.2f} > 0.7? {self.state.confidence > 0.7}
- Execute signal: {self.state.should_generate_signal()}"""

        steps.append(("Reasoning", reasoning_text, None, None))

        # Step 4: Acting (if signal generated)
        if signal:
            acting_text = f"Generating {signal['direction']} signal for subscribers"

            steps.append((
                "Acting",
                acting_text,
                "signal_generator",
                {
                    "asset": signal["asset"],
                    "direction": signal["direction"],
                    "entry_price": signal["entry_price"],
                    "stop_loss": signal["stop_loss"],
                    "take_profit": signal["take_profit"],
                    "position_size": signal["position_size"],
                    "risk_reward_ratio": signal["risk_reward_ratio"]
                }
            ))
        else:
            steps.append((
                "Acting",
                "Thresholds not met. Continuing to monitor market conditions.",
                None,
                None
            ))

        return steps

    def get_context_snapshot(self) -> Dict:
        """
        Get current context for trace encryption

        Returns:
            dict: Agent's internal state
        """
        return {
            "current_position": self.state.current_position,
            "market_sentiment": self.state.market_sentiment,
            "confidence": self.state.confidence,
            "sentiment_trend": self.state.sentiment_trend,
            "btc_price": self.btc_price,
            "news_history_count": len(self.news_history),
            "total_signals_generated": self.signal_count,
            "last_5_news_signals": [h["signal"] for h in self.news_history[-5:]]
        }


if __name__ == "__main__":
    # Test the Bitcoin agent
    import sys
    sys.path.append('../data_sources')
    from news_fetcher import NewsFetcher
    from sentiment_analyzer import SentimentAnalyzer

    print("\nBitcoin Investment Agent - Test Output\n")
    print("=" * 80)

    # Initialize components
    agent = BitcoinAgent(
        agent_id="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        initial_btc_price=70000
    )

    fetcher = NewsFetcher()
    analyzer = SentimentAnalyzer()

    print("\nProcessing 10 news items...\n")

    signals_generated = 0

    for i in range(10):
        print(f"\n--- Cycle {i+1} ---")

        # Fetch and analyze news
        news = fetcher.fetch()
        sentiment = analyzer.analyze(news)

        print(f"News: {news['headline'][:60]}...")
        print(f"Sentiment: {sentiment['sentiment']:+.2f} ({sentiment['signal']}) | Confidence: {sentiment['confidence']:.2f}")

        # Process through agent
        signal = agent.process_news(news, sentiment)

        if signal:
            signals_generated += 1
            print(f"\n🚨 SIGNAL GENERATED!")
            print(f"   {signal['direction']} {signal['asset']} @ ${signal['entry_price']:,.0f}")
            print(f"   Stop-Loss: ${signal['stop_loss']:,.0f} | Take-Profit: ${signal['take_profit']:,.0f}")
            print(f"   Position Size: {signal['position_size']}")
            print(f"   Risk/Reward: {signal['risk_reward_ratio']}")
        else:
            state_summary = agent.state.get_state_summary()
            print(f"   No signal (sentiment: {state_summary['market_sentiment']:+.2f}, confidence: {state_summary['confidence']:.2f})")

    print("\n" + "=" * 80)
    print(f"Test Summary:")
    print(f"  News items processed: 10")
    print(f"  Signals generated: {signals_generated}")
    print(f"  Final BTC price: ${agent.btc_price:,.0f}")
    print(f"  Final market sentiment: {agent.state.market_sentiment:+.2f}")
