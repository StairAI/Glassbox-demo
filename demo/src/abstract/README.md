# Abstract Base Classes

This module provides abstract base classes for the Glass Box Protocol, ensuring consistent interfaces across the system.

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    Glass Box Protocol                        │
└──────────────────────────────────────────────────────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
    ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
    │ Sources │          │Pipelines│          │ Agents  │
    └─────────┘          └─────────┘          └─────────┘
         │                     │                     │
    Extract data         Create Signals      Process Signals
         │                     │                     │
         ▼                     ▼                     ▼
    NewsArticle            Signal              Signal
    PriceData           (stored data)          (output)
```

## Module Structure

### 1. Data Sources (`news_source.py`, `price_source.py`)

Abstract interfaces for external data sources.

**Key Classes:**
- `NewsSource`: Abstract base for news APIs (CryptoPanic, NewsAPI, etc.)
- `PriceSource`: Abstract base for price oracles (CoinGecko, Pyth, etc.)

**Purpose:**
- Standardize data fetching from multiple APIs
- Return consistent dataclass objects (`NewsArticle`, `PriceData`)
- Handle API-specific errors uniformly

**Example:**
```python
from src.abstract import NewsSource, NewsArticle

class CryptoPanicSource(NewsSource):
    def fetch_news(self, currencies=None, limit=100) -> List[NewsArticle]:
        # Fetch from CryptoPanic API
        # Transform to NewsArticle objects
        return articles
```

### 2. Pipelines (`pipeline.py`)

Abstract ETL pipeline interface. Pipelines transform external data into signals.

**Key Classes:**
- `Pipeline`: Base ETL pipeline (Extract, Transform, Load)
- `ScheduledPipeline`: Pipeline with scheduling capabilities
- `SignalStorage`: Abstract storage interface

**Key Principles:**
- Pipelines are NOT agents (no reasoning, no LLM)
- Pipelines output `Signal` objects
- Pipelines follow ETL pattern: Extract → Transform → Load

**Example:**
```python
from src.abstract import Pipeline
from src.core.signal import NewsSignal

class NewsPipeline(Pipeline):
    def extract(self, currencies=None, limit=20):
        # Fetch from news API
        return self.news_source.fetch_news(currencies, limit)

    def transform(self, raw_data):
        # Convert to storage format
        return {"articles": [...], "total_count": 10}

    def load(self, transformed_data) -> NewsSignal:
        # Store on Walrus + SUI
        # Return NewsSignal
        return self.publisher.publish_news_signal(transformed_data)
```

### 3. Signal Storage (`signal_storage.py`)

Concrete implementations of signal storage backends.

**Key Classes:**
- `FileBasedSignalStorage`: JSON file storage (demo/development)
- `BlockchainSignalRegistry`: Query signals from SUI blockchain (read-only)
- `HybridSignalStorage`: File cache + blockchain (best of both)

**Purpose:**
- Provide fast local access to signals (for agents)
- Maintain permanent record on blockchain
- Support offline development/testing

**Example:**
```python
from src.abstract import create_signal_storage

# File-based storage (fast, local)
storage = create_signal_storage("file", storage_path="data/signals.json")

# Store a signal
storage.store(news_signal)

# Query signals
recent_news = storage.list(signal_type="news", limit=10)
```

## Data Flow

### Pipeline → Signal → Agent

```
1. Pipeline extracts data
   ↓
2. Pipeline transforms data
   ↓
3. Pipeline creates Signal
   ↓
4. Signal stored in SignalStorage
   ↓
5. Agent queries SignalStorage
   ↓
6. Agent fetches full data via Signal.fetch_full_data()
   ↓
7. Agent processes data
   ↓
8. Agent outputs Signal with type="insight"
```

### Storage Architecture

```
┌─────────────────┐
│  NewsPipeline   │
└────────┬────────┘
         │ creates
         ▼
┌─────────────────┐
│  NewsSignal    │◄──── Agents query this
├─────────────────┤
│ object_id       │
│ walrus_blob_id  │◄──── Reference to full data
│ data_hash       │
│ size_bytes      │
└────────┬────────┘
         │ stored in
         ▼
┌──────────────────────────┐
│   SignalStorage         │
├──────────────────────────┤
│  FileBasedSignalStorage │ ← Fast, local, dev
│  BlockchainSignalRegistry│ ← Permanent, on-chain
│  HybridSignalStorage    │ ← Best of both
└──────────────────────────┘
         │ persists to
         ▼
