#!/usr/bin/env python3
"""
Agent B: Investment Prediction Agent

This agent:
1. Accepts sentiment signals from Agent A + price signals as input
2. Fetches full data from Walrus
3. Analyzes with LLM to predict BTC price in 24h
4. Generates prediction with confidence and direction
5. Records all reasoning steps using ReasoningLedger SDK
6. Outputs InsightSignal with price prediction

This agent extends the abstract Agent base class.
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

from src.abstract import Agent, Signal, InsightSignal, PriceSignal
from src.reasoning_ledger.reasoning_ledger_sdk import ReasoningLedger
from src.storage.walrus_client import WalrusClient


class AgentBInvestment(Agent):
    """
    Agent B: BTC Price Prediction Agent

    Extends the abstract Agent base class to provide:
    - Standardized signal input/output
    - Automatic reasoning trace recording
    - LLM-based price prediction
    """

    def __init__(
        self,
        reasoning_ledger: Optional[ReasoningLedger] = None,
        walrus_client: Optional[WalrusClient] = None,
        api_key: Optional[str] = None,
        agent_version: str = "1.0"
    ):
        """
        Initialize Agent B.

        Args:
            reasoning_ledger: ReasoningLedger for storing reasoning traces
            walrus_client: WalrusClient for fetching signal data
            api_key: Anthropic API key
            agent_version: Agent version for traceability
        """
        # Initialize parent Agent class
        super().__init__(
            agent_id="agent_b_investment",
            agent_version=agent_version,
            reasoning_ledger=reasoning_ledger
        )

        # Agent-specific configuration
        self.walrus_client = walrus_client
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        # Initialize LLM client
        self._init_llm()

    def _init_llm(self):
        """Initialize Claude (Anthropic) client."""
        try:
            import anthropic
            self.llm_client = anthropic.Anthropic(api_key=self.api_key)
            self.llm_available = True
            print(f"  ✓ LLM initialized: Claude Sonnet 4.5")
        except ImportError:
            print("  WARNING: Anthropic package not installed. Using fallback prediction.")
            self.llm_available = False
        except Exception as e:
            print(f"  WARNING: Failed to initialize Claude: {e}. Using fallback prediction.")
            self.llm_available = False

    # ==================================================================================
    # CORE INTERFACE - Required by abstract Agent
    # ==================================================================================

    def process_signals(self, signals: List[Signal]) -> Dict[str, Any]:
        """
        Process sentiment + price signals and generate BTC price prediction.

        This is the core reasoning logic called by Agent.run().

        Args:
            signals: List of input signals (InsightSignals for sentiment + PriceSignals)

        Returns:
            Dict with price prediction and confidence
        """
        # Step 1: Separate and fetch signals
        sentiment_data = None
        price_data = None

        for signal in signals:
            if isinstance(signal, InsightSignal):
                # Fetch sentiment data from Walrus
                insight_data = signal.fetch_full_data(walrus_client=self.walrus_client)
                if insight_data.get("insight_type") == "sentiment":
                    sentiment_data = insight_data

            elif isinstance(signal, PriceSignal):
                # Fetch price data from Walrus
                price_data = signal.fetch_full_data(walrus_client=self.walrus_client)

        self.record_step(
            step_name="fetch_signal_data",
            description="Fetched sentiment and price data from Walrus",
            input_data={"signal_count": len(signals)},
            output_data={
                "has_sentiment": sentiment_data is not None,
                "has_price": price_data is not None
            }
        )

        # Validate we have required data
        if not price_data:
            raise ValueError("Missing price signal - cannot make prediction without current BTC price")

        # Step 2: Generate price prediction
        prediction = self._generate_prediction(sentiment_data, price_data)

        self.record_step(
            step_name="generate_prediction",
            description="Generated 24h BTC price prediction",
            input_data={
                "current_price": price_data.get("price_usd"),
                "has_sentiment": sentiment_data is not None
            },
            output_data=prediction,
            confidence=prediction.get("prediction_confidence", 0.7)
        )

        # Return output in format expected by Agent base class
        return {
            "prediction": prediction,
            "confidence": prediction.get("prediction_confidence", 0.7),
            "current_price": price_data.get("price_usd"),
            "predicted_price_24h": prediction.get("predicted_price_24h")
        }

    # ==================================================================================
    # OPTIONAL HOOKS - Override for custom behavior
    # ==================================================================================

    def validate_input(self, signals: List[Signal]) -> bool:
        """
        Validate that we have at least a price signal.

        Args:
            signals: Input signals

        Returns:
            True if valid, False otherwise
        """
        if not signals:
            return False

        # Check that we have at least one PriceSignal
        has_price_signal = any(isinstance(s, PriceSignal) for s in signals)

        if not has_price_signal:
            print("  WARNING: No PriceSignal found in input signals")
            return False

        return True

    def before_process(self, signals: List[Signal]) -> None:
        """
        Hook called before processing.

        Use this for initialization, logging, etc.
        """
        price_signals = [s for s in signals if isinstance(s, PriceSignal)]
        sentiment_signals = [s for s in signals if isinstance(s, InsightSignal)]

        print(f"  Price signals: {len(price_signals)}")
        print(f"  Sentiment signals: {len(sentiment_signals)}")
        print(f"  LLM available: {self.llm_available}")

    # ==================================================================================
    # PREDICTION LOGIC
    # ==================================================================================

    def _generate_prediction(
        self,
        sentiment_data: Optional[Dict],
        price_data: Dict
    ) -> Dict[str, Any]:
        """
        Generate BTC price prediction using LLM or fallback.

        Args:
            sentiment_data: Sentiment analysis from Agent A (optional)
            price_data: Current BTC price data from CoinGecko

        Returns:
            Dict with price prediction, confidence, and reasoning
        """
        if not self.llm_available:
            return self._fallback_prediction(sentiment_data, price_data)

        # Prepare context for LLM
        context = self._prepare_context(sentiment_data, price_data)
        prompt = self._create_prediction_prompt(context)

        try:
            # Call LLM
            response = self._call_claude(prompt)

            # Record LLM call
            self.record_llm_call(
                prompt=prompt[:500],  # Truncate for storage
                response=response[:500],
                model="claude-sonnet-4.5"
            )

            # Parse response
            prediction = self._parse_llm_response(response, price_data)

            return prediction

        except Exception as e:
            print(f"  WARNING: LLM prediction failed: {e}. Using fallback.")
            return self._fallback_prediction(sentiment_data, price_data)

    def _prepare_context(
        self,
        sentiment_data: Optional[Dict],
        price_data: Dict
    ) -> Dict[str, Any]:
        """
        Prepare context for LLM prediction.

        Args:
            sentiment_data: Sentiment analysis data
            price_data: Current price data

        Returns:
            Context dict with all relevant information
        """
        context = {
            "current_price": price_data.get("price_usd"),
            "price_change_24h": price_data.get("price_change_24h"),
            "volume_24h": price_data.get("volume_24h"),
            "market_cap": price_data.get("market_cap"),
            "timestamp": price_data.get("timestamp"),
            "has_sentiment": sentiment_data is not None
        }

        if sentiment_data:
            # Extract sentiment scores
            signal_value = sentiment_data.get("signal_value", {})
            sentiment_scores = signal_value.get("sentiment_scores", {})

            context["sentiment"] = {
                "overall_score": sentiment_scores.get("overall_sentiment", 0),
                "btc_score": sentiment_scores.get("BTC", 0),
                "confidence": sentiment_data.get("confidence", 0)
            }

        return context

    def _create_prediction_prompt(self, context: Dict[str, Any]) -> str:
        """
        Create LLM prompt for price prediction.

        Args:
            context: Context data

        Returns:
            Prompt string
        """
        current_price = context["current_price"]
        price_change = context.get("price_change_24h", 0)
        volume = context.get("volume_24h", 0)

        prompt = f"""You are a cryptocurrency price prediction AI analyzing Bitcoin (BTC).

