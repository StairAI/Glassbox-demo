"""
Agent B: Investment Suggestion Agent

Consumes sentiment signals from Agent A and current BTC price.
Generates 24h BTC price predictions with confidence scores.
RAID scoring based on prediction accuracy (MAE, direction accuracy, consistency).

Signal Output Format:
{
    "agent_id": "agent_b",
    "timestamp": "2024-...",
    "predicted_btc_price": float,
    "current_btc_price": float,
    "predicted_change_pct": float,
    "confidence": 0.0 to 1.0,
    "prediction_horizon_hours": 24,
    "sentiment_influence": float,  # How much sentiment affected prediction
    "raid_score": 0.0 to 1.0,      # Current RAID score
    "prediction_id": str            # For tracking validation
}
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import json
import random

# Handle imports for both standalone and package usage
try:
    from ..state.state_machine import create_agent_b_state_machine
    from ..scoring.prediction_tracker import PredictionTracker
    from ..data_sources.price_fetcher import PriceFetcher
except (ImportError, ValueError):
    # Standalone execution or being imported from runner
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from state.state_machine import create_agent_b_state_machine
    from scoring.prediction_tracker import PredictionTracker
    from data_sources.price_fetcher import PriceFetcher


class AgentB:
    """
    Investment Suggestion Agent

    Generates BTC price predictions based on sentiment + technical analysis.
    Tracks prediction accuracy via RAID scoring.
    """

    def __init__(
        self,
        agent_id: str = "agent_b",
        price_fetcher: Optional[PriceFetcher] = None,
        output_dir: Optional[Path] = None
    ):
        """
        Initialize Agent B

        Args:
            agent_id: Agent identifier
            price_fetcher: Price data source (shared across agents)
            output_dir: Directory to store signals
        """
        self.agent_id = agent_id

        if output_dir is None:
            output_dir = Path(__file__).parent.parent.parent / "output" / "signals"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # State machine
        self.state = create_agent_b_state_machine(agent_id)

        # Price fetcher (shared resource)
        self.price_fetcher = price_fetcher if price_fetcher else PriceFetcher()

        # Prediction tracker (RAID scoring)
        self.tracker = PredictionTracker(agent_id)

        # Prediction history
        self.prediction_history = []

        # Model parameters (simulated ML model weights)
        self.sentiment_weight = 0.65  # How much sentiment influences prediction
        self.momentum_weight = 0.35   # How much recent price momentum influences

        print(f"[{self.agent_id}] Agent B initialized")

    def consume_sentiment_signal(self, sentiment_signal: Dict):
        """
        Consume sentiment signal from Agent A

        Args:
            sentiment_signal: Sentiment signal dict from Agent A
        """
        self.state.transition("ANALYZING", "Processing sentiment signal from Agent A")

        # Store sentiment in state metadata
        self.state.update_metadata("sentiment", sentiment_signal["overall_sentiment"])
        self.state.update_metadata("sentiment_trend", sentiment_signal["sentiment_trend"])
        self.state.update_metadata("sentiment_volatility", sentiment_signal["sentiment_volatility"])

    def generate_prediction(self, sentiment_signal: Dict) -> Dict:
        """
        Generate BTC price prediction based on sentiment + price data

        Args:
            sentiment_signal: Sentiment signal from Agent A

        Returns:
            dict: Prediction signal
        """
        self.state.transition("PREDICTING", "Generating 24h BTC price prediction")

        # Get current price
        price_data = self.price_fetcher.fetch_prices()
        current_price = price_data["btc"]["price"]
        price_change_24h = price_data["btc"]["change_24h_pct"]
        current_volatility = price_data["btc"]["volatility"]

        # Extract sentiment
        sentiment = sentiment_signal["overall_sentiment"]
        sentiment_volatility = sentiment_signal["sentiment_volatility"]

        # Prediction model (simplified)
        # Real implementation would use ML model, but we simulate intelligent behavior

        # 1. Sentiment component
        # Sentiment ranges from -1.0 to +1.0, scale to price change %
        sentiment_influence = sentiment * self.sentiment_weight * 0.10  # Up to ±6.5% from sentiment

        # 2. Momentum component
        # Use recent 24h price change as momentum indicator
        momentum_influence = (price_change_24h / 100) * self.momentum_weight

        # 3. Random noise (market unpredictability)
        noise = random.gauss(0, current_volatility * 0.3)

        # Combine components
        predicted_change_pct = (sentiment_influence + momentum_influence + noise) * 100

        # Apply bounds (realistic daily BTC movement: -15% to +15%)
        predicted_change_pct = max(-15.0, min(15.0, predicted_change_pct))

        predicted_price = current_price * (1 + predicted_change_pct / 100)

        # Calculate confidence
        # Higher confidence when:
        # - Sentiment is strong (high absolute value)
        # - Sentiment volatility is low
        # - Recent RAID score is high
        base_confidence = 0.55
        sentiment_contribution = abs(sentiment) * 0.15
        volatility_penalty = sentiment_volatility * 0.10

        latest_raid = self.tracker.get_latest_raid_score()
        raid_contribution = latest_raid["raid_score"] * 0.15 if latest_raid else 0.05

        confidence = base_confidence + sentiment_contribution + raid_contribution - volatility_penalty
        confidence = max(0.3, min(0.95, confidence))

        # Generate prediction ID
        prediction_id = f"pred_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

        # Record prediction for future validation
        self.tracker.record_prediction(
            prediction_id=prediction_id,
            predicted_price=predicted_price,
            current_price=current_price,
            confidence=confidence,
            prediction_horizon_hours=24,
            metadata={
                "sentiment": sentiment,
                "sentiment_trend": sentiment_signal["sentiment_trend"],
                "price_change_24h": price_change_24h
            }
        )

        # Update state
        self.state.update_metadata("predicted_price", predicted_price)
        self.state.update_metadata("confidence", confidence)
        self.state.update_metadata("prediction_id", prediction_id)

        return {
            "agent_id": self.agent_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "predicted_btc_price": round(predicted_price, 2),
            "current_btc_price": round(current_price, 2),
            "predicted_change_pct": round(predicted_change_pct, 2),
            "confidence": round(confidence, 3),
            "prediction_horizon_hours": 24,
            "sentiment_influence": round(sentiment_influence * 100, 2),
            "prediction_id": prediction_id
        }

    def validate_predictions(self):
        """
        Validate previous predictions with actual outcomes (simulated)

        In production, this would check predictions made 24h ago against actual prices.
        For demo, we simulate validation with some randomness.
        """
        self.state.transition("VALIDATING", "Checking previous prediction accuracy")

        # Get recent unvalidated predictions
        recent_predictions = [p for p in self.tracker.get_prediction_history(limit=5) if not p["validated"]]

        if not recent_predictions:
            return

        # Simulate validation (in real system, wait 24h and check actual price)
        for pred in recent_predictions:
            # Simulate actual price (close to predicted but with some error)
            predicted = pred["predicted_price"]
            current = pred["current_price"]

            # Actual price will be somewhere between predicted and a random walk
            error_factor = random.gauss(0, 0.03)  # 3% average prediction error
            actual_price = predicted * (1 + error_factor)

            # Validate prediction
            self.tracker.validate_prediction(pred["prediction_id"], actual_price)

    def calculate_raid_score(self) -> Dict:
        """
        Calculate current RAID score based on prediction performance

        Returns:
            dict: RAID score breakdown
        """
        self.state.transition("VALIDATING", "Calculating RAID score")

        raid_score = self.tracker.calculate_raid_score(lookback_hours=168)  # 7 days

        self.state.update_metadata("raid_score", raid_score["raid_score"])
        self.state.update_metadata("mae_pct", raid_score["mae_pct"])
        self.state.update_metadata("direction_accuracy", raid_score["direction_accuracy"])

        return raid_score

    def publish_signal(self, prediction: Dict, raid_score: Optional[Dict] = None):
        """
        Publish prediction signal to file

        Args:
            prediction: Prediction signal
            raid_score: Optional RAID score to include
        """
        self.state.transition("PUBLISHING", "Publishing prediction signal")

        # Add RAID score to signal
        if raid_score:
            prediction["raid_score"] = raid_score["raid_score"]
            prediction["raid_metrics"] = {
                "accuracy_score": raid_score["accuracy_score"],
                "direction_score": raid_score["direction_score"],
                "consistency_score": raid_score["consistency_score"],
                "mae_pct": raid_score["mae_pct"],
                "direction_accuracy": raid_score["direction_accuracy"]
            }
        else:
            prediction["raid_score"] = 0.5  # Neutral score if no history

        # Write to JSONL file
        signal_file = self.output_dir / f"{self.agent_id}_signals.jsonl"

        with open(signal_file, 'a') as f:
            f.write(json.dumps(prediction) + "\n")

        print(f"[{self.agent_id}] Published signal: BTC ${prediction['predicted_btc_price']:,.0f} "
              f"({prediction['predicted_change_pct']:+.2f}%), "
              f"confidence={prediction['confidence']:.1%}, "
              f"RAID={prediction['raid_score']:.3f}")

        # Store in history
        self.prediction_history.append(prediction)
        if len(self.prediction_history) > 50:
            self.prediction_history = self.prediction_history[-50:]

        # Return to MONITORING state
        self.state.transition("MONITORING", "Signal published, monitoring for next cycle")

    def run_cycle(self, sentiment_signal: Dict) -> Dict:
        """
        Execute one full prediction cycle

        Args:
            sentiment_signal: Sentiment signal from Agent A

        Returns:
            dict: Published prediction signal
        """
        # MONITORING → ANALYZING
        self.consume_sentiment_signal(sentiment_signal)

        # ANALYZING → PREDICTING
        prediction = self.generate_prediction(sentiment_signal)

        # PREDICTING → VALIDATING (validate previous predictions)
        self.validate_predictions()

        # VALIDATING → PUBLISHING
        raid_score = self.calculate_raid_score()

        # PUBLISHING → MONITORING
        self.publish_signal(prediction, raid_score)

        return prediction

    def get_latest_signal(self) -> Optional[Dict]:
        """Get most recent prediction signal"""
        return self.prediction_history[-1] if self.prediction_history else None

    def get_signal_history(self, limit: int = 10) -> List[Dict]:
        """Get recent prediction signals"""
        return self.prediction_history[-limit:]


if __name__ == "__main__":
    # Test Agent B
    print("\nAgent B: Investment Suggestion Agent - Test Output\n")
    print("=" * 80)

    # Initialize with shared price fetcher
    price_fetcher = PriceFetcher(initial_btc_price=70000)
    agent_b = AgentB(price_fetcher=price_fetcher)

    # Simulate sentiment signals from Agent A
    sentiment_signals = [
        {
            "agent_id": "agent_a",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_sentiment": 0.3,
            "sentiment_volatility": 0.2,
            "news_volume": 10,
            "bullish_ratio": 0.7,
            "sentiment_trend": "RISING",
            "key_topics": ["bullish", "neutral"]
        },
        {
            "agent_id": "agent_a",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_sentiment": 0.65,
            "sentiment_volatility": 0.15,
            "news_volume": 12,
            "bullish_ratio": 0.85,
            "sentiment_trend": "RISING",
            "key_topics": ["bullish"]
        },
        {
            "agent_id": "agent_a",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_sentiment": -0.4,
            "sentiment_volatility": 0.4,
            "news_volume": 8,
            "bullish_ratio": 0.3,
            "sentiment_trend": "FALLING",
            "key_topics": ["bearish", "neutral"]
        }
    ]

    print("\n1. Running prediction cycles with varying sentiment...\n")

    for i, sentiment in enumerate(sentiment_signals, 1):
        print(f"--- Cycle {i}: Sentiment {sentiment['overall_sentiment']:+.2f} ({sentiment['sentiment_trend']}) ---")

        # Run full cycle
        signal = agent_b.run_cycle(sentiment)

        print(f"Prediction: ${signal['predicted_btc_price']:,.0f} ({signal['predicted_change_pct']:+.2f}%)")
        print(f"Confidence: {signal['confidence']:.1%}")
        print(f"RAID Score: {signal['raid_score']:.3f}")
        print()

    print("-" * 80)

    print("\n2. Latest RAID Score Breakdown:")
    latest_raid = agent_b.tracker.get_latest_raid_score()
    if latest_raid:
        print(f"  Overall RAID: {latest_raid['raid_score']:.3f}")
        print(f"  ├─ Accuracy: {latest_raid['accuracy_score']:.3f} (MAE: {latest_raid['mae_pct']:.2f}%)")
        print(f"  ├─ Direction: {latest_raid['direction_score']:.3f} ({latest_raid['direction_accuracy']:.1%})")
        print(f"  └─ Consistency: {latest_raid['consistency_score']:.3f}")
        print(f"\n  Validated Predictions: {latest_raid['validated_predictions']}/{latest_raid['total_predictions']}")

    print("\n3. Prediction History:")
    for sig in agent_b.get_signal_history(limit=5):
        print(f"  [{sig['prediction_id']}] BTC ${sig['predicted_btc_price']:,.0f} "
              f"({sig['predicted_change_pct']:+.2f}%) | "
              f"Confidence: {sig['confidence']:.1%} | "
              f"RAID: {sig['raid_score']:.3f}")

    print("\n4. Current State Machine Status:")
    print(agent_b.state.get_state_description())

    print("\n" + "=" * 80)
    print("Test completed successfully!")
    print(f"Signals saved to: {agent_b.output_dir}")
