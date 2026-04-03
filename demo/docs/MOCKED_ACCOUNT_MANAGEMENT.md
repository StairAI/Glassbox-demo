# Mocked Account Management

## Overview

The system now includes a database table to track "mocked account addresses" used for indexing and organizing data across different projects. This provides a centralized registry of all account addresses being used, their purposes, and metadata.

## What Are Mocked Accounts?

In the current implementation using the **Sponsor Pattern**, data ownership is managed through metadata fields rather than separate private keys:

- **Transaction Signer**: Your main wallet (with private key) signs all transactions and pays gas
- **Data Owner**: Configurable address stored in trigger metadata (no private key needed)

"Mocked accounts" are these owner addresses - they're used for indexing and organization, but don't require separate private keys or gas funding.

## Database Schema

The `mocked_accounts` table tracks:

```sql
CREATE TABLE mocked_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    account_address TEXT UNIQUE NOT NULL,      -- The mocked account address
    project_name TEXT NOT NULL,                 -- Project identifier
    description TEXT,                           -- Human-readable description
    is_active INTEGER DEFAULT 1,                -- Active/inactive status
    metadata TEXT                               -- JSON metadata
)
```

**Indexes:**
- `account_address` (unique constraint + index)
- `project_name` (index for filtering)

## API Methods

### 1. Register Mocked Account

```python
from src.storage.activity_db import ActivityDB

db = ActivityDB("data/activity.db")

# Register a new mocked account
account_id = db.register_mocked_account(
    account_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1",
    project_name="BTC-News-Pipeline",
    description="Bitcoin news sentiment analysis project",
    metadata={"currency": "BTC", "frequency": "5min"}
)

# Returns: ID of registered account (or existing ID if duplicate)
```

**Note:** If the address already exists, returns the existing ID without error.

### 2. Get Account by Address

```python
account = db.get_mocked_account("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1")

# Returns:
# {
#     "id": 1,
#     "created_at": "2026-04-01T07:11:49.118620",
#     "account_address": "0x742d35...",
#     "project_name": "BTC-News-Pipeline",
#     "description": "Bitcoin news sentiment analysis project",
#     "is_active": 1,
#     "metadata": '{"currency": "BTC", "frequency": "5min"}'
# }
```

### 3. List Accounts

```python
# List all active accounts
accounts = db.list_mocked_accounts(active_only=True)

# Filter by project name
btc_accounts = db.list_mocked_accounts(project_name="BTC-News-Pipeline")

# List all accounts including inactive
all_accounts = db.list_mocked_accounts(active_only=False)
```

### 4. Update Account

```python
# Update any field(s)
success = db.update_mocked_account(
    account_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1",
    description="Bitcoin news sentiment - UPDATED",
    metadata={"currency": "BTC", "frequency": "10min", "updated": True}
)
# Returns: True if updated, False if not found
```

### 5. Deactivate Account

```python
# Mark account as inactive (soft delete)
success = db.deactivate_mocked_account("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1")
# Returns: True if deactivated, False if not found
```

## Pipeline Integration

The news pipeline automatically registers mocked accounts when initialized:

```python
from src.pipeline.news_pipeline_v2 import NewsPipelineV2
from src.blockchain.sui_publisher import OnChainPublisher
from src.storage.activity_db import ActivityDB

# Initialize components
db = ActivityDB("data/activity.db")
publisher = OnChainPublisher(
    owner_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1"
)

# Pipeline automatically registers the owner address
pipeline = NewsPipelineV2(
    api_token="YOUR_TOKEN",
    publisher=publisher,
    db=db,
    owner_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1",
    auto_register_account=True  # Default: True
)

# The owner address is now registered in mocked_accounts table
# under project_name="news_pipeline_v2"
```

**To disable auto-registration:**

```python
pipeline = NewsPipelineV2(
    ...,
    auto_register_account=False  # Don't register account
)
```

## Use Cases

### 1. Multi-Project Organization

Track different accounts used for different purposes:

```python
# Register accounts for different projects
db.register_mocked_account(
    account_address="0xProjectA...",
    project_name="BTC-Sentiment-Analysis",
    description="Bitcoin sentiment tracking"
)

db.register_mocked_account(
    account_address="0xProjectB...",
    project_name="SUI-Ecosystem-News",
    description="SUI ecosystem updates"
)

db.register_mocked_account(
    account_address="0xProjectC...",
    project_name="Multi-Token-Aggregator",
    description="Cross-chain sentiment aggregation"
)
```

### 2. Query by Project

```python
# Find all accounts for a specific project
project_accounts = db.list_mocked_accounts(project_name="BTC-Sentiment-Analysis")

for account in project_accounts:
    print(f"Address: {account['account_address']}")
    print(f"Description: {account['description']}")
```

### 3. Deactivate Old Projects

```python
# Deactivate accounts for deprecated projects
db.deactivate_mocked_account("0xOldProjectAddress...")

# List only active accounts
active_accounts = db.list_mocked_accounts(active_only=True)
```

### 4. Track Metadata

Store additional context in the metadata field:

```python
db.register_mocked_account(
    account_address="0x...",
    project_name="News-Pipeline",
    metadata={
        "currencies": ["BTC", "ETH", "SUI"],
        "fetch_frequency_seconds": 300,
        "start_date": "2026-04-01",
        "owner_email": "project@example.com"
    }
)
```

## Database Statistics

The mocked accounts table is included in database statistics:

```python
stats = db.get_stats()

print(f"Mocked Accounts: {stats['mocked_accounts']}")
print(f"News Articles: {stats['news_articles']}")
print(f"API Calls: {stats['api_calls']}")
```

## Testing

Run the test script to verify functionality:

```bash
python scripts/test_mocked_accounts.py
```

This demonstrates:
- Account registration
- Querying by address and project
- Updating account details
- Deactivation
- Filtering active/inactive accounts

## Future: Smart Contract Accounts

This mocked account system provides indexing for the current **Sponsor Pattern** implementation. In the future, when implementing **Smart Contract Account Management** (Phase 2), these mocked accounts can be migrated to real on-chain managed accounts.

See [SMART_CONTRACT_ACCOUNTS.md](./SMART_CONTRACT_ACCOUNTS.md) for the future roadmap.

## Comparison

| Feature | Mocked Accounts (Current) | Smart Contract Accounts (Future) |
|---------|---------------------------|----------------------------------|
| Private Keys | None (metadata only) | None (controlled by parent) |
| On-Chain Relationship | No (database tracking) | Yes (smart contract enforced) |
| Gas Management | Parent wallet pays all | Separate gas budgets |
| Deactivation | Database flag | On-chain revocation |
| Queryability | Database queries | On-chain events + indexing |
| Implementation | ✓ Complete | Phase 2 roadmap |

## Summary

Mocked account management provides:

1. **Centralized Registry**: Track all account addresses in one place
2. **Project Organization**: Group accounts by project name
3. **Metadata Storage**: Store additional context about each account
4. **Soft Deletion**: Deactivate accounts without losing history
5. **Easy Querying**: Filter by project, address, or active status
6. **Pipeline Integration**: Automatic registration when pipelines are initialized

This system provides the indexing and organizational benefits of multiple accounts while maintaining the simplicity of the Sponsor Pattern (one private key for all transactions).
