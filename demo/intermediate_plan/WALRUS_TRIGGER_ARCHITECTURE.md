# Walrus + Signal Architecture Plan

**Date**: 2026-03-28
**Status**: 🎯 Planning

## Overview

Simplify the architecture with:
1. **Walrus** for large data storage (news articles)
2. **On-chain oracles** for price data (already on SUI)
3. **Unified Signal abstraction** for agent inputs

## Key Simplifications

### 1. News Data Flow
```
CryptoPanic API → NewsPipeline → Walrus (full data)
                              → SUI (metadata + blob_id)
                              → Signal: NewsSignal
```

### 2. Price Data Flow
```
On-chain Oracle (Pyth/Switchboard) → SuiPricePipeline → Read from SUI
                                                       → Signal: PriceSignal
```

### 3. Agent Input
```
All agents receive: List[Signal]

Signal types:
- NewsSignal: {blob_id, data_hash, timestamp}
- PriceSignal: {symbol, price, oracle_source}
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     DATA SOURCES                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   CryptoPanic API              On-Chain Oracle (Pyth/Switchboard)
│   (News Articles)              (Already on SUI!)                │
│                                                                 │
└──────────┬─────────────────────────────────────┬────────────────┘
           │                                     │
           ▼                                     ▼
┌──────────────────────┐            ┌──────────────────────┐
│   NewsPipeline       │            │  SuiPricePipeline    │
│   (Fetch + Store)    │            │  (Read from SUI)     │
└──────────┬───────────┘            └──────────┬───────────┘
           │                                   │
           │ Store large data                  │ Just read
           ▼                                   │
┌──────────────────────┐                      │
│   Walrus Storage     │                      │
│   (Full articles)    │                      │
└──────────────────────┘                      │
           │                                   │
           │ blob_id                           │
           ▼                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SUI BLOCKCHAIN                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  NewsSignal Object              PriceSignal Object           │
│  • signal_type: "news"          • signal_type: "price"       │
│  • walrus_blob_id                • symbol                      │
│  • data_hash                     • price_usd                   │
│  • timestamp                     • oracle_source               │
│                                  • timestamp                   │
│                                                                 │
└──────────────┬──────────────────────────────────┬──────────────┘
               │                                  │
               │ Unified Signal Interface        │
               ▼                                  ▼
    ┌──────────────────────────────────────────────────┐
    │            Agent Input Layer                     │
    │                                                  │
    │  process(signals: List[Signal])                │
    │                                                  │
    │  for signal in signals:                        │
    │      if signal.type == "news":                  │
    │          data = walrus.fetch(signal.blob_id)    │
    │      elif signal.type == "price":               │
    │          data = signal.price_usd                │
    │                                                  │
    └──────────────────┬───────────────────────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │      Agent A         │
            │  (Sentiment Analysis)│
            │                      │
            │  ✓ LLM Reasoning     │
            │  ✓ Walrus Traces     │
            └──────────────────────┘
```

---

## Implementation Plan

### Phase 1: Walrus Integration ✅

**File**: `src/storage/walrus_client.py`

```python
class WalrusClient:
    """Client for Walrus decentralized storage."""

    def store(self, data: bytes) -> str:
        """
        Store data on Walrus.

        Args:
            data: Raw bytes to store

        Returns:
            blob_id: Walrus blob identifier
        """

    def fetch(self, blob_id: str) -> bytes:
        """
        Fetch data from Walrus.

        Args:
            blob_id: Walrus blob identifier

        Returns:
            data: Raw bytes
        """

    def exists(self, blob_id: str) -> bool:
        """Check if blob exists."""
```

---

### Phase 2: Unified Signal Abstraction ✅

**File**: `src/core/signal.py`

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Signal(ABC):
    """
    Base class for all agent signals.

    All agent inputs are signals - lightweight references to data.
    """
    signal_type: str           # "news", "price", "insight"
    timestamp: datetime
    object_id: str              # SUI object ID

    @abstractmethod
    def fetch_full_data(self) -> Dict[str, Any]:
        """Fetch the full data referenced by this signal."""
        pass


@dataclass
class NewsSignal(Signal):
    """
    Signal for news data.
    Full data stored on Walrus, only metadata on-chain.
    """
    walrus_blob_id: str         # Reference to Walrus
    data_hash: str              # SHA-256 for integrity
    size_bytes: int             # Size info
    articles_count: int         # Preview info

    def fetch_full_data(self) -> Dict[str, Any]:
        """Fetch full news data from Walrus."""
        from src.storage.walrus_client import WalrusClient
        client = WalrusClient()
        data_bytes = client.fetch(self.walrus_blob_id)
        return json.loads(data_bytes)


