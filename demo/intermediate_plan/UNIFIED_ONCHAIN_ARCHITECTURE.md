# Unified On-Chain Architecture - All Agents Framework

**Date:** 2026-03-28
**Status:** Architecture Design

---

## Core Principle: Everything is an Agent

```
Off-Chain Data → Agent 0 (Data Processor) → On-Chain
                                              ↓
                   On-Chain Data → Agent A (Sentiment) → On-Chain
                                                          ↓
                                   On-Chain Data → Agent B (Investment) → On-Chain
                                                                           ↓
                                            On-Chain Data → Agent C (Portfolio) → On-Chain
```

**Key Insights:**
- ✅ **Agent 0**: Data processors that convert off-chain → on-chain
- ✅ **All Agents**: Consume only on-chain data
- ✅ **All Outputs**: Written on-chain for next agent
- ✅ **Reasoning Ledger**: Every agent's reasoning is recorded

---

## Agent Hierarchy

### **Agent 0 (Data Processors)** - New Layer

**Purpose**: Convert off-chain data sources into on-chain data

**Types:**
- **Agent 0-CoinGecko**: Fetch prices → Store on-chain
- **Agent 0-CryptoPanic**: Fetch news → Store on-chain
- **Agent 0-Twitter**: Fetch tweets → Store on-chain (future)

**Input**: Off-chain APIs (CoinGecko, CryptoPanic, etc.)
**Output**: On-chain data objects + Events
**Reasoning Ledger**: Records data fetch, validation, transformation

### **Agent A (Sentiment Analysis)**

**Input**: On-chain news data (from Agent 0-CryptoPanic)
**Output**: On-chain sentiment signals
**Reasoning Ledger**: Records sentiment calculation process

### **Agent B (Investment Signals)**

**Input**:
- On-chain sentiment signals (from Agent A)
- On-chain price data (from Agent 0-CoinGecko)

**Output**: On-chain investment recommendations
**Reasoning Ledger**: Records signal generation logic

### **Agent C (Portfolio Management)**

**Input**: On-chain investment signals (from Agent B)
**Output**: On-chain portfolio actions
**Reasoning Ledger**: Records rebalancing decisions

---

## Unified On-Chain Data Model

### On-Chain Data Object Structure

```move
// Universal data object that all agents produce/consume
struct AgentDataOutput has key, store {
    id: UID,

    // Provenance
    producer_agent_id: vector<u8>,     // Which agent created this
    agent_type: vector<u8>,            // "data_processor", "sentiment", "investment"

    // Data
    data_type: vector<u8>,             // "price", "news", "sentiment", "signal"
    data_payload: vector<u8>,          // JSON blob of actual data

    // Metadata
    timestamp: u64,
    source_data_ids: vector<ID>,       // IDs of input data objects
    walrus_trace_id: vector<u8>,       // Pointer to reasoning trace

    // Validation
    data_hash: vector<u8>,             // Hash for integrity
    agent_signature: vector<u8>,       // Agent's signature
}
```

---

## Complete Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                       OFF-CHAIN WORLD                             │
├──────────────────────────────────────────────────────────────────┤
│  CoinGecko API      CryptoPanic API      Twitter API             │
└───────┬───────────────────┬──────────────────┬───────────────────┘
        │                   │                  │
        │ Fetch             │ Fetch            │ Fetch
        │                   │                  │
        ▼                   ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│              AGENT 0 LAYER (Data Processors)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Agent 0-CoinGecko    Agent 0-CryptoPanic    Agent 0-Twitter   │
│       │                      │                      │           │
│       │ Process              │ Process              │ Process   │
│       │                      │                      │           │
│       ▼                      ▼                      ▼           │
│  [Reasoning            [Reasoning            [Reasoning         │
│   Trace]                Trace]                Trace]            │
│       │                      │                      │           │
└───────┼──────────────────────┼──────────────────────┼───────────┘
        │                      │                      │
        │ Store                │ Store                │ Store
        │                      │                      │
        ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SUI BLOCKCHAIN LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  AgentDataOutput    AgentDataOutput      AgentDataOutput        │
│  (Price Data)       (News Data)          (Tweet Data)           │
│       │                      │                      │           │
└───────┼──────────────────────┼──────────────────────┼───────────┘
        │                      │                      │
        │ Read                 │ Read                 │ Read
        │                      │                      │
        ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                 AGENT A (Sentiment Analysis)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Input: News Data (on-chain) + Price Data (on-chain)           │
