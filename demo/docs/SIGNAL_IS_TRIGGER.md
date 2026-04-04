# Signal Is Just a Signal Type

**IMPORTANT**: There is NO separate "Signal" class in the Glass Box Protocol.

## Key Concept

**Everything is a Signal.**

"Signal" is simply a `signal_type="insight"`, not a separate class or concept.

## Architecture

```
All Data = Signals
├── signal_type="news"     → NewsSignal class
├── signal_type="price"    → PriceSignal class
└── signal_type="insight"   → InsightSignal class
```

## What Are Signals?

Signals are **agent outputs** that can signal downstream agents.

### Examples of Signals

1. **Sentiment Analysis Output**
   ```python
   InsightSignal(
       signal_type="insight",  # <-- Just a type, not a separate class
       signal_type="sentiment",
       signal_value={"BTC": 0.75, "ETH": 0.60},
       confidence=0.85,
       producer="agent_a_sentiment"
   )
   ```

2. **Investment Recommendation**
   ```python
   InsightSignal(
       signal_type="insight",
       signal_type="investment",
       signal_value={"action": "buy", "asset": "BTC", "amount": 1.5},
       confidence=0.90,
       producer="agent_b_investment"
   )
   ```

3. **Portfolio Rebalancing**
   ```python
   InsightSignal(
       signal_type="insight",
       signal_type="portfolio",
       signal_value={"allocations": {"BTC": 0.6, "ETH": 0.4}},
       confidence=0.88,
       producer="agent_c_portfolio"
   )
   ```

## Why No Separate Signal Class?

### Unified Architecture

Everything flowing through the system is a Signal:

```
External API → Pipeline → NewsSignal
                              ↓
                         Agent (reads)
                              ↓
                         InsightSignal (writes)
                              ↓
                    Downstream Agent (reads)
                              ↓
                         InsightSignal (writes)
```

All signals:
- Have same interface: `Signal.fetch_full_data()`
- Stored same way: `SignalStorage.store(signal)`
- Queried same way: `SignalStorage.list(signal_type="insight")`

### Simplicity

Having a separate Signal class would create unnecessary complexity:

**❌ Bad (Separate Classes):**
```python
# Need separate storage
signal_storage = SignalStorage()
signal_storage = SignalStorage()

# Need separate query methods
signals = signal_storage.list()
signals = signal_storage.list()

# Need conversion between types
signal = signal.to_signal()  # ???
```

**✅ Good (Unified):**
```python
# One storage for everything
storage = SignalStorage()

# One query method
news_signals = storage.list(signal_type="news")
signal_signals = storage.list(signal_type="insight")

# No conversion needed - everything is a Signal
```

## Data Flow

```
┌─────────────┐
│News Pipeline│
└──────┬──────┘
       │ outputs
       ▼
  NewsSignal (type="news")
       │
       │ consumed by
       ▼
┌─────────────┐
│  Agent A    │ Sentiment Analysis
└──────┬──────┘
       │ outputs
       ▼
  InsightSignal (type="insight", signal_type="sentiment")
       │
       │ consumed by
       ▼
┌─────────────┐
│  Agent B    │ Investment Decision
└──────┬──────┘
       │ outputs
       ▼
  InsightSignal (type="insight", signal_type="investment")
       │
       │ consumed by
       ▼
┌─────────────┐
│  Agent C    │ Portfolio Management
└──────┬──────┘
       │ outputs
       ▼
  InsightSignal (type="insight", signal_type="portfolio")
```

**All outputs are signals. Signals are just signals from agents.**

## Code Examples

### Agent Creating a Signal

```python
from src.core.signal import InsightSignal
from src.abstract import create_signal_storage
from datetime import datetime

class SentimentAgent:
    def __init__(self):
        self.storage = create_signal_storage("file")

    def run(self):
        # Get news signals
        news_signals = self.storage.list(signal_type="news", limit=10)

        # Process news
        sentiment = self.analyze_sentiment(news_signals)

        # Create signal signal (NOT a separate Signal object!)
        signal = InsightSignal(
            object_id=generate_id(),
            signal_type="sentiment",
            signal_value=sentiment,
            confidence=0.85,
            timestamp=datetime.now(),
            producer="sentiment_agent"
        )

        # Store like any other signal
        self.storage.store(signal)

        return signal
```

### Downstream Agent Consuming Signal

```python
class InvestmentAgent:
    def __init__(self):
        self.storage = create_signal_storage("file")

    def run(self):
        # Get signal signals (agent outputs)
        sentiment_signals = self.storage.list(
            signal_type="insight",  # <-- Just filtering by type
            limit=10
        )

        for signal in sentiment_signals:
            # Fetch full data (same interface as news/price signals)
            data = signal.fetch_full_data()

            # Check signal type
            if data["signal_type"] == "sentiment":
                # Use sentiment for investment decision
                self.make_decision(data["signal_value"])
```

## Storage

Signals are stored the same way as news and price signals:

```python
from src.abstract import FileBasedSignalStorage

storage = FileBasedSignalStorage("data/signals.json")

# Store all signal types the same way
storage.store(news_signal)      # type="news"
storage.store(price_signal)     # type="price"
storage.store(signal_signal)    # type="insight"

# Query by type
news = storage.list(signal_type="news")
prices = storage.list(signal_type="price")
signals = storage.list(signal_type="insight")  # <-- Same interface
```

## Summary

1. **Signal is NOT a separate class** - it's `signal_type="insight"`
2. **InsightSignal IS a Signal subclass** - implements Signal interface
3. **All agent outputs are signals** - stored and queried the same way
4. **Unified architecture** - one storage, one interface, simpler code

**Remember**: When you see "signal" in the codebase, think "signal from an agent" not "separate thing."

## Related Documentation

- [Signal Architecture](../src/core/signal.py)
- [Pipeline and Signal Architecture](../PIPELINE_TRIGGER_ARCHITECTURE.md)
- [Abstract Base Classes](../src/abstract/README.md)
