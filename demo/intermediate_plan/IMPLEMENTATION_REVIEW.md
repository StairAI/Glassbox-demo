# Implementation Review: Walrus + Signal Architecture

**Status**: ✅ Ready for Review (Steps 4 & 5 Complete)

## What's Been Implemented

### 1. ✅ WalrusClient ([src/storage/walrus_client.py](../src/storage/walrus_client.py))

**Purpose**: Standalone tool for decentralized data storage

**Key Features**:
- `store(data: bytes) -> blob_id`: Store data on Walrus
- `fetch(blob_id: str) -> bytes`: Retrieve data from Walrus
- `exists(blob_id: str) -> bool`: Check if blob exists
- Simulated mode for demo/testing
- Real mode ready for Walrus testnet integration

**Helper**:
- `WalrusHelper.store_json()`: Store JSON directly
- `WalrusHelper.fetch_json()`: Fetch and parse JSON

**Architecture**:
```python
client = WalrusClient(simulated=True)

# Store
blob_id = client.store(data_bytes)

# Fetch
data = client.fetch(blob_id)
```

---

### 2. ✅ Unified Signal Abstraction ([src/core/signal.py](../src/core/signal.py))

**Purpose**: Unified interface for all agent inputs

**Three Signal Types**:

#### NewsSignal
```python
NewsSignal(
    object_id="0xabc...",           # SUI object ID
    walrus_blob_id="xyz123...",     # Walrus reference
    data_hash="hash...",             # SHA-256
    size_bytes=4096,
    articles_count=5,
    timestamp=datetime.now(),
    producer="news_pipeline"
)

# Fetch full data
data = signal.fetch_full_data()  # Fetches from Walrus
```

#### PriceSignal
```python
PriceSignal(
    object_id="0xdef...",
    symbol="BTC",
    price_usd=66434.0,
    oracle_source="pyth",
    confidence=0.01,
    timestamp=datetime.now(),
    producer="sui_price_pipeline"
)

# Fetch full data
data = signal.fetch_full_data()  # Data already in signal
```

#### InsightSignal
```python
InsightSignal(
    object_id="0xghi...",
    signal_type="sentiment",
    signal_value={"BTC": 0.72, "ETH": 0.45},
    confidence=0.85,
    timestamp=datetime.now(),
    producer="agent_a",
    walrus_trace_id="trace123..."    # Reasoning trace on Walrus
)

# Fetch full data + reasoning trace
data = signal.fetch_full_data()  # Includes trace from Walrus
```

**Key Benefit**: Agents receive `List[Signal]` regardless of data source!

---

### 3. ✅ Updated OnChainPublisher ([src/blockchain/sui_publisher.py](../src/blockchain/sui_publisher.py))

**Purpose**: Publish signals to SUI with hybrid storage strategy

**Three Publishing Methods**:

#### publish_news_signal()
```python
signal = publisher.publish_news_signal(
    news_data={
        "articles": [...],
        "total_count": 5
    },
    producer="news_pipeline"
)

# Internally:
# 1. Store full data on Walrus → blob_id
# 2. Publish metadata + blob_id to SUI → object_id
# 3. Return NewsSignal
```

**Storage Strategy**: Large data (news) → Walrus + SUI metadata

#### publish_price_signal()
```python
signal = publisher.publish_price_signal(
    symbol="BTC",
    price_usd=66434.0,
    oracle_source="pyth",
    confidence=0.01
)

# Internally:
# 1. Create signal data (small, < 200 bytes)
# 2. Publish directly to SUI → object_id
# 3. Return PriceSignal
```

**Storage Strategy**: Small data (price) → Direct SUI storage

#### publish_signal_signal()
```python
signal = publisher.publish_signal_signal(
    signal_type="sentiment",
    signal_value={"BTC": 0.72},
    confidence=0.85,
    producer="agent_a",
    reasoning_trace={
        "input": "...",
        "llm_prompt": "...",
        "llm_response": "...",
        "output": "..."
    }
)

# Internally:
# 1. Store reasoning trace on Walrus → trace_id
# 2. Publish signal + trace_id to SUI → object_id
# 3. Return InsightSignal
```