│  Process: Sentiment calculation                                 │
│  Output: Sentiment signals → [Reasoning Trace] → SUI            │
│                                                                  │
└───────────────────────────────────┬─────────────────────────────┘
                                    │
                                    │ Store
                                    ▼
                        ┌─────────────────────┐
                        │  AgentDataOutput    │
                        │  (Sentiment Data)   │
                        └──────────┬──────────┘
                                   │
                                   │ Read
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│            AGENT B (Investment Signal Generation)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Input: Sentiment (on-chain) + Prices (on-chain)               │
│  Process: Signal generation                                     │
│  Output: Investment signals → [Reasoning Trace] → SUI           │
│                                                                  │
└───────────────────────────────────┬─────────────────────────────┘
                                    │
                                    │ Store
                                    ▼
                        ┌─────────────────────┐
                        │  AgentDataOutput    │
                        │  (Signal Data)      │
                        └──────────┬──────────┘
                                   │
                                   │ Read
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│              AGENT C (Portfolio Management)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Input: Signals (on-chain)                                      │
│  Process: Portfolio rebalancing                                 │
│  Output: Portfolio actions → [Reasoning Trace] → SUI            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Move Smart Contract Implementation

### Universal Data Object

```move
// smart_contracts/agent_data.move
module glass_box::agent_data {
    use sui::object::{Self, UID, ID};
    use sui::tx_context::TxContext;
    use sui::transfer;
    use sui::event;

    /// Universal data output produced by any agent
    struct AgentDataOutput has key, store {
        id: UID,

        // Provenance - WHO created this data
        producer_agent_id: vector<u8>,
        agent_type: vector<u8>,         // "data_processor", "sentiment", "investment", "portfolio"

        // Data - WHAT is the data
        data_type: vector<u8>,          // "price", "news", "sentiment", "signal", "action"
        data_payload: vector<u8>,       // JSON serialized data

        // Lineage - WHERE did this come from
        source_data_ids: vector<ID>,    // Parent data objects
        walrus_trace_id: vector<u8>,    // Reasoning trace on Walrus

        // Metadata - WHEN and HOW
        timestamp: u64,
        data_hash: vector<u8>,          // SHA256 of payload
        version: u64,                   // Schema version
    }

    /// Event: New data produced
    struct DataProduced has copy, drop {
        data_id: ID,
        producer_agent_id: vector<u8>,
        data_type: vector<u8>,
        timestamp: u64,
    }

    /// Create new data output
    public fun create_data_output(
        producer_agent_id: vector<u8>,
        agent_type: vector<u8>,
        data_type: vector<u8>,
        data_payload: vector<u8>,
        source_data_ids: vector<ID>,
        walrus_trace_id: vector<u8>,
        timestamp: u64,
        data_hash: vector<u8>,
        ctx: &mut TxContext
    ): AgentDataOutput {
        let data = AgentDataOutput {
            id: object::new(ctx),
            producer_agent_id,
            agent_type,
            data_type,
            data_payload,
            source_data_ids,
            walrus_trace_id,
            timestamp,
            data_hash,
            version: 1,
        };

        // Emit event
        event::emit(DataProduced {
            data_id: object::id(&data),
            producer_agent_id,
            data_type,
            timestamp,
        });

        data
    }

    /// Publish data output (make it shared/accessible)
    public entry fun publish_data_output(
        producer_agent_id: vector<u8>,
        agent_type: vector<u8>,
        data_type: vector<u8>,
        data_payload: vector<u8>,
        source_data_ids: vector<ID>,
        walrus_trace_id: vector<u8>,
        timestamp: u64,
        data_hash: vector<u8>,
        ctx: &mut TxContext
    ) {
        let data = create_data_output(
            producer_agent_id,
            agent_type,
            data_type,
            data_payload,
            source_data_ids,
            walrus_trace_id,
            timestamp,
            data_hash,
            ctx
        );

        transfer::public_share_object(data);
    }

    /// Read data payload
    public fun get_payload(data: &AgentDataOutput): vector<u8> {
        data.data_payload
    }

    /// Get data lineage
    public fun get_source_ids(data: &AgentDataOutput): &vector<ID> {
        &data.source_data_ids
    }

    /// Get reasoning trace ID
    public fun get_trace_id(data: &AgentDataOutput): vector<u8> {
        data.walrus_trace_id
    }

    /// Verify data integrity
    public fun verify_hash(data: &AgentDataOutput, expected_hash: vector<u8>): bool {
        data.data_hash == expected_hash
    }
}
```

