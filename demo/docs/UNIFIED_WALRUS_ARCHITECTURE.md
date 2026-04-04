# Unified Walrus Storage Architecture

## Overview

The Glass Box Protocol now uses a **unified storage architecture** where all signals store their full data on Walrus, regardless of size.

This provides:
- **Consistency**: Same storage pattern for all signal types
- **Scalability**: No on-chain storage limitations
- **Transparency**: All data accessible via Walrus
- **Efficiency**: Blockchain only stores lightweight metadata

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SUI BLOCKCHAIN                            │
│  (Lightweight metadata only - < 500 bytes per signal)       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Signal Object:                                              │
│  ├─ object_id: "0x..."                                       │
│  ├─ signal_type: "news" | "price" | "insight"               │
│  ├─ walrus_blob_id: "abc123..."  ← Reference to Walrus      │
│  ├─ data_hash: "sha256..."                                   │
│  ├─ size_bytes: 4096                                         │
│  ├─ timestamp: "2024-01-01T00:00:00Z"                        │
│  ├─ producer: "agent_a"                                      │
│  └─ [type-specific preview fields]                           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ fetch via walrus_blob_id
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    WALRUS STORAGE                            │
│  (Full data - unlimited size)                               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Blob: abc123...                                             │
│  ├─ Full signal data (articles, prices, insights)           │
│  ├─ Metadata (timestamps, sources)                          │
│  ├─ Additional context                                       │
│  └─ Historical data (optional)                               │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Signal Types

### 1. NewsSignal

**On-chain (SUI):**
```json
{
  "object_id": "0x123...",
  "signal_type": "news",
  "walrus_blob_id": "LQ7f-dZoAGCqgk8k...",
  "data_hash": "abc123...",
  "size_bytes": 8192,
  "articles_count": 5,
  "timestamp": "2024-01-01T00:00:00Z",
  "producer": "news_pipeline"
}
```

**On Walrus:**
```json
{
  "articles": [
    {
      "title": "Bitcoin surges to new high",
      "body": "Full article text...",
      "source": "CryptoPanic",
      "published_at": "2024-01-01T00:00:00Z"
    }
  ],
  "fetch_timestamp": "2024-01-01T00:00:00Z",
  "total_count": 5
}
```

### 2. PriceSignal

**On-chain (SUI):**
```json
{
  "object_id": "0x456...",
  "signal_type": "price",
  "walrus_blob_id": "xyz789...",
  "data_hash": "def456...",
  "size_bytes": 512,
  "symbol": "BTC",
  "price_usd": 45000.0,
  "timestamp": "2024-01-01T00:00:00Z",
  "producer": "price_pipeline"
}
```

**On Walrus:**
```json
{
  "symbol": "BTC",
  "price_usd": 45000.0,
  "oracle_source": "pyth",
  "confidence": 0.99,
  "timestamp": "2024-01-01T00:00:00Z",
  "historical_data": [
    {"timestamp": "2024-01-01T00:00:00Z", "price": 45000.0},
    {"timestamp": "2024-01-01T00:05:00Z", "price": 45100.0}
  ]
}
```

### 3. InsightSignal

**On-chain (SUI):**
```json
{
  "object_id": "0x789...",
  "signal_type": "insight",
  "walrus_blob_id": "signal_abc123...",
  "walrus_trace_id": "trace_def456...",
  "data_hash": "ghi789...",
  "size_bytes": 1024,
  "insight_type": "sentiment",
  "confidence": 0.85,
  "timestamp": "2024-01-01T00:00:00Z",
  "producer": "agent_a_sentiment"
}
```

**On Walrus (Signal Data):**
```json
{
  "insight_type": "sentiment",
  "signal_value": {
    "sentiment_scores": {
      "tokens": [
        {
          "target_token": "BTC",
          "target_token_sentiment": 0.75,
          "confidence": 0.85,
          "reasoning": "Bullish news trend detected"
        }
      ],
      "overall_confidence": 0.85
    }
  },
  "confidence": 0.85,
  "timestamp": "2024-01-01T00:00:00Z",
  "producer": "agent_a_sentiment"
}
```

**On Walrus (Reasoning Trace - separate blob):**
```json
{
  "agent_id": "agent_a_sentiment",
  "agent_version": "2.0",
  "input_signals": ["0x123..."],
  "output_signal": "0x789...",
  "reasoning_steps": [
    {
      "step_name": "fetch_news_data",
      "description": "Fetched news articles from Walrus",
      "input_data": {"signal_count": 1},
      "output_data": {"articles_count": 5},
      "timestamp": "2024-01-01T00:00:00Z"
    },
    {
      "step_name": "analyze_sentiment",
      "description": "Analyzed sentiment for 2 tokens",
      "input_data": {
        "target_tokens": ["BTC", "ETH"],
        "articles_count": 5
      },
      "output_data": {
        "tokens": [...],
        "overall_confidence": 0.85
      },
      "confidence": 0.85,
      "timestamp": "2024-01-01T00:00:01Z"
    }
  ],
  "final_output": {...},
  "confidence": 0.85,
  "timestamp": "2024-01-01T00:00:01Z",
  "execution_time_ms": 1250
}
```

## Benefits

### 1. Unified Interface

All signals use the same `fetch_full_data()` interface:

```python
# Works for ALL signal types
signal = get_signal_from_chain(object_id)
full_data = signal.fetch_full_data(walrus_client)
```

