#!/usr/bin/env python3
"""
Populate mocked_accounts table with standard demo accounts.

This script registers commonly used mock wallet addresses in the database
so they can be used for signal ownership in the demo.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv('config/.env')

from src.demo.signal_registry import SignalRegistry


def main():
    print("=" * 80)
    print("POPULATE MOCKED ACCOUNTS")
    print("=" * 80)
    print()

    # Initialize registry
    registry = SignalRegistry()

    # Define standard demo accounts
    accounts = [
        {
            "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1",
            "name": "Demo Account Alpha",
            "description": "Primary demo account for testing signal flows"
        },
        {
            "address": "0x9876543210abcdef9876543210abcdef98765432",
            "name": "Demo Account Beta",
            "description": "Secondary demo account for multi-user scenarios"
        },
        {
            "address": "0xabcdef1234567890abcdef1234567890abcdef12",
            "name": "Demo Account Gamma",
            "description": "Third demo account for complex workflows"
        },
        {
            "address": "0xDEMO_PIPELINE_OWNER",
            "name": "Demo Pipeline Owner",
            "description": "Unified owner account for E2E pipeline runs (news, agents, all outputs)"
        },
        {
            "address": "0xSUI_PIPELINE_PRODUCER",
            "name": "SUI Pipeline Producer",
            "description": "Automated SUI price pipeline producer account"
        },
        {
            "address": "0xNEWS_PIPELINE_PRODUCER",
            "name": "News Pipeline Producer",
            "description": "Automated news data pipeline producer account"
        },
        {
            "address": "0xAGENT_A_OWNER",
            "name": "Agent A Owner",
            "description": "Owner account for Agent A sentiment analysis signals"
        },
        {
            "address": "0xAGENT_B_OWNER",
            "name": "Agent B Owner",
            "description": "Owner account for Agent B investment prediction signals"
        },
        {
            "address": "0xAGENT_C_OWNER",
            "name": "Agent C Owner",
            "description": "Owner account for Agent C portfolio management signals"
        }
    ]

    print(f"Registering {len(accounts)} mocked accounts...")
    print()

    for account in accounts:
        registry.register_mocked_account(
            address=account["address"],
            name=account["name"],
            description=account["description"]
        )

    print()
    print("=" * 80)
    print("REGISTRATION COMPLETE")
    print("=" * 80)
    print()

    # Verify accounts
    all_accounts = registry.get_mocked_accounts()
    print(f"✅ Registered {len(all_accounts)} mocked accounts:")
    print()
    for account in all_accounts:
        print(f"  • {account['name']}")
        print(f"    Address: {account['address']}")
        if account['description']:
            print(f"    Description: {account['description']}")
        print()


if __name__ == "__main__":
    main()
