# Smart Contract Account Management on SUI

## Overview

This document explains how to implement Account Abstraction on SUI, allowing your main wallet to create and manage sub-accounts controlled by smart contracts.

## Architecture

### Traditional EOA (What we DON'T want)
```
Wallet A (private key A) → Independent
Wallet B (private key B) → Independent
Wallet C (private key C) → Independent
```
**Problem:** No on-chain relationship, must manage multiple private keys

### Smart Contract Accounts (What you WANT)
```
Your Main Wallet (one private key)
    ↓ (controls via smart contract)
Managed Account A, B, C... (no private keys needed)
```
**Benefit:** On-chain parent-child relationship, one private key controls all

## Implementation

### Step 1: Deploy Account Manager Contract

```move
// contracts/sources/account_manager.move
module publisher::account_manager {
    use sui::object::{Self, UID};
    use sui::transfer;
    use sui::tx_context::{Self, TxContext};
    use sui::coin::{Self, Coin};
    use sui::sui::SUI;
    use sui::balance::{Self, Balance};

    /// Managed account controlled by parent wallet
    struct ManagedAccount has key, store {
        id: UID,
        parent: address,           // Parent wallet that controls this account
        owner_label: address,      // Project identifier (can be any address)
        balance: Balance<SUI>,     // SUI balance for gas fees
        created_at: u64,
        is_active: bool
    }

    /// Event emitted when account is created
    struct AccountCreated has copy, drop {
        account_id: address,
        parent: address,
        owner_label: address
    }

    /// Create a new managed account
    /// Only parent wallet can call this
    public entry fun create_account(
        owner_label: address,
        ctx: &mut TxContext
    ) {
        let account = ManagedAccount {
            id: object::new(ctx),
            parent: tx_context::sender(ctx),
            owner_label: owner_label,
            balance: balance::zero(),
            created_at: tx_context::epoch(ctx),
            is_active: true
        };

        let account_id = object::uid_to_address(&account.id);

        // Emit event
        sui::event::emit(AccountCreated {
            account_id,
            parent: tx_context::sender(ctx),
            owner_label
        });

        // Share object so it can be used in transactions
        transfer::share_object(account);
    }

    /// Fund a managed account
    /// Only parent can fund
    public entry fun fund_account(
        account: &mut ManagedAccount,
        payment: Coin<SUI>,
        ctx: &mut TxContext
    ) {
        // Verify caller is parent
        assert!(account.parent == tx_context::sender(ctx), 0);
        assert!(account.is_active, 1);

        // Add funds to account balance
        let payment_balance = coin::into_balance(payment);
        balance::join(&mut account.balance, payment_balance);
    }

    /// Withdraw from managed account
    /// Only parent can withdraw
    public entry fun withdraw_from_account(
        account: &mut ManagedAccount,
        amount: u64,
        ctx: &mut TxContext
    ) {
        // Verify caller is parent
        assert!(account.parent == tx_context::sender(ctx), 0);
        assert!(account.is_active, 1);

        // Withdraw and send to parent
        let withdrawn = coin::take(&mut account.balance, amount, ctx);
        transfer::public_transfer(withdrawn, tx_context::sender(ctx));
    }

    /// Deactivate account (only parent)
    public entry fun deactivate_account(
        account: &mut ManagedAccount,
        ctx: &mut TxContext
    ) {
        assert!(account.parent == tx_context::sender(ctx), 0);
        account.is_active = false;
    }

    /// Get account balance
    public fun get_balance(account: &ManagedAccount): u64 {
        balance::value(&account.balance)
    }

    /// Verify parent
    public fun verify_parent(account: &ManagedAccount, caller: address): bool {
        account.parent == caller && account.is_active
    }
}
```

### Step 2: Python Integration

```python
# src/blockchain/account_manager.py
from typing import Optional
from pysui import SyncClient, SuiConfig
from pysui.sui.sui_txn import SyncTransaction
from pysui.sui.sui_types import ObjectID, SuiAddress

class SUIAccountManager:
    """
    Manages smart contract accounts on SUI.

    Your main wallet creates and controls multiple managed accounts.
    Each managed account has its own gas balance and can sign transactions.
    """

    def __init__(
        self,
        parent_private_key: str,
        package_id: str,
        network: str = "testnet"
    ):
        """
        Initialize account manager.

        Args:
            parent_private_key: Your main wallet private key
            package_id: Deployed account_manager contract package ID
            network: "testnet" or "mainnet"
        """
        self.config = SuiConfig.testnet_config() if network == "testnet" else SuiConfig.mainnet_config()
        self.client = SyncClient(self.config)
        self.parent_keypair = self._load_keypair(parent_private_key)
        self.package_id = package_id

    def create_managed_account(
        self,
        owner_label: str,
        initial_funding_sui: float = 0.1
    ) -> dict:
        """
        Create a new managed account controlled by your main wallet.

        Args:
            owner_label: Project identifier (can be any SUI address)
            initial_funding_sui: Initial SUI to fund the account

        Returns:
            Dict with account details:
            {
                "account_id": "0x...",
                "parent": "0x...",
                "owner_label": "0x...",
                "balance": 0.1
            }
        """
        txn = SyncTransaction(
            client=self.client,
            initial_sender=self.parent_keypair
        )

        # Call create_account function
        txn.move_call(
            target=f"{self.package_id}::account_manager::create_account",
            arguments=[
                owner_label  # owner_label parameter
            ]
        )

        # Execute transaction
        result = txn.execute(gas_budget=10_000_000)

        # Get created account ID from events
        account_id = self._extract_account_id_from_events(result)

        # Fund the account if requested
        if initial_funding_sui > 0:
            self.fund_account(account_id, initial_funding_sui)

        return {
            "account_id": account_id,
            "parent": self.parent_keypair.public_key.to_address(),
            "owner_label": owner_label,
            "balance": initial_funding_sui
        }

    def fund_account(
        self,
        account_id: str,
        amount_sui: float
    ) -> str:
        """
        Fund a managed account from your main wallet.

        Args:
            account_id: The managed account object ID
            amount_sui: Amount of SUI to transfer

        Returns:
            Transaction digest
        """
        txn = SyncTransaction(
            client=self.client,
            initial_sender=self.parent_keypair
        )

        # Split coin for payment
        amount_mist = int(amount_sui * 1_000_000_000)  # Convert SUI to MIST
        payment_coin = txn.split_coin(
            coin=txn.gas,
            amounts=[amount_mist]
        )

        # Call fund_account function
        txn.move_call(
            target=f"{self.package_id}::account_manager::fund_account",
            arguments=[
                account_id,    # &mut ManagedAccount
                payment_coin   # Coin<SUI>
            ]
        )

        result = txn.execute(gas_budget=10_000_000)
        return result.digest

    def get_account_balance(self, account_id: str) -> float:
        """
        Get balance of a managed account.

        Args:
            account_id: The managed account object ID

        Returns:
            Balance in SUI
        """
        # Query object
        account_obj = self.client.get_object(account_id)
        balance_mist = account_obj.data.content.fields.balance
        return balance_mist / 1_000_000_000  # Convert MIST to SUI

    def list_managed_accounts(self) -> list:
        """
        List all managed accounts created by your wallet.

        Returns:
            List of account dictionaries
        """
        # Query all ManagedAccount objects owned by events
        # (Implementation depends on your indexing strategy)
        pass
```

