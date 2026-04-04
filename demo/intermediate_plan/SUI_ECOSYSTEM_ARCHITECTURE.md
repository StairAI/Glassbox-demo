# SUI Ecosystem Architecture for Glass Box Protocol

**Date:** 2026-03-28
**Status:** Architecture Design

---

## Three Distinct Use Cases

### Use Case 1: Event Signals & Data Source Inventory
**What**: Real-time events that signal agent execution
**Examples**:
- Price threshold crossed (BTC > $70k)
- News article published (crypto regulatory news)
- Time-based signals (daily portfolio rebalance)
- Data source updates inventory

### Use Case 2: Reasoning Ledger
**What**: Complete reasoning traces for transparency
**Examples**:
- Input data captured
- Step-by-step decision process
- Output signals generated
- Execution metadata

### Use Case 3: Reputation Scores
**What**: Calculated RAID scores and performance
**Examples**:
- Agent reputation score (0.0 - 1.0)
- Prediction accuracy metrics
- Historical performance data
- Validation results

---

## Solution Architecture Matrix

| Use Case | Best Solution | Why | Cost | Latency |
|----------|--------------|-----|------|---------|
| **1. Event Signals** | SUI Events + Objects | On-chain events, queryable | Low | <1s |
| **2. Reasoning Ledger** | Walrus DA | Large data, immutable | Very Low | ~5s |
| **3. Reputation Scores** | SUI Smart Contract | Queryable, programmable | Low | <1s |

---

## Detailed Architecture

### Use Case 1: Event Signals & Data Inventory

#### Solution: **SUI Events + Dynamic Fields**

**Why SUI Events?**
- ✅ Real-time event emission
- ✅ Queryable by event type
- ✅ Lightweight (only metadata)
- ✅ Can signal off-chain watchers
- ✅ Indexed automatically

**Architecture:**

```
┌─────────────────────────────────────────────────────┐
│              Data Source Events                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│  CoinGecko → Price Update Event → SUI Chain         │
│  CryptoPanic → News Event → SUI Chain               │
│  Timer → Scheduled Event → SUI Chain                │
│                                                      │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │  Event Watcher  │
         │  (Python Agent) │
         └────────┬────────┘
                  │
                  ▼
         Signal Agent Execution
```

**Implementation:**

```move
// Move Smart Contract: event_registry.move
module glass_box::event_registry {
    use sui::event;
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;

    /// Event: Price threshold crossed
    struct PriceThresholdEvent has copy, drop {
        asset: vector<u8>,        // "BTC"
        price: u64,               // 66036 (in cents)
        threshold: u64,           // 70000
        direction: vector<u8>,    // "above" or "below"
        timestamp: u64,
        data_source: vector<u8>,  // "coingecko"
    }

    /// Event: News article published
    struct NewsEvent has copy, drop {
        title: vector<u8>,
        source: vector<u8>,       // "cryptopanic"
        currencies: vector<vector<u8>>,
        sentiment: vector<u8>,    // "bullish", "bearish", "neutral"
        timestamp: u64,
    }

    /// Event: Data source inventory update
    struct DataInventoryEvent has copy, drop {
        source_name: vector<u8>,  // "coingecko"
        source_type: vector<u8>,  // "price" or "news"
        last_update: u64,
        status: vector<u8>,       // "active", "error", "rate_limited"
        request_count: u64,
    }

    /// Emit price threshold event
    public entry fun emit_price_event(
        asset: vector<u8>,
        price: u64,
        threshold: u64,
        direction: vector<u8>,
        timestamp: u64,
        data_source: vector<u8>,
        _ctx: &mut TxContext
    ) {
        event::emit(PriceThresholdEvent {
            asset,
            price,
            threshold,
            direction,
            timestamp,
            data_source,
        });
    }

    /// Emit news event
    public entry fun emit_news_event(
        title: vector<u8>,
        source: vector<u8>,
        currencies: vector<vector<u8>>,
        sentiment: vector<u8>,
        timestamp: u64,
        _ctx: &mut TxContext
    ) {
        event::emit(NewsEvent {
            title,
            source,
            currencies,
            sentiment,
            timestamp,
        });
    }

    /// Emit data inventory event
    public entry fun emit_inventory_event(
        source_name: vector<u8>,
        source_type: vector<u8>,
        last_update: u64,
        status: vector<u8>,
        request_count: u64,
        _ctx: &mut TxContext
    ) {
        event::emit(DataInventoryEvent {
            source_name,
            source_type,
            last_update,
            status,
            request_count,
        });
    }
}
```

