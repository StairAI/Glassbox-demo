# SUI Wallet Ownership Architecture

## Overview

Yes, you can create EOA wallets on SUI and make data ownership configurable. Here's how it works:

## Key Concepts

### 1. **Your Personal Wallet (Gas Payer)**
- The wallet with the private key you control
- **Role:** Signs transactions and pays gas fees
- **Does NOT** have to be the data owner

### 2. **Data Owner (Configurable)**
- The address that "owns" the on-chain objects
- Can be ANY SUI address (doesn't need private key)
- Embedded in object metadata

### 3. **Separation of Concerns**
```
┌─────────────────────────────────────────────────────────┐
│              Transaction Signing vs Ownership           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Transaction Signer (Your Wallet)                      │
│  └─> Has private key                                   │
│  └─> Pays gas fees                                     │
│  └─> Signs all transactions                            │
│                                                         │
│  Object Owner (Configurable Address)                   │
│  └─> Recorded in object metadata                       │
│  └─> Visible on blockchain                             │
│  └─> Can query "owned" objects                         │
│  └─> Does NOT need private key                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## How SUI Ownership Works

### **On SUI, there are 2 types of "ownership":**

#### **A. Object Owner (Built-in SUI field)**
```move
// In SUI Move smart contract
public struct NewsTrigger has key {
    id: UID,
    // This is set by SUI framework automatically
    // Owner = transaction signer by default
}
```

#### **B. Metadata Owner (Custom field)** ← **Recommended for your use case**
```move
public struct NewsTrigger has key {
    id: UID,
    owner: address,  // ← Custom field, fully configurable
    creator: address, // ← Who created it (your wallet)
    walrus_blob_id: String,
    ...
}
```

## Implementation Options

### **Option 1: Sponsor Pattern (Recommended)**

Your wallet sponsors transactions but data is owned by a configurable address:

```python
# Your wallet (has private key, pays gas)
sponsor_wallet = "0xYourPersonalWallet"

# Configurable data owner (can be any address)
data_owner = "0xProjectWallet"  # Or "0xUserWallet", etc.

# Create object
registry.register_trigger({
    "owner": data_owner,          # ← Configurable!
    "creator": sponsor_wallet,    # ← Your wallet (immutable)
    "walrus_blob_id": blob_id,
    ...
})

# Transaction signature
# - Signed by: sponsor_wallet (your private key)
# - Gas paid by: sponsor_wallet
# - Object owner field: data_owner
```

**Benefits:**
- ✅ Separate payment from ownership
- ✅ Owner is configurable (no private key needed)
- ✅ Your wallet can sponsor for multiple projects
- ✅ Easy to transfer ownership later

### **Option 2: Create New Wallets Programmatically**

Generate new EOA wallets on the fly:

```python
import hashlib
import secrets

def create_sui_wallet():
    """Create a new SUI wallet (Ed25519 keypair)."""
    # Generate random 32-byte private key
    private_key = secrets.token_bytes(32)

    # Derive public key and address
    # (In production, use SUI SDK or cryptography library)
    address = derive_sui_address(private_key)

    return {
        "private_key": private_key.hex(),
        "address": address,
        "type": "EOA"
    }

# Usage
project_wallet = create_sui_wallet()
print(f"New wallet address: {project_wallet['address']}")

# Use as data owner
registry.register_trigger({
    "owner": project_wallet['address'],  # New wallet
    ...
})
```

**Benefits:**
- ✅ True separate wallets
- ✅ Can transfer tokens to these wallets
- ✅ Complete isolation

**Drawbacks:**
- ❌ Need to manage multiple private keys
- ❌ Each wallet needs SUI tokens for gas (if signing)

### **Option 3: Hierarchical Deterministic (HD) Wallets**

Derive multiple wallets from a single seed phrase:

```python
# Single seed phrase
seed = "your twelve word seed phrase goes here..."

# Derive multiple wallets
wallet_0 = derive_wallet(seed, path="m/44'/784'/0'/0'/0'")  # Your main wallet
wallet_1 = derive_wallet(seed, path="m/44'/784'/0'/0'/1'")  # Project A
wallet_2 = derive_wallet(seed, path="m/44'/784'/0'/0'/2'")  # Project B

# Use different wallets for different projects
register_trigger(owner=wallet_1['address'])  # Project A
register_trigger(owner=wallet_2['address'])  # Project B
```

**Benefits:**
- ✅ Single seed backs up all wallets
- ✅ Deterministic (same seed = same wallets)
- ✅ Industry standard (BIP-44)

## Recommended Architecture for Your Use Case

```python
# demo/config/.env
SUI_PRIVATE_KEY=0xYourPersonalKey  # Gas payer
PROJECT_OWNER_ADDRESS=0xConfigurableAddress  # Data owner

# Code
class OnChainPublisher:
    def __init__(
        self,
        private_key: str,        # Your wallet (signs tx)
        owner_address: str = None  # Configurable owner
    ):
        self.signer = private_key
        self.owner = owner_address or derive_address(private_key)

    def publish_news_trigger(self, news_data):
        # Create trigger object
        trigger = {
            "owner": self.owner,      # ← Configurable
            "creator": self.signer_address,
            "walrus_blob_id": blob_id,
            ...
        }

        # Sign with your wallet, but owner field is different
        return self.sign_and_submit(trigger)
```

## Query by Owner

```python
# Query all objects owned by specific address
triggers = registry.get_triggers(owner="0xProjectAddress")

# Query by creator (who paid for it)
triggers = registry.get_triggers(creator="0xYourWallet")

# Both fields are indexed and queryable
```

## Example: Multi-Project Setup

```python
# Project A
publisher_a = OnChainPublisher(
    private_key=YOUR_KEY,
    owner_address="0xProjectA_Address"
)
publisher_a.publish_news_trigger(data)

# Project B
publisher_b = OnChainPublisher(
    private_key=YOUR_KEY,  # Same payer!
    owner_address="0xProjectB_Address"  # Different owner!
)
publisher_b.publish_news_trigger(data)

# Query
project_a_data = query_triggers(owner="0xProjectA_Address")
project_b_data = query_triggers(owner="0xProjectB_Address")
```

## Implementation Plan

1. **Add `owner` parameter to OnChainPublisher** ✓ (next step)
2. **Add `owner` field to TriggerRegistry** ✓
3. **Update visualization to filter by owner** ✓
4. **Support wallet creation utilities** (optional)

## Security Notes

- ✅ Your personal wallet private key: Keep secret, used for signing
- ✅ Owner addresses: Public, no private key needed
- ✅ Objects are immutable once created (owner can't be changed)
- ✅ Transfer ownership = create new object with different owner

## Summary

**Answer to your question:**

> "Can I create EOA wallet on SUI? The private key I provided is my personal wallet but I want the owner of the data to be configurable."

**Yes!** Here's how:

1. **Simplest:** Use your wallet to sign, but set a custom `owner` field in metadata (no new wallet needed)
2. **Advanced:** Generate new wallets programmatically (need to manage keys)
3. **Best Practice:** HD wallets from seed phrase (one backup for all wallets)

**I recommend Option 1 (Sponsor Pattern)** - your wallet pays gas, but owner is configurable via metadata field. No need to manage multiple private keys!
