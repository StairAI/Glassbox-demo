# Corrected Architecture: Data Pipeline vs Agents

**Date:** 2026-03-28
**Status:** Final Architecture

---

## Key Principle

**Data Pipeline Processors ≠ Agents**

- **Data Processors**: ETL only (Extract, Transform, Load) - No reasoning
- **Agents**: LLM-powered reasoning and decision making

---

## Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    LAYER 1: DATA PIPELINE                    │
│                  (Processors - NOT Agents)                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Off-Chain APIs → Clients → Sources → On-Chain Publisher    │
│                                                              │
│  Role: Fetch, normalize, publish raw data                   │
│  No LLM, No reasoning, No decision making                   │
│                                                              │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                   LAYER 2: ON-CHAIN DATA                     │
│                   (SUI Blockchain Storage)                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Raw Data Objects:                                           │
│  - News articles (title, content, source, timestamp)        │
│  - Price data (OHLCV, exchange, timestamp)                  │
│  - Social posts (tweet, sentiment_raw, timestamp)           │
│                                                              │
│  No processing, just storage                                │
│                                                              │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                   LAYER 3: AGENTS                            │
│              (LLM-Powered Reasoning & Decisions)             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Agent A: Read raw news → Analyze sentiment → Output signal │
│  Agent B: Read signals + prices → Generate trades           │
│  Agent C: Read trades → Manage portfolio                    │
│                                                              │
│  All reasoning traces stored on Walrus                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Data Pipeline (NOT Agents)

### Architecture

```python
# Pipeline: Off-Chain → On-Chain
# No LLM, No reasoning, Pure ETL

┌──────────────┐
│  Off-Chain   │ (CryptoPanic API, CoinGecko API)
│  Data Source │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Data Client │ (HTTP requests, rate limiting)
│  Layer       │ Returns: Raw JSON
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Data Source │ (Transform to unified format)
│  Layer       │ Returns: NewsArticle dataclass
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  On-Chain    │ (Publish to SUI)
│  Publisher   │ Returns: Object ID
└──────────────┘
```

### Implementation

```python
# src/pipeline/news_pipeline.py
from typing import List
from ..data_clients import CryptoPanicClient
from ..data_sources import CryptoPanicSource
from ..blockchain.sui_publisher import OnChainPublisher

class NewsPipeline:
    """
    Data pipeline for news articles.

    NOT an agent - no reasoning, just ETL.
    """

    def __init__(self, api_token: str, sui_publisher: OnChainPublisher):
        # Client: HTTP layer
        self.client = CryptoPanicClient(api_token)

        # Source: Transform layer
        self.source = CryptoPanicSource(api_token)

        # Publisher: On-chain writer
        self.publisher = sui_publisher

    def fetch_and_publish(
        self,
        currencies: List[str],
        limit: int = 10
    ) -> str:
        """
        Fetch news from API and publish to blockchain.

        No reasoning, just:
        1. Fetch raw JSON
        2. Transform to NewsArticle
        3. Publish to SUI

        Returns:
            On-chain object ID
        """
        # Step 1: Fetch from API (via source layer)
        articles = self.source.fetch_news(
            currencies=currencies,
            limit=limit
        )

        # Step 2: Prepare for on-chain
        news_data = {
            "data_type": "news_raw",  # Mark as raw, unprocessed
            "producer": "news_pipeline",  # Not an agent
            "articles": [
                {
                    "title": article.title,
                    "source": article.source,
                    "published_at": article.published_at.isoformat(),
                    "kind": article.kind,
                    "url": article.url,
                }
                for article in articles
            ],
            "count": len(articles),
            "timestamp": datetime.now().isoformat(),
        }

        # Step 3: Publish to SUI
        object_id = self.publisher.publish_raw_data(news_data)

        logger.info(f"Published {len(articles)} news articles to SUI: {object_id}")

        return object_id
```

```python
# src/pipeline/price_pipeline.py
from ..data_clients import CoinGeckoClient
from ..data_sources import CoinGeckoSource
from ..blockchain.sui_publisher import OnChainPublisher

class PricePipeline:
    """
    Data pipeline for price data.

    NOT an agent - no reasoning, just ETL.
    """

    def __init__(self, sui_publisher: OnChainPublisher):
        self.client = CoinGeckoClient()
        self.source = CoinGeckoSource()
        self.publisher = sui_publisher

    def fetch_and_publish(
        self,
        symbols: List[str]
    ) -> str:
        """
        Fetch prices from API and publish to blockchain.

        Returns:
            On-chain object ID
        """
        # Fetch from API
        prices = self.source.get_prices(symbols)

        # Prepare for on-chain
        price_data = {
            "data_type": "price_raw",
            "producer": "price_pipeline",
            "prices": {
                symbol: {
                    "price_usd": float(data.price_usd),
                    "market_cap": float(data.market_cap) if data.market_cap else None,
                    "volume_24h": float(data.volume_24h) if data.volume_24h else None,
                    "change_24h": float(data.price_change_24h) if data.price_change_24h else None,
                }
                for symbol, data in prices.items()
            },
            "timestamp": datetime.now().isoformat(),
        }

        # Publish to SUI
        object_id = self.publisher.publish_raw_data(price_data)

        logger.info(f"Published price data for {len(prices)} assets to SUI: {object_id}")

        return object_id
```

