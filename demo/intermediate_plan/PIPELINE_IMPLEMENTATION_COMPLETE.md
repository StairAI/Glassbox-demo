# Data Pipeline Architecture - Implementation Complete

**Date**: 2026-03-28
**Status**: ✅ Implementation Complete

## Overview

Successfully implemented the corrected data pipeline architecture where:
- **Data Pipelines** (NOT agents) handle pure ETL operations
- **Real Agents** perform LLM-powered reasoning on on-chain data
- Clear separation between data movement and intelligent processing

## Implementation Summary

### 1. Blockchain Infrastructure ✅

**File**: `src/blockchain/sui_publisher.py`

Implemented two key classes:

#### OnChainPublisher
```python
class OnChainPublisher:
    """Publishes raw data to SUI blockchain (used by pipelines)"""

    def publish_raw_data(data, producer, data_type) -> str:
        # 1. Validate and prepare data
        # 2. Compute hash for integrity
        # 3. Publish to blockchain
        # Returns: Object ID
```

#### OnChainEventEmitter
```python
class OnChainEventEmitter:
    """Emits lightweight events to signal agents"""

    def emit_event(event_type, object_id, metadata) -> str:
        # Emit event with reference to full data
        # Events are < 200 bytes
```

**Features**:
- Simulated mode for demo/development
- Real blockchain mode (ready for pysui integration)
- Data hashing for integrity verification
- Event emission for agent signaling

---

### 2. News Pipeline ✅

**File**: `src/pipeline/news_pipeline.py`

#### NewsPipeline Class
```python
class NewsPipeline:
    """ETL pipeline for news data (NOT an agent)"""

    def fetch_and_publish(currencies, limit) -> str:
        # Step 1: EXTRACT - Fetch from CryptoPanic API
        articles = self.source.fetch_news(currencies, limit)

        # Step 2: TRANSFORM - Convert to on-chain format
        news_data = self._transform_for_onchain(articles)

        # Step 3: LOAD - Publish to blockchain
        object_id = self.publisher.publish_raw_data(...)

        # Step 4: EMIT - Signal agents (optional)
        self.event_emitter.emit_event(...)

        return object_id
```

**Key Characteristics**:
- ❌ No LLM
- ❌ No reasoning
- ✅ Pure ETL
- ✅ Producer type: "pipeline"

**Architecture Layers**:
1. `CryptoPanicClient` - Raw HTTP requests
2. `CryptoPanicSource` - Data transformation
3. `OnChainPublisher` - Blockchain storage

#### NewsScheduler Class
```python
class NewsScheduler:
    """Run news pipeline periodically"""

    def run_periodic(interval_seconds=300):
        # Fetch news every 5 minutes
```

---

### 3. Price Pipeline ✅

**File**: `src/pipeline/price_pipeline.py`

#### PricePipeline Class
```python
class PricePipeline:
    """ETL pipeline for price data (NOT an agent)"""

    def fetch_and_publish(symbols, vs_currency="usd") -> str:
        # Step 1: EXTRACT - Fetch from CoinGecko API
        prices = []
        for symbol in symbols:
            price_data = self.source.get_price(symbol, vs_currency)
            prices.append(price_data)

        # Step 2: TRANSFORM - Convert to on-chain format
        price_data = self._transform_for_onchain(prices, vs_currency)

        # Step 3: LOAD - Publish to blockchain
        object_id = self.publisher.publish_raw_data(...)

        # Step 4: EMIT - Signal agents (optional)
        self.event_emitter.emit_event(...)

        return object_id
```

**Additional Methods**:
```python
def fetch_historical_and_publish(symbol, days=30) -> str:
    # Fetch and publish historical price data
```

**Key Characteristics**:
- ❌ No LLM
- ❌ No reasoning
- ✅ Pure ETL
- ✅ Producer type: "pipeline"

**Architecture Layers**:
1. `CoinGeckoClient` - Raw HTTP requests
2. `CoinGeckoSource` - Data transformation
3. `OnChainPublisher` - Blockchain storage

#### PriceScheduler Class
```python
class PriceScheduler:
    """Run price pipeline periodically"""

    def run_periodic(symbols, interval_seconds=60):
        # Fetch prices every 1 minute
```

---

### 4. Smart Contract ✅

**File**: `smart_contracts/raw_data.move`

