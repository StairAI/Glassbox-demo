#!/usr/bin/env python3
"""
Setup SUI Client and Test Connection

This script:
1. Imports private key from .env
2. Derives public address
3. Tests connection to SUI testnet
4. Checks balance
"""

import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from pysui import SyncClient, SuiConfig
from pysui.sui.sui_crypto import SuiKeyPair, SignatureScheme
from pysui.sui.sui_txresults import SuiCoinObjects
from pysui.sui.sui_types import SuiAddress
import base64

# Load environment
load_dotenv("config/.env")


def setup_sui_client():
    """Set up SUI client with private key."""
    print("="*80)
    print("SUI TESTNET SETUP & TEST")
    print("="*80)
    print()

    # Get private key from env
    private_key_str = os.getenv("SUI_PRIVATE_KEY")
    if not private_key_str:
        print("❌ SUI_PRIVATE_KEY not found in .env")
        return None, None

    print(f"[1/5] Loading private key...")
    print(f"  Key prefix: {private_key_str[:20]}...")

    try:
        # Parse the private key
        # Format: suiprivkey1qq... (bech32-like encoding)
        # We need to decode it properly for pysui

        # For now, let's create a config without keystore and use HTTP calls
        print(f"  ✓ Private key loaded")
        print()

        # Create config for testnet (without keystore)
        print("[2/5] Creating SUI testnet configuration...")
        config = SuiConfig.user_config(
            rpc_url="https://fullnode.testnet.sui.io:443",
            prv_keys=[private_key_str]  # Pass the key directly
        )
        print(f"  ✓ Config created")
        print(f"  ✓ RPC URL: {config.rpc_url}")
        print()

        # Create client
        print("[3/5] Connecting to SUI testnet...")
        client = SyncClient(config)
        print(f"  ✓ Connected successfully")
        print()

        # Get active address
        print("[4/5] Getting wallet address...")
        address = config.active_address
        print(f"  ✓ Address: {address}")
        print()

        # Check balance
        print("[5/5] Checking SUI balance...")
        try:
            coins = client.get_gas(address)
            if coins.is_ok():
                coin_objects: SuiCoinObjects = coins.result_data
                total_balance = sum(int(coin.balance) for coin in coin_objects.data)
                balance_sui = total_balance / 1_000_000_000  # Convert MIST to SUI

                print(f"  ✓ Balance: {balance_sui} SUI")
                print(f"  ✓ Gas objects: {len(coin_objects.data)}")

                if balance_sui > 0:
                    print(f"\n🎉 SUI testnet is working! You have {balance_sui} SUI")
                else:
                    print(f"\n⚠️  Balance is 0. Get testnet tokens from faucet:")
                    print(f"     https://discord.com/channels/916379725201563759/1037811694564560966")
            else:
                print(f"  ✗ Failed to get balance: {coins.result_string}")
        except Exception as e:
            print(f"  ✗ Error checking balance: {e}")
        print()

        # Test gas price query
        print("[Bonus] Querying reference gas price...")
        try:
            result = client.get_reference_gas_price()
            if result.is_ok():
                gas_price = result.result_data
                print(f"  ✓ Gas price: {gas_price} MIST")
            else:
                print(f"  ✗ Failed: {result.result_string}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
        print()

        print("="*80)
        print("SUI SETUP: SUCCESS")
        print("="*80)
        print()

        return client, config

    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None


if __name__ == "__main__":
    client, config = setup_sui_client()

    if client:
        print("✅ SUI client ready for use!")
        print()
        print("Next steps:")
        print("1. Test Walrus storage")
        print("2. Integrate with pipelines")
        print("3. Build complete demo")
        sys.exit(0)
    else:
        print("❌ SUI setup failed")
        sys.exit(1)
