#!/usr/bin/env python3
"""
Test the new 'enabled' field in mocked_accounts table.

This script demonstrates:
1. Adding the enabled field to existing accounts
2. Filtering accounts by enabled status
3. Updating account enabled status
"""

import sys
import os
from pathlib import Path

# Add demo directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.activity_db import ActivityDB


def main():
    print("=" * 80)
    print("Testing 'enabled' Field in Mocked Accounts")
    print("=" * 80)
    print()

    # Initialize database
    db = ActivityDB(db_path="data/activity.db")

    print("Step 1: List all accounts (enabled only)")
    print("-" * 80)
    enabled_accounts = db.list_mocked_accounts(active_only=True, enabled_only=True)
    print(f"Found {len(enabled_accounts)} enabled accounts:")
    for acc in enabled_accounts:
        print(f"  - {acc['account_address'][:20]}... | {acc['project_name']} | enabled={acc.get('enabled', 'N/A')}")
    print()

    print("Step 2: List all accounts (including disabled)")
    print("-" * 80)
    all_accounts = db.list_mocked_accounts(active_only=True, enabled_only=False)
    print(f"Found {len(all_accounts)} total accounts:")
    for acc in all_accounts:
        print(f"  - {acc['account_address'][:20]}... | {acc['project_name']} | enabled={acc.get('enabled', 'N/A')}")
    print()

    if len(all_accounts) > 1:
        # Test disabling second account
        test_account = all_accounts[1]
        print(f"Step 3: Disable account '{test_account['project_name']}'")
        print("-" * 80)
        success = db.update_mocked_account(
            account_address=test_account['account_address'],
            enabled=False
        )
        print(f"Update result: {'Success' if success else 'Failed'}")
        print()

        print("Step 4: List enabled accounts again")
        print("-" * 80)
        enabled_accounts = db.list_mocked_accounts(active_only=True, enabled_only=True)
        print(f"Found {len(enabled_accounts)} enabled accounts:")
        for acc in enabled_accounts:
            print(f"  - {acc['account_address'][:20]}... | {acc['project_name']}")
        print()

        print(f"Step 5: Re-enable account '{test_account['project_name']}'")
        print("-" * 80)
        success = db.update_mocked_account(
            account_address=test_account['account_address'],
            enabled=True
        )
        print(f"Update result: {'Success' if success else 'Failed'}")
        print()

    print("Step 6: Register a new account with enabled=False")
    print("-" * 80)
    new_account_id = db.register_mocked_account(
        account_address="0xTEST_DISABLED_ACCOUNT_12345678901234567890",
        project_name="Test-Disabled-Account",
        description="Test account that is disabled by default",
        enabled=False
    )
    print(f"Registered account ID: {new_account_id}")
    print()

    print("Step 7: Verify new disabled account is not in enabled list")
    print("-" * 80)
    enabled_accounts = db.list_mocked_accounts(active_only=True, enabled_only=True)
    print(f"Enabled accounts: {len(enabled_accounts)}")
    all_accounts = db.list_mocked_accounts(active_only=True, enabled_only=False)
    print(f"All accounts: {len(all_accounts)}")
    print(f"Disabled accounts: {len(all_accounts) - len(enabled_accounts)}")
    print()

    print("=" * 80)
    print("✓ Test Complete")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"- Total accounts: {len(all_accounts)}")
    print(f"- Enabled accounts: {len(enabled_accounts)}")
    print(f"- Disabled accounts: {len(all_accounts) - len(enabled_accounts)}")
    print()
    print("The visualization will now only show enabled accounts in the dropdown.")
    print()


if __name__ == "__main__":
    main()