```move
module glass_box::raw_data {
    /// Store raw data from pipelines
    struct RawDataObject has key, store {
        id: UID,
        producer: vector<u8>,           // "news_pipeline", "price_pipeline"
        producer_type: vector<u8>,      // "pipeline" (NOT "agent")
        data_type: vector<u8>,          // "news_raw", "price_raw"
        timestamp: u64,
        data_payload: vector<u8>,       // JSON blob
        data_hash: vector<u8>,          // SHA-256 hash
    }

    /// Event for raw data publication
    struct RawDataPublished has copy, drop {
        object_id: address,
        producer: vector<u8>,
        data_type: vector<u8>,
        timestamp: u64,
        data_hash: vector<u8>,
    }

    /// Event to signal agents
    struct DataAvailableEvent has copy, drop {
        event_type: vector<u8>,     // "news_available", "price_updated"
        object_id: address,         // Reference to RawDataObject
        metadata: vector<u8>,       // Lightweight metadata (JSON)
        timestamp: u64,
    }

    /// Publish raw data (called by pipelines)
    public entry fun publish_data(...) {
        // Create RawDataObject
        // Emit RawDataPublished event
        // Transfer to sender
    }

    /// Emit event to signal agents
    public entry fun emit_data_event(...) {
        // Emit DataAvailableEvent
    }

    /// Make data publicly shareable
    public entry fun share_data(raw_data: RawDataObject) {
        // Share for agent access
    }

    // Getter functions for agents to read data
    public fun get_producer(...) -> &vector<u8>
    public fun get_data_type(...) -> &vector<u8>
    public fun get_data_payload(...) -> &vector<u8>
    // ... more getters
}
```

**Features**:
- Clear producer_type distinction ("pipeline" vs "agent")
- Lightweight events for signaling
- Data integrity verification via hash
- Public sharing for agent access

---

### 5. Demo Script ✅

**File**: `scripts/demo_pipeline_architecture.py`

Complete end-to-end demonstration:

#### Part 1: News Pipeline
```
NEWS PIPELINE: Starting ETL Process
[1/4] EXTRACT: Fetching from CryptoPanic API
  ✓ Fetched 5 articles
[2/4] TRANSFORM: Converting to on-chain format
  ✓ Prepared 5 articles
[3/4] LOAD: Publishing to SUI blockchain
  ✓ Mock Object ID: 0x914197285212592f...
[4/4] EMIT: Signaling agent events
  ✓ 5 events emitted
```

#### Part 2: Price Pipeline
```
PRICE PIPELINE: Starting ETL Process
[1/4] EXTRACT: Fetching from CoinGecko API
  ✓ BTC: $66,434.00
[2/4] TRANSFORM: Converting to on-chain format
  ✓ Prepared 1 price records
[3/4] LOAD: Publishing to SUI blockchain
  ✓ Mock Object ID: 0x0581c00d605a3e81...
[4/4] EMIT: Signaling agent events
  ✓ 1 event emitted
```

#### Part 3: Agent A (Simulated)
- Detects news_available event
- Fetches full data from blockchain
- Uses LLM for sentiment analysis
- Stores reasoning trace on Walrus
- Publishes sentiment signals

#### Part 4: Agent B (Simulated)
- Detects sentiment_available + price_updated events
- Fetches data from blockchain
- Uses LLM for investment signals
- Stores reasoning trace on Walrus
- Publishes investment signals

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     OFF-CHAIN DATA SOURCES                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   CryptoPanic API                     CoinGecko API            │
│   (News Articles)                     (Price Data)             │
│                                                                 │
└──────────────┬────────────────────────────────┬─────────────────┘
               │                                │
               │ API Clients                    │ API Clients
               │ (Layer 1)                      │ (Layer 1)
               ▼                                ▼
    ┌──────────────────────┐       ┌──────────────────────┐
    │  CryptoPanicClient   │       │   CoinGeckoClient    │
    │  (Raw HTTP)          │       │   (Raw HTTP)         │
    └──────────┬───────────┘       └──────────┬───────────┘
               │                                │
               │ Data Sources                   │ Data Sources
               │ (Layer 2)                      │ (Layer 2)
               ▼                                ▼
    ┌──────────────────────┐       ┌──────────────────────┐
    │  CryptoPanicSource   │       │   CoinGeckoSource    │
    │  (Transformation)    │       │   (Transformation)   │
    └──────────┬───────────┘       └──────────┬───────────┘
               │                                │
               │ Pipelines                      │ Pipelines
               │ (Layer 3)                      │ (Layer 3)
               ▼                                ▼
    ┌──────────────────────┐       ┌──────────────────────┐
    │   NewsPipeline       │       │   PricePipeline      │
    │   (ETL - NO LLM)     │       │   (ETL - NO LLM)     │
    └──────────┬───────────┘       └──────────┬───────────┘
               │                                │
               │ OnChainPublisher               │ OnChainPublisher
               │ (Layer 4)                      │ (Layer 4)
               ▼                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                      SUI BLOCKCHAIN                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  RawDataObject (News)           RawDataObject (Prices)          │
│  • producer: "news_pipeline"     • producer: "price_pipeline"   │
│  • producer_type: "pipeline"     • producer_type: "pipeline"    │
│  • data_type: "news_raw"         • data_type: "price_raw"       │
│  • data_payload: JSON            • data_payload: JSON           │
│                                                                  │
│  Events: news_available          Events: price_updated          │
│                                                                  │
└──────────────┬────────────────────────────────┬──────────────────┘
               │                                │
               │ Event Watchers                 │ Event Watchers
               ▼                                ▼
    ┌──────────────────────┐       ┌──────────────────────┐
    │      Agent A         │       │      Agent B         │
    │  (Sentiment Analysis)│       │ (Investment Signals) │
    │                      │       │                      │
    │  ✓ LLM Reasoning     │◄──────┤  ✓ LLM Reasoning     │
    │  ✓ Walrus Traces     │       │  ✓ Walrus Traces     │
    │  ✓ On-chain Input    │       │  ✓ On-chain Input    │
    │  ✓ On-chain Output   │       │  ✓ On-chain Output   │
    └──────────────────────┘       └──────────────────────┘
