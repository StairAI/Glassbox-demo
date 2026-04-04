#!/usr/bin/env python3
"""
E2E Full Pipeline Test

This script tests the complete glass box pipeline end-to-end:
1. Register a new mocked account (enabled for visualization)
2. Fetch news articles (100 BTC + 100 SUI) from CryptoPanic
3. Publish each article individually to Walrus with owner address
4. Initialize Agent A under the same owner account
5. Process each news signal to generate sentiment signals
6. Publish signals + reasoning traces under the same owner

All data will be tagged with the same owner address for filtering in the visualization.
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import time
import hashlib
import secrets

# Add demo directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv('config/.env')

# Import all components
from src.storage.activity_db import ActivityDB
from src.storage.walrus_client import WalrusClient, WalrusHelper
from src.data_clients.cryptopanic_client import CryptoPanicClient
from src.data_sources.cryptopanic_source import CryptoPanicSource
from src.blockchain.sui_publisher import OnChainPublisher
from src.demo.signal_registry import SignalRegistry


class E2EFullPipeline:
    """End-to-end full pipeline test."""

    def __init__(self, owner_address: str, project_name: str, description: str):
        """
        Initialize E2E pipeline.

        Args:
            owner_address: Owner address for all published data
            project_name: Project name for mocked account
            description: Description for the project
        """
        self.owner_address = owner_address
        self.project_name = project_name
        self.description = description

        # Initialize components
        self.db = ActivityDB(db_path="data/activity.db")
        # Use real Walrus testnet API
        walrus_publisher = os.getenv("WALRUS_PUBLISHER_URL", "https://publisher.walrus-testnet.walrus.space")
        walrus_aggregator = os.getenv("WALRUS_AGGREGATOR_URL", "https://aggregator.walrus-testnet.walrus.space")
        self.walrus_client = WalrusClient(
            publisher_url=walrus_publisher,
            aggregator_url=walrus_aggregator,
            simulated=False  # Use REAL Walrus testnet
        )
        self.registry = SignalRegistry(registry_path="data/signal_registry.json")

        # Initialize publisher with owner address
        self.publisher = OnChainPublisher(
            walrus_client=self.walrus_client,
            owner_address=owner_address,  # All publications will have this owner
            simulated=True
        )

        # CryptoPanic API
        self.crypto_api_key = os.getenv("CRYPTOPANIC_API_TOKEN")
        if not self.crypto_api_key:
            raise ValueError("CRYPTOPANIC_API_TOKEN not found in environment")

        self.news_source = CryptoPanicSource(api_token=self.crypto_api_key)

        # Anthropic API
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.anthropic_api_key:
            print("WARNING: ANTHROPIC_API_KEY not found. Agent A will use fallback sentiment analysis.")

        # Statistics
        self.stats = {
            "articles_fetched": 0,
            "articles_published": 0,
            "signals_generated": 0,
            "start_time": None,
            "end_time": None
        }

    def run(self):
        """Execute the full E2E pipeline."""
        print()
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 20 + "E2E FULL PIPELINE TEST" + " " * 30 + "║")
        print("╚" + "=" * 78 + "╝")
        print()

        self.stats["start_time"] = datetime.now()

        try:
            # Step 1: Register mocked account
            self._register_account()

            # Step 2: Fetch news articles
            articles = self._fetch_news_articles()

            # Step 3: Publish articles individually
            self._publish_articles(articles)

            # Step 4: Initialize and run Agent A
            self._run_agent_a()

            # Step 5: Print summary
            self._print_summary()

        except KeyboardInterrupt:
            print("\n\n[INTERRUPTED] Pipeline stopped by user")
            self._print_summary()
        except Exception as e:
            print(f"\n\n[ERROR] Pipeline failed: {e}")
            import traceback
            traceback.print_exc()
            self._print_summary()

    def _register_account(self):
        """Step 1: Register mocked account."""
        print("[Step 1] Registering Mocked Account")
        print("=" * 80)

        # Register account (enabled=True by default)
        account_id = self.db.register_mocked_account(
            account_address=self.owner_address,
            project_name=self.project_name,
            description=self.description,
            enabled=True  # Visible in visualization
        )

        print(f"  ✓ Account registered (ID: {account_id})")
        print(f"    Address: {self.owner_address}")
        print(f"    Project: {self.project_name}")
        print(f"    Status: Enabled (visible in visualization)")
        print()

    def _fetch_news_articles(self) -> List[Dict[str, Any]]:
        """Step 2: Fetch news articles from CryptoPanic."""
        print("[Step 2] Fetching News Articles")
        print("=" * 80)

        # Step 2.0: Health check
        print(f"  [2.0] Checking CryptoPanic API health...")
        health = self.news_source._client.health_check()

        print(f"    Status: {'✓ Healthy' if health['healthy'] else '✗ Unhealthy'}")
        if health['status_code']:
            print(f"    HTTP Status: {health['status_code']}")
        if health['response_time_ms']:
            print(f"    Response Time: {health['response_time_ms']}ms")
        print(f"    Message: {health['message']}")
        print()

        # If API is unhealthy, skip fetching
        if not health['healthy']:
            print(f"  ⚠️  CryptoPanic API is not available. Skipping article fetch.")
            print(f"  Error: {health['error']}")
            print()
            return []

        all_articles = []

        # Fetch BTC articles
        print(f"  [2.1] Fetching 100 BTC articles...")
        try:
            btc_articles = self.news_source.fetch_news(
                currencies=["BTC"],
                limit=100
            )
            # Convert to dict format
            btc_articles_dict = [self._article_to_dict(a) for a in btc_articles]
            all_articles.extend(btc_articles_dict)
            print(f"    ✓ Fetched {len(btc_articles_dict)} BTC articles")
        except Exception as e:
            print(f"    ✗ Failed to fetch BTC articles: {e}")

        time.sleep(1)  # Rate limit pause

        # Fetch SUI articles
        print(f"  [2.2] Fetching 100 SUI articles...")
        try:
            sui_articles = self.news_source.fetch_news(
                currencies=["SUI"],
                limit=100
            )
            # Convert to dict format
            sui_articles_dict = [self._article_to_dict(a) for a in sui_articles]
            all_articles.extend(sui_articles_dict)
            print(f"    ✓ Fetched {len(sui_articles_dict)} SUI articles")
        except Exception as e:
            print(f"    ✗ Failed to fetch SUI articles: {e}")

        self.stats["articles_fetched"] = len(all_articles)
        print()
        print(f"  ✓ Total articles fetched: {len(all_articles)}")
        print()

        return all_articles

    def _article_to_dict(self, article) -> Dict[str, Any]:
        """Convert NewsArticle object to dict."""
        return {
            "title": article.title,
            "url": article.url,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "source": article.source,
            "domain": article.domain,
            "currencies": article.currencies or [],
            "kind": article.kind,
            "sentiment": article.sentiment,
            "votes": article.votes
        }

    def _publish_articles(self, articles: List[Dict[str, Any]]):
        """Step 3: Publish each article individually to Walrus."""
        print("[Step 3] Publishing Articles to Walrus")
        print("=" * 80)

        if not articles:
            print("  No articles to publish")
            print()
            return

        print(f"  Publishing {len(articles)} articles individually...")
        print(f"  Owner: {self.owner_address}")
        print()

        for i, article in enumerate(articles, 1):
            try:
                # Create news data payload (one article per signal)
                news_data = {
                    "articles": [article],
                    "fetched_at": datetime.now().isoformat(),
                    "source": "cryptopanic",
                    "currencies": article.get("currencies", [])
                }

                # Publish to Walrus and register signal
                signal = self.publisher.publish_news_signal(
                    news_data=news_data,
                    producer=f"{self.project_name}_news_pipeline"
                )

                # Register in SignalRegistry
                self.registry.register_signal({
                    "signal_type": "news",
                    "walrus_blob_id": signal.walrus_blob_id,
                    "data_hash": signal.data_hash,
                    "size_bytes": signal.size_bytes,
                    "articles_count": 1,
                    "producer": f"{self.project_name}_news_pipeline",
                    "owner": self.owner_address,  # Tag with owner
                    "timestamp": datetime.now().isoformat()
                })

                self.stats["articles_published"] += 1

                if i % 10 == 0:
                    print(f"    Progress: {i}/{len(articles)} articles published")

            except Exception as e:
                print(f"    ✗ Failed to publish article {i}: {e}")

        print()
        print(f"  ✓ Published {self.stats['articles_published']}/{len(articles)} articles")
        print()

    def _run_agent_a(self):
        """Step 4: Initialize and run Agent A."""
        print("[Step 4] Running Agent A (Sentiment Analysis)")
        print("=" * 80)

        # Initialize Agent A with new abstract Agent interface
        from src.agents.agent_a_sentiment import AgentASentiment
        from src.reasoning_ledger.reasoning_ledger_sdk import ReasoningLedger
        from src.abstract import NewsSignal

        # Create ReasoningLedger for trace storage
        reasoning_ledger = ReasoningLedger(self.walrus_client)

        agent_a = AgentASentiment(
            reasoning_ledger=reasoning_ledger,
            walrus_client=self.walrus_client,
            target_tokens=["BTC", "SUI"],
            api_key=self.anthropic_api_key
        )

        # Get news signals for this owner
        all_news_signals = self.registry.get_signals(signal_type="news", limit=1000)
        owner_news_signals = [
            t for t in all_news_signals
            if t.get("owner") == self.owner_address
        ]

        print(f"  Found {len(owner_news_signals)} news signals for this owner")
        print(f"  Processing all signals...")
        print()

        # Process all signals
        for i, signal_data in enumerate(owner_news_signals, 1):
            try:
                print(f"  [Processing {i}/{len(owner_news_signals)}] Signal: {signal_data['signal_id']}")

                # Convert signal_data to NewsSignal object
                news_signal = NewsSignal(
                    object_id=signal_data['signal_id'],
                    walrus_blob_id=signal_data['walrus_blob_id'],
                    data_hash=signal_data['data_hash'],
                    size_bytes=signal_data['size_bytes'],
                    articles_count=signal_data.get('articles_count', 1),
                    timestamp=datetime.fromisoformat(signal_data['timestamp']),
                    producer=signal_data['producer']
                )

                # Process signal using Agent.run() - this automatically:
                # 1. Fetches news data from Walrus
                # 2. Analyzes sentiment
                # 3. Records reasoning steps
                # 4. Stores signal data on Walrus
                # 5. Stores reasoning trace on Walrus
                # 6. Returns InsightSignal
                insight_signal = agent_a.run(signals=[news_signal])

                # Register insight signal in registry
                self.registry.register_signal({
                    "signal_type": "insight",
                    "insight_type": insight_signal.insight_type,
                    "walrus_blob_id": insight_signal.walrus_blob_id,
                    "data_hash": insight_signal.data_hash,
                    "size_bytes": insight_signal.size_bytes,
                    "confidence": insight_signal.confidence,
                    "producer": insight_signal.producer,
                    "walrus_trace_id": insight_signal.walrus_trace_id,
                    "owner": self.owner_address,  # Tag with owner
                    "timestamp": insight_signal.timestamp.isoformat()
                })

                self.stats["signals_generated"] += 1

                if i % 10 == 0:
                    print(f"    Progress: {i}/{len(owner_news_signals)} signals generated")

            except Exception as e:
                print(f"    ✗ Failed to process signal {i}: {e}")
                import traceback
                traceback.print_exc()

        print()
        print(f"  ✓ Generated {self.stats['signals_generated']}/{len(owner_news_signals)} sentiment signals")
        print()

    def _print_summary(self):
        """Print pipeline summary."""
        self.stats["end_time"] = datetime.now()

        duration = None
        if self.stats["start_time"] and self.stats["end_time"]:
            duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()

        print()
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 30 + "PIPELINE SUMMARY" + " " * 27 + "║")
        print("╚" + "=" * 78 + "╝")
        print()
        print(f"  Owner Address:       {self.owner_address}")
        print(f"  Project Name:        {self.project_name}")
        print()
        print(f"  Articles Fetched:    {self.stats['articles_fetched']}")
        print(f"  Articles Published:  {self.stats['articles_published']}")
        print(f"  Signals Generated:   {self.stats['signals_generated']}")
        print()
        if duration:
            print(f"  Execution Time:      {duration:.1f} seconds")
        print()
        print("  All data has been tagged with the owner address and is now visible")
        print("  in the Glass Box Explorer visualization.")
        print()
        print(f"  View at: http://localhost:8080")
        print()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="E2E Full Pipeline Test")
    parser.add_argument(
        "--owner",
        type=str,
        default=None,
        help="Owner address for all published data (auto-generated if not specified)"
    )
    parser.add_argument(
        "--project",
        type=str,
        default=None,
        help="Project name for mocked account (auto-generated if not specified)"
    )
    parser.add_argument(
        "--description",
        type=str,
        default=None,
        help="Description for the project (auto-generated if not specified)"
    )

    args = parser.parse_args()

    # Generate unique values for each run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_id = secrets.token_hex(4)  # 8-character random hex

    # Generate owner address if not provided
    owner_address = args.owner or f"0xE2E_{run_id}_{timestamp}"

    # Generate project name if not provided
    project_name = args.project or f"E2E-Pipeline-{timestamp[-6:]}"

    # Generate description if not provided
    description = args.description or f"E2E test run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (ID: {run_id})"

    # Create and run pipeline
    pipeline = E2EFullPipeline(
        owner_address=owner_address,
        project_name=project_name,
        description=description
    )

    pipeline.run()


if __name__ == "__main__":
    main()