**Storage Strategy**: Signal on SUI + reasoning trace on Walrus

---

### 4. ✅ Simplified NewsPipeline ([src/pipeline/news_pipeline.py](../src/pipeline/news_pipeline.py))

**Key Change**: ALL news data goes directly to Walrus

**Flow**:
```
1. EXTRACT: Fetch from CryptoPanic API
   ↓
2. TRANSFORM: Convert to standard format
   ↓
3. LOAD: publisher.publish_news_signal()
   ├─> Walrus: Full data (4KB+)
   └─> SUI: Metadata + blob_id (< 500 bytes)
   ↓
4. RETURN: NewsSignal
```

**Usage**:
```python
pipeline = NewsPipeline(
    api_token="YOUR_TOKEN",
    publisher=OnChainPublisher()
)

signal = pipeline.fetch_and_publish(
    currencies=["BTC", "ETH"],
    limit=5
)

print(f"Signal: {signal.object_id}")
print(f"Walrus blob: {signal.walrus_blob_id}")
print(f"Articles: {signal.articles_count}")
```

**Key Points**:
- ✅ Simple: All data → Walrus
- ✅ Cost-efficient: Only metadata on SUI
- ✅ Returns NewsSignal for agents
- ❌ No LLM, no reasoning

---

### 5. ✅ SuiPricePipeline ([src/pipeline/sui_price_pipeline.py](../src/pipeline/sui_price_pipeline.py))

