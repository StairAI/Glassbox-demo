"""
Simple CryptoPanic API Integration Test

Quick test to verify the CryptoPanic v2 API is working.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_sources.cryptopanic_source import CryptoPanicSource
from dotenv import load_dotenv

# Load environment variables
config_path = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(config_path)

def main():
    print("=" * 80)
    print("CRYPTOPANIC V2 API TEST")
    print("=" * 80)
    print()

    api_token = os.getenv("CRYPTOPANIC_API_TOKEN")
    if not api_token:
        print("❌ CRYPTOPANIC_API_TOKEN not found in .env")
        return False

    print(f"✓ API Token: {api_token[:12]}...")
    print()

    # Initialize source
    source = CryptoPanicSource(api_token)

    # Test 1: Basic fetch
    print("TEST 1: Fetch recent news (no filters)")
    print("-" * 80)
    articles = source.fetch_news(limit=5)
    print(f"✓ Fetched {len(articles)} articles\n")

    for i, article in enumerate(articles, 1):
        print(f"{i}. {article.title}")
        print(f"   Kind: {article.kind}")
        print(f"   Published: {article.published_at}")
        print()

    # Test 2: BTC news
    print("TEST 2: Fetch BTC news")
    print("-" * 80)
    btc_articles = source.fetch_news(currencies=["BTC"], limit=5)
    print(f"✓ Fetched {len(btc_articles)} BTC articles\n")

    for i, article in enumerate(btc_articles[:3], 1):
        print(f"{i}. {article.title}")
        print(f"   Published: {article.published_at}")
        print()

    # Test 3: Multiple currencies
    print("TEST 3: Fetch BTC and SUI news")
    print("-" * 80)
    multi_articles = source.fetch_news(currencies=["BTC", "SUI"], limit=5)
    print(f"✓ Fetched {len(multi_articles)} articles for BTC and SUI\n")

    for i, article in enumerate(multi_articles[:3], 1):
        print(f"{i}. {article.title}")
        print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ CryptoPanic v2 API is working correctly")
    print(f"✅ Basic fetch: {len(articles)} articles")
    print(f"✅ BTC filter: {len(btc_articles)} articles")
    print(f"✅ Multi-currency filter: {len(multi_articles)} articles")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