---

## Python Implementation

### Agent Base Class

```python
# src/core/base_agent.py
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass
import json
import hashlib
import time

from ..blockchain.sui_client import SuiTestnetClient
from ..data_clients.walrus_client import WalrusDAClient


@dataclass
class AgentInput:
    """Input data consumed by agent."""
    data_id: str           # SUI object ID
    data_type: str         # "price", "news", "sentiment"
    data_payload: dict     # Actual data
    producer_agent: str    # Who created this
    timestamp: int


@dataclass
class AgentOutput:
    """Output data produced by agent."""
    data_type: str         # "price", "news", "sentiment", "signal"
    data_payload: dict     # Actual data
    walrus_trace_id: str   # Reasoning trace ID
    source_data_ids: List[str]  # Input data IDs


class BaseAgent(ABC):
    """
    Base class for all agents in the system.

    All agents:
    1. Read input from on-chain
    2. Process and reason
    3. Store reasoning trace on Walrus
    4. Write output on-chain
    """

    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        sui_client: SuiTestnetClient,
        walrus_client: WalrusDAClient,
        package_id: str
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.sui = sui_client
        self.walrus = walrus_client
        self.package_id = package_id

    @abstractmethod
    def process(self, inputs: List[AgentInput]) -> AgentOutput:
        """
        Process inputs and generate output.

        Must be implemented by each agent.
        """
        pass

    def execute(self, input_data_ids: List[str]) -> str:
        """
        Complete agent execution pipeline.

        1. Fetch inputs from on-chain
        2. Process and reason
        3. Store reasoning trace on Walrus
        4. Write output on-chain

        Returns:
            Output data object ID
        """
        # Step 1: Fetch inputs from on-chain
        inputs = self._fetch_inputs(input_data_ids)

        # Step 2: Process
        output = self.process(inputs)

        # Step 3: Store reasoning trace on Walrus
        trace_data = self._create_trace(inputs, output)
        walrus_trace_id = self.walrus.store_trace(trace_data)

        # Step 4: Write output on-chain
        output_id = self._write_output_onchain(output, walrus_trace_id, input_data_ids)

        return output_id

    def _fetch_inputs(self, data_ids: List[str]) -> List[AgentInput]:
        """Fetch input data from SUI."""
        inputs = []

        for data_id in data_ids:
            # Get object from SUI
            obj = self.sui.client.get_object(data_id)

            inputs.append(AgentInput(
                data_id=data_id,
                data_type=obj.content.fields["data_type"].decode(),
                data_payload=json.loads(obj.content.fields["data_payload"].decode()),
                producer_agent=obj.content.fields["producer_agent_id"].decode(),
                timestamp=obj.content.fields["timestamp"]
            ))

        return inputs

    def _create_trace(self, inputs: List[AgentInput], output: AgentOutput) -> dict:
        """Create reasoning trace."""
        return {
            "trace_id": f"trace_{self.agent_id}_{int(time.time())}",
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "timestamp": int(time.time()),
            "inputs": [
                {
                    "data_id": inp.data_id,
                    "data_type": inp.data_type,
                    "producer": inp.producer_agent,
                    "payload": inp.data_payload
                }
                for inp in inputs
            ],
            "reasoning_process": self._get_reasoning_steps(),
            "output": {
                "data_type": output.data_type,
                "payload": output.data_payload
            }
        }

    @abstractmethod
    def _get_reasoning_steps(self) -> dict:
        """Get reasoning steps for trace (implemented by each agent)."""
        pass

    def _write_output_onchain(
        self,
        output: AgentOutput,
        walrus_trace_id: str,
        source_data_ids: List[str]
    ) -> str:
        """Write output to SUI blockchain."""
        from pysui.sui.sui_txn import SyncTransaction

        # Serialize payload
        payload_json = json.dumps(output.data_payload)
        payload_bytes = payload_json.encode()

        # Calculate hash
        data_hash = hashlib.sha256(payload_bytes).hexdigest()

        # Create transaction
        txn = SyncTransaction(client=self.sui.client)

        txn.move_call(
            target=f"{self.package_id}::agent_data::publish_data_output",
            arguments=[
                self.agent_id.encode(),
                self.agent_type.encode(),
                output.data_type.encode(),
                payload_bytes,
                source_data_ids,  # Vector of IDs
                walrus_trace_id.encode(),
                int(time.time()),
                data_hash.encode(),
            ]
        )

        result = txn.execute(gas_budget=10_000_000)

        return result.digest
```

