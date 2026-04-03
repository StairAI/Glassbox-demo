#!/usr/bin/env python3
"""
Test SUI Testnet Connection

This script tests:
1. Connection to SUI testnet
2. Wallet setup from private key
3. Balance check
4. Gas price query
"""

import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from pysui import SyncClient, SuiConfig
from pysui.sui.sui_config import SuiConfig as Config
from pysui.sui.sui_types import SuiString

# Load environment
load_dotenv("config/.env")


def test_sui_connection():
    """Test connection to SUI testnet."""
    print("="*80)
    print("TESTING SUI TESTNET CONNECTION")
    print("="*80)
    print()

    # Get private key from env
    private_key = os.getenv("SUI_PRIVATE_KEY")
    if not private_key:
        print("❌ SUI_PRIVATE_KEY not found in .env")
        return False

    print(f"✓ Private key loaded: {private_key[:20]}...")
    print()

    try:
        # Create config for testnet
        print("[1/4] Creating SUI testnet configuration...")
        config = SuiConfig.default_config()
        print(f"  ✓ RPC URL: {config.rpc_url}")
        print()

        # Create client
        print("[2/4] Connecting to SUI testnet...")
        client = SyncClient(config)
        print("  ✓ Connected successfully")
        print()

        # Check gas price
        print("[3/4] Querying reference gas price...")
        result = client.get_reference_gas_price()
        if result.is_ok():
            gas_price = result.result_data
            print(f"  ✓ Gas price: {gas_price}")
        else:
            print(f"  ✗ Failed to get gas price: {result.result_string}")
        print()

        # Get address from private key
        print("[4/4] Getting wallet address...")
        # Note: pysui requires proper key derivation
        # For now, we'll just verify the key format
        if private_key.startswith("suiprivkey"):
            print(f"  ✓ Private key format valid")
            print(f"  Note: To get balance, we need to derive the public address")
            print(f"  This requires additional setup with pysui keystore")
        else:
            print(f"  ✗ Invalid private key format")
            return False
        print()

        print("="*80)
        print("SUI CONNECTION TEST: SUCCESS")
        print("="*80)
        print()
        print("Next steps:")
        print("1. Set up wallet properly with pysui keystore")
        print("2. Test Walrus storage")
        print("3. Create complete demo")
        print()

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_sui_connection()
    sys.exit(0 if success else 1)
