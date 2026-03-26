"""
Text-Based State Machine for LLM Agents
Based on tech-design.md Section 7
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


class AgentState:
    """Text-based state machine optimized for LLM processing"""

    def __init__(self, state_file: str = None):
        """
        Initialize state machine

        Args:
            state_file: Path to state file (default: ../../output/state/agent_state.txt)
        """
        if state_file is None:
            current_dir = Path(__file__).parent
            state_dir = current_dir.parent.parent / "output" / "state"
            state_dir.mkdir(parents=True, exist_ok=True)
            state_file = state_dir / "agent_state.txt"

        self.state_file = Path(state_file)

        # Initialize default state if file doesn't exist
        if not self.state_file.exists():
            self._initialize_default_state()

        self.state_text = self.load_state()

        # Parse state into structured data
        self._parse_state()

    def _initialize_default_state(self):
        """Create default initial state"""
        default_state = """=== AGENT STATE ===
Timestamp: {timestamp}
Market Sentiment: 0.00 (NEUTRAL)
Signal Strength: NEUTRAL
Confidence: 0.00
Current Position: MONITORING

=== NEWS STREAM ===
Last 5 Headlines:
(empty - no news processed yet)

Average Sentiment: 0.00
Sentiment Trend: STABLE

=== SIGNAL HISTORY ===
(empty - no signals generated yet)
""".format(timestamp=datetime.now(timezone.utc).isoformat())

        with open(self.state_file, 'w') as f:
            f.write(default_state)

    def load_state(self) -> str:
        """Load current state as plaintext"""
        with open(self.state_file, 'r') as f:
            return f.read()

    def save_state(self, new_state_text: str):
        """Persist updated state"""
        with open(self.state_file, 'w') as f:
            f.write(new_state_text)
        self.state_text = new_state_text
        self._parse_state()

    def _parse_state(self):
        """Parse state text into structured attributes"""
        lines = self.state_text.split('\n')

        # Extract key metrics
        for line in lines:
            if 'Market Sentiment:' in line:
                parts = line.split(':')[1].strip().split(' ')
                self.market_sentiment = float(parts[0])
            elif 'Signal Strength:' in line:
                self.signal_strength = line.split(':')[1].strip()
            elif 'Confidence:' in line:
                self.confidence = float(line.split(':')[1].strip())
            elif 'Current Position:' in line:
                self.current_position = line.split(':')[1].strip()
            elif 'Average Sentiment:' in line:
                self.avg_sentiment = float(line.split(':')[1].strip())
            elif 'Sentiment Trend:' in line:
                self.sentiment_trend = line.split(':')[1].strip()

    def update_from_news(self, news: Dict, sentiment_analysis: Dict, news_history: List[Dict]):
        """
        Update state based on new news item

        Args:
            news: News item dict
            sentiment_analysis: Sentiment analysis result
            news_history: List of recent news with sentiment
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        sentiment = sentiment_analysis['sentiment']
        signal = sentiment_analysis['signal']

        # Calculate running average sentiment (last 5 items)
        recent_sentiments = [item['sentiment'] for item in news_history[-5:]]
        avg_sentiment = sum(recent_sentiments) / len(recent_sentiments) if recent_sentiments else 0.0

        # Determine sentiment trend
        if len(recent_sentiments) >= 3:
            first_half = recent_sentiments[:len(recent_sentiments)//2]
            second_half = recent_sentiments[len(recent_sentiments)//2:]
            avg_first = sum(first_half) / len(first_half)
            avg_second = sum(second_half) / len(second_half)

            if avg_second > avg_first + 0.1:
                trend = "RISING"
            elif avg_second < avg_first - 0.1:
                trend = "FALLING"
            else:
                trend = "STABLE"
        else:
            trend = "STABLE"

        # Calculate confidence
        confidence = sentiment_analysis['confidence']

        # Format recent news
        news_lines = []
        for i, item in enumerate(news_history[-5:], 1):
            headline_short = item['headline'][:60] + "..." if len(item['headline']) > 60 else item['headline']
            news_lines.append(f"  [{i}] {item['signal']:8} ({item['sentiment']:+.2f}) - {headline_short}")

        if not news_lines:
            news_lines = ["  (none)"]

        # Build new state
        new_state = f"""=== AGENT STATE ===
Timestamp: {timestamp}
Market Sentiment: {avg_sentiment:+.2f} ({signal})
Signal Strength: {signal}
Confidence: {confidence:.2f}
Current Position: MONITORING

=== NEWS STREAM ===
Last 5 Headlines:
{chr(10).join(news_lines)}

Average Sentiment: {avg_sentiment:+.2f}
Sentiment Trend: {trend}

=== SIGNAL HISTORY ===
{self._get_signal_history_text()}
"""

        self.save_state(new_state)

    def add_signal_to_history(self, signal_data: Dict):
        """Add a generated signal to history"""
        timestamp = datetime.now(timezone.utc).isoformat()

        signal_line = (
            f"[{timestamp}] {signal_data['direction']:5} signal @ ${signal_data['entry_price']:,.0f} "
            f"(SL: ${signal_data['stop_loss']:,.0f}, TP: ${signal_data['take_profit']:,.0f})"
        )

        # Load current state
        lines = self.state_text.split('\n')

        # Find signal history section and append
        in_signal_section = False
        new_lines = []
        for line in lines:
            if '=== SIGNAL HISTORY ===' in line:
                in_signal_section = True
                new_lines.append(line)
                continue

            if in_signal_section:
                if line.strip() == '(empty - no signals generated yet)':
                    new_lines.append(signal_line)
                    continue
                elif line.startswith('==='):
                    # End of signal section, insert before next section
                    new_lines.insert(-1, signal_line)
                    new_lines.append(line)
                    in_signal_section = False
                    continue

            new_lines.append(line)

        # If still in signal section (it's the last section)
        if in_signal_section:
            new_lines.append(signal_line)

        self.save_state('\n'.join(new_lines))

    def _get_signal_history_text(self) -> str:
        """Extract signal history from current state"""
        lines = self.state_text.split('\n')
        in_signal_section = False
        signal_lines = []

        for line in lines:
            if '=== SIGNAL HISTORY ===' in line:
                in_signal_section = True
                continue
            if in_signal_section:
                if line.startswith('==='):
                    break
                if line.strip() and line.strip() != '(empty - no signals generated yet)':
                    signal_lines.append(line)

        return '\n'.join(signal_lines) if signal_lines else "(empty - no signals generated yet)"

    def should_generate_signal(self) -> bool:
        """
        Determine if conditions are met to generate a trading signal

        Threshold: |sentiment| > 0.5 AND confidence > 0.7
        """
        return abs(self.market_sentiment) > 0.5 and self.confidence > 0.7

    def get_state_summary(self) -> Dict:
        """Get structured summary of current state"""
        return {
            "market_sentiment": self.market_sentiment,
            "signal_strength": self.signal_strength,
            "confidence": self.confidence,
            "current_position": self.current_position,
            "sentiment_trend": self.sentiment_trend,
            "should_signal": self.should_generate_signal()
        }


if __name__ == "__main__":
    # Test the state machine
    print("\nAgent State Machine - Test Output\n")
    print("=" * 80)

    # Initialize state
    state = AgentState()

    print("1. Initial state:")
    print(state.state_text)

    print("\n" + "=" * 80)
    print("2. Simulating news updates...\n")

    # Simulate processing 3 news items
    news_history = []

    for i in range(3):
        mock_news = {
            "headline": f"Bitcoin {'surges' if i % 2 == 0 else 'drops'} in volatile trading session",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        mock_sentiment = {
            "sentiment": 0.7 if i % 2 == 0 else -0.6,
            "confidence": 0.8,
            "signal": "BULLISH" if i % 2 == 0 else "BEARISH"
        }

        news_history.append({
            "headline": mock_news["headline"],
            "sentiment": mock_sentiment["sentiment"],
            "signal": mock_sentiment["signal"]
        })

        state.update_from_news(mock_news, mock_sentiment, news_history)

        print(f"Processed news {i+1}: {mock_news['headline'][:50]}...")
        summary = state.get_state_summary()
        print(f"  Market Sentiment: {summary['market_sentiment']:+.2f}")
        print(f"  Confidence: {summary['confidence']:.2f}")
        print(f"  Should Signal: {summary['should_signal']}")

    print("\n" + "=" * 80)
    print("3. Final state:")
    print(state.state_text)
