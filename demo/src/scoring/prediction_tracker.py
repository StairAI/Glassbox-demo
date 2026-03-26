"""
Prediction Tracker - Agent B RAID Scoring

Tracks Agent B's BTC price predictions and calculates RAID score based on:
- Prediction accuracy (Mean Absolute Error)
- Direction accuracy (up/down/sideways)
- Consistency over time
"""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional


class PredictionTracker:
    """
    Track Agent B's prediction performance and calculate RAID score

    RAID Score Components:
    - Accuracy (40%): Based on Mean Absolute Error (MAE)
    - Direction Accuracy (35%): Correct prediction of price movement direction
    - Consistency (25%): Standard deviation of errors (lower = better)
    """

    def __init__(self, agent_id: str = "agent_b", storage_dir: Optional[Path] = None):
        """
        Initialize prediction tracker

        Args:
            agent_id: Agent identifier
            storage_dir: Directory to store prediction history
        """
        self.agent_id = agent_id

        if storage_dir is None:
            storage_dir = Path(__file__).parent.parent.parent / "output" / "scoring"
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Prediction history: list of predictions with outcomes
        self.predictions = []

        # RAID score history
        self.raid_scores = []

        # Load persisted data
        self._load_data()

    def record_prediction(
        self,
        prediction_id: str,
        predicted_price: float,
        current_price: float,
        confidence: float,
        prediction_horizon_hours: int = 24,
        metadata: Optional[Dict] = None
    ):
        """
        Record a new price prediction

        Args:
            prediction_id: Unique identifier for this prediction
            predicted_price: Predicted BTC price
            current_price: Current BTC price at prediction time
            confidence: Agent's confidence (0.0 to 1.0)
            prediction_horizon_hours: Hours ahead for prediction
            metadata: Additional context
        """
        prediction = {
            "prediction_id": prediction_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "predicted_price": predicted_price,
            "current_price": current_price,
            "confidence": confidence,
            "prediction_horizon_hours": prediction_horizon_hours,
            "target_timestamp": (
                datetime.now(timezone.utc) + timedelta(hours=prediction_horizon_hours)
            ).isoformat(),
            "actual_price": None,  # To be filled when outcome is known
            "error_pct": None,
            "direction_correct": None,
            "validated": False,
            "metadata": metadata or {}
        }

        self.predictions.append(prediction)
        self._save_data()

        print(f"[{self.agent_id}] Recorded prediction: ${predicted_price:,.2f} "
              f"(current: ${current_price:,.2f}, confidence: {confidence:.2%})")

    def validate_prediction(
        self,
        prediction_id: str,
        actual_price: float
    ) -> Optional[Dict]:
        """
        Validate a prediction with actual outcome

        Args:
            prediction_id: Prediction to validate
            actual_price: Actual price at target timestamp

        Returns:
            dict: Validation results with error metrics
        """
        # Find prediction
        prediction = None
        for p in self.predictions:
            if p["prediction_id"] == prediction_id:
                prediction = p
                break

        if not prediction:
            print(f"[{self.agent_id}] Prediction {prediction_id} not found")
            return None

        if prediction["validated"]:
            print(f"[{self.agent_id}] Prediction {prediction_id} already validated")
            return prediction

        # Calculate error metrics
        predicted = prediction["predicted_price"]
        actual = actual_price
        current = prediction["current_price"]

        # Percentage error
        error_pct = abs((predicted - actual) / actual) * 100

        # Direction accuracy
        predicted_direction = "up" if predicted > current else ("down" if predicted < current else "sideways")
        actual_direction = "up" if actual > current else ("down" if actual < current else "sideways")
        direction_correct = predicted_direction == actual_direction

        # Update prediction
        prediction["actual_price"] = actual
        prediction["error_pct"] = error_pct
        prediction["direction_correct"] = direction_correct
        prediction["validated"] = True
        prediction["validated_at"] = datetime.now(timezone.utc).isoformat()

        self._save_data()

        print(f"[{self.agent_id}] Validated prediction {prediction_id}:")
        print(f"  Predicted: ${predicted:,.2f} | Actual: ${actual:,.2f}")
        print(f"  Error: {error_pct:.2f}% | Direction: {direction_correct}")

        return prediction

    def calculate_raid_score(self, lookback_hours: int = 168) -> Dict:
        """
        Calculate RAID score based on recent prediction performance

        Args:
            lookback_hours: Hours of history to consider (default: 7 days)

        Returns:
            dict: RAID score and component metrics
        """
        # Filter validated predictions within lookback window
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)

        validated_predictions = [
            p for p in self.predictions
            if p["validated"] and datetime.fromisoformat(p["timestamp"]) > cutoff_time
        ]

        if not validated_predictions:
            return {
                "raid_score": 0.5,  # Neutral score with no data
                "accuracy_score": 0.5,
                "direction_score": 0.5,
                "consistency_score": 0.5,
                "total_predictions": 0,
                "validated_predictions": 0,
                "mae_pct": 0.0,
                "direction_accuracy": 0.0,
                "error_std_dev": 0.0,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        # Calculate metrics

        # 1. Mean Absolute Error (MAE) - lower is better
        errors = [p["error_pct"] for p in validated_predictions]
        mae = sum(errors) / len(errors)

        # Accuracy score: 1.0 for 0% error, 0.0 for 20%+ error
        accuracy_score = max(0.0, min(1.0, 1.0 - (mae / 20.0)))

        # 2. Direction Accuracy - percentage of correct direction predictions
        direction_correct_count = sum(1 for p in validated_predictions if p["direction_correct"])
        direction_accuracy = direction_correct_count / len(validated_predictions)
        direction_score = direction_accuracy

        # 3. Consistency - lower standard deviation = more consistent
        if len(errors) > 1:
            mean_error = sum(errors) / len(errors)
            variance = sum((e - mean_error) ** 2 for e in errors) / len(errors)
            std_dev = variance ** 0.5

            # Consistency score: 1.0 for 0 std dev, 0.0 for 10%+ std dev
            consistency_score = max(0.0, min(1.0, 1.0 - (std_dev / 10.0)))
        else:
            std_dev = 0.0
            consistency_score = 1.0

        # Combined RAID score (weighted average)
        raid_score = (
            accuracy_score * 0.40 +
            direction_score * 0.35 +
            consistency_score * 0.25
        )

        result = {
            "raid_score": round(raid_score, 3),
            "accuracy_score": round(accuracy_score, 3),
            "direction_score": round(direction_score, 3),
            "consistency_score": round(consistency_score, 3),
            "total_predictions": len(self.predictions),
            "validated_predictions": len(validated_predictions),
            "mae_pct": round(mae, 2),
            "direction_accuracy": round(direction_accuracy, 3),
            "error_std_dev": round(std_dev, 2),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # Store RAID score history
        self.raid_scores.append(result)
        self._save_data()

        return result

    def get_prediction_history(self, limit: int = 10) -> List[Dict]:
        """Get recent predictions"""
        return self.predictions[-limit:]

    def get_raid_score_history(self, limit: int = 10) -> List[Dict]:
        """Get recent RAID scores"""
        return self.raid_scores[-limit:]

    def get_latest_raid_score(self) -> Optional[Dict]:
        """Get most recent RAID score"""
        return self.raid_scores[-1] if self.raid_scores else None

    def _save_data(self):
        """Persist prediction data to disk"""
        data_file = self.storage_dir / f"{self.agent_id}_predictions.json"

        data = {
            "agent_id": self.agent_id,
            "predictions": self.predictions[-100:],  # Keep last 100
            "raid_scores": self.raid_scores[-50:]    # Keep last 50
        }

        with open(data_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _load_data(self):
        """Load persisted prediction data"""
        data_file = self.storage_dir / f"{self.agent_id}_predictions.json"

        if not data_file.exists():
            return

        try:
            with open(data_file, 'r') as f:
                data = json.load(f)

            self.predictions = data.get("predictions", [])
            self.raid_scores = data.get("raid_scores", [])

            print(f"[{self.agent_id}] Loaded {len(self.predictions)} predictions, "
                  f"{len(self.raid_scores)} RAID scores")

        except Exception as e:
            print(f"[{self.agent_id}] Warning: Could not load data: {e}")


if __name__ == "__main__":
    # Test prediction tracker
    print("\nPrediction Tracker - Test Output\n")
    print("=" * 80)

    tracker = PredictionTracker()

    print("\n1. Recording predictions...")
    tracker.record_prediction(
        prediction_id="pred_001",
        predicted_price=71500,
        current_price=70000,
        confidence=0.78
    )

    tracker.record_prediction(
        prediction_id="pred_002",
        predicted_price=69800,
        current_price=70000,
        confidence=0.65
    )

    tracker.record_prediction(
        prediction_id="pred_003",
        predicted_price=72100,
        current_price=70000,
        confidence=0.82
    )

    print("\n2. Validating predictions with actual outcomes...")
    tracker.validate_prediction("pred_001", actual_price=71200)  # Close, correct direction
    tracker.validate_prediction("pred_002", actual_price=71000)  # Wrong direction
    tracker.validate_prediction("pred_003", actual_price=71800)  # Close, correct direction

    print("\n3. Calculating RAID score...")
    raid_score = tracker.calculate_raid_score()

    print(f"\nRAID Score Report:")
    print(f"  Overall RAID Score: {raid_score['raid_score']:.3f}")
    print(f"  ├─ Accuracy Score: {raid_score['accuracy_score']:.3f} (MAE: {raid_score['mae_pct']:.2f}%)")
    print(f"  ├─ Direction Score: {raid_score['direction_score']:.3f} ({raid_score['direction_accuracy']:.1%})")
    print(f"  └─ Consistency Score: {raid_score['consistency_score']:.3f} (StdDev: {raid_score['error_std_dev']:.2f}%)")
    print(f"\n  Validated Predictions: {raid_score['validated_predictions']}/{raid_score['total_predictions']}")

    print("\n4. Prediction History:")
    for pred in tracker.get_prediction_history(limit=5):
        if pred["validated"]:
            print(f"  [{pred['prediction_id']}] Predicted: ${pred['predicted_price']:,.0f} | "
                  f"Actual: ${pred['actual_price']:,.0f} | "
                  f"Error: {pred['error_pct']:.2f}% | "
                  f"Direction: {'✓' if pred['direction_correct'] else '✗'}")
        else:
            print(f"  [{pred['prediction_id']}] Predicted: ${pred['predicted_price']:,.0f} | "
                  f"Awaiting validation")

    print("\n" + "=" * 80)
    print("Test completed successfully!")
    print(f"Data saved to: {tracker.storage_dir}")