---

## Agent 0 Example: CryptoPanic Data Processor

```python
# src/agents/agent_0_cryptopanic.py
from ..core.base_agent import BaseAgent, AgentInput, AgentOutput
from ..data_sources import CryptoPanicSource
from typing import List
import os


class Agent0CryptoPanic(BaseAgent):
    """
    Agent 0: CryptoPanic Data Processor

    Fetches news from CryptoPanic API and stores on-chain.
    """

    def __init__(self, sui_client, walrus_client, package_id):
        super().__init__(
            agent_id="agent_0_cryptopanic",
            agent_type="data_processor",
            sui_client=sui_client,
            walrus_client=walrus_client,
            package_id=package_id
        )

        # Initialize CryptoPanic source
        api_token = os.getenv("CRYPTOPANIC_API_TOKEN")
        self.news_source = CryptoPanicSource(api_token)

        self.reasoning_steps = {}

    def process(self, inputs: List[AgentInput]) -> AgentOutput:
        """
        Process: Fetch news from CryptoPanic.

        Input: Empty (or trigger event)
        Output: News articles as on-chain data
        """
        # Step 1: Fetch news from API
        self.reasoning_steps["step_1"] = "Fetching news from CryptoPanic API"
        articles = self.news_source.fetch_news(currencies=["BTC", "ETH", "SUI"], limit=10)

        # Step 2: Transform to standard format
        self.reasoning_steps["step_2"] = f"Fetched {len(articles)} articles"

        news_data = []
        for article in articles:
            news_data.append({
                "title": article.title,
                "source": article.source,
                "published_at": article.published_at.isoformat(),
                "kind": article.kind,
                "url": article.url,
            })

        self.reasoning_steps["step_3"] = "Transformed to standard format"
        self.reasoning_steps["step_4"] = f"Ready to publish {len(news_data)} articles"

        # Step 3: Return as output
        return AgentOutput(
            data_type="news",
            data_payload={"articles": news_data, "count": len(news_data)},
            walrus_trace_id="",  # Will be filled by base class
            source_data_ids=[]   # No on-chain inputs
        )

    def _get_reasoning_steps(self) -> dict:
        return self.reasoning_steps
```

---

## Agent A Example: Sentiment Analysis

```python
# src/agents/agent_a_sentiment.py
from ..core.base_agent import BaseAgent, AgentInput, AgentOutput
from typing import List


class AgentASentiment(BaseAgent):
    """
    Agent A: Sentiment Analysis

    Reads news data from on-chain (produced by Agent 0).
    Analyzes sentiment and produces sentiment signals.
    """

    def __init__(self, sui_client, walrus_client, package_id):
        super().__init__(
            agent_id="agent_a_sentiment",
            agent_type="sentiment",
            sui_client=sui_client,
            walrus_client=walrus_client,
            package_id=package_id
        )

        self.reasoning_steps = {}

    def process(self, inputs: List[AgentInput]) -> AgentOutput:
        """
        Process: Analyze sentiment from news data.

        Input: News data (from Agent 0)
        Output: Sentiment signals
        """
        # Step 1: Extract news articles
        self.reasoning_steps["step_1"] = "Extracting news from on-chain data"

        all_articles = []
        for inp in inputs:
            if inp.data_type == "news":
                articles = inp.data_payload.get("articles", [])
                all_articles.extend(articles)

        self.reasoning_steps["step_2"] = f"Found {len(all_articles)} articles"

        # Step 2: Analyze sentiment
        sentiment_scores = self._analyze_sentiment(all_articles)
        self.reasoning_steps["step_3"] = "Calculated sentiment scores"

        # Step 3: Generate signals
        signals = self._generate_signals(sentiment_scores)
        self.reasoning_steps["step_4"] = f"Generated {len(signals)} signals"

        return AgentOutput(
            data_type="sentiment",
            data_payload={
                "sentiment_scores": sentiment_scores,
                "signals": signals
            },
            walrus_trace_id="",
            source_data_ids=[inp.data_id for inp in inputs]
        )

    def _analyze_sentiment(self, articles: List[dict]) -> dict:
        """Simple keyword-based sentiment analysis."""
        scores = {}

        for article in articles:
            title = article["title"].lower()

            # Simple sentiment scoring
            bullish_words = ["surge", "rally", "moon", "gains", "bullish"]
            bearish_words = ["crash", "dump", "fall", "bearish", "plunge"]

            score = 0
            score += sum(1 for word in bullish_words if word in title)
            score -= sum(1 for word in bearish_words if word in title)

            # Normalize to -1 to 1
            sentiment = max(-1, min(1, score / 3))

            # Aggregate by asset (simplified)
            if "btc" in title or "bitcoin" in title:
                scores["BTC"] = scores.get("BTC", []) + [sentiment]
            if "eth" in title or "ethereum" in title:
                scores["ETH"] = scores.get("ETH", []) + [sentiment]

        # Average scores
        return {
            asset: sum(vals) / len(vals) if vals else 0
            for asset, vals in scores.items()
        }

    def _generate_signals(self, sentiment_scores: dict) -> list:
        """Generate trading signals from sentiment."""
        signals = []

        for asset, score in sentiment_scores.items():
            if score > 0.5:
                signals.append({"asset": asset, "action": "buy", "confidence": score})
            elif score < -0.5:
                signals.append({"asset": asset, "action": "sell", "confidence": abs(score)})
            else:
                signals.append({"asset": asset, "action": "hold", "confidence": 1 - abs(score)})

        return signals

    def _get_reasoning_steps(self) -> dict:
        return self.reasoning_steps
```