### 2. Scalability

- **On-chain**: Only ~300 bytes per signal (constant size)
- **Walrus**: Unlimited size (news articles, historical price data, etc.)
- No blockchain storage limitations

### 3. Transparency

All data is verifiable:
- **Data Hash**: SHA-256 hash for integrity verification
- **Reasoning Trace**: Complete audit trail of agent decisions
- **Immutable**: Both on-chain and Walrus data are immutable

### 4. Cost Efficiency

- **SUI**: Low cost for small metadata
- **Walrus**: Cost-efficient for large data (1 SUI ≈ 5 MB per year)

## Data Flow

```
┌─────────────────┐
│  Data Source    │
│ (News, Prices)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Pipeline      │
│  (ETL Process)  │
└────────┬────────┘
         │
         ├─────────────────────────────┐
         │                             │
         ▼                             ▼
┌─────────────────┐          ┌─────────────────┐
│  Store on       │          │  Register on    │
│  Walrus         │          │  SUI Blockchain │
│  (Full Data)    │          │  (Metadata)     │
└────────┬────────┘          └────────┬────────┘
         │                             │
         │  Returns blob_id            │
         └─────────────┬───────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  Signal Object  │
              │  Created        │
              └─────────────────┘
```

## Agent Workflow

```
Agent A receives NewsSignal
    │
    ├─ Reads metadata from SUI blockchain
    │  (object_id, walrus_blob_id, articles_count)
    │
    ├─ Fetches full data from Walrus
    │  (all news articles)
    │
    ├─ Processes data (sentiment analysis)
    │  Records reasoning steps
    │
    ├─ Stores signal data on Walrus
    │  (sentiment scores + metadata)
    │
    ├─ Stores reasoning trace on Walrus
    │  (complete audit trail)
    │
    └─ Creates InsightSignal
       (references both Walrus blobs)

Agent B receives InsightSignal
    │
    ├─ Reads metadata from SUI blockchain
    │
    ├─ Fetches signal data from Walrus
    │  (sentiment scores)
    │
    ├─ Optionally fetches reasoning trace
    │  (to understand Agent A's decision)
    │
    └─ Continues processing...
```

## Code Examples

### Creating a Signal (Pipeline)

```python
from src.abstract import NewsSignal
from src.storage.walrus_client import WalrusClient, WalrusHelper
import hashlib
import json

# Prepare data
news_data = {
    "articles": [...],
    "fetch_timestamp": "2024-01-01T00:00:00Z",
    "total_count": 5
}

# Store on Walrus
walrus_client = WalrusClient(...)
blob_id = WalrusHelper.store_json(walrus_client, news_data)

# Compute hash
data_json = json.dumps(news_data, sort_keys=True)
data_hash = hashlib.sha256(data_json.encode()).hexdigest()

# Create signal
signal = NewsSignal(
    object_id="0x123...",  # From SUI transaction
    walrus_blob_id=blob_id,
    data_hash=data_hash,
    size_bytes=len(data_json),
    articles_count=5,
    timestamp=datetime.now(),
    producer="news_pipeline"
)

# Register on SUI blockchain (metadata only)
# sui_client.register_signal(signal.to_dict())
```

### Consuming a Signal (Agent)

```python
from src.abstract import Agent, Signal

class MyAgent(Agent):
    def process_signals(self, signals: List[Signal]) -> Dict[str, Any]:
        for signal in signals:
            # Fetch full data from Walrus (automatic)
            full_data = signal.fetch_full_data(
                walrus_client=self.walrus_client
            )

            # Data is verified automatically (hash check)
            # Process the data...
```

### Verifying Data Integrity

```python
# Fetch signal metadata from blockchain
signal = get_signal_from_chain("0x123...")

# Fetch full data from Walrus
full_data = signal.fetch_full_data(walrus_client)

# Verification happens automatically:
# 1. Compute hash of fetched data
# 2. Compare with data_hash from blockchain
# 3. Raise error if mismatch

# If no error raised, data is verified ✓
```

## Migration Notes

### Old Architecture (Mixed Storage)

```
NewsSignal:    Walrus (full data)  ✓
PriceSignal:   SUI (on-chain)      ✗
InsightSignal: SUI (on-chain)      ✗
```

### New Architecture (Unified Walrus)

```
NewsSignal:    Walrus (full data)  ✓
PriceSignal:   Walrus (full data)  ✓
InsightSignal: Walrus (full data)  ✓
```

### Breaking Changes

1. **PriceSignal Constructor**: Now requires `walrus_blob_id`, `data_hash`, `size_bytes`
2. **InsightSignal Constructor**: Now requires `walrus_blob_id`, `data_hash`, `size_bytes`
3. **Agent Output**: Automatically stores signal data on Walrus

### Backward Compatibility

The abstract `Agent` class handles Walrus storage automatically:
- Agents implementing `process_signals()` don't need changes
- Signal data is stored on Walrus in `Agent.run()`
- Reasoning traces are stored separately

## Summary

**Before:**
- Mixed storage strategy (some on-chain, some on Walrus)
- Inconsistent interfaces
- On-chain storage limitations

**After:**
- Unified Walrus storage for all signals
- Consistent interface (`fetch_full_data()`)
- No storage limitations
- Complete transparency (signal data + reasoning traces)

**Key Principle:**
> All signals store full data on Walrus.
> Blockchain only stores metadata + Walrus references.