**Python Integration:**

```python
# src/blockchain/sui_events.py
from pysui import SuiClient
from pysui.sui.sui_txn import SyncTransaction
import logging

logger = logging.getLogger(__name__)

class SuiEventEmitter:
    """Emit events to SUI blockchain."""

    def __init__(self, client: SuiClient, package_id: str):
        self.client = client
        self.package_id = package_id

    def emit_price_event(
        self,
        asset: str,
        price: float,
        threshold: float,
        direction: str,
        data_source: str
    ):
        """Emit price threshold event."""
        txn = SyncTransaction(client=self.client)

        txn.move_call(
            target=f"{self.package_id}::event_registry::emit_price_event",
            arguments=[
                asset.encode(),
                int(price * 100),  # Convert to cents
                int(threshold * 100),
                direction.encode(),
                int(time.time()),
                data_source.encode(),
            ]
        )

        result = txn.execute(gas_budget=10_000_000)
        logger.info(f"Emitted price event: {asset} @ {price}")

        return result.digest

    def emit_news_event(
        self,
        title: str,
        source: str,
        currencies: list[str],
        sentiment: str
    ):
        """Emit news article event."""
        txn = SyncTransaction(client=self.client)

        txn.move_call(
            target=f"{self.package_id}::event_registry::emit_news_event",
            arguments=[
                title.encode(),
                source.encode(),
                [c.encode() for c in currencies],
                sentiment.encode(),
                int(time.time()),
            ]
        )

        result = txn.execute(gas_budget=10_000_000)
        logger.info(f"Emitted news event: {title[:50]}...")

        return result.digest

    def emit_inventory_event(
        self,
        source_name: str,
        source_type: str,
        status: str,
        request_count: int
    ):
        """Emit data source inventory event."""
        txn = SyncTransaction(client=self.client)

        txn.move_call(
            target=f"{self.package_id}::event_registry::emit_inventory_event",
            arguments=[
                source_name.encode(),
                source_type.encode(),
                int(time.time()),
                status.encode(),
                request_count,
            ]
        )

        result = txn.execute(gas_budget=10_000_000)
        logger.info(f"Emitted inventory event: {source_name}")

        return result.digest
```

**Event Watcher:**

```python
# src/blockchain/event_watcher.py
from pysui import SuiClient
from pysui.sui.sui_types import EventFilter
import asyncio
import logging

logger = logging.getLogger(__name__)

class EventWatcher:
    """Watch SUI events and signal agent execution."""

    def __init__(self, client: SuiClient, package_id: str):
        self.client = client
        self.package_id = package_id

    async def watch_price_events(self, callback):
        """Watch for price threshold events."""
        event_type = f"{self.package_id}::event_registry::PriceThresholdEvent"

        # Subscribe to events
        async for event in self.client.subscribe_event(
            filter=EventFilter.from_event_type(event_type)
        ):
            logger.info(f"Price event detected: {event}")
            await callback(event)

    async def watch_news_events(self, callback):
        """Watch for news events."""
        event_type = f"{self.package_id}::event_registry::NewsEvent"

        async for event in self.client.subscribe_event(
            filter=EventFilter.from_event_type(event_type)
        ):
            logger.info(f"News event detected: {event}")
            await callback(event)
```

---

### Use Case 2: Reasoning Ledger

#### Solution: **Walrus + SUI Object Reference**

**Why Walrus?**
- ✅ Large data storage (reasoning traces can be 10KB+)
- ✅ Immutable by design
- ✅ Cost-effective for large blobs
- ✅ Decentralized data availability
- ❌ NOT good for queries (use SUI for metadata)

**Hybrid Approach: Walrus (data) + SUI (metadata)**

**Architecture:**

