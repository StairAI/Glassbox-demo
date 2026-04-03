# Demo Setup: Required Credentials & Configuration

**Goal**: Get real Walrus storage and SUI blockchain working (no smart contracts needed for demo)

## Credentials Needed

### 1. SUI Wallet Setup

#### Install SUI CLI
```bash
# Install SUI CLI
cargo install --locked --git https://github.com/MystenLabs/sui.git --branch testnet sui

# Verify installation
sui --version
```

#### Create Wallet
```bash
# Create new wallet (or connect existing)
sui client new-address ed25519

# This will output:
# Created new keypair for address: 0xYOUR_ADDRESS
# Secret Recovery Phrase: [12 words - SAVE THESE!]
```

#### Get Testnet SUI Tokens (Free)
```bash
# Switch to testnet
sui client switch --env testnet

# Get free testnet tokens
sui client faucet

# Check balance
sui client gas
```

**What you need to save**:
- ✅ Wallet address: `0xYOUR_ADDRESS`
- ✅ Secret recovery phrase (12 words)
- ✅ Or private key from `~/.sui/sui_config/sui.keystore`

---

### 2. Walrus Setup

#### Walrus Testnet Access

Walrus is currently in testnet. Here's how to get access:

**Option A: Use Walrus Testnet (Recommended)**
```bash
# Walrus testnet endpoints are public:
Publisher: https://publisher.walrus-testnet.walrus.space
Aggregator: https://aggregator.walrus-testnet.walrus.space

# No authentication required for testnet!
```

**Option B: Run Local Walrus (Advanced)**
```bash
# Install Walrus CLI
cargo install --git https://github.com/MystenLabs/walrus.git walrus

# Configure local node (if needed)
walrus init
```

**What you need**:
- ✅ No credentials needed for testnet!
- ✅ Just use the public endpoints

---

## Configuration Files

### Update `.env` File

```bash
# config/.env

# Existing
CRYPTOPANIC_API_TOKEN=72101129f9f637bc26a837a8b61ad6bae189ab2f

# Add these for SUI
SUI_NETWORK=testnet
SUI_WALLET_ADDRESS=0xYOUR_ADDRESS_HERE
SUI_PRIVATE_KEY=YOUR_PRIVATE_KEY_HERE  # From ~/.sui/sui_config/sui.keystore

# Add these for Walrus
WALRUS_PUBLISHER_URL=https://publisher.walrus-testnet.walrus.space
WALRUS_AGGREGATOR_URL=https://aggregator.walrus-testnet.walrus.space
WALRUS_ENABLED=true  # Set to false for simulated mode
```

---

## Testing Walrus (Real Mode)

### Test 1: Store Data on Walrus

```python
# test_walrus_real.py
from src.storage.walrus_client import WalrusClient

# Use real Walrus testnet
client = WalrusClient(
    publisher_url="https://publisher.walrus-testnet.walrus.space",
    aggregator_url="https://aggregator.walrus-testnet.walrus.space",
    simulated=False  # Real mode!
)

# Store data
test_data = b"Hello Walrus from Glass Box Protocol!"
blob_id = client.store(test_data)
print(f"Stored on Walrus: {blob_id}")

# Fetch data back
fetched_data = client.fetch(blob_id)
print(f"Fetched: {fetched_data.decode()}")

# Verify
assert fetched_data == test_data
print("✓ Walrus storage working!")
```

### Test 2: Store JSON on Walrus

```python
from src.storage.walrus_client import WalrusClient, WalrusHelper

client = WalrusClient(simulated=False)

# Store news data
news_data = {
    "articles": [
        {"title": "Bitcoin hits $70k", "source": "cryptopanic"},
        {"title": "Ethereum upgrade coming", "source": "cryptopanic"}
    ],
    "total_count": 2
}

blob_id = WalrusHelper.store_json(client, news_data)
print(f"News stored on Walrus: {blob_id}")

# Fetch back
fetched_news = WalrusHelper.fetch_json(client, blob_id)
print(f"Fetched articles: {fetched_news['total_count']}")

print("✓ Walrus JSON storage working!")
```

---

## Testing SUI (Real Mode)

### Install pysui

```bash
pip install pysui
```

### Test 1: Connect to SUI Testnet

```python
# test_sui_connection.py
from pysui import SyncClient, SuiConfig

# Connect to testnet
config = SuiConfig.default_config()
client = SyncClient(config)

# Check connection
result = client.get_reference_gas_price()
print(f"✓ Connected to SUI testnet")
print(f"Gas price: {result.result_data}")

# Check your balance
address = "0xYOUR_ADDRESS"
coins = client.get_coins(address)
print(f"Your SUI balance: {coins.result_data}")
```

### Test 2: Read from SUI (Example)

```python
from pysui import SyncClient, SuiConfig
from pysui.sui.sui_types.scalars import ObjectID

config = SuiConfig.default_config()
client = SyncClient(config)

# Read an object (example)
object_id = ObjectID("0xSOME_OBJECT_ID")
result = client.get_object(object_id)

print(f"Object data: {result.result_data}")
```

