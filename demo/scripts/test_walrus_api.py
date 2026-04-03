#!/usr/bin/env python3
"""
Test Walrus API Directly

Tests the actual Walrus HTTP API to find the correct format.
"""

import requests
import sys

def test_walrus_api():
    """Test Walrus HTTP API."""
    print("="*80)
    print("TESTING WALRUS HTTP API")
    print("="*80)
    print()

    publisher_url = "https://publisher.walrus-testnet.walrus.space"
    aggregator_url = "https://aggregator.walrus-testnet.walrus.space"

    # Test 1: Get API spec
    print("[Test 1] Fetching API spec...")
    try:
        response = requests.get(f"{publisher_url}/v1/api", timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✓ API spec available")
            # print(f"  Spec: {response.text[:500]}...")
        else:
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"  Error: {e}")
    print()

    # Test 2: Try storing a small blob
    print("[Test 2] Attempting to store blob...")
    test_data = b"Hello Walrus from Glass Box Protocol!"

    # Try different endpoints and methods
    endpoints_to_try = [
        ("PUT", f"{publisher_url}/v1/store"),
        ("POST", f"{publisher_url}/v1/store"),
        ("PUT", f"{publisher_url}/v1/blobs"),
        ("POST", f"{publisher_url}/v1/blobs"),
    ]

    for method, url in endpoints_to_try:
        print(f"\n  Trying {method} {url}...")
        try:
            if method == "PUT":
                response = requests.put(
                    url,
                    data=test_data,
                    headers={"Content-Type": "application/octet-stream"},
                    timeout=30
                )
            else:
                response = requests.post(
                    url,
                    data=test_data,
                    headers={"Content-Type": "application/octet-stream"},
                    timeout=30
                )

            print(f"    Status: {response.status_code}")
            if response.status_code in [200, 201]:
                print(f"    ✓ SUCCESS!")
                print(f"    Response: {response.text[:500]}")
                return True
            else:
                print(f"    Response: {response.text[:200]}")

        except Exception as e:
            print(f"    Error: {e}")

    print()
    print("="*80)
    print("Could not find working endpoint")
    print("="*80)
    return False


if __name__ == "__main__":
    success = test_walrus_api()
    sys.exit(0 if success else 1)