┌──────────────────────────┐
│  Storage Backends        │
├──────────────────────────┤
│  signals.json           │ ← File
│  SUI Blockchain          │ ← Blockchain
│  Walrus Storage          │ ← Blob data
└──────────────────────────┘
```

## Usage Examples

### Creating a Pipeline

```python
from src.abstract import Pipeline
from src.abstract import FileBasedSignalStorage

class MyPipeline(Pipeline):
    def __init__(self, api_client, publisher, signal_storage):
        super().__init__(
            name="my_pipeline",
            signal_storage=signal_storage
        )
        self.api_client = api_client
        self.publisher = publisher

    def extract(self, **kwargs):
        # Fetch from API
        return self.api_client.fetch_data()

    def transform(self, raw_data):
        # Convert to standard format
        return {"processed": raw_data}

    def load(self, transformed_data):
        # Create and return signal
        return self.publisher.publish_signal(transformed_data)

    def validate_config(self):
        return self.api_client is not None

# Use the pipeline
storage = FileBasedSignalStorage("data/signals.json")
pipeline = MyPipeline(api_client, publisher, storage)

# Run once
signal = pipeline.run()

# Run periodically
scheduled = ScheduledPipeline(
    name="my_pipeline",
    signal_storage=storage,
    interval_seconds=300  # Every 5 minutes
)
scheduled.run_periodic()
```

### Using Signal Storage

```python
from src.abstract import create_signal_storage

# Create storage
storage = create_signal_storage("file")

# Store signals
storage.store(news_signal)
storage.store(price_signal)
storage.store(signal_signal)

# Query signals
all_signals = storage.list(limit=100)
news_signals = storage.list(signal_type="news", limit=10)
signal_signals = storage.list(signal_type="insight", limit=5)

# Get specific signal
signal = storage.get("signal_object_id_here")

# Count signals
total = storage.count()
news_count = storage.count(signal_type="news")

# Delete signal
storage.delete("signal_id")
```

### Agent Using Signals

```python
from src.abstract import create_signal_storage

class MyAgent:
    def __init__(self):
        self.storage = create_signal_storage("file")

    def process(self):
        # Get recent news signals
        news_signals = self.storage.list(
            signal_type="news",
            limit=10
        )

        for signal in news_signals:
            # Fetch full data from storage
            full_data = signal.fetch_full_data()

            # Process data
            result = self.analyze(full_data)

            # Create output signal (new signal)
            signal = self.create_signal(result)

            # Store signal signal
            self.storage.store(signal)
```

## Design Principles

### 1. Separation of Concerns

- **Data Sources**: Fetch raw data from APIs
- **Pipelines**: Transform data and create signals (no reasoning)
- **Agents**: Process signals and generate insights (with reasoning)

### 2. Signal-Based Architecture

- All data flows through signals
- Signals are lightweight references to data
- Actual data stored separately (Walrus, SUI, etc.)
- Unified interface for all data types

### 3. Storage Flexibility

- File-based for development/testing
- Blockchain for production/transparency
- Hybrid for best performance
- Easy to switch between backends

### 4. Extensibility

- Add new data sources by implementing `NewsSource`/`PriceSource`
- Add new pipelines by extending `Pipeline`
- Add new storage backends by implementing `SignalStorage`

## Testing

Run tests for abstract classes:

```bash
# Test pipeline abstraction
pytest tests/pipeline/ -v

# Test signal storage
pytest tests/storage/ -v

# Test data sources
pytest tests/data_sources/ -v
```

## Future Enhancements

1. **Database Storage**: Add PostgreSQL/MySQL implementation of `SignalStorage`
2. **Caching Layer**: Add Redis cache for frequently accessed signals
3. **Event Streaming**: Add Kafka/RabbitMQ support for real-time signal distribution
4. **Query Interface**: Add SQL-like query interface for complex signal queries
5. **Blockchain Indexer**: Implement efficient blockchain signal indexing

## Related Modules

- [`src/core/`](../core/README.md) - Core data structures (Signal types: news, price, signal)
- [`src/pipeline/`](../pipeline/README.md) - Concrete pipeline implementations
- [`src/data_sources/`](../data_sources/README.md) - Data source implementations
- [`src/agents/`](../agents/README.md) - Agent implementations

## License

Part of the Glass Box Protocol demo project.