---

## Simplified Demo Architecture (No Smart Contracts)

For the demo, we'll use a **centralized trigger registry** instead of smart contracts:

```
┌─────────────────────────────────────────────────────────┐
│                    DATA FLOW (Demo)                     │
└─────────────────────────────────────────────────────────┘

1. NewsPipeline
   ├─> Store full data on Walrus (REAL) ✅
   ├─> Store trigger metadata in local JSON file (FAKE) ⚠️
   └─> Return NewsTrigger

2. SuiPricePipeline
   ├─> Read from simulated oracle (FAKE) ⚠️
   ├─> Store trigger metadata in local JSON file (FAKE) ⚠️
   └─> Return PriceTrigger

3. Agent A
   ├─> Read trigger metadata from local JSON (FAKE) ⚠️
   ├─> Fetch full news from Walrus (REAL) ✅
   ├─> Process with LLM
   └─> Output sentiment signals
```

### Centralized Trigger Registry (For Demo)

```python
# src/demo/trigger_registry.py

import json
from pathlib import Path
from typing import List, Dict, Any

class TriggerRegistry:
    """
    Centralized trigger registry for demo.

    In production, this would be replaced by SUI smart contracts.
    For demo, we just use a local JSON file.
    """

    def __init__(self, registry_path: str = "data/trigger_registry.json"):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(exist_ok=True)

        # Initialize empty registry if doesn't exist
        if not self.registry_path.exists():
            self._save_registry([])

    def register_trigger(self, trigger_data: Dict[str, Any]) -> str:
        """Register a trigger and return its ID."""
        triggers = self._load_registry()

        # Generate ID
        trigger_id = f"trigger_{len(triggers):04d}"
        trigger_data["trigger_id"] = trigger_id

        triggers.append(trigger_data)
        self._save_registry(triggers)

        print(f"[TriggerRegistry] Registered {trigger_data['trigger_type']} trigger: {trigger_id}")
        return trigger_id

    def get_triggers(self, trigger_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all triggers, optionally filtered by type."""
        triggers = self._load_registry()

        if trigger_type:
            triggers = [t for t in triggers if t.get("trigger_type") == trigger_type]

        return triggers

    def get_trigger(self, trigger_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific trigger by ID."""
        triggers = self._load_registry()

        for trigger in triggers:
            if trigger.get("trigger_id") == trigger_id:
                return trigger

        return None

    def _load_registry(self) -> List[Dict[str, Any]]:
        """Load triggers from JSON file."""
        with open(self.registry_path, 'r') as f:
            return json.load(f)

    def _save_registry(self, triggers: List[Dict[str, Any]]):
        """Save triggers to JSON file."""
        with open(self.registry_path, 'w') as f:
            json.dump(triggers, f, indent=2)
```

---

## What You Need to Get Started

### Minimal Setup (Walrus Only)
```bash
# 1. No credentials needed - Walrus testnet is public!

# 2. Update code to use real Walrus:
# In your demo script:
walrus_client = WalrusClient(simulated=False)  # Use real Walrus!

# 3. Test it:
python test_walrus_real.py
```

### Full Setup (Walrus + SUI)
```bash
# 1. Install SUI CLI
cargo install --locked --git https://github.com/MystenLabs/sui.git --branch testnet sui

# 2. Create wallet & get testnet tokens
sui client new-address ed25519
sui client faucet

# 3. Save credentials to .env:
SUI_WALLET_ADDRESS=0xYOUR_ADDRESS
SUI_PRIVATE_KEY=suiprivkey1q...  # From ~/.sui/sui_config/sui.keystore

# 4. Install pysui
pip install pysui

# 5. Test connection
python test_sui_connection.py
```

---

## Summary: What's Real vs Fake in Demo

| Component | Demo Mode | Production Mode |
|-----------|-----------|-----------------|
| **Walrus Storage** | ✅ REAL (use testnet) | ✅ REAL (use mainnet) |
| **News Data** | ✅ REAL (CryptoPanic API) | ✅ REAL |
| **Trigger Registry** | ⚠️ FAKE (local JSON) | ✅ REAL (smart contracts) |
| **Price Oracle** | ⚠️ FAKE (simulated) | ✅ REAL (Pyth/Switchboard) |
| **Agent Processing** | ✅ REAL (LLM) | ✅ REAL (LLM) |

---

## Next Steps

1. **Get Walrus Working** (Easiest - no credentials!)
   - Update code to use `simulated=False`
   - Test storing and fetching data

2. **Create Trigger Registry** (Simple - just local JSON)
   - Implement TriggerRegistry class
   - Store trigger metadata locally

3. **Build Complete Demo**
   - NewsPipeline → Walrus (real) + TriggerRegistry (fake)
   - Agent reads from TriggerRegistry → fetches from Walrus (real)

4. **Optional: Add SUI** (Later)
   - Get SUI wallet and tokens
   - Read from price oracles
   - Eventually replace TriggerRegistry with smart contracts

Want me to implement the TriggerRegistry and update the demo to use real Walrus?
