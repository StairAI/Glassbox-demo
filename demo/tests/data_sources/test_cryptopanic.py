"""
CryptoPanic API Integration Test

Tests the CryptoPanicSource implementation with real API calls.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_sources.cryptopanic_source import CryptoPanicSource
from src.abstract import NewsSourceError, RateLimitError, AuthenticationError
from dotenv import load_dotenv

# Load environment variables
config_path = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(config_path)


def test_cryptopanic_connection():
    """Test basic connection to CryptoPanic API."""
    print("=" * 80)
    print("TEST 1: CryptoPanic Connection Test")
    print("=" * 80)

    api_token = os.getenv("CRYPTOPANIC_API_TOKEN")
    if not api_token:
        print("❌ FAILED: CRYPTOPANIC_API_TOKEN not found in .env file")
        return False

    print(f"✓ API Token loaded: {api_token[:8]}...")

    try:
        source = CryptoPanicSource(api_token)
        is_available = source.is_available()

        if is_available:
            print("✓ CryptoPanic API is available")
            return True
        else:
            print("❌ FAILED: CryptoPanic API is not available")
            return False

    except AuthenticationError as e:
        print(f"❌ FAILED: Authentication error - {e}")
        return False
    except Exception as e:
        print(f"❌ FAILED: Unexpected error - {e}")
        return False


def test_fetch_news_basic():
    """Test fetching news without filters."""
    print("\n" + "=" * 80)
    print("TEST 2: Fetch News (No Filters)")
    print("=" * 80)

    api_token = os.getenv("CRYPTOPANIC_API_TOKEN")
    source = CryptoPanicSource(api_token)

    try:
        articles = source.fetch_news(limit=5)

        print(f"✓ Fetched {len(articles)} articles")
        print("\nSample Articles:")
        print("-" * 80)

        for i, article in enumerate(articles, 1):
            print(f"\n{i}. {article.title}")
            print(f"   Source: {article.domain}")
            print(f"   Published: {article.published_at}")
            print(f"   URL: {article.url}")
            if article.currencies:
                print(f"   Currencies: {', '.join(article.currencies)}")
            if article.votes:
                print(f"   Votes: +{article.votes.get('positive', 0)} -{article.votes.get('negative', 0)}")

        return len(articles) > 0

    except RateLimitError as e:
        print(f"❌ FAILED: Rate limit exceeded - {e}")
        return False
    except NewsSourceError as e:
        print(f"❌ FAILED: News source error - {e}")
        return False
    except Exception as e:
        print(f"❌ FAILED: Unexpected error - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fetch_news_with_currencies():
    """Test fetching news filtered by currencies."""
    print("\n" + "=" * 80)
    print("TEST 3: Fetch News (Filtered by BTC, SUI)")
    print("=" * 80)

    api_token = os.getenv("CRYPTOPANIC_API_TOKEN")
    source = CryptoPanicSource(api_token)

    try:
        articles = source.fetch_news(
            currencies=["BTC", "SUI"],
            limit=10,
            filter_type="hot"
        )

        print(f"✓ Fetched {len(articles)} articles for BTC and SUI")
        print("\nCurrency Distribution:")
        print("-" * 80)

        currency_counts = {}
        for article in articles:
            if article.currencies:
                for currency in article.currencies:
                    currency_counts[currency] = currency_counts.get(currency, 0) + 1

        for currency, count in sorted(currency_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {currency}: {count} articles")

        print("\nSample BTC/SUI Articles:")
        print("-" * 80)

        for i, article in enumerate(articles[:3], 1):
            print(f"\n{i}. {article.title}")
            print(f"   Currencies: {', '.join(article.currencies) if article.currencies else 'None'}")
            print(f"   Published: {article.published_at}")

        return len(articles) > 0

    except RateLimitError as e:
        print(f"❌ FAILED: Rate limit exceeded - {e}")
        return False
    except NewsSourceError as e:
        print(f"❌ FAILED: News source error - {e}")
        return False
    except Exception as e:
        print(f"❌ FAILED: Unexpected error - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fetch_news_filters():
    """Test different filter types."""
    print("\n" + "=" * 80)
    print("TEST 4: Fetch News (Different Filters)")
    print("=" * 80)

    api_token = os.getenv("CRYPTOPANIC_API_TOKEN")
    source = CryptoPanicSource(api_token)

    filters = ["hot", "rising", "bullish", "bearish"]
    results = {}

    for filter_type in filters:
        try:
            articles = source.fetch_news(
                currencies=["BTC"],
                limit=3,
                filter_type=filter_type
            )
            results[filter_type] = len(articles)
            print(f"✓ Filter '{filter_type}': {len(articles)} articles")

            if articles:
                print(f"   Sample: {articles[0].title[:80]}...")

        except Exception as e:
            results[filter_type] = 0
            print(f"❌ Filter '{filter_type}' failed: {e}")

    return sum(results.values()) > 0


def test_rate_limit_info():
    """Test getting rate limit information."""
    print("\n" + "=" * 80)
    print("TEST 5: Rate Limit Info")
    print("=" * 80)

    api_token = os.getenv("CRYPTOPANIC_API_TOKEN")
    source = CryptoPanicSource(api_token)

    try:
        rate_limit_info = source.get_rate_limit_info()

        if rate_limit_info:
            print("✓ Rate Limit Info:")
            print(f"   Limit: {rate_limit_info['limit']} requests per {rate_limit_info['period']}")
            print(f"   Source: {rate_limit_info['source']}")
            return True
        else:
            print("❌ FAILED: No rate limit info available")
            return False

    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("CRYPTOPANIC API INTEGRATION TESTS")
    print("=" * 80)
    print()

    tests = [
        test_cryptopanic_connection,
        test_fetch_news_basic,
        test_fetch_news_with_currencies,
        test_fetch_news_filters,
        test_rate_limit_info,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")

    if passed == total:
        print("\n✅ ALL TESTS PASSED")
    else:
        print(f"\n❌ {total - passed} TEST(S) FAILED")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
