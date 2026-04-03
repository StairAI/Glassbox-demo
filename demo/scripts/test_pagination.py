#!/usr/bin/env python3
"""
Test Pagination Support

Demonstrates fetching 100 articles using pagination.
The API returns ~20 articles per page, so fetching 100 will make ~5 API calls.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data_sources.cryptopanic_source import CryptoPanicSource
from dotenv import load_dotenv

def main():
    """Test pagination."""

    # Load environment
    load_dotenv('config/.env')

    print("=" * 80)
    print("PAGINATION TEST")
    print("=" * 80)
    print()

    # API Key
    api_key = "1faf4af4f599defbd358148d7edbce39c9da3dcb"

    # Initialize source
    source = CryptoPanicSource(api_token=api_key)

    # Test 1: Fetch 100 BTC articles (will use pagination)
    print("TEST 1: Fetch 100 BTC articles")
    print("-" * 80)
    print("Expected: ~5 API calls (20 articles per page)")
    print()

    articles_btc = source.fetch_news(currencies=["BTC"], limit=100)

    print(f"\n✓ Fetched {len(articles_btc)} BTC articles")
    print(f"\nFirst 5 articles:")
    for i, article in enumerate(articles_btc[:5], 1):
        print(f"  {i}. {article.title[:70]}...")
        print(f"     Published: {article.published_at}")

    print(f"\nLast 5 articles:")
    for i, article in enumerate(articles_btc[-5:], len(articles_btc) - 4):
        print(f"  {i}. {article.title[:70]}...")
        print(f"     Published: {article.published_at}")

    # Test 2: Fetch all available SUI articles (no limit override)
    print("\n" + "=" * 80)
    print("TEST 2: Fetch SUI articles (limit=50)")
    print("-" * 80)
    print()

    articles_sui = source.fetch_news(currencies=["SUI"], limit=50)

    print(f"\n✓ Fetched {len(articles_sui)} SUI articles")
    print(f"\nFirst 3 articles:")
    for i, article in enumerate(articles_sui[:3], 1):
        print(f"  {i}. {article.title[:70]}...")
        print(f"     Published: {article.published_at}")

    # Test 3: Small limit (should only fetch 1 page)
    print("\n" + "=" * 80)
    print("TEST 3: Fetch only 15 articles (should be 1 API call)")
    print("-" * 80)
    print()

    articles_small = source.fetch_news(currencies=["BTC"], limit=15)

    print(f"\n✓ Fetched {len(articles_small)} articles")
    print("Expected: 1 page fetched (no pagination needed)")

    # Rate limit info
    print("\n" + "=" * 80)
    print("RATE LIMIT INFO")
    print("=" * 80)

    rate_info = source.get_rate_limit_info()
    print(f"\nRequests made: {rate_info['requests_made']}/{rate_info['limit']}")
    print(f"Period: {rate_info['period']}")

    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
