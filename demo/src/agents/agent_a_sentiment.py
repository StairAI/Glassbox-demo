#!/usr/bin/env python3
"""
Agent A: Sentiment Analysis Agent

This agent:
1. Accepts news signals as input (List[Signal])
2. Fetches full news data from Walrus
3. Analyzes sentiment with LLM
4. Generates sentiment scores for target tokens
5. Records all reasoning steps using ReasoningLedger SDK
6. Outputs InsightSignal with sentiment scores

This agent now extends the abstract Agent base class.
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from src.abstract import Agent, Signal, NewsSignal, InsightSignal
from src.reasoning_ledger.reasoning_ledger_sdk import ReasoningLedger
from src.storage.walrus_client import WalrusClient


class AgentASentiment(Agent):
    """
    Agent A: Sentiment Analysis for crypto news

    Extends the abstract Agent base class to provide:
    - Standardized signal input/output
    - Automatic reasoning trace recording
    - LLM-based sentiment analysis
    """

    def __init__(
        self,
        reasoning_ledger: Optional[ReasoningLedger] = None,
        walrus_client: Optional[WalrusClient] = None,
        target_tokens: Optional[List[str]] = None,
        api_key: Optional[str] = None,
        agent_version: str = "2.0"
    ):
        """
        Initialize Agent A.

        Args:
            reasoning_ledger: ReasoningLedger for storing reasoning traces
            walrus_client: WalrusClient for fetching news data
            target_tokens: List of tokens to analyze (e.g., ["BTC", "ETH", "SUI"])
            api_key: Anthropic API key
            agent_version: Agent version for traceability
        """
        # Initialize parent Agent class
        super().__init__(
            agent_id="agent_a_sentiment",
            agent_version=agent_version,
            reasoning_ledger=reasoning_ledger
        )

        # Agent-specific configuration
        self.walrus_client = walrus_client
        self.target_tokens = target_tokens or ["BTC", "ETH"]
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
            print("  WARNING: Anthropic package not installed. Using fallback sentiment.")
            self.llm_available = False
        except Exception as e:
            print(f"  WARNING: Failed to initialize Claude: {e}. Using fallback sentiment.")
            self.llm_available = False

    # ==================================================================================
    # CORE INTERFACE - Required by abstract Agent
    # ==================================================================================

    def process_signals(self, signals: List[Signal]) -> Dict[str, Any]:
        """
        Process news signals and generate sentiment scores.

        This is the core reasoning logic called by Agent.run().

        Args:
            signals: List of input signals (expected to be NewsSignals)

        Returns:
            Dict with sentiment scores and confidence
        """
        # Step 1: Fetch news data from signals
        all_articles = []
        for signal in signals:
            if isinstance(signal, NewsSignal):
                # Fetch full news data
                news_data = signal.fetch_full_data(walrus_client=self.walrus_client)
                articles = news_data.get('articles', [])
                all_articles.extend(articles)

        self.record_step(
            step_name="fetch_news_data",
            description="Fetched news articles from Walrus",
            input_data={"signal_count": len(signals)},
            output_data={"articles_count": len(all_articles)}
        )

        # Step 2: Analyze sentiment
        sentiment_scores = self._analyze_sentiment(all_articles)

        self.record_step(
            step_name="analyze_sentiment",
            description=f"Analyzed sentiment for {len(self.target_tokens)} tokens",
            input_data={
                "target_tokens": self.target_tokens,
                "articles_count": len(all_articles)
            },
            output_data=sentiment_scores,
            confidence=sentiment_scores.get("overall_confidence", 0.8)
        )

        # Return output in format expected by Agent base class
        return {
            "sentiment_scores": sentiment_scores,
            "confidence": sentiment_scores.get("overall_confidence", 0.8),
            "tokens_analyzed": self.target_tokens,
            "articles_count": len(all_articles)
        }

    # ==================================================================================
    # OPTIONAL HOOKS - Override for custom behavior
    # ==================================================================================

    def validate_input(self, signals: List[Signal]) -> bool:
        """
        Validate that we have news signals to process.

        Args:
            signals: Input signals

        Returns:
            True if valid, False otherwise
        """
        if not signals:
            return False

        # Check that at least one signal is a NewsSignal
        has_news_signal = any(isinstance(s, NewsSignal) for s in signals)

        if not has_news_signal:
            print("  WARNING: No NewsSignal found in input signals")
            return False

        return True

    def before_process(self, signals: List[Signal]) -> None:
        """
        Hook called before processing.

        Use this for initialization, loading state, etc.
        """
        print(f"  Target tokens: {', '.join(self.target_tokens)}")
        print(f"  LLM available: {self.llm_available}")

    # ==================================================================================
    # SENTIMENT ANALYSIS LOGIC
    # ==================================================================================

    def _analyze_sentiment(self, articles: List[Dict]) -> Dict[str, Any]:
        """
        Analyze sentiment of news articles using LLM or fallback.

        Args:
            articles: List of news articles

        Returns:
            Dict with sentiment scores for each currency
        """
        if not self.llm_available:
            return self._fallback_sentiment(articles)

        # Prepare prompt
        articles_text = self._format_articles_for_llm(articles)
        prompt = self._create_sentiment_prompt(articles_text)

        try:
            # Call LLM
            response = self._call_claude(prompt)

            # Record LLM call
            self.record_llm_call(
                prompt=prompt[:500],  # Truncate for storage
                response=response[:500],
                model="claude-sonnet-4-20250514",
                provider="anthropic"
            )

            # Parse response
            sentiment_scores = self._parse_llm_response(response)
            return sentiment_scores

        except Exception as e:
            print(f"    WARNING: Claude call failed: {e}. Using fallback.")
            self.record_step(
                step_name="llm_fallback",
                description=f"LLM call failed, using rule-based fallback",
                input_data={"error": str(e)}
            )
            return self._fallback_sentiment(articles)

    def _format_articles_for_llm(self, articles: List[Dict], max_articles: int = 10) -> str:
        """Format articles for LLM input."""
        formatted = []
        for i, article in enumerate(articles[:max_articles], 1):
            formatted.append(f"{i}. {article.get('title', 'No title')}")
            if article.get('body'):
                formatted.append(f"   {article['body'][:200]}...")
        return "\n".join(formatted)

    def _create_sentiment_prompt(self, articles_text: str) -> str:
        """Create prompt for sentiment analysis."""
        tokens_str = ", ".join(self.target_tokens)

        # Build JSON structure dynamically
        json_fields = []
        for token in self.target_tokens:
            json_fields.append(f'  "target_token": "{token}",')
            json_fields.append(f'  "target_token_sentiment": <score from -1.0 to 1.0>,')

        json_structure = "\n".join(json_fields)

        return f"""Analyze the sentiment of these cryptocurrency news articles for {tokens_str}.