```
┌─────────────────────────────────────────────────────┐
│                Agent Execution                       │
└──────────────────┬──────────────────────────────────┘
                   │
                   ├─────────────────────────────────┐
                   │                                 │
                   ▼                                 ▼
         ┌──────────────────┐            ┌──────────────────┐
         │  Walrus Storage  │            │  SUI Blockchain  │
         │                  │            │                  │
         │ Full Trace Data  │◄───────────│  Metadata Object │
         │ (10KB JSON)      │  blob_id   │  (200 bytes)     │
         └──────────────────┘            └──────────────────┘
              Immutable                     Queryable
```

**Move Smart Contract:**

```move
// Move Smart Contract: reasoning_ledger.move
module glass_box::reasoning_ledger {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;

    /// Reasoning trace metadata (stored on-chain)
    struct TraceMetadata has key, store {
        id: UID,
        trace_id: vector<u8>,
        agent_id: vector<u8>,
        timestamp: u64,
        walrus_blob_id: vector<u8>,  // Pointer to Walrus
        input_hash: vector<u8>,      // SHA256 of input
        output_hash: vector<u8>,     // SHA256 of output
        execution_time_ms: u64,
        success: bool,
    }

    /// Create new trace metadata
    public entry fun create_trace_metadata(
        trace_id: vector<u8>,
        agent_id: vector<u8>,
        timestamp: u64,
        walrus_blob_id: vector<u8>,
        input_hash: vector<u8>,
        output_hash: vector<u8>,
        execution_time_ms: u64,
        success: bool,
        ctx: &mut TxContext
    ) {
        let metadata = TraceMetadata {
            id: object::new(ctx),
            trace_id,
            agent_id,
            timestamp,
            walrus_blob_id,
            input_hash,
            output_hash,
            execution_time_ms,
            success,
        };

        transfer::public_share_object(metadata);
    }

    /// Get trace metadata (for queries)
    public fun get_walrus_blob_id(metadata: &TraceMetadata): vector<u8> {
        metadata.walrus_blob_id
    }
}
```

**Python Integration:**

```python
# src/core/reasoning_ledger.py
from ..data_clients.walrus_client import WalrusDAClient
from ..blockchain.sui_client import SuiTestnetClient
import hashlib
import json
import time

class ReasoningLedger:
    """
    Hybrid reasoning ledger using Walrus + SUI.

    - Full trace data → Walrus (cheap, immutable)
    - Metadata → SUI (queryable, verifiable)
    """

    def __init__(self, walrus: WalrusDAClient, sui: SuiTestnetClient, package_id: str):
        self.walrus = walrus
        self.sui = sui
        self.package_id = package_id

    def store_reasoning_trace(
        self,
        trace_id: str,
        agent_id: str,
        input_data: dict,
        reasoning_process: dict,
        output_signal: dict,
        execution_time_ms: int,
        success: bool
    ) -> tuple[str, str]:
        """
        Store reasoning trace.

        Returns:
            (walrus_blob_id, sui_object_id)
        """
        # 1. Create full trace data
        trace_data = {
            "trace_id": trace_id,
            "agent_id": agent_id,
            "timestamp": int(time.time()),
            "input_data": input_data,
            "reasoning_process": reasoning_process,
            "output_signal": output_signal,
            "execution_time_ms": execution_time_ms,
            "success": success,
        }

        # 2. Store full data on Walrus
        walrus_blob_id = self.walrus.store_trace(trace_data)

        # 3. Calculate hashes for verification
        input_hash = hashlib.sha256(
            json.dumps(input_data, sort_keys=True).encode()
        ).hexdigest()

        output_hash = hashlib.sha256(
            json.dumps(output_signal, sort_keys=True).encode()
        ).hexdigest()

        # 4. Store metadata on SUI
        txn = SyncTransaction(client=self.sui.client)

        txn.move_call(
            target=f"{self.package_id}::reasoning_ledger::create_trace_metadata",
            arguments=[
                trace_id.encode(),
                agent_id.encode(),
                int(time.time()),
                walrus_blob_id.encode(),
                input_hash.encode(),
                output_hash.encode(),
                execution_time_ms,
                success,
            ]
        )

        result = txn.execute(gas_budget=10_000_000)

        logger.info(f"Stored reasoning trace: Walrus={walrus_blob_id}, SUI={result.digest}")

        return walrus_blob_id, result.digest

    def retrieve_trace(self, walrus_blob_id: str) -> dict:
        """Retrieve full trace from Walrus."""
        return self.walrus.retrieve_trace(walrus_blob_id)

    def verify_trace(self, walrus_blob_id: str, sui_object_id: str) -> bool:
        """
        Verify trace integrity by comparing hashes.

        Returns:
            True if trace is authentic
        """
        # Get full trace from Walrus
        trace = self.retrieve_trace(walrus_blob_id)

        # Get metadata from SUI
        metadata = self.sui.get_object(sui_object_id)

        # Recalculate hashes
        input_hash = hashlib.sha256(
            json.dumps(trace["input_data"], sort_keys=True).encode()
        ).hexdigest()

        output_hash = hashlib.sha256(
            json.dumps(trace["output_signal"], sort_keys=True).encode()
        ).hexdigest()

        # Compare
        return (
            input_hash == metadata["input_hash"] and
            output_hash == metadata["output_hash"]
        )
```