@dataclass
class PriceSignal(Signal):
    """
    Signal for price data.
    Data already on-chain from oracle, no need for Walrus.
    """
    symbol: str                 # "BTC", "ETH", "SUI"
    price_usd: float            # Current price
    oracle_source: str          # "pyth", "switchboard"
    confidence: Optional[float] # Oracle confidence

    def fetch_full_data(self) -> Dict[str, Any]:
        """Price data is already in signal (small enough)."""
        return {
            "symbol": self.symbol,
            "price_usd": self.price_usd,
            "oracle_source": self.oracle_source,
            "confidence": self.confidence,
            "timestamp": self.timestamp
        }
```

---

### Phase 3: Update OnChainPublisher ✅

**File**: `src/blockchain/sui_publisher.py`

```python
class OnChainPublisher:
    """
    Publishes signals to SUI blockchain.

    Uses Walrus for large data, direct storage for small data.
    """

    def __init__(
        self,
        walrus_client: Optional[WalrusClient] = None,
        sui_client = None,
        simulated: bool = True
    ):
        self.walrus_client = walrus_client
        self.sui_client = sui_client
        self.simulated = simulated

        # Threshold: if data > 1KB, use Walrus
        self.walrus_threshold_bytes = 1024

    def publish_news_signal(
        self,
        news_data: Dict[str, Any],
        producer: str
    ) -> str:
        """
        Publish news signal.
        - Full data → Walrus
        - Metadata → SUI
        """
        # 1. Store full data on Walrus
        data_bytes = json.dumps(news_data).encode()
        data_hash = hashlib.sha256(data_bytes).hexdigest()

        blob_id = self.walrus_client.store(data_bytes)

        # 2. Create signal metadata (lightweight!)
        signal_metadata = {
            "signal_type": "news",
            "walrus_blob_id": blob_id,
            "data_hash": data_hash,
            "size_bytes": len(data_bytes),
            "articles_count": len(news_data.get("articles", [])),
            "timestamp": int(datetime.now().timestamp()),
            "producer": producer
        }

        # 3. Publish metadata to SUI (< 500 bytes)
        object_id = self._publish_to_sui(signal_metadata)

        return object_id

    def publish_price_signal(
        self,
        symbol: str,
        price_usd: float,
        oracle_source: str,
        confidence: Optional[float] = None
    ) -> str:
        """
        Publish price signal.
        - Data is small, store directly on SUI
        """
        signal_data = {
            "signal_type": "price",
            "symbol": symbol,
            "price_usd": price_usd,
            "oracle_source": oracle_source,
            "confidence": confidence,
            "timestamp": int(datetime.now().timestamp())
        }

        object_id = self._publish_to_sui(signal_data)

        return object_id
```

---

### Phase 4: Update NewsPipeline ✅

**File**: `src/pipeline/news_pipeline.py`

```python
class NewsPipeline:
    """
    News ETL Pipeline with Walrus storage.
    """

    def __init__(
        self,
        api_token: str,
        publisher: OnChainPublisher,
        walrus_client: WalrusClient
    ):
        self.source = CryptoPanicSource(api_token=api_token)
        self.publisher = publisher
        self.walrus_client = walrus_client

    def fetch_and_publish(
        self,
        currencies: Optional[List[str]] = None,
        limit: int = 20
    ) -> str:
        """
        Fetch news and publish to Walrus + SUI.

        Returns:
            object_id: SUI object ID of the signal
        """
        # Step 1: Fetch from API
        articles = self.source.fetch_news(currencies=currencies, limit=limit)

        # Step 2: Transform
        news_data = self._transform_for_storage(articles)

        # Step 3: Publish to Walrus + SUI
        # (Walrus handles full data, SUI stores metadata)
        object_id = self.publisher.publish_news_signal(
            news_data=news_data,
            producer="news_pipeline"
        )

        return object_id
```

---

### Phase 5: Create SuiPricePipeline ✅

**File**: `src/pipeline/sui_price_pipeline.py`

```python
class SuiPricePipeline:
    """
    Pipeline to read price data from on-chain oracles.

    Unlike NewsPipeline, this READS from SUI (doesn't fetch from API).
    Oracles like Pyth/Switchboard already post prices on-chain.
    """

    def __init__(
        self,
        sui_client,
        publisher: OnChainPublisher,
        oracle_package_id: str  # Pyth or Switchboard package
    ):
        self.sui_client = sui_client
        self.publisher = publisher
        self.oracle_package_id = oracle_package_id

    def read_and_publish_signal(
        self,
        symbol: str
    ) -> str:
        """
        Read price from on-chain oracle and create signal.

        Args:
            symbol: Asset symbol (e.g., "BTC")

        Returns:
            object_id: SUI object ID of the signal
        """
        # Step 1: Read from on-chain oracle
        price_data = self._read_oracle_price(symbol)

        # Step 2: Publish signal to SUI
        # (No Walrus needed - data is already on-chain and small)
        object_id = self.publisher.publish_price_signal(
            symbol=symbol,
            price_usd=price_data["price"],
            oracle_source=price_data["source"],
            confidence=price_data.get("confidence")
        )

        return object_id

    def _read_oracle_price(self, symbol: str) -> Dict[str, Any]:
        """
        Read price from on-chain oracle (Pyth/Switchboard).

        This is a READ operation, not a write.
        """
        # Pseudocode for reading from Pyth oracle:
        # price_feed_id = SYMBOL_TO_FEED_ID[symbol]
        # price_obj = self.sui_client.get_object(price_feed_id)
        # return parse_price_object(price_obj)

        # For demo, simulate
        return {
            "symbol": symbol,
            "price": 66434.0,
            "source": "pyth",
            "confidence": 0.01
        }