CURRENT MARKET DATA:
- Current BTC Price: ${current_price:,.2f}
- 24h Price Change: {price_change:+.2f}%
- 24h Volume: ${volume:,.0f}
- Market Cap: ${context.get("market_cap", 0):,.0f}
"""

        if context.get("has_sentiment"):
            sentiment = context["sentiment"]
            prompt += f"""
SENTIMENT ANALYSIS:
- Overall Market Sentiment: {sentiment['overall_score']:.2f} (-1 = very bearish, +1 = very bullish)
- BTC-Specific Sentiment: {sentiment['btc_score']:.2f}
- Sentiment Confidence: {sentiment['confidence']:.2f}
"""

        prompt += """
TASK: Predict the BTC price 24 hours from now.

Analyze:
1. Recent price momentum (24h change)
2. Trading volume and market activity
3. Sentiment indicators (if available)
4. Overall market confidence

Provide your prediction in JSON format:
{
  "predicted_price_24h": <number>,
  "prediction_confidence": <0.0-1.0>,
  "direction": "<BULLISH|BEARISH|NEUTRAL>",
  "expected_return_pct": <percentage change>,
  "risk_level": "<LOW|MODERATE|HIGH>",
  "reasoning_summary": "<1-2 sentence explanation>"
}

Respond ONLY with the JSON object, no additional text."""

        return prompt

    def _call_claude(self, prompt: str) -> str:
        """
        Call Claude API for prediction.

        Args:
            prompt: Prediction prompt

        Returns:
            LLM response text
        """
        response = self.llm_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response.content[0].text

    def _parse_llm_response(
        self,
        response: str,
        price_data: Dict
    ) -> Dict[str, Any]:
        """
        Parse LLM response into prediction format.

        Args:
            response: Raw LLM response
            price_data: Current price data

        Returns:
            Prediction dict
        """
        try:
            # Extract JSON from response
            # Sometimes Claude wraps JSON in markdown code blocks
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:]
            if response_clean.startswith("```"):
                response_clean = response_clean[3:]
            if response_clean.endswith("```"):
                response_clean = response_clean[:-3]

            prediction = json.loads(response_clean.strip())

            # Add metadata
            prediction["asset"] = "BTC"
            prediction["current_price"] = price_data.get("price_usd")
            prediction["timestamp"] = datetime.now().isoformat()
            prediction["prediction_horizon_hours"] = 24
            prediction["signal_type"] = "price_prediction"

            return prediction

        except json.JSONDecodeError as e:
            print(f"  WARNING: Failed to parse LLM response as JSON: {e}")
            return self._fallback_prediction(None, price_data)

    def _fallback_prediction(
        self,
        sentiment_data: Optional[Dict],
        price_data: Dict
    ) -> Dict[str, Any]:
        """
        Fallback prediction when LLM is unavailable.

        Uses simple heuristics based on price momentum and sentiment.

        Args:
            sentiment_data: Sentiment data (optional)
            price_data: Current price data

        Returns:
            Prediction dict
        """
        current_price = price_data.get("price_usd", 0)
        price_change_24h = price_data.get("price_change_24h", 0)

        # Simple momentum-based prediction
        # Assume price will continue in current direction with some mean reversion
        momentum_factor = 0.5  # 50% of current trend continues
        predicted_change_pct = price_change_24h * momentum_factor

        # Adjust for sentiment if available
        if sentiment_data:
            signal_value = sentiment_data.get("signal_value", {})
            sentiment_scores = signal_value.get("sentiment_scores", {})
            btc_sentiment = sentiment_scores.get("BTC", 0)

            # Add sentiment influence (±1% for extreme sentiment)
            sentiment_influence = btc_sentiment * 1.0
            predicted_change_pct += sentiment_influence

        # Calculate predicted price
        predicted_price = current_price * (1 + predicted_change_pct / 100)

        # Determine direction
        if predicted_change_pct > 1:
            direction = "BULLISH"
            risk_level = "MODERATE"
        elif predicted_change_pct < -1:
            direction = "BEARISH"
            risk_level = "MODERATE"
        else:
            direction = "NEUTRAL"
            risk_level = "LOW"

        return {
            "signal_type": "price_prediction",
            "asset": "BTC",
            "current_price": current_price,
            "predicted_price_24h": round(predicted_price, 2),
            "prediction_confidence": 0.65,  # Lower confidence for fallback
            "direction": direction,
            "expected_return_pct": round(predicted_change_pct, 2),
            "risk_level": risk_level,
            "reasoning_summary": f"Momentum-based prediction: {price_change_24h:+.2f}% 24h trend with mean reversion",
            "timestamp": datetime.now().isoformat(),
            "prediction_horizon_hours": 24
        }
