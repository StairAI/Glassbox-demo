#!/usr/bin/env python3
"""
Test that the API correctly returns only enabled accounts.
"""

import sys
import os
from pathlib import Path

# Add demo directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.activity_db import ActivityDB


def main():
    print("=" * 80)
    print("Testing API Owners Endpoint Filtering")
    print("=" * 80)
    print()

    # Initialize database (this simulates what the API server does)
    db = ActivityDB(db_path="data/activity.db")

    print("What the API endpoint '/api/owners' returns:")
    print("-" * 80)

    # This is what the API does: list_mocked_accounts(active_only=True)
    # With our changes, it now defaults to enabled_only=True
    accounts = db.list_mocked_accounts(active_only=True, enabled_only=True)

    print(f"Found {len(accounts)} enabled accounts:")
    for acc in accounts:
        print(f"  - Address: {acc['account_address']}")
        print(f"    Project: {acc['project_name']}")
        print(f"    Enabled: {acc.get('enabled', 'N/A')}")
        print()

    print("These are the accounts that will appear in the visualization dropdown.")
    print()

    print("All accounts in database (including disabled):")
    print("-" * 80)
    all_accounts = db.list_mocked_accounts(active_only=True, enabled_only=False)
    print(f"Total accounts: {len(all_accounts)}")
    for acc in all_accounts:
        enabled_status = "✓ Enabled" if acc.get('enabled', 1) == 1 else "✗ Disabled"
        print(f"  {enabled_status}: {acc['project_name']} ({acc['account_address'][:20]}...)")
    print()


if __name__ == "__main__":
    main()
