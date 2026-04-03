#!/usr/bin/env python3
"""
Test script for mocked account management functionality.

Demonstrates how to:
- Register mocked account addresses for different projects
- Query accounts by address or project
- Update account details
- Deactivate accounts
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.activity_db import ActivityDB


def main():
    print("="*80)
    print("MOCKED ACCOUNT MANAGEMENT TEST")
    print("="*80)

    # Initialize database
    db = ActivityDB(db_path="data/activity.db")

    # Test 1: Register mocked accounts
    print("\n[1] REGISTERING MOCKED ACCOUNTS")
    print("-" * 80)

    account1 = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1"
    account2 = "0x9876543210abcdef9876543210abcdef98765432"
    account3 = "0xabcdef1234567890abcdef1234567890abcdef12"

    id1 = db.register_mocked_account(
        account_address=account1,
        project_name="BTC-News-Pipeline",
        description="Bitcoin news sentiment analysis project",
        metadata={"currency": "BTC", "frequency": "5min"}
    )
    print(f"  ✓ Registered account for BTC-News-Pipeline (ID: {id1})")
    print(f"    Address: {account1}")

    id2 = db.register_mocked_account(
        account_address=account2,
        project_name="SUI-News-Pipeline",
        description="SUI ecosystem news tracking",
        metadata={"currency": "SUI", "frequency": "10min"}
    )
    print(f"  ✓ Registered account for SUI-News-Pipeline (ID: {id2})")
    print(f"    Address: {account2}")

    id3 = db.register_mocked_account(
        account_address=account3,
        project_name="Multi-Token-Sentiment",
        description="Multi-token sentiment aggregator",
        metadata={"currencies": ["BTC", "ETH", "SUI"], "frequency": "15min"}
    )
    print(f"  ✓ Registered account for Multi-Token-Sentiment (ID: {id3})")
    print(f"    Address: {account3}")

    # Test duplicate registration (should return existing ID)
    id1_dup = db.register_mocked_account(
        account_address=account1,
        project_name="BTC-News-Pipeline-V2"  # Different project name
    )
    print(f"  ℹ Duplicate registration returned existing ID: {id1_dup} (same as {id1})")

    # Test 2: Get account by address
    print("\n[2] QUERYING ACCOUNT BY ADDRESS")
    print("-" * 80)

    account = db.get_mocked_account(account1)
    if account:
        print(f"  Account Details:")
        print(f"    ID: {account['id']}")
        print(f"    Address: {account['account_address']}")
        print(f"    Project: {account['project_name']}")
        print(f"    Description: {account['description']}")
        print(f"    Created: {account['created_at']}")
        print(f"    Active: {'Yes' if account['is_active'] else 'No'}")
        print(f"    Metadata: {account['metadata']}")

    # Test 3: List all accounts
    print("\n[3] LISTING ALL ACTIVE ACCOUNTS")
    print("-" * 80)

    accounts = db.list_mocked_accounts(active_only=True)
    print(f"  Found {len(accounts)} active account(s):\n")

    for acc in accounts:
        print(f"  - {acc['project_name']}")
        print(f"    Address: {acc['account_address'][:42]}...")
        print(f"    Description: {acc['description']}")
        print()

    # Test 4: Filter by project name
    print("[4] FILTERING BY PROJECT NAME")
    print("-" * 80)

    btc_accounts = db.list_mocked_accounts(project_name="BTC-News-Pipeline")
    print(f"  Accounts for 'BTC-News-Pipeline': {len(btc_accounts)}")
    for acc in btc_accounts:
        print(f"    - {acc['account_address']}")

    # Test 5: Update account details
    print("\n[5] UPDATING ACCOUNT DETAILS")
    print("-" * 80)

    success = db.update_mocked_account(
        account_address=account2,
        description="SUI ecosystem news tracking - UPDATED",
        metadata={"currency": "SUI", "frequency": "5min", "updated": True}
    )
    print(f"  ✓ Updated account {account2[:20]}... - Success: {success}")

    # Verify update
    updated_account = db.get_mocked_account(account2)
    print(f"    New description: {updated_account['description']}")
    print(f"    New metadata: {updated_account['metadata']}")

    # Test 6: Deactivate account
    print("\n[6] DEACTIVATING ACCOUNT")
    print("-" * 80)

    success = db.deactivate_mocked_account(account3)
    print(f"  ✓ Deactivated account {account3[:20]}... - Success: {success}")

    # Verify deactivation
    deactivated = db.get_mocked_account(account3)
    print(f"    Account status: {'Active' if deactivated['is_active'] else 'Inactive'}")

    # List active accounts again (should exclude deactivated)
    print("\n[7] LISTING ACTIVE ACCOUNTS (AFTER DEACTIVATION)")
    print("-" * 80)

    active_accounts = db.list_mocked_accounts(active_only=True)
    print(f"  Active accounts: {len(active_accounts)}")
    for acc in active_accounts:
        print(f"    - {acc['project_name']}: {acc['account_address'][:20]}...")

    # List ALL accounts including inactive
    all_accounts = db.list_mocked_accounts(active_only=False)
    print(f"\n  All accounts (including inactive): {len(all_accounts)}")
    for acc in all_accounts:
        status = "✓ Active" if acc['is_active'] else "✗ Inactive"
        print(f"    - {acc['project_name']}: {status}")

    # Test 8: Database statistics
    print("\n[8] DATABASE STATISTICS")
    print("-" * 80)

    stats = db.get_stats()
    print(f"  Mocked Accounts: {stats.get('mocked_accounts', 0)}")
    print(f"  News Articles: {stats.get('news_articles', 0)}")
    print(f"  API Calls: {stats.get('api_calls', 0)}")
    print(f"  Walrus Operations: {stats.get('walrus_operations', 0)}")
    print(f"  SUI Transactions: {stats.get('sui_transactions', 0)}")

    print("\n" + "="*80)
    print("MOCKED ACCOUNT MANAGEMENT TEST COMPLETE")
    print("="*80 + "\n")

    # Close database
    db.close()


if __name__ == "__main__":
    main()
