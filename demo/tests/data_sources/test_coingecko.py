"""
CoinGecko API Integration Test

Tests the CoinGeckoSource implementation with real API calls.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_sources.coingecko_source import CoinGeckoSource
from src.abstract import PriceSourceError, RateLimitError, SymbolNotFoundError
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
config_path = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(config_path)


def test_coingecko_connection():
    """Test basic connection to CoinGecko API."""
    print("=" * 80)
    print("TEST 1: CoinGecko Connection Test")
    print("=" * 80)

    try:
        source = CoinGeckoSource()
        is_available = source.is_available()

        if is_available:
            print("✓ CoinGecko API is available")
            return True
        else:
            print("❌ FAILED: CoinGecko API is not available")
            return False

    except Exception as e:
        print(f"❌ FAILED: Unexpected error - {e}")
        return False


def test_get_single_price():
    """Test fetching a single price."""
    print("\n" + "=" * 80)
    print("TEST 2: Get Single Price (BTC)")
    print("=" * 80)

    source = CoinGeckoSource()

    try:
        price_data = source.get_price("BTC")

        print(f"✓ Fetched BTC price successfully")
        print(f"\nPrice Data:")
        print(f"  Symbol: {price_data.symbol}")
        print(f"  Price: ${price_data.price_usd:,.2f}")
        print(f"  Timestamp: {price_data.timestamp}")
        print(f"  Market Cap: ${price_data.market_cap:,.0f}" if price_data.market_cap else "  Market Cap: N/A")
        print(f"  24h Volume: ${price_data.volume_24h:,.0f}" if price_data.volume_24h else "  24h Volume: N/A")
        print(f"  24h Change: {price_data.price_change_24h:,.2f}%" if price_data.price_change_24h else "  24h Change: N/A")

        return price_data.price_usd > 0

    except SymbolNotFoundError as e:
        print(f"❌ FAILED: Symbol not found - {e}")
        return False
    except RateLimitError as e:
        print(f"❌ FAILED: Rate limit exceeded - {e}")
        return False
    except PriceSourceError as e:
        print(f"❌ FAILED: Price source error - {e}")
        return False
    except Exception as e:
        print(f"❌ FAILED: Unexpected error - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_multiple_prices():
    """Test fetching multiple prices at once."""
    print("\n" + "=" * 80)
    print("TEST 3: Get Multiple Prices (BTC, ETH, SUI)")
    print("=" * 80)

    source = CoinGeckoSource()

    try:
        symbols = ["BTC", "ETH", "SUI"]
        prices = source.get_prices(symbols)

        print(f"✓ Fetched {len(prices)} prices successfully")
        print("\nPrice Summary:")
        print("-" * 80)

        for symbol in symbols:
            if symbol in prices:
                price_data = prices[symbol]
                change_str = f"{price_data.price_change_24h:+.2f}%" if price_data.price_change_24h else "N/A"
                print(f"  {symbol:6s}: ${price_data.price_usd:>12,.2f}  (24h: {change_str:>8s})")
            else:
                print(f"  {symbol:6s}: NOT FOUND")

        return len(prices) == len(symbols)

    except RateLimitError as e:
        print(f"❌ FAILED: Rate limit exceeded - {e}")
        return False
    except PriceSourceError as e:
        print(f"❌ FAILED: Price source error - {e}")
        return False
    except Exception as e:
        print(f"❌ FAILED: Unexpected error - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_historical_price():
    """Test fetching historical price."""
    print("\n" + "=" * 80)
    print("TEST 4: Get Historical Price (BTC, 7 days ago)")
    print("=" * 80)

    source = CoinGeckoSource()

    try:
        # Get price from 7 days ago
        date = datetime.now() - timedelta(days=7)
        price_data = source.get_historical_price("BTC", date)

        print(f"✓ Fetched historical BTC price successfully")
        print(f"\nHistorical Price Data:")
        print(f"  Date: {date.strftime('%Y-%m-%d')}")
        print(f"  Symbol: {price_data.symbol}")
        print(f"  Price: ${price_data.price_usd:,.2f}")
        print(f"  Market Cap: ${price_data.market_cap:,.0f}" if price_data.market_cap else "  Market Cap: N/A")
        print(f"  24h Volume: ${price_data.volume_24h:,.0f}" if price_data.volume_24h else "  24h Volume: N/A")

        return price_data.price_usd > 0

    except RateLimitError as e:
        print(f"❌ FAILED: Rate limit exceeded - {e}")
        return False
    except PriceSourceError as e:
        print(f"❌ FAILED: Price source error - {e}")
        return False
    except Exception as e:
        print(f"❌ FAILED: Unexpected error - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_price_caching():
    """Test that price caching works."""
    print("\n" + "=" * 80)
    print("TEST 5: Price Caching")
    print("=" * 80)

    source = CoinGeckoSource()

    try:
        # First call - should fetch from API
        print("Fetching BTC price (first call)...")
        price_data_1 = source.get_price("BTC")
        timestamp_1 = price_data_1.timestamp

        # Second call - should use cache
        print("Fetching BTC price again (should use cache)...")
        price_data_2 = source.get_price("BTC")
        timestamp_2 = price_data_2.timestamp

        # Timestamps should be the same if caching works
        if timestamp_1 == timestamp_2:
            print(f"✓ Cache working - both requests returned same timestamp")
            print(f"  Timestamp: {timestamp_1}")
            return True
        else:
            print(f"❌ FAILED: Cache not working - different timestamps")
            print(f"  First: {timestamp_1}")
            print(f"  Second: {timestamp_2}")
            return False

    except Exception as e:
        print(f"❌ FAILED: Unexpected error - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rate_limiting():
    """Test rate limiting behavior."""
    print("\n" + "=" * 80)
    print("TEST 6: Rate Limiting")
    print("=" * 80)

    source = CoinGeckoSource()

    try:
        rate_limit_info = source.get_rate_limit_info()

        if rate_limit_info:
            print("✓ Rate Limit Info:")
            print(f"   Limit: {rate_limit_info['limit']} requests per {rate_limit_info['period']}")
            print(f"   Min Interval: {rate_limit_info['min_interval_seconds']} seconds")
            print(f"   Tier: {rate_limit_info.get('tier', rate_limit_info.get('source', 'N/A'))}")
            return True
        else:
            print("❌ FAILED: No rate limit info available")
            return False

    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_symbol_mapping():
    """Test symbol to CoinGecko ID mapping."""
    print("\n" + "=" * 80)
    print("TEST 7: Symbol Mapping")
    print("=" * 80)

    source = CoinGeckoSource()

    test_symbols = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SUI": "sui",
        "USDC": "usd-coin",
    }

    print("Symbol Mappings:")
    all_correct = True
    for symbol, expected_id in test_symbols.items():
        actual_id = source._client.symbol_to_id(symbol)
        status = "✓" if actual_id == expected_id else "❌"
        print(f"  {status} {symbol} -> {actual_id} (expected: {expected_id})")
        if actual_id != expected_id:
            all_correct = False

    return all_correct


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("COINGECKO API INTEGRATION TESTS")
    print("=" * 80)
    print()

    tests = [
        test_coingecko_connection,
        test_get_single_price,
        test_get_multiple_prices,
        test_get_historical_price,
        test_price_caching,
        test_rate_limiting,
        test_symbol_mapping,
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
