#!/usr/bin/env python3
"""
Agent A: Sentiment Analysis Agent

This agent:
1. Reads news triggers from TriggerRegistry
2. Fetches full news data from Walrus
3. Analyzes sentiment with LLM
4. Generates sentiment scores for BTC/ETH
5. Stores reasoning trace on Walrus
6. Publishes sentiment signal trigger
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
import json

from src.core.trigger import NewsTrigger, SignalTrigger
from src.demo.trigger_registry import TriggerRegistry
from src.blockchain.sui_publisher import OnChainPublisher
from src.storage.walrus_client import WalrusClient, WalrusHelper


class AgentA:
    """Agent A: Sentiment Analysis for crypto news"""

    def __init__(
        self,
        registry: TriggerRegistry,
        publisher: OnChainPublisher,
        target_tokens: Optional[List[str]] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize Agent A.

        Args:
            registry: TriggerRegistry for reading news triggers
            publisher: OnChainPublisher for publishing sentiment signals
            target_tokens: List of tokens to analyze (e.g., ["BTC", "ETH"])
            api_key: Anthropic API key
        """
        self.registry = registry
        self.publisher = publisher
        self.target_tokens = target_tokens or ["BTC", "ETH"]
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        # Initialize LLM client (Claude only)
        self._init_llm()

    def _init_llm(self):
        """Initialize Claude (Anthropic) client."""
        try:
            import anthropic
            self.llm_client = anthropic.Anthropic(api_key=self.api_key)
            self.llm_available = True
        except ImportError:
            print("WARNING: Anthropic package not installed. Install with: pip install anthropic")
            self.llm_available = False
        except Exception as e:
            print(f"WARNING: Failed to initialize Claude: {e}")
            self.llm_available = False

    def run(self, max_triggers: int = 1) -> List[SignalTrigger]:
        """
        Main execution loop for Agent A.

        Args:
            max_triggers: Maximum number of news triggers to process

        Returns:
            List of generated SignalTriggers
        """
        print()
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 20 + "AGENT A: SENTIMENT ANALYSIS" + " " * 25 + "║")
        print("╚" + "=" * 78 + "╝")
        print()

        # Step 1: Read news triggers
        print("[Step 1] Reading news triggers from registry...")
        news_triggers = self.registry.get_triggers(trigger_type="news", limit=max_triggers)

        if not news_triggers:
            print("  No news triggers found")
            return []

        print(f"  Found {len(news_triggers)} news trigger(s)")
        print()

        # Step 2: Process each trigger
        signal_triggers = []
        for i, trigger_data in enumerate(news_triggers, 1):
            print(f"[Processing {i}/{len(news_triggers)}] Trigger: {trigger_data['trigger_id']}")

            try:
                signal = self._process_news_trigger(trigger_data)
                signal_triggers.append(signal)
                print(f"  Sentiment signal generated")
            except Exception as e:
                print(f"  Error: {e}")
            print()

        print("=" * 80)
        print(f"AGENT A: Processed {len(signal_triggers)}/{len(news_triggers)} triggers")
        print("=" * 80)
        print()

        return signal_triggers

    def _process_news_trigger(self, trigger_data: Dict) -> SignalTrigger:
        """Process a single news trigger and generate sentiment signal."""

        # Step 1: Fetch full news data from Walrus
        print("  [1/5] Fetching news data from Walrus...")
        trigger_obj = NewsTrigger(
            object_id=trigger_data['trigger_id'],
            walrus_blob_id=trigger_data['walrus_blob_id'],
            data_hash=trigger_data['data_hash'],
            size_bytes=trigger_data['size_bytes'],
            articles_count=trigger_data['articles_count'],
            timestamp=datetime.fromisoformat(trigger_data['timestamp']),
            producer=trigger_data['producer']
        )

        # Pass the publisher's walrus_client to use the same instance
        news_data = trigger_obj.fetch_full_data(walrus_client=self.publisher.walrus_client)
        print(f"    Fetched {len(news_data['articles'])} articles")

        # Step 2: Analyze sentiment with LLM
        print("  [2/5] Analyzing sentiment with LLM...")
        sentiment_scores = self._analyze_sentiment(news_data['articles'])
        print(f"    Generated sentiment scores")

        # Step 3: Create reasoning trace
        print("  [3/5] Creating reasoning trace...")
        reasoning_trace = {
            "agent": "agent_a_sentiment",
            "input_trigger": trigger_data['trigger_id'],
            "input_walrus_blob": trigger_data['walrus_blob_id'],
            "articles_analyzed": len(news_data['articles']),
            "sentiment_scores": sentiment_scores,
            "target_tokens": self.target_tokens,
            "llm_provider": "anthropic",
            "llm_model": "claude-sonnet-4.5-20250514",
            "timestamp": datetime.utcnow().isoformat()
        }
        print(f"    Reasoning trace created")

        # Step 4: Publish sentiment signal trigger (reasoning trace stored by publisher)
        print("  [4/5] Publishing sentiment signal...")
        signal_trigger = self.publisher.publish_signal_trigger(
            signal_type="sentiment",
            signal_value=sentiment_scores,
            confidence=sentiment_scores.get("overall_confidence", 0.8),
            producer="agent_a",
            reasoning_trace=reasoning_trace  # Pass trace dict, publisher will store it
        )

        # Get the trace blob ID from the signal trigger
        trace_blob_id = signal_trigger.walrus_trace_id

        # Step 5: Register in TriggerRegistry
        print("  [5/5] Registering signal trigger...")
        signal_id = self.registry.register_trigger({
            "trigger_type": "signal",
            "signal_type": "sentiment",
            "signal_value": sentiment_scores,
            "confidence": sentiment_scores.get("overall_confidence", 0.8),
            "producer": "agent_a",
            "walrus_trace_id": trace_blob_id if trace_blob_id else None,
            "timestamp": datetime.utcnow().isoformat()
        })
        print(f"    Signal registered: {signal_id}")

        return signal_trigger

    def _analyze_sentiment(self, articles: List[Dict]) -> Dict[str, Any]:
        """
        Analyze sentiment of news articles using LLM.

        Args:
            articles: List of news articles

        Returns:
            Dict with sentiment scores for each currency
        """
        if not self.llm_available:
            # Fallback: Simple rule-based sentiment
            return self._fallback_sentiment(articles)

        # Prepare prompt for LLM
        articles_text = self._format_articles_for_llm(articles)
        prompt = self._create_sentiment_prompt(articles_text)

        try:
            response = self._call_claude(prompt)
            # Parse LLM response
            sentiment_scores = self._parse_llm_response(response)
            return sentiment_scores

        except Exception as e:
            print(f"    WARNING: Claude call failed: {e}. Using fallback sentiment.")
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

        # Build the JSON structure dynamically based on target tokens
        json_fields = []
        for token in self.target_tokens:
            json_fields.append(f'  "target_token": "{token}",')
            json_fields.append(f'  "target_token_sentiment": <score from -1.0 (very negative) to 1.0 (very positive)>,')

        json_structure = "\n".join(json_fields)

        return f"""Analyze the sentiment of these cryptocurrency news articles and provide sentiment scores for {tokens_str}.

News Articles:
{articles_text}

For each target token, analyze the sentiment expressed in these articles.

Return a JSON response with this exact structure (one object per token):
[
{{
{json_structure}
  "confidence": <confidence score from 0.0 to 1.0>,
  "reasoning": "<brief explanation of the sentiment analysis for this token>"
}}
]

Important:
- Return a JSON array with one object per target token
- Each object must have: target_token, target_token_sentiment, confidence, reasoning
- Sentiment score should be from -1.0 (very negative) to 1.0 (very positive)
- Only return the JSON array, no other text."""

    def _call_claude(self, prompt: str) -> str:
        """Call Claude API (Sonnet 4.5)."""
        response = self.llm_client.messages.create(
            model="claude-sonnet-4.5-20250514",
            max_tokens=2048,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.content[0].text

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response to extract sentiment scores."""
        try:
            # Try to extract JSON array from response
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                sentiment_array = json.loads(json_match.group())

                # Convert array to dict format for compatibility
                result = {
                    "tokens": sentiment_array,
                    "overall_confidence": sum(item["confidence"] for item in sentiment_array) / len(sentiment_array)
                }
                return result
            else:
                raise ValueError("No JSON array found in response")
        except Exception as e:
            print(f"    WARNING: Failed to parse Claude response: {e}")
            raise

    def _fallback_sentiment(self, articles: List[Dict]) -> Dict[str, Any]:
        """
        Fallback sentiment analysis using simple rules.
        Used when LLM is not available.
        """
        positive_words = ['bullish', 'surge', 'gain', 'rise', 'up', 'high', 'positive', 'growth']
        negative_words = ['bearish', 'drop', 'fall', 'down', 'crash', 'negative', 'decline', 'loss']

        # Token name to search terms mapping
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

                # Check if this article mentions the token
                if any(term in text for term in search_terms):
                    mention_count += 1

                    # Count positive/negative words
                    pos_count = sum(1 for word in positive_words if word in text)
                    neg_count = sum(1 for word in negative_words if word in text)

                    # Simple scoring
                    if pos_count + neg_count > 0:
                        article_score = (pos_count - neg_count) / (pos_count + neg_count)
                        token_score += article_score

            # Normalize score
            if mention_count > 0:
                token_score /= mention_count

            # Clip to [-1, 1] range
            token_score = max(-1.0, min(1.0, token_score))

            token_results.append({
                "target_token": token,
                "target_token_sentiment": round(token_score, 2),
                "confidence": 0.5,  # Lower confidence for rule-based
                "reasoning": f"Rule-based sentiment analysis (Claude not available). Based on {mention_count} mentions."
            })

        return {
            "tokens": token_results,
            "overall_confidence": 0.5
        }