```

---

### Phase 6: Update Smart Contract ✅

**File**: `smart_contracts/signal.move`

```move
module glass_box::signal {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    use sui::transfer;
    use sui::event;

    /// Base signal object
    struct SignalObject has key, store {
        id: UID,
        signal_type: vector<u8>,   // "news", "price", "insight"
        timestamp: u64,
        producer: vector<u8>,
    }

    /// News signal - references Walrus
    struct NewsSignal has key, store {
        id: UID,
        signal_type: vector<u8>,   // "news"
        walrus_blob_id: vector<u8>, // Walrus reference
        data_hash: vector<u8>,      // SHA-256
        size_bytes: u64,
        articles_count: u64,
        timestamp: u64,
        producer: vector<u8>,
    }

    /// Price signal - data on-chain
    struct PriceSignal has key, store {
        id: UID,
        signal_type: vector<u8>,   // "price"
        symbol: vector<u8>,
        price_usd: u64,             // Scaled by 1e8
        oracle_source: vector<u8>,  // "pyth", "switchboard"
        confidence: u64,            // Scaled by 1e8
        timestamp: u64,
    }

    /// Event emitted when signal is created
    struct SignalCreated has copy, drop {
        signal_id: address,
        signal_type: vector<u8>,
        timestamp: u64,
    }

    /// Publish news signal
    public entry fun publish_news_signal(
        walrus_blob_id: vector<u8>,
        data_hash: vector<u8>,
        size_bytes: u64,
        articles_count: u64,
        timestamp: u64,
        producer: vector<u8>,
        ctx: &mut TxContext
    ) {
        let signal = NewsSignal {
            id: object::new(ctx),
            signal_type: b"news",
            walrus_blob_id,
            data_hash,
            size_bytes,
            articles_count,
            timestamp,
            producer,
        };

        let signal_id = object::uid_to_address(&signal.id);

        event::emit(SignalCreated {
            signal_id,
            signal_type: b"news",
            timestamp,
        });

        transfer::public_share_object(signal);
    }

    /// Publish price signal
    public entry fun publish_price_signal(
        symbol: vector<u8>,
        price_usd: u64,
        oracle_source: vector<u8>,
        confidence: u64,
        timestamp: u64,
        ctx: &mut TxContext
    ) {
        let signal = PriceSignal {
            id: object::new(ctx),
            signal_type: b"price",
            symbol,
            price_usd,
            oracle_source,
            confidence,
            timestamp,
        };

        let signal_id = object::uid_to_address(&signal.id);

        event::emit(SignalCreated {
            signal_id,
            signal_type: b"price",
            timestamp,
        });

        transfer::public_share_object(signal);
    }
}
```

---

## Benefits

### 1. Cost Efficiency
- Large data (news) → Walrus (cheap)
- Small data (prices) → SUI (acceptable)
- No redundant data movement

### 2. Leverage Existing Infrastructure
- Price oracles already on SUI
- No need to fetch from off-chain APIs
- Just read and create signals

### 3. Unified Agent Interface
```python
# All agents receive signals
def process(self, signals: List[Signal]) -> AgentOutput:
    for signal in signals:
        if isinstance(signal, NewsSignal):
            data = signal.fetch_full_data()  # From Walrus
        elif isinstance(signal, PriceSignal):
            data = signal.fetch_full_data()  # Already in signal
```

### 4. Clear Separation
- **NewsPipeline**: Fetch from API → Walrus + SUI
- **SuiPricePipeline**: Read from SUI → Create signal
- **Agents**: Process signals (unified interface)

---

## Next Steps

1. ✅ Implement WalrusClient
2. ✅ Create Signal abstraction
3. ✅ Update OnChainPublisher with Walrus support
4. ✅ Update NewsPipeline to use Walrus
5. ✅ Create SuiPricePipeline for on-chain oracle
6. ✅ Update smart contract with signal types
7. ✅ Create demo showing full flow
