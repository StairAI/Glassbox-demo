# Pipeline and Signal Architecture

This document describes the abstract base classes for pipelines and signal storage in the Glass Box Protocol.

## Overview

We've established a clear architectural pattern:

```
┌──────────────┐
│   Pipeline   │  ETL Process (Extract, Transform, Load)
│              │  - Fetches external data
│  (no LLM)    │  - Transforms to standard format
└──────┬───────┘  - Creates Signals
       │
       │ outputs
       ▼
┌──────────────┐
│   Signal    │  Reference to stored data
│              │  - Lightweight metadata
│  (stored)    │  - Points to full data
└──────┬───────┘  - Stored in SignalStorage
       │
       │ consumed by
       ▼
┌──────────────┐
│    Agent     │  Reasoning Process
│              │  - Fetches data via Signal
│  (with LLM)  │  - Processes with reasoning
└──────────────┘  - Outputs new Signals (type="insight")
```

## Key Principles

### 1. Pipelines Generate Signals

**All pipelines follow the same pattern:**

```python
class Pipeline(ABC):
    def extract(self, **kwargs) -> Any:
        """EXTRACT: Fetch data from external sources"""
        pass

    def transform(self, raw_data: Any) -> Dict[str, Any]:
        """TRANSFORM: Convert to standard format"""
        pass

    def load(self, transformed_data: Dict[str, Any]) -> Signal:
        """LOAD: Create Signal and store it"""
        pass

    def run(self, **kwargs) -> Signal:
        """Run complete ETL pipeline"""
        raw = self.extract(**kwargs)
        transformed = self.transform(raw)
        signal = self.load(transformed)
        return signal
```

**Pipelines are pure ETL:**
- No reasoning
- No LLM calls
- Just data movement

### 2. Signals Are Stored

**All signals must be stored in a SignalStorage implementation:**

```python
class SignalStorage(ABC):
    def store(self, signal: Signal) -> bool:
        """Store a signal"""
        pass

    def get(self, signal_id: str) -> Optional[Signal]:
        """Retrieve a signal by ID"""
        pass

    def list(self, signal_type: Optional[str] = None, limit: int = 100) -> List[Signal]:
        """List signals with filtering"""
        pass

    def delete(self, signal_id: str) -> bool:
        """Delete a signal"""
        pass

    def count(self, signal_type: Optional[str] = None) -> int:
        """Count signals"""
        pass
```

**Storage implementations:**
- `FileBasedSignalStorage`: JSON file (fast, local, dev)
- `BlockchainSignalRegistry`: SUI blockchain (permanent, read-only)
- `HybridSignalStorage`: File cache + blockchain (best of both)

### 3. Data Flow

```
External API
    │
    ▼
┌─────────────────────┐
│  Pipeline.extract() │  Fetch raw data
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│Pipeline.transform() │  Convert to standard format
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Pipeline.load()   │  Store data + create Signal
└──────────┬──────────┘
           │
           ▼
     Signal object
           │
           ▼
┌─────────────────────┐
│ SignalStorage.store│  Persist signal metadata
└──────────┬──────────┘
           │
           ▼
   Stored in registry
           │
           ▼
┌─────────────────────┐
│Agent.query_signals │  Fetch signals for processing
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│Signal.fetch_full() │  Get full data from storage
└──────────┬──────────┘
           │
           ▼
    Agent processes
           │
           ▼
   Signal (new Signal)
```

## Implementation Examples

### Example 1: News Pipeline

```python
from src.abstract import Pipeline, FileBasedSignalStorage
from src.core.signal import NewsSignal

class NewsPipeline(Pipeline):
    def __init__(self, news_source, publisher, signal_storage):
        super().__init__(
            name="news_pipeline",
            signal_storage=signal_storage
        )
        self.news_source = news_source
        self.publisher = publisher

    def extract(self, currencies=None, limit=20):
        """Fetch news from API"""
        return self.news_source.fetch_news(currencies, limit)

    def transform(self, raw_data):
        """Convert to storage format"""
        return {
            "articles": [article.to_dict() for article in raw_data],
            "total_count": len(raw_data),
            "fetch_timestamp": datetime.now().isoformat()
        }

    def load(self, transformed_data) -> NewsSignal:
        """Store on Walrus + SUI, return NewsSignal"""
        signal = self.publisher.publish_news_signal(
            news_data=transformed_data,
            producer="news_pipeline"
        )
        return signal

    def validate_config(self):
        return self.news_source is not None and self.publisher is not None

# Usage
storage = FileBasedSignalStorage("data/signals.json")
pipeline = NewsPipeline(news_source, publisher, storage)

# Run once
news_signal = pipeline.run(currencies=["BTC", "SUI"], limit=10)
# Pipeline automatically stores signal in storage

# Run periodically
from src.abstract import ScheduledPipeline

scheduled = ScheduledPipeline(
    name="news_pipeline",
    signal_storage=storage,
    interval_seconds=300
)
scheduled.run_periodic(currencies=["BTC"])
```

### Example 2: Agent Using Signals

```python
from src.abstract import create_signal_storage

class SentimentAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        # Agents query signals from storage
        self.storage = create_signal_storage("file")

    def run(self):
        # Get recent news signals
        news_signals = self.storage.list(
            signal_type="news",
            limit=10
        )

        for signal in news_signals:
            # Fetch full data
            full_data = signal.fetch_full_data()

            # Process with LLM
            sentiment = self.analyze_sentiment(full_data)

            # Create signal signal
            signal = InsightSignal(
                object_id=generate_id(),
                signal_type="sentiment",
                signal_value=sentiment,
                confidence=0.85,
                timestamp=datetime.now(),
                producer="sentiment_agent"
            )

            # Store signal for downstream agents
            self.storage.store(signal)

    def analyze_sentiment(self, news_data):
        # Use LLM to analyze
        response = self.llm_client.call(
            prompt=f"Analyze sentiment: {news_data}",
            temperature=0.2
        )
        return parse_sentiment(response)
```