---

## On-Chain Publisher

```python
# src/blockchain/sui_publisher.py
from pysui import SuiClient
from pysui.sui.sui_txn import SyncTransaction
import json
import hashlib
import time

class OnChainPublisher:
    """
    Publishes raw data to SUI blockchain.

    Used by data pipelines (NOT agents).
    """

    def __init__(self, sui_client: SuiClient, package_id: str):
        self.client = sui_client
        self.package_id = package_id

    def publish_raw_data(self, data: dict) -> str:
        """
        Publish raw data to SUI blockchain.

        Args:
            data: Dictionary with:
                - data_type: "news_raw", "price_raw", etc.
                - producer: "news_pipeline", "price_pipeline"
                - ... actual data ...

        Returns:
            On-chain object ID
        """
        # Serialize data
        data_json = json.dumps(data, sort_keys=True)
        data_bytes = data_json.encode()

        # Calculate hash
        data_hash = hashlib.sha256(data_bytes).hexdigest()

        # Create transaction
        txn = SyncTransaction(client=self.client)

        txn.move_call(
            target=f"{self.package_id}::raw_data::publish_data",
            arguments=[
                data["producer"].encode(),
                "pipeline".encode(),  # producer_type
                data["data_type"].encode(),
                data_bytes,
                [],  # No source_data_ids (it's raw)
                "".encode(),  # No walrus trace (not an agent)
                int(time.time()),
                data_hash.encode(),
            ]
        )

        result = txn.execute(gas_budget=10_000_000)

        return result.digest
```

---

## Move Smart Contract: Raw Data

```move
// smart_contracts/raw_data.move
module glass_box::raw_data {
    use sui::object::{Self, UID, ID};
    use sui::tx_context::TxContext;
    use sui::transfer;
    use sui::event;

    /// Raw data published by data pipelines (NOT agents)
    struct RawDataObject has key, store {
        id: UID,

        // Provenance
        producer: vector<u8>,           // "news_pipeline", "price_pipeline"
        producer_type: vector<u8>,      // "pipeline" (not "agent")

        // Data
        data_type: vector<u8>,          // "news_raw", "price_raw"
        data_payload: vector<u8>,       // JSON blob

        // Lineage
        source_data_ids: vector<ID>,    // Empty for raw data
        walrus_trace_id: vector<u8>,    // Empty (no reasoning)

        // Metadata
        timestamp: u64,
        data_hash: vector<u8>,
    }

    /// Publish raw data (called by pipelines)
    public entry fun publish_data(
        producer: vector<u8>,
        producer_type: vector<u8>,
        data_type: vector<u8>,
        data_payload: vector<u8>,
        source_data_ids: vector<ID>,
        walrus_trace_id: vector<u8>,
        timestamp: u64,
        data_hash: vector<u8>,
        ctx: &mut TxContext
    ) {
        let data = RawDataObject {
            id: object::new(ctx),
            producer,
            producer_type,
            data_type,
            data_payload,
            source_data_ids,
            walrus_trace_id,
            timestamp,
            data_hash,
        };

        transfer::public_share_object(data);
    }
}
```

---

## Layer 3: Agent A (Sentiment Analysis)

**Agent A is a REAL agent** - uses LLM, reasoning, produces traces

