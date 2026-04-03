#!/usr/bin/env python3
"""
Disable all existing mocked accounts from visualization.

This script sets enabled=0 for all accounts, making them invisible in the frontend.
"""

import sys
import os
from pathlib import Path

# Add demo directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.activity_db import ActivityDB


def main():
    print("=" * 80)
    print("Disabling All Mocked Accounts")
    print("=" * 80)
    print()

    # Initialize database
    db = ActivityDB(db_path="data/activity.db")

    # Get all accounts (including already disabled ones)
    all_accounts = db.list_mocked_accounts(active_only=True, enabled_only=False)

    print(f"Found {len(all_accounts)} accounts in database")
    print()

    disabled_count = 0
    for acc in all_accounts:
        address = acc['account_address']
        project_name = acc['project_name']
        current_status = acc.get('enabled', 1)

        if current_status == 1:
            # Disable this account
            success = db.update_mocked_account(
                account_address=address,
                enabled=False
            )

            if success:
                print(f"✓ Disabled: {project_name} ({address[:20]}...)")
                disabled_count += 1
            else:
                print(f"✗ Failed to disable: {project_name}")
        else:
            print(f"  Already disabled: {project_name} ({address[:20]}...)")

    print()
    print("=" * 80)
    print(f"Disabled {disabled_count} account(s)")
    print("=" * 80)
    print()

    # Verify
    enabled_accounts = db.list_mocked_accounts(active_only=True, enabled_only=True)
    print(f"Enabled accounts remaining: {len(enabled_accounts)}")
    print()
    print("All accounts are now invisible in the visualization frontend.")
    print()


if __name__ == "__main__":
    main()