News Articles:
{articles_text}

Return a JSON array with one object per token:
[
{{
{json_structure}
  "confidence": <0.0 to 1.0>,
  "reasoning": "<brief explanation>"
}}
]

Sentiment: -1.0 (very negative) to 1.0 (very positive)
Return ONLY the JSON array."""

    def _call_claude(self, prompt: str) -> str:
        """Call Claude API."""
        response = self.llm_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.content[0].text

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response to extract sentiment scores."""
        try:
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                sentiment_array = json.loads(json_match.group())
                return {
                    "tokens": sentiment_array,
                    "overall_confidence": sum(
                        item["confidence"] for item in sentiment_array
                    ) / len(sentiment_array)
                }
            else:
                raise ValueError("No JSON array found in response")
        except Exception as e:
            print(f"    WARNING: Failed to parse Claude response: {e}")
            raise

    def _fallback_sentiment(self, articles: List[Dict]) -> Dict[str, Any]:
        """
        Rule-based sentiment analysis fallback.
        Used when LLM is not available.
        """
        positive_words = ['bullish', 'surge', 'gain', 'rise', 'up', 'high', 'positive', 'growth']
        negative_words = ['bearish', 'drop', 'fall', 'down', 'crash', 'negative', 'decline', 'loss']

        token_search_terms = {
            "BTC": ['btc', 'bitcoin'],
            "ETH": ['eth', 'ethereum'],
            "SUI": ['sui'],
            "SOL": ['sol', 'solana'],
        }

        token_results = []

        for token in self.target_tokens:
            search_terms = token_search_terms.get(token, [token.lower()])
            token_score = 0.0
            mention_count = 0

            for article in articles:
                text = (article.get('title', '') + ' ' + article.get('body', '')).lower()

                if any(term in text for term in search_terms):
                    mention_count += 1
                    pos_count = sum(1 for word in positive_words if word in text)
                    neg_count = sum(1 for word in negative_words if word in text)

                    if pos_count + neg_count > 0:
                        article_score = (pos_count - neg_count) / (pos_count + neg_count)
                        token_score += article_score

            if mention_count > 0:
                token_score /= mention_count

            token_score = max(-1.0, min(1.0, token_score))

            token_results.append({
                "target_token": token,
                "target_token_sentiment": round(token_score, 2),
                "confidence": 0.5,
                "reasoning": f"Rule-based analysis. {mention_count} mentions found."
            })

        return {
            "tokens": token_results,
            "overall_confidence": 0.5
        }