---

### Use Case 3: Reputation Scores

#### Solution: **SUI Smart Contract with Dynamic Fields**

**Why SUI Smart Contract?**
- ✅ Queryable on-chain
- ✅ Programmable validation logic
- ✅ Can aggregate scores
- ✅ Access control (who can update)
- ✅ Historical tracking

**Move Smart Contract:**

```move
// Move Smart Contract: raid_scores.move
module glass_box::raid_scores {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;
    use sui::vec_map::{Self, VecMap};
    use sui::event;

    /// Agent reputation object
    struct AgentReputation has key, store {
        id: UID,
        agent_id: vector<u8>,
        raid_score: u64,           // Score * 1000 (e.g., 750 = 0.75)
        total_predictions: u64,
        successful_predictions: u64,
        total_impact: u64,
        last_updated: u64,
        history: VecMap<u64, u64>, // timestamp → score
    }

    /// Event: RAID score updated
    struct RAIDScoreUpdated has copy, drop {
        agent_id: vector<u8>,
        old_score: u64,
        new_score: u64,
        timestamp: u64,
    }

    /// Create new agent reputation
    public entry fun create_agent_reputation(
        agent_id: vector<u8>,
        initial_score: u64,
        ctx: &mut TxContext
    ) {
        let reputation = AgentReputation {
            id: object::new(ctx),
            agent_id,
            raid_score: initial_score,
            total_predictions: 0,
            successful_predictions: 0,
            total_impact: 0,
            last_updated: tx_context::epoch(ctx),
            history: vec_map::empty(),
        };

        transfer::public_share_object(reputation);
    }

    /// Update RAID score
    public entry fun update_raid_score(
        reputation: &mut AgentReputation,
        new_score: u64,
        prediction_success: bool,
        impact: u64,
        ctx: &mut TxContext
    ) {
        let old_score = reputation.raid_score;
        let timestamp = tx_context::epoch(ctx);

        // Update score
        reputation.raid_score = new_score;
        reputation.total_predictions = reputation.total_predictions + 1;

        if (prediction_success) {
            reputation.successful_predictions = reputation.successful_predictions + 1;
        };

        reputation.total_impact = reputation.total_impact + impact;
        reputation.last_updated = timestamp;

        // Add to history
        vec_map::insert(&mut reputation.history, timestamp, new_score);

        // Emit event
        event::emit(RAIDScoreUpdated {
            agent_id: reputation.agent_id,
            old_score,
            new_score,
            timestamp,
        });
    }

    /// Get current RAID score
    public fun get_raid_score(reputation: &AgentReputation): u64 {
        reputation.raid_score
    }

    /// Get success rate
    public fun get_success_rate(reputation: &AgentReputation): u64 {
        if (reputation.total_predictions == 0) {
            return 0
        };

        (reputation.successful_predictions * 1000) / reputation.total_predictions
    }

    /// Get historical scores
    public fun get_score_at_time(reputation: &AgentReputation, timestamp: u64): u64 {
        if (vec_map::contains(&reputation.history, &timestamp)) {
            *vec_map::get(&reputation.history, &timestamp)
        } else {
            0
        }
    }
}
```

**Python Integration:**

