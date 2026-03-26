"""
Mock SUI Price Predictor
Generates mock SUI price predictions to feed into Agent C
"""

import random
from datetime import datetime, timezone
from typing import Dict


class SUIPredictorMock:
    """
    Mock SUI price prediction generator

    In production, this would be replaced by:
    - Agent B's actual SUI predictions
    - External ML models
    - Market analysis services

    For demo purposes, generates realistic mock predictions with configurable accuracy
    """

    def __init__(self, accuracy_bias: float = 0.7):
        """
        Initialize mock predictor

        Args:
            accuracy_bias: 0.0 to 1.0, higher = more accurate predictions
        """
        self.accuracy_bias = accuracy_bias

    def predict_sui_price(self, current_price: float, sentiment: float = 0.0) -> Dict:
        """
        Generate mock SUI price prediction for 24h ahead

        Args:
            current_price: Current SUI price in USD
            sentiment: Sentiment signal from Agent A (-1.0 to +1.0)

        Returns:
            dict: {
                "predicted_price": float,
                "confidence": float,
                "prediction_horizon_hours": int,
                "expected_change_pct": float,
                "sentiment_influence": float,
                "timestamp": str
            }
        """
        # Generate prediction with sentiment influence
        # Higher accuracy_bias = predictions closer to realistic outcomes

        # Base volatility (SUI is more volatile than BTC)
        base_volatility = 0.08  # ±8% typical daily movement

        # Sentiment influence on prediction (stronger than BTC due to smaller cap)
        sentiment_factor = sentiment * 0.15  # Up to ±15% from sentiment

        # Random component (reduced by accuracy_bias)
        random_noise = random.gauss(0, base_volatility * (1 - self.accuracy_bias))

        # Combined prediction
        total_change_pct = (random_noise + sentiment_factor) * 100
        predicted_price = current_price * (1 + total_change_pct / 100)

        # Confidence based on accuracy_bias and sentiment strength
        confidence = 0.5 + (self.accuracy_bias * 0.3) + (abs(sentiment) * 0.2)
        confidence = max(0.3, min(0.95, confidence))  # Clamp to [0.3, 0.95]

        return {
            "predicted_price": round(predicted_price, 4),
            "confidence": round(confidence, 3),
            "prediction_horizon_hours": 24,
            "expected_change_pct": round(total_change_pct, 2),
            "sentiment_influence": round(sentiment_factor * 100, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "current_price": round(current_price, 4)
        }

    def get_prediction_with_bounds(
        self,
        current_price: float,
        sentiment: float = 0.0
    ) -> Dict:
        """
        Generate prediction with confidence bounds

        Args:
            current_price: Current SUI price
            sentiment: Sentiment signal

        Returns:
            dict: Prediction with upper/lower bounds
        """
        prediction = self.predict_sui_price(current_price, sentiment)

        # Calculate confidence bounds (wider for lower confidence)
        confidence_range = (1 - prediction["confidence"]) * 0.15

        upper_bound = prediction["predicted_price"] * (1 + confidence_range)
        lower_bound = prediction["predicted_price"] * (1 - confidence_range)

        prediction["upper_bound"] = round(upper_bound, 4)
        prediction["lower_bound"] = round(lower_bound, 4)

        return prediction


if __name__ == "__main__":
    # Test the SUI predictor
    print("\nMock SUI Predictor - Test Output\n")
    print("=" * 80)

    predictor = SUIPredictorMock(accuracy_bias=0.7)

    print("\n1. Neutral Sentiment Prediction (sentiment = 0.0):")
    current_sui_price = 2.5
    prediction = predictor.get_prediction_with_bounds(current_sui_price, sentiment=0.0)
    print(f"   Current Price: ${prediction['current_price']:.4f}")
    print(f"   Predicted Price (24h): ${prediction['predicted_price']:.4f}")
    print(f"   Expected Change: {prediction['expected_change_pct']:+.2f}%")
    print(f"   Confidence: {prediction['confidence']:.1%}")
    print(f"   Bounds: ${prediction['lower_bound']:.4f} - ${prediction['upper_bound']:.4f}")

    print("\n2. Bullish Sentiment Prediction (sentiment = +0.7):")
    prediction = predictor.get_prediction_with_bounds(current_sui_price, sentiment=0.7)
    print(f"   Current Price: ${prediction['current_price']:.4f}")
    print(f"   Predicted Price (24h): ${prediction['predicted_price']:.4f}")
    print(f"   Expected Change: {prediction['expected_change_pct']:+.2f}%")
    print(f"   Sentiment Influence: {prediction['sentiment_influence']:+.2f}%")
    print(f"   Confidence: {prediction['confidence']:.1%}")
    print(f"   Bounds: ${prediction['lower_bound']:.4f} - ${prediction['upper_bound']:.4f}")

    print("\n3. Bearish Sentiment Prediction (sentiment = -0.6):")
    prediction = predictor.get_prediction_with_bounds(current_sui_price, sentiment=-0.6)
    print(f"   Current Price: ${prediction['current_price']:.4f}")
    print(f"   Predicted Price (24h): ${prediction['predicted_price']:.4f}")
    print(f"   Expected Change: {prediction['expected_change_pct']:+.2f}%")
    print(f"   Sentiment Influence: {prediction['sentiment_influence']:+.2f}%")
    print(f"   Confidence: {prediction['confidence']:.1%}")
    print(f"   Bounds: ${prediction['lower_bound']:.4f} - ${prediction['upper_bound']:.4f}")

    print("\n4. Testing Different Accuracy Levels:")
    for accuracy in [0.3, 0.5, 0.7, 0.9]:
        predictor_test = SUIPredictorMock(accuracy_bias=accuracy)
        pred = predictor_test.predict_sui_price(current_sui_price, sentiment=0.5)
        print(f"   Accuracy {accuracy:.1f}: Predicted ${pred['predicted_price']:.4f} "
              f"({pred['expected_change_pct']:+.2f}%), Confidence {pred['confidence']:.1%}")

    print("\n" + "=" * 80)
    print("Test completed successfully!")