```python
# src/agents/agent_a_sentiment.py
from ..core.base_agent import BaseAgent, AgentInput, AgentOutput
from typing import List
import logging

logger = logging.getLogger(__name__)

class AgentASentiment(BaseAgent):
    """
    Agent A: Sentiment Analysis

    This IS an agent - uses LLM reasoning.

    Input: Raw news data (from on-chain, published by pipeline)
    Process: LLM analyzes sentiment, generates insights
    Output: Sentiment signals → On-chain
    Reasoning Ledger: Stored on Walrus
    """

    def __init__(self, sui_client, walrus_client, package_id, llm):
        super().__init__(
            agent_id="agent_a_sentiment",
            agent_type="agent",  # Mark as agent, not pipeline
            sui_client=sui_client,
            walrus_client=walrus_client,
            package_id=package_id
        )

        self.llm = llm
        self.reasoning_steps = {}

    def process(self, inputs: List[AgentInput]) -> AgentOutput:
        """
        Process raw news data with LLM reasoning.

        This is where the REAL processing happens:
        - LLM reads news articles
        - Analyzes sentiment
        - Generates investment signals
        """
        # Step 1: Extract raw news from on-chain
        self.reasoning_steps["step_1"] = "Reading raw news data from on-chain"

        all_articles = []
        for inp in inputs:
            if inp.data_type == "news_raw":
                articles = inp.data_payload.get("articles", [])
                all_articles.extend(articles)

        self.reasoning_steps["step_2"] = f"Found {len(all_articles)} articles to analyze"

        # Step 2: Use LLM to analyze sentiment
        self.reasoning_steps["step_3"] = "Analyzing sentiment with LLM"

        # Build prompt for LLM
        news_text = "\n\n".join([
            f"Article {i+1}:\nTitle: {article['title']}\nSource: {article['source']}\nDate: {article['published_at']}"
            for i, article in enumerate(all_articles)
        ])

        prompt = f"""Analyze the sentiment of these cryptocurrency news articles:

{news_text}

For each major cryptocurrency mentioned (BTC, ETH, SUI), provide:
1. Sentiment score (-1.0 to +1.0)
2. Key themes (bullish or bearish)
3. Specific evidence from articles

Output as JSON."""

        # LLM reasoning happens here
        llm_response = self.llm.invoke(prompt)
        sentiment_analysis = self._parse_llm_response(llm_response.content)

        self.reasoning_steps["step_4"] = "LLM analysis complete"
        self.reasoning_steps["step_5"] = f"Generated sentiment scores: {sentiment_analysis}"

        # Step 3: Generate investment signals
        signals = self._generate_signals(sentiment_analysis)
        self.reasoning_steps["step_6"] = f"Generated {len(signals)} investment signals"

        # Return as AgentOutput (will be stored on-chain + Walrus)
        return AgentOutput(
            data_type="sentiment_signals",  # Processed data
            data_payload={
                "sentiment_analysis": sentiment_analysis,
                "signals": signals,
                "articles_analyzed": len(all_articles),
            },
            walrus_trace_id="",  # Filled by BaseAgent
            source_data_ids=[inp.data_id for inp in inputs]
        )

    def _parse_llm_response(self, response_text: str) -> dict:
        """Parse LLM JSON response."""
        import json
        try:
            return json.loads(response_text)
        except:
            # Fallback parsing
            return {"error": "Failed to parse LLM response"}

    def _generate_signals(self, sentiment_analysis: dict) -> list:
        """Generate trading signals from sentiment."""
        signals = []

        for asset, data in sentiment_analysis.items():
            if asset in ["BTC", "ETH", "SUI"]:
                score = data.get("sentiment_score", 0)

                if score > 0.5:
                    signals.append({
                        "asset": asset,
                        "action": "buy",
                        "confidence": score,
                        "reason": data.get("themes", "")
                    })
                elif score < -0.5:
                    signals.append({
                        "asset": asset,
                        "action": "sell",
                        "confidence": abs(score),
                        "reason": data.get("themes", "")
                    })
                else:
                    signals.append({
                        "asset": asset,
                        "action": "hold",
                        "confidence": 1 - abs(score),
                        "reason": "Neutral sentiment"
                    })

        return signals

    def _get_reasoning_steps(self) -> dict:
        """Return reasoning steps for Walrus trace."""
        return self.reasoning_steps
```

---

## Complete Data Flow

### Example: News Data Pipeline