# ==================================================================================
# BACKWARD COMPATIBILITY WRAPPER (Optional)
# ==================================================================================

class AgentA:
    """
    Backward compatibility wrapper for the old AgentA interface.

    This allows existing code to continue working while using the new
    abstract Agent-based implementation under the hood.
    """

    def __init__(
        self,
        registry,
        publisher,
        target_tokens: Optional[List[str]] = None,
        api_key: Optional[str] = None
    ):
        """Maintain old interface for backward compatibility."""
        self.registry = registry
        self.publisher = publisher

        # Create ReasoningLedger from publisher's walrus_client
        from src.reasoning_ledger.reasoning_ledger_sdk import ReasoningLedger
        reasoning_ledger = ReasoningLedger(publisher.walrus_client)

        # Initialize new agent
        self.agent = AgentASentiment(
            reasoning_ledger=reasoning_ledger,
            walrus_client=publisher.walrus_client,
            target_tokens=target_tokens,
            api_key=api_key
        )

    def run(self, max_signals: int = 1) -> List[InsightSignal]:
        """
        Backward compatible run method.

        Converts old registry-based interface to new signal-based interface.
        """
        print()
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 20 + "AGENT A: SENTIMENT ANALYSIS" + " " * 25 + "║")
        print("╚" + "=" * 78 + "╝")
        print()

        # Get signals from registry (old way)
        print("[Step 1] Reading news signals from registry...")
        news_signal_dicts = self.registry.get_signals(signal_type="news", limit=max_signals)

        if not news_signal_dicts:
            print("  No news signals found")
            return []

        print(f"  Found {len(news_signal_dicts)} news signal(s)")
        print()

        # Convert to Signal objects
        news_signals = []
        for signal_data in news_signal_dicts:
            signal_obj = NewsSignal(
                object_id=signal_data['signal_id'],
                walrus_blob_id=signal_data['walrus_blob_id'],
                data_hash=signal_data['data_hash'],
                size_bytes=signal_data['size_bytes'],
                articles_count=signal_data['articles_count'],
                timestamp=datetime.fromisoformat(signal_data['timestamp']),
                producer=signal_data['producer']
            )
            news_signals.append(signal_obj)

        # Process signals using new agent
        print("[Step 2] Processing signals with AgentASentiment...")
        try:
            insight_signal = self.agent.run(signals=news_signals)

            # Register in old registry for backward compatibility
            print("[Step 3] Registering insight signal in registry...")
            signal_id = self.registry.register_signal({
                "signal_type": "insight",
                "insight_type": "sentiment",
                "signal_value": insight_signal.signal_value,
                "confidence": insight_signal.confidence,
                "producer": "agent_a",
                "walrus_trace_id": insight_signal.walrus_trace_id,
                "timestamp": insight_signal.timestamp.isoformat()
            })
            print(f"  ✓ Signal registered: {signal_id}")

            print()
            print("=" * 80)
            print(f"AGENT A: Processing complete")
            print("=" * 80)
            print()

            return [insight_signal]

        except Exception as e:
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
            return []
