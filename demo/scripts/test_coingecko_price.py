#!/usr/bin/env python3
"""
Quick test to verify CoinGecko API integration works.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_sources.coingecko_source import CoinGeckoSource
from dotenv import load_dotenv

# Load environment
load_dotenv("config/.env")

print("="*80)
print("COINGECKO PRICE TEST")
print("="*80)
print()

# Initialize source (no API key needed for free tier)
source = CoinGeckoSource()

# Test 1: Check API availability
print("[1] Checking CoinGecko API availability...")
is_available = source.is_available()
print(f"    Status: {'✓ Available' if is_available else '✗ Not Available'}")
print()

if not is_available:
    print("❌ CoinGecko API is not available. Exiting.")
    sys.exit(1)

# Test 2: Get BTC price
print("[2] Fetching BTC current price...")
try:
    btc_price = source.get_price("BTC")

    print(f"    ✓ Successfully fetched BTC price")
    print()
    print(f"    Symbol:           {btc_price.symbol}")
    print(f"    Price (USD):      ${btc_price.price_usd:,.2f}")
    print(f"    Source:           {btc_price.source}")
    print(f"    Timestamp:        {btc_price.timestamp}")

    if btc_price.price_change_24h:
        print(f"    24h Change:       {btc_price.price_change_24h:+.2f}%")

    if btc_price.volume_24h:
        print(f"    24h Volume:       ${btc_price.volume_24h:,.0f}")

    if btc_price.market_cap:
        print(f"    Market Cap:       ${btc_price.market_cap:,.0f}")

    print()

    # Test 3: Convert to dict (for Walrus storage)
    print("[3] Converting to dict for Walrus storage...")
    price_dict = btc_price.to_dict()

    print(f"    ✓ Converted to dict")
    print(f"    Keys: {list(price_dict.keys())}")
    print(f"    Size: ~{len(str(price_dict))} bytes")
    print()

    # Test 4: Get rate limit info
    print("[4] Checking rate limits...")
    rate_info = source.get_rate_limit_info()
    if rate_info:
        print(f"    Limit:       {rate_info['limit']} requests per {rate_info['period']}")
        print(f"    Min Interval: {rate_info['min_interval_seconds']} seconds")
        print(f"    Tier:        {rate_info['tier']}")
    print()

    print("="*80)
    print("✅ ALL TESTS PASSED - CoinGecko integration is working!")
    print("="*80)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