```python
# scripts/demo_complete_flow.py
import os
from dotenv import load_dotenv

from src.pipeline.news_pipeline import NewsPipeline
from src.pipeline.price_pipeline import PricePipeline
from src.blockchain.sui_publisher import OnChainPublisher
from src.blockchain.sui_client import SuiTestnetClient
from src.data_clients.walrus_client import WalrusDAClient
from src.agents.agent_a_sentiment import AgentASentiment
from langchain_openai import ChatOpenAI

load_dotenv("config/.env")

# Initialize infrastructure
sui = SuiTestnetClient()
walrus = WalrusDAClient(epochs=10)
publisher = OnChainPublisher(sui, package_id="0x...")
llm = ChatOpenAI(model="gpt-4")

print("=" * 80)
print("COMPLETE DATA PIPELINE FLOW")
print("=" * 80)

# ============================================================================
# LAYER 1: DATA PIPELINE (NOT AGENT)
# ============================================================================
print("\n[LAYER 1: DATA PIPELINE]")
print("Fetching news from CryptoPanic API...")

news_pipeline = NewsPipeline(
    api_token=os.getenv("CRYPTOPANIC_API_TOKEN"),
    sui_publisher=publisher
)

# Pipeline fetches and publishes raw data (no reasoning)
news_object_id = news_pipeline.fetch_and_publish(
    currencies=["BTC", "ETH", "SUI"],
    limit=10
)

print(f"✓ Raw news data published to SUI: {news_object_id}")
print("  - No reasoning occurred")
print("  - Pure ETL: API → Transform → On-chain")

# ============================================================================
# LAYER 1: Price Pipeline (NOT AGENT)
# ============================================================================
print("\nFetching prices from CoinGecko API...")

price_pipeline = PricePipeline(sui_publisher=publisher)

price_object_id = price_pipeline.fetch_and_publish(
    symbols=["BTC", "ETH", "SUI"]
)

print(f"✓ Raw price data published to SUI: {price_object_id}")

# ============================================================================
# LAYER 3: AGENT A (REAL AGENT)
# ============================================================================
print("\n[LAYER 3: AGENT A - SENTIMENT ANALYSIS]")
print("Agent A reading raw news from on-chain...")

agent_a = AgentASentiment(sui, walrus, "0x...", llm)

# Agent reads raw data from on-chain and processes with LLM
sentiment_object_id = agent_a.execute([news_object_id])

print(f"✓ Sentiment signals published to SUI: {sentiment_object_id}")
print("  - LLM reasoning used")
print("  - Reasoning trace stored on Walrus")
print("  - Processed output on SUI")

# ============================================================================
# VERIFICATION
# ============================================================================
print("\n" + "=" * 80)
print("DATA LINEAGE:")
print("=" * 80)
print(f"Off-Chain API → Pipeline → On-Chain ({news_object_id})")
print(f"                              ↓")
print(f"               On-Chain → Agent A → On-Chain ({sentiment_object_id})")
print()
print("✓ Pipeline: No reasoning, just ETL")
print("✓ Agent A: Full reasoning trace on Walrus")
print("✓ Complete verifiable lineage")
```

---

## Summary of Corrections

### ❌ **Wrong: Agent 0**

```python
class Agent0CryptoPanic(BaseAgent):  # WRONG
    def process(self, inputs):
        articles = self.news_source.fetch_news()  # This is just ETL!
        return AgentOutput(...)  # No reasoning happened
```

### ✅ **Correct: Data Pipeline**

```python
class NewsPipeline:  # CORRECT - Not a BaseAgent
    def fetch_and_publish(self):
        # 1. Fetch from API
        articles = self.source.fetch_news()

        # 2. Transform to dict
        news_data = {...}

        # 3. Publish to SUI
        object_id = self.publisher.publish_raw_data(news_data)

        # No LLM, no reasoning, just ETL
        return object_id
```

---

## Key Differences

| Aspect | Data Pipeline | Agent |
|--------|--------------|-------|
| **Base Class** | None (or custom Pipeline class) | BaseAgent |
| **LLM Usage** | ❌ No | ✅ Yes |
| **Reasoning** | ❌ No | ✅ Yes (stored on Walrus) |
| **Input** | Off-chain APIs | On-chain data objects |
| **Output** | Raw data → On-chain | Processed data → On-chain |
| **Purpose** | ETL (Extract, Transform, Load) | Analyze, reason, decide |
| **Complexity** | Simple data transformation | Complex decision making |

---

## File Structure

```
src/
├── pipeline/                  # NEW: Data pipelines (NOT agents)
│   ├── __init__.py
│   ├── news_pipeline.py      # CryptoPanic → SUI
│   ├── price_pipeline.py     # CoinGecko → SUI
│   └── social_pipeline.py    # Twitter → SUI (future)
│
├── blockchain/
│   ├── sui_publisher.py      # NEW: Publish raw data to SUI
│   └── sui_client.py         # Existing
│
├── agents/                    # Agents only
│   ├── agent_a_sentiment.py  # LLM-powered sentiment analysis
│   ├── agent_b_investment.py # LLM-powered investment signals
│   └── agent_c_portfolio.py  # LLM-powered portfolio management
│
├── core/
│   └── base_agent.py         # Only for agents (has LLM, Walrus)
│
└── data_sources/             # Existing (used by pipelines)
    ├── cryptopanic_source.py
    └── coingecko_source.py
```

---

## Next Steps

Would you like me to:
1. **Implement the data pipeline classes** (NewsPipeline, PricePipeline)?
2. **Implement OnChainPublisher** for SUI?
3. **Create the Move smart contract** for raw data storage?
4. **Update Agent A** to read from on-chain raw data?

This corrected architecture clearly separates:
- **Pipelines**: Dumb ETL (no reasoning)
- **Agents**: Smart LLM-powered reasoning

Let me know which component to implement first! 🚀