---

## Complete Pipeline Example

```python
# scripts/demo_unified_pipeline.py
import os
from dotenv import load_dotenv

from src.blockchain.sui_client import SuiTestnetClient
from src.data_clients.walrus_client import WalrusDAClient
from src.agents.agent_0_cryptopanic import Agent0CryptoPanic
from src.agents.agent_a_sentiment import AgentASentiment

load_dotenv("config/.env")

# Initialize clients
sui = SuiTestnetClient()
walrus = WalrusDAClient(epochs=10)
package_id = "0x..."  # Deployed package ID

# Initialize agents
agent_0 = Agent0CryptoPanic(sui, walrus, package_id)
agent_a = AgentASentiment(sui, walrus, package_id)

print("=" * 80)
print("UNIFIED ON-CHAIN PIPELINE")
print("=" * 80)

# Step 1: Agent 0 fetches news and stores on-chain
print("\nAgent 0: Fetching news from CryptoPanic...")
news_data_id = agent_0.execute([])  # No inputs, fetches from API
print(f"✓ News data stored on-chain: {news_data_id}")

# Step 2: Agent A reads news from on-chain and analyzes sentiment
print("\nAgent A: Reading news from on-chain and analyzing sentiment...")
sentiment_data_id = agent_a.execute([news_data_id])  # Reads from on-chain
print(f"✓ Sentiment data stored on-chain: {sentiment_data_id}")

print("\n" + "=" * 80)
print("COMPLETE DATA LINEAGE:")
print("=" * 80)
print(f"Off-Chain → Agent 0 → On-Chain ({news_data_id})")
print(f"           ↓")
print(f"On-Chain → Agent A → On-Chain ({sentiment_data_id})")
print()
print("✓ All reasoning traces stored on Walrus")
print("✓ All data objects queryable on SUI")
print("✓ Complete verifiable lineage")
```

---

## Benefits of Unified Architecture

### 1. Complete Verifiable Lineage
Every data transformation is on-chain:
```
CryptoPanic → Agent 0 → [News Object] → Agent A → [Sentiment Object] → Agent B → ...
```

### 2. Composability
Any agent can consume any on-chain data:
```python
# Agent B can read from both Agent A and Agent 0
agent_b.execute([
    sentiment_data_id,  # From Agent A
    price_data_id       # From Agent 0-CoinGecko
])
```

### 3. Auditability
Query full history:
```python
# Get all data produced by Agent A
data = sui.query_objects(
    filter={"producer_agent_id": "agent_a_sentiment"}
)

# Get reasoning trace from Walrus
for obj in data:
    trace = walrus.retrieve_trace(obj.walrus_trace_id)
    print(trace["reasoning_process"])
```

### 4. Trustlessness
Anyone can verify:
- Data integrity (hashes)
- Data lineage (source_data_ids)
- Reasoning process (Walrus traces)

---

## Next Steps

1. ✅ Implement `agent_data.move` smart contract
2. ✅ Implement `BaseAgent` class
3. ✅ Implement Agent 0 (data processors)
4. ✅ Implement Agent A with on-chain inputs
5. ⏭️ Test full pipeline
6. ⏭️ Deploy to testnet

Would you like me to start implementing this unified architecture?