### Example 3: Signal Storage Implementations

```python
from src.abstract import (
    FileBasedSignalStorage,
    BlockchainSignalRegistry,
    HybridSignalStorage
)

# File-based (fast, local)
file_storage = FileBasedSignalStorage("data/signals.json")
file_storage.store(news_signal)
signals = file_storage.list(limit=10)

# Blockchain registry (permanent, read-only)
blockchain_registry = BlockchainSignalRegistry(sui_client)
signals = blockchain_registry.list(signal_type="news")

# Hybrid (file cache + blockchain)
hybrid = HybridSignalStorage(
    file_storage=file_storage,
    blockchain_registry=blockchain_registry
)
hybrid.store(signal)  # Stores in file
signals = hybrid.list()  # Reads from file (fast)
```

## File Structure

```
demo/src/abstract/
├── __init__.py                 # Module exports
├── README.md                   # Comprehensive documentation
├── news_source.py              # NewsSource abstract class
├── price_source.py             # PriceSource abstract class
├── pipeline.py                 # Pipeline, ScheduledPipeline, SignalStorage
└── signal_storage.py          # Storage implementations

demo/src/core/
└── signal.py                  # Signal classes (NewsSignal, etc.)

demo/src/pipeline/
├── news_pipeline.py            # Concrete NewsPipeline implementation
├── price_pipeline.py           # Concrete PricePipeline implementation
└── ...

demo/data/
└── signal_registry.json       # FileBasedSignalStorage data
```

## Benefits

### 1. Clear Separation of Concerns

- **Pipelines**: Data movement (no reasoning)
- **Agents**: Data processing (with reasoning)
- **Storage**: Data persistence

### 2. Uniform Interface

All pipelines follow the same ETL pattern:
```python
signal = pipeline.run()  # Extract → Transform → Load
```

All signals are stored the same way:
```python
storage.store(signal)
signals = storage.list(signal_type="news")
```

### 3. Testability

Each component can be tested independently:

```python
# Test pipeline
def test_news_pipeline():
    mock_source = MockNewsSource()
    mock_publisher = MockPublisher()
    storage = FileBasedSignalStorage("/tmp/test_signals.json")

    pipeline = NewsPipeline(mock_source, mock_publisher, storage)
    signal = pipeline.run()

    assert signal.signal_type == "news"
    assert storage.count() == 1

# Test storage
def test_signal_storage():
    storage = FileBasedSignalStorage("/tmp/test.json")
    storage.store(news_signal)

    retrieved = storage.get(news_signal.object_id)
    assert retrieved.object_id == news_signal.object_id
```

### 4. Extensibility

Add new pipelines easily:

```python
class TwitterPipeline(Pipeline):
    def extract(self, hashtags=None):
        return self.twitter_client.fetch_tweets(hashtags)

    def transform(self, tweets):
        return {"tweets": [t.to_dict() for t in tweets]}

    def load(self, transformed_data):
        return self.publisher.publish_social_signal(transformed_data)

    def validate_config(self):
        return self.twitter_client is not None
```

Add new storage backends:

```python
class PostgreSQLSignalStorage(SignalStorage):
    def store(self, signal):
        self.db.execute("INSERT INTO signals ...")

    def get(self, signal_id):
        return self.db.query("SELECT * FROM signals WHERE id = ?")

    # ... etc
```

## Migration Path

### Current Code

Many existing pipelines don't fully follow this pattern. Migration path:

1. **Identify pipelines** that create signals
2. **Inherit from `Pipeline`** abstract class
3. **Implement ETL methods**: `extract()`, `transform()`, `load()`
4. **Add `SignalStorage`** to persist signals
5. **Update tests** to use new interface

### Example Migration

**Before:**
```python
class NewsPipeline:
    def fetch_and_publish(self, currencies, limit):
        articles = self.source.fetch_news(currencies, limit)
        news_data = self._transform(articles)
        signal = self.publisher.publish_news_signal(news_data)
        return signal
```

**After:**
```python
class NewsPipeline(Pipeline):
    def extract(self, currencies=None, limit=20):
        return self.source.fetch_news(currencies, limit)

    def transform(self, articles):
        return self._transform(articles)

    def load(self, transformed_data):
        return self.publisher.publish_news_signal(transformed_data)

    def validate_config(self):
        return self.source is not None
```

## Next Steps

1. ✅ Create abstract base classes
2. ✅ Implement file-based signal storage
3. ⏳ Migrate existing pipelines to use `Pipeline` base class
4. ⏳ Add tests for pipeline and storage abstractions
5. ⏳ Implement blockchain signal registry
6. ⏳ Create example pipelines using new architecture

## Related Documentation

- [Abstract Base Classes README](src/abstract/README.md)
- [Signal Architecture](documents/tech-design.md#signal-architecture)
- [Pipeline Implementation Guide](src/pipeline/README.md)

## Summary

The pipeline and signal architecture provides:

1. **Clear ETL Pattern**: Extract → Transform → Load
2. **Signal-Based Data Flow**: Pipelines output Signals
3. **Flexible Storage**: File, Blockchain, or Hybrid
4. **Separation of Concerns**: Pipelines ≠ Agents
5. **Uniform Interfaces**: Easy to extend and test

All pipelines generate signals. All signals are stored. Agents consume signals.
