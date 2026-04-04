#!/usr/bin/env python3
"""
Test Real Walrus Storage

This script tests storing and fetching data from Walrus testnet.
"""

import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.storage.walrus_client import WalrusClient, WalrusHelper

# Load environment
load_dotenv("config/.env")


def test_walrus_storage():
    """Test real Walrus storage."""
    print("="*80)
    print("TESTING REAL WALRUS STORAGE")
    print("="*80)
    print()

    # Check if Walrus is enabled
    walrus_enabled = os.getenv("WALRUS_ENABLED", "false").lower() == "true"
    publisher_url = os.getenv("WALRUS_PUBLISHER_URL")
    aggregator_url = os.getenv("WALRUS_AGGREGATOR_URL")

    print(f"Walrus Enabled: {walrus_enabled}")
    print(f"Publisher URL: {publisher_url}")
    print(f"Aggregator URL: {aggregator_url}")
    print()

    # Create client (will use real Walrus if not simulated)
    simulated = not walrus_enabled
    client = WalrusClient(
        publisher_url=publisher_url,
        aggregator_url=aggregator_url,
        simulated=simulated
    )

    print(f"Client mode: {'SIMULATED' if simulated else 'REAL WALRUS TESTNET'}")
    print()

    # Test 1: Store simple text
    print("[Test 1] Storing simple text data...")
    test_data = b"Hello from Glass Box Protocol! This is a test of Walrus storage."
    blob_id = client.store(test_data)
    print(f"  ✓ Stored successfully")
    print(f"  ✓ Blob ID: {blob_id}")
    print()

    # Test 2: Fetch the data back
    print("[Test 2] Fetching data from Walrus...")
    fetched_data = client.fetch(blob_id)
    print(f"  ✓ Fetched successfully")
    print(f"  ✓ Data: {fetched_data.decode()[:50]}...")
    print()

    # Test 3: Verify data integrity
    print("[Test 3] Verifying data integrity...")
    if fetched_data == test_data:
        print(f"  ✓ Data integrity verified!")
    else:
        print(f"  ✗ Data mismatch!")
        return False
    print()

    # Test 4: Store JSON data
    print("[Test 4] Storing JSON data...")
    json_data = {
        "test": "walrus_storage",
        "articles": [
            {"title": "Bitcoin hits $70k", "source": "cryptopanic"},
            {"title": "Ethereum upgrade", "source": "cryptopanic"}
        ],
        "total_count": 2
    }
    json_blob_id = WalrusHelper.store_json(client, json_data)
    print(f"  ✓ JSON stored successfully")
    print(f"  ✓ Blob ID: {json_blob_id}")
    print()

    # Test 5: Fetch JSON back
    print("[Test 5] Fetching JSON from Walrus...")
    fetched_json = WalrusHelper.fetch_json(client, json_blob_id)
    print(f"  ✓ JSON fetched successfully")
    print(f"  ✓ Articles count: {fetched_json['total_count']}")
    print()

    # Test 6: Verify JSON integrity
    print("[Test 6] Verifying JSON integrity...")
    if fetched_json == json_data:
        print(f"  ✓ JSON data integrity verified!")
    else:
        print(f"  ✗ JSON data mismatch!")
        return False
    print()

    # Test 7: Check if blob exists
    print("[Test 7] Checking blob existence...")
    exists = client.exists(blob_id)
    print(f"  ✓ Blob exists: {exists}")
    print()

    # Test 8: Get blob info
    print("[Test 8] Getting blob info...")
    try:
        info = client.get_blob_info(blob_id)
        print(f"  ✓ Blob info: {info}")
    except Exception as e:
        print(f"  Note: {e}")
    print()

    print("="*80)
    print("WALRUS STORAGE TEST: SUCCESS")
    print("="*80)
    print()
    print("Summary:")
    print(f"  Mode: {'SIMULATED' if simulated else 'REAL WALRUS TESTNET'}")
    print(f"  Text blob ID: {blob_id[:32]}...")
    print(f"  JSON blob ID: {json_blob_id[:32]}...")
    print()

    if not simulated:
        print("🎉 Real Walrus testnet storage is working!")
        print()
        print("Next steps:")
        print("1. Integrate with NewsPipeline")
        print("2. Store news data on Walrus")
        print("3. Create signals in SignalRegistry")
        print("4. Build agent to fetch and process data")
    else:
        print("Note: Running in simulated mode.")
        print("To use real Walrus, set WALRUS_ENABLED=true in .env")

    print()
    return True


if __name__ == "__main__":
    try:
        success = test_walrus_storage()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