```python
# src/blockchain/raid_contract.py
from pysui import SuiClient
from pysui.sui.sui_txn import SyncTransaction

class RAIDScoreContract:
    """Interface to RAID score smart contract."""

    def __init__(self, client: SuiClient, package_id: str):
        self.client = client
        self.package_id = package_id

    def create_agent_reputation(self, agent_id: str, initial_score: float):
        """Create new agent reputation object."""
        txn = SyncTransaction(client=self.client)

        txn.move_call(
            target=f"{self.package_id}::raid_scores::create_agent_reputation",
            arguments=[
                agent_id.encode(),
                int(initial_score * 1000),  # Convert to integer
            ]
        )

        result = txn.execute(gas_budget=10_000_000)
        return result.digest

    def update_raid_score(
        self,
        reputation_object_id: str,
        new_score: float,
        prediction_success: bool,
        impact: int
    ):
        """Update RAID score."""
        txn = SyncTransaction(client=self.client)

        txn.move_call(
            target=f"{self.package_id}::raid_scores::update_raid_score",
            arguments=[
                reputation_object_id,
                int(new_score * 1000),
                prediction_success,
                impact,
            ]
        )

        result = txn.execute(gas_budget=10_000_000)
        return result.digest

    def get_raid_score(self, reputation_object_id: str) -> float:
        """Get current RAID score."""
        result = self.client.get_object(reputation_object_id)
        score = result.content.fields["raid_score"]
        return score / 1000.0  # Convert back to float

    def get_success_rate(self, reputation_object_id: str) -> float:
        """Get prediction success rate."""
        result = self.client.get_object(reputation_object_id)
        total = result.content.fields["total_predictions"]
        successful = result.content.fields["successful_predictions"]

        if total == 0:
            return 0.0

        return successful / total
```

---

## Comparison Table

| Feature | SUI Events | Walrus | SUI Smart Contract |
|---------|-----------|--------|-------------------|
| **Cost** | ~0.001 SUI | ~0.001 SUI/KB | ~0.01 SUI |
| **Latency** | <1s | ~5s | <1s |
| **Queryable** | ✅ Yes | ❌ No | ✅ Yes |
| **Programmable** | ❌ No | ❌ No | ✅ Yes |
| **Immutable** | ✅ Yes | ✅ Yes | ⚠️ Mutable |
| **Data Size** | Small (<1KB) | Large (10KB+) | Small (<10KB) |
| **Best For** | Signals | Archives | State |

---

## Recommended Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Glass Box Protocol                     │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Data Sources → Agents → Blockchain Integration          │
│                                                           │
└───┬─────────────────┬──────────────────┬────────────────┘
    │                 │                  │
    │                 │                  │
    ▼                 ▼                  ▼
┌─────────┐    ┌──────────┐      ┌─────────────┐
│   SUI   │    │  Walrus  │      │     SUI     │
│ Events  │    │    DA    │      │   Smart     │
│         │    │          │      │  Contract   │
├─────────┤    ├──────────┤      ├─────────────┤
│• Price  │    │• Full    │      │• RAID       │
│  alerts │    │  traces  │      │  scores     │
│• News   │    │• Input   │      │• Reputation │
│  events │    │  data    │      │• History    │
│• Timers │    │• Reason  │      │• Queries    │
│         │    │  steps   │      │             │
└─────────┘    └──────────┘      └─────────────┘
  Signals       Archives            State
```

---

## Implementation Priority

### Phase 1: Core Functionality (Week 1)
1. ✅ SUI Smart Contract for RAID scores
2. ✅ Walrus client for reasoning traces
3. ✅ Basic integration with Agent A

### Phase 2: Events (Week 2)
4. ⏭️ SUI Events for price/news signals
5. ⏭️ Event watcher for automated execution
6. ⏭️ Data inventory tracking

### Phase 3: Production Ready (Week 3)
7. ⏭️ Deploy all contracts to testnet
8. ⏭️ Full integration testing
9. ⏭️ Documentation and demos

---

## Next Steps

Would you like me to:
1. **Implement SUI Smart Contracts** (Move code for events, ledger, RAID)?
2. **Create Python integration layer** (clients for all three use cases)?
3. **Build event watcher system** (automated agent signaling)?
4. **All of the above** (full implementation)?

Let me know which direction you'd like to go! 🚀
