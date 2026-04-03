#!/usr/bin/env python3
"""
CryptoPanic API Explorer

This script calls the CryptoPanic API and records all payload data
to understand how to use it more efficiently.
"""

import os
import sys
import json
import requests
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def explore_api(api_key: str):
    """
    Explore CryptoPanic API endpoints and record responses.

    Args:
        api_key: CryptoPanic API key
    """
    base_url = "https://cryptopanic.com/api/developer/v2"

    print("=" * 80)
    print("CRYPTOPANIC API EXPLORER")
    print("=" * 80)
    print(f"\nUsing API Key: {api_key[:20]}...")
    print()

    # Test configurations
    test_cases = [
        {
            "name": "1. Basic Posts (No Filter)",
            "endpoint": "/posts/",
            "params": {
                "auth_token": api_key,
            }
        },
        {
            "name": "2. BTC Currency Filter",
            "endpoint": "/posts/",
            "params": {
                "auth_token": api_key,
                "currencies": "BTC"
            }
        },
        {
            "name": "3. SUI Currency Filter",
            "endpoint": "/posts/",
            "params": {
                "auth_token": api_key,
                "currencies": "SUI"
            }
        },
        {
            "name": "4. Multiple Currencies (BTC,ETH)",
            "endpoint": "/posts/",
            "params": {
                "auth_token": api_key,
                "currencies": "BTC,ETH"
            }
        },
        {
            "name": "5. Filter by Kind (news only)",
            "endpoint": "/posts/",
            "params": {
                "auth_token": api_key,
                "currencies": "BTC",
                "kind": "news"
            }
        },
        {
            "name": "6. Filter by Region (en)",
            "endpoint": "/posts/",
            "params": {
                "auth_token": api_key,
                "currencies": "BTC",
                "regions": "en"
            }
        },
        {
            "name": "7. Pagination Test (Page 2)",
            "endpoint": "/posts/",
            "params": {
                "auth_token": api_key,
                "currencies": "BTC",
                "page": 2
            }
        }
    ]

    results = {}

    for i, test in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"{test['name']}")
        print(f"{'=' * 80}")

        url = base_url + test['endpoint']
        print(f"\nEndpoint: {url}")
        print(f"Params: {json.dumps({k: v for k, v in test['params'].items() if k != 'auth_token'}, indent=2)}")

        try:
            response = requests.get(url, params=test['params'], timeout=10)

            print(f"\nStatus Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()

                # Analyze response structure
                print(f"\n📊 Response Structure:")
                print(f"  - Keys: {list(data.keys())}")

                if 'results' in data:
                    results_count = len(data['results'])
                    print(f"  - Results Count: {results_count}")

                    if results_count > 0:
                        first_post = data['results'][0]
                        print(f"\n📝 First Post Structure:")
                        print(f"  - Keys: {list(first_post.keys())}")
                        print(f"  - ID: {first_post.get('id')}")
                        print(f"  - Title: {first_post.get('title', '')[:80]}...")
                        print(f"  - Published: {first_post.get('published_at')}")
                        print(f"  - Source: {first_post.get('source', {}).get('title')}")
                        print(f"  - URL: {first_post.get('url', '')[:80]}...")

                        if 'currencies' in first_post:
                            currencies = [c.get('code') for c in first_post.get('currencies', [])]
                            print(f"  - Currencies: {currencies}")

                        if 'kind' in first_post:
                            print(f"  - Kind: {first_post.get('kind')}")

                        if 'votes' in first_post:
                            votes = first_post.get('votes', {})
                            print(f"  - Votes: positive={votes.get('positive')}, negative={votes.get('negative')}")

                if 'next' in data:
                    print(f"\n🔗 Pagination:")
                    print(f"  - Next: {data['next'][:80] if data['next'] else 'None'}...")

                if 'count' in data:
                    print(f"  - Total Count: {data['count']}")

                # Save full response
                results[test['name']] = {
                    "status": response.status_code,
                    "data": data
                }

            else:
                error_msg = response.text
                print(f"\n❌ Error: {error_msg}")
                results[test['name']] = {
                    "status": response.status_code,
                    "error": error_msg
                }

        except Exception as e:
            print(f"\n❌ Exception: {e}")
            results[test['name']] = {
                "error": str(e)
            }

    # Save results to file
    output_file = "output/cryptopanic_api_exploration.json"
    os.makedirs("output", exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'=' * 80}")
    print("EXPLORATION COMPLETE")
    print(f"{'=' * 80}")
    print(f"\n✅ Full results saved to: {output_file}")
    print(f"\n💡 Key Findings:")
    print(f"  - Check the output file for complete API responses")
    print(f"  - Analyze pagination structure for efficient batching")
    print(f"  - Review available filters (currencies, kind, regions)")
    print()


def main():
    """Main function."""
    # Use the new API key
    api_key = "1faf4af4f599defbd358148d7edbce39c9da3dcb"

    explore_api(api_key)


if __name__ == "__main__":
    main()