```

---

## Key Distinctions

### Pipelines vs Agents

| Aspect | Pipelines | Agents |
|--------|-----------|--------|
| **Purpose** | Move data (ETL) | Process data (reasoning) |
| **LLM Usage** | ❌ No | ✅ Yes |
| **Reasoning** | ❌ No | ✅ Yes |
| **Input Source** | Off-chain APIs | On-chain data |
| **Producer Type** | "pipeline" | "agent" |
| **Walrus Traces** | ❌ No | ✅ Yes |
| **Classes** | NewsPipeline, PricePipeline | Agent A, Agent B, Agent C |

---

## Data Flow

```
1. Off-Chain APIs
   ↓
2. API Clients (Layer 1: Raw HTTP)
   ↓
3. Data Sources (Layer 2: Transformation)
   ↓
4. Pipelines (Layer 3: ETL Orchestration)
   ↓
5. OnChainPublisher (Layer 4: Blockchain Storage)
   ↓
6. SUI Blockchain (RawDataObject + Events)
   ↓
7. Event Watchers (Signal agents on events)
   ↓
8. Real Agents (LLM reasoning + Walrus traces)
   ↓
9. Agent Output → Back to Blockchain
```

---

## File Structure

```
demo/
├── src/
│   ├── blockchain/
│   │   └── sui_publisher.py         ✅ OnChainPublisher + EventEmitter
│   ├── pipeline/
│   │   ├── __init__.py              ✅ Module exports
│   │   ├── news_pipeline.py         ✅ NewsPipeline + NewsScheduler
│   │   └── price_pipeline.py        ✅ PricePipeline + PriceScheduler
│   ├── data_clients/                (Already exists)
│   │   ├── cryptopanic_client.py
│   │   └── coingecko_client.py
│   └── data_sources/                (Already exists)
│       ├── cryptopanic_source.py
│       └── coingecko_source.py
├── smart_contracts/
│   └── raw_data.move                ✅ RawDataObject + Events
└── scripts/
    └── demo_pipeline_architecture.py ✅ Complete demo
```

---

## Testing

### Running the Demo

```bash
cd demo
python3 scripts/demo_pipeline_architecture.py
```

### Expected Output

1. ✅ News pipeline fetches and publishes 5 articles
2. ✅ Price pipeline fetches and publishes BTC price
3. ✅ Events emitted for agent signaling
4. ✅ Simulated agent processing shown

### Sample Output

```
NEWS PIPELINE: ETL Complete
✓ Fetched 5 articles
✓ Published to blockchain: 0x914197...
✓ 5 events emitted

PRICE PIPELINE: ETL Complete
✓ Fetched 1 price (BTC: $66,434.00)
✓ Published to blockchain: 0x0581c0...
✓ 1 event emitted
```

---

## Benefits of This Architecture

### 1. Clear Separation of Concerns
- Pipelines: Pure data movement (no intelligence)
- Agents: Pure reasoning (no data fetching)

### 2. Verifiable Data Lineage
- All agent inputs come from blockchain
- Can trace every decision back to source data
- Immutable audit trail

### 3. Transparency
- Reasoning traces stored on Walrus
- All data on-chain
- Producer type distinguishes pipelines from agents

### 4. Scalability
- Add new data sources → Just add new pipeline
- Add new agents → Just subscribe to events
- Pipelines and agents are decoupled

### 5. Cost Efficiency
- Lightweight events (< 200 bytes) signal agents
- Full data stored once on-chain
- Agents fetch only when needed

---

## Next Steps

### Phase 1: Real Agent Implementation
1. ✅ Implement Agent A with LLM reasoning
2. ✅ Implement Agent B with LLM reasoning
3. ⬜ Implement Agent C (Portfolio Management)
4. ⬜ Add Walrus SDK integration for reasoning storage

### Phase 2: Blockchain Deployment
1. ⬜ Deploy raw_data.move to SUI testnet
2. ⬜ Integrate pysui SDK for real transactions
3. ⬜ Test end-to-end with real blockchain

### Phase 3: Production Readiness
1. ⬜ Add error handling and retry logic
2. ⬜ Implement proper scheduling (APScheduler)
3. ⬜ Add monitoring and alerting
4. ⬜ Deploy to production environment

---

## Conclusion

The data pipeline architecture has been successfully implemented with clear separation between:
- **Pipelines**: Pure ETL operations (no LLM, no reasoning)
- **Agents**: LLM-powered reasoning on on-chain data

All components are working in simulated mode and ready for integration with real SUI blockchain and Walrus storage.

**Status**: ✅ Ready for agent implementation