**Key Difference**: READS from on-chain oracles (doesn't fetch from APIs)

**Flow**:
```
1. READ: Fetch price from SUI oracle (Pyth/Switchboard)
   ↓
2. TRANSFORM: Already standardized (no transformation needed)
   ↓
3. PUBLISH: publisher.publish_price_signal()
   └─> SUI: Price signal (< 200 bytes)
   ↓
4. RETURN: PriceSignal
```

**Usage**:
```python
pipeline = SuiPricePipeline(
    sui_client=sui_client,
    publisher=OnChainPublisher(),
    oracle_type="pyth",
    simulated=True
)

signal = pipeline.read_and_publish_signal(symbol="BTC")

print(f"Signal: {signal.object_id}")
print(f"Price: ${signal.price_usd}")
print(f"Oracle: {signal.oracle_source}")
```

**Key Points**:
- ✅ Reads from on-chain (not API)
- ✅ Lighter pipeline (just abstraction layer)
- ✅ No Walrus needed (data is small)
- ✅ Supports multiple oracles (Pyth, Switchboard)
- ❌ No LLM, no reasoning

---

## Architecture Summary

### Data Flow

```
┌────────────────────────────────────────────────────────────┐
│                     DATA SOURCES                           │
└────────────────────────────────────────────────────────────┘
         │                                 │
         │ CryptoPanic API                 │ On-Chain Oracle
         │ (Off-chain)                     │ (Already on SUI)
         ▼                                 ▼
┌──────────────────┐              ┌──────────────────┐
│  NewsPipeline    │              │ SuiPricePipeline │
│  (Fetch + Store) │              │  (Read + Wrap)   │
└────────┬─────────┘              └────────┬─────────┘
         │                                 │
         │ Large data                      │ Small data
         ▼                                 │
┌──────────────────┐                      │
│  Walrus Storage  │                      │
│  (Full articles) │                      │
└────────┬─────────┘                      │
         │                                 │
         │ blob_id                         │
         ▼                                 ▼
┌────────────────────────────────────────────────────────────┐
│                     SUI BLOCKCHAIN                         │
│                                                            │
│  NewsSignal               PriceSignal                   │
│  • walrus_blob_id          • symbol                       │
│  • data_hash               • price_usd                    │
│  • size_bytes              • oracle_source                │
│  • articles_count          • confidence                   │
│                                                            │
└──────────────────────────┬─────────────────────────────────┘
                           │
                           │ Unified Signal Interface
                           ▼
                  ┌─────────────────┐
                  │  Agent Inputs   │
                  │                 │
                  │  List[Signal]  │
                  └─────────────────┘
```

### Storage Strategy

| Data Type | Size | Storage | Metadata on SUI |
|-----------|------|---------|-----------------|
| News articles | 4KB+ | ✅ Walrus | blob_id + hash |
| Current prices | <200B | ✅ SUI direct | N/A |
| Historical prices | 10KB+ | ✅ Walrus | blob_id + hash |
| Agent signals | <500B | ✅ SUI direct | N/A |
| Reasoning traces | 1KB+ | ✅ Walrus | trace_id |

### Key Benefits

1. **Cost Efficiency**
   - Large data → Walrus (cheap)
   - Small data → SUI (acceptable)
   - Only metadata on expensive chain

2. **Unified Interface**
   - All agents receive `List[Signal]`
   - `signal.fetch_full_data()` works regardless of source
   - Easy to add new data sources

3. **Leverage Existing Infrastructure**
   - Price oracles already on SUI
   - Just read and wrap in signal
   - No redundant API calls

4. **Clear Separation**
   - NewsPipeline: Fetch from API → Walrus + SUI
   - SuiPricePipeline: Read from SUI → Wrap in signal
   - Agents: Process signals (next step!)

---

## What's Next: Smart Contract Review

Before implementing the smart contracts, let's review the requirements:

### Required Signal Objects on SUI

#### NewsSignal Object
```move
struct NewsSignal has key, store {
    id: UID,
    signal_type: vector<u8>,   // "news"
    walrus_blob_id: vector<u8>, // Walrus reference
    data_hash: vector<u8>,      // SHA-256
    size_bytes: u64,
    articles_count: u64,
    timestamp: u64,
    producer: vector<u8>,       // "news_pipeline"
}
```

#### PriceSignal Object
```move
struct PriceSignal has key, store {
    id: UID,
    signal_type: vector<u8>,   // "price"
    symbol: vector<u8>,
    price_usd: u64,             // Scaled by 1e8
    oracle_source: vector<u8>,  // "pyth", "switchboard"
    confidence: u64,            // Scaled by 1e8
    timestamp: u64,
    producer: vector<u8>,       // "sui_price_pipeline"
}
```

#### InsightSignal Object
```move
struct InsightSignal has key, store {
    id: UID,
    signal_type: vector<u8>,   // "signal"
    signal_type: vector<u8>,    // "sentiment", "investment"
    signal_value: vector<u8>,   // JSON blob
    confidence: u64,            // Scaled by 1e8
    walrus_trace_id: vector<u8>, // Optional reasoning trace
    timestamp: u64,
    producer: vector<u8>,       // "agent_a", "agent_b"
}
```

### Required Events

```move
struct SignalCreated has copy, drop {
    signal_id: address,
    signal_type: vector<u8>,
    timestamp: u64,
}
```

---

## Questions for Review

1. **Smart Contract Structure**: Should we have:
   - One module `glass_box::signal` with all three structs?
   - Three separate modules (news_signal, price_signal, signal_signal)?

2. **Data Scaling**: For prices and confidence, we're using `u64` with scaling factor (1e8). Is this acceptable or should we use a different representation?

3. **Signal Value Storage**: InsightSignal stores `signal_value` as JSON blob (vector<u8>). Should we have a more structured format?

4. **Access Control**: Should signals be:
   - Publicly shared objects (any agent can read)?
   - Owned objects (only specific agents can read)?
   - Hybrid (some public, some private)?

5. **Additional Fields**: Are there any other fields needed for signals?
   - Producer reputation score?
   - Expiration timestamp?
   - Version number?

Ready to proceed with smart contract implementation after your review!