### Step 3: Integration with OnChainPublisher

```python
# Modified OnChainPublisher to use managed accounts

class OnChainPublisher:
    def __init__(
        self,
        parent_private_key: str,
        managed_account_id: Optional[str] = None,  # NEW
        walrus_client: Optional[WalrusClient] = None,
        package_id: str = None,
        account_manager_package: str = None,  # NEW
        simulated: bool = False
    ):
        """
        Publisher that can use managed accounts for gas.

        Args:
            parent_private_key: Your main wallet (creates transactions)
            managed_account_id: Optional managed account to pay gas from
            account_manager_package: Account manager contract package ID
        """
        self.parent_key = parent_private_key
        self.managed_account_id = managed_account_id
        self.account_manager = SUIAccountManager(
            parent_private_key=parent_private_key,
            package_id=account_manager_package
        ) if account_manager_package else None

    def publish_news_signal(
        self,
        news_data: Dict[str, Any],
        producer: str = "news_pipeline",
        use_managed_account: bool = True  # NEW
    ) -> NewsSignal:
        """
        Publish news signal, optionally using managed account for gas.
        """
        if use_managed_account and self.managed_account_id:
            # Use managed account's balance for gas
            return self._publish_with_managed_account(news_data, producer)
        else:
            # Use parent wallet for gas
            return self._publish_with_parent_wallet(news_data, producer)
```

## Usage Example

```python
from src.blockchain.account_manager import SUIAccountManager
from src.blockchain.sui_publisher import OnChainPublisher

# Step 1: Initialize account manager with your main wallet
account_mgr = SUIAccountManager(
    parent_private_key="suiprivkey1qqe5zz9t0...",  # Your ONE private key
    package_id="0xPACKAGE_ID",  # Deployed contract
    network="testnet"
)

# Step 2: Create managed accounts for different projects
project_a_account = account_mgr.create_managed_account(
    owner_label="0xProjectAAAAA",  # Can be any address as label
    initial_funding_sui=1.0  # Fund with 1 SUI for gas
)
# Returns: {"account_id": "0xManagedAccountA", "balance": 1.0}

project_b_account = account_mgr.create_managed_account(
    owner_label="0xProjectBBBBB",
    initial_funding_sui=0.5
)

# Step 3: Use managed accounts to publish data
publisher_a = OnChainPublisher(
    parent_private_key="suiprivkey1qqe5zz9t0...",  # Same key
    managed_account_id=project_a_account["account_id"],
    package_id="0xPUBLISHER_PACKAGE"
)

# Publish uses Project A's managed account for gas
signal = publisher_a.publish_news_signal(
    news_data={"articles": [...]},
    use_managed_account=True  # Gas paid from managed account balance
)

# Step 4: Monitor and refill accounts
balance = account_mgr.get_account_balance(project_a_account["account_id"])
if balance < 0.1:
    # Refill from main wallet
    account_mgr.fund_account(
        account_id=project_a_account["account_id"],
        amount_sui=1.0
    )
```

## Benefits

1. **One Private Key**: Control all accounts with your main wallet
2. **On-Chain Relationship**: Parent-child enforced by smart contract
3. **Separate Gas Budgets**: Each project has its own SUI balance
4. **Revocable**: Parent can deactivate accounts anytime
5. **Queryable**: Can find all accounts created by your wallet
6. **No Key Management**: Managed accounts don't have private keys

## Comparison

| Feature | Simple EOA | Managed Account |
|---------|-----------|-----------------|
| Private Keys | Multiple (1 per account) | One (parent only) |
| On-Chain Link | None | Smart contract enforced |
| Gas Management | Manual transfer | Parent funds on-demand |
| Revocable | No | Yes (parent can deactivate) |
| Query by Parent | No | Yes (events + indexing) |
| Security | Key per account | One key to manage all |
