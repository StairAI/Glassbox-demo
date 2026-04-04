# Multi-Agent Investment System - Complete Design Document

**Version:** 2.0 (Real Data Integration)
**Last Updated:** March 27, 2026
**Status:** Design Complete - Ready for Implementation

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Real Data Integration Summary](#real-data-integration-summary)
4. [Agent Specifications](#agent-specifications)
5. [Implementation Phases](#implementation-phases)
6. [Directory Structure](#directory-structure)
7. [Data Flow Examples](#data-flow-examples)
8. [Success Criteria](#success-criteria)
9. [Future Enhancements](#future-enhancements)

---

## Overview

**Objective:** Build a sophisticated 3-agent system (Sentiment Digestion → Investment Suggestion → Portfolio Management) with Glass Box Protocol reasoning trace integration and agent-specific RAID scoring.

### Key Features

✅ **100% Real Data** - No mocking (except for demo seeding)
✅ **Zero Cost** - All services use free tiers
✅ **Real Blockchain** - SUI Testnet with actual transactions
✅ **Real DA Layer** - Walrus for immutable reasoning traces
✅ **Real Validation** - 24-hour price predictions verified with actual data
✅ **Simplified Architecture** - No complex state machines, just status tracking

### System Components

| Component | Implementation | Status |
|-----------|---------------|--------|
| **Price Data** | CoinGecko API (BTC/SUI) | ✅ Real |
| **News Data** | CryptoPanic API | ✅ Real |
| **Blockchain** | SUI Testnet | ✅ Real |
| **Data Availability** | Walrus DA | ✅ Real |
| **RAID Validation** | Real price comparison (24h) | ✅ Real |
| **Reasoning Traces** | Walrus blob storage | ✅ Real |

---

## Architecture

### High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    REAL DATA SOURCES (ALL LIVE!)                    │
│  [CryptoPanic API] [CoinGecko API: BTC] [CoinGecko API: SUI]       │
└───────────┬────────────────┬─────────────────────────────┬──────────┘
            │                │                             │
            ▼                │                             │
    ┌───────────────┐        │                             │
    │   AGENT A     │        │                             │
    │   Sentiment   │        │                             │
    │   Digestion   │        │                             │
    └───────┬───────┘        │                             │
            │                │                             │
            │ Signal A       │                             │
            │ (Sentiment     │                             │
            │  Metrics)      │                             │
            │                │                             │
            └────────┬───────┘                             │
                     ▼                                     │
            ┌────────────────┐                             │
            │   AGENT B      │                             │
            │  Investment    │◄────────────────────────────┘
            │  Suggestion    │   (Real BTC Price - CoinGecko)
            └───────┬────────┘
                    │
                    │ Signal B
                    │ (BTC Price
                    │  Prediction)
                    │
                    └──────┬─────────────────┐
                           ▼                 │
                   ┌────────────────┐        │ (Real SUI Price)
                   │   AGENT C      │        │
                   │   Portfolio    │◄───────┘
                   │   Management   │
                   └────────┬───────┘
                            │
                            ▼
                   [Asset Allocation Actions]
                            │
                            ▼
            ┌───────────────────────────────────────┐
            │  SUI TESTNET + WALRUS DA INTEGRATION  │
            │  • Agent Identity (testnet addresses) │
            │  • Reasoning traces → Walrus DA       │
            │  • RAID scores → SUI chain            │
            │  • Portfolio state → SUI chain        │
            │  • Rebalancing txs → SUI chain        │
            └───────────────────────────────────────┘
```

### Data Flow Pipeline

```
CryptoPanic API (News)
    ↓
[Agent A: Sentiment]
    ↓
    Reasoning Trace → Walrus DA (Blob ID: 7Jqe...)
    Signal → Local JSONL
    ↓
CoinGecko API (BTC Price)
    ↓
[Agent B: Predictions]
    ↓
    Reasoning Trace → Walrus DA (Blob ID: 8KpD...)
    Prediction → SQLite (with timestamp)
    Signal → Local JSONL
    ↓
    [Wait 24h]
    ↓
    Validate with Real Price (CoinGecko)
    Calculate RAID Score
    Update SUI Testnet Chain
    ↓
[Agent C: Portfolio]
    ↓
    Reasoning Trace → Walrus DA (Blob ID: 9LqE...)
    Portfolio State → SUI Testnet
    Rebalancing TX → SUI Testnet
    RAID Score → SUI Testnet
```

---

## Real Data Integration Summary

### ✅ REAL (No Mocking!)

#### 1. Price Data - CoinGecko API
- **Status:** FULLY FEASIBLE
- **Endpoint:** `https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,sui&vs_currencies=usd`
- **Rate Limit:** 5-15 calls/min (free tier)
- **Cost:** FREE (no API key required)
- **Coverage:** BTC, SUI, 14,000+ cryptocurrencies
- **Update Frequency:** ~60 seconds

**Example Response:**
```json
{
  "bitcoin": {"usd": 70234.56},
  "sui": {"usd": 2.48}
}
```

#### 2. Blockchain - SUI Testnet
- **Status:** FULLY FEASIBLE
- **RPC Endpoint:** `https://fullnode.testnet.sui.io:443`
- **SDK:** `pysui` (official Python SDK)
- **Tokens:** Free from faucet at `https://faucet.sui.io/`
- **Features:**
  - Create real SUI addresses (testnet)
  - Submit real transactions
  - Store RAID scores on-chain
  - Track portfolio rebalancing
  - Query transaction history

#### 3. Data Availability - Walrus DA Layer
- **Status:** FULLY FEASIBLE
- **Network:** SUI Testnet (launched Oct 2024)
- **CLI Installation:** `curl https://install.walrus.xyz | sh`
- **Storage Command:** `walrus store reasoning_trace.json --epochs 10 --context testnet`
- **File Limit:** 10 MiB via web, unlimited via CLI
- **Features:**
  - Immutable blob storage
  - Permanent blob IDs for retrieval
  - Erasure coding (4x-5x replication)
  - Decentralized across nodes

**Example Upload:**
```bash
$ walrus store reasoning_trace.json --epochs 5 --context testnet
Blob ID: 7Jqe8Z...ABC123
```

#### 4. News Data - CryptoPanic API
- **Status:** ALREADY INTEGRATED (needs endpoint fix)
- **Token:** `72101129f9f637bc26a837a8b61ad6bae189ab2f`
- **Rate Limit:** 100 requests/day (free tier)
- **Coverage:** BTC, SUI, 100+ news sources
- **Current Issue:** 404 errors (endpoint may have changed v1→v2)

#### 5. RAID Validation - Real Price Comparison
- **Status:** FULLY FEASIBLE (depends on CoinGecko)
- **Logic:**
  1. Agent B makes prediction at T0
  2. Store prediction with timestamp in SQLite
  3. After 24h, fetch actual price from CoinGecko
  4. Calculate MAE, direction accuracy, consistency
  5. Update RAID score and submit to SUI testnet

**Metrics:**
- Accuracy: % predictions within 5% of actual
- Mean Absolute Error (MAE)
- Direction Accuracy: Did price move as predicted?
- RAID Score = 0.5 × accuracy + 0.3 × direction + 0.2 × (1 - MAE)

#### 6. Reasoning Traces - Walrus DA Storage
- **Status:** FULLY FEASIBLE
- **Flow:**
  1. Agent generates reasoning trace (JSON)
  2. Upload to Walrus DA (get blob ID)
  3. Store blob ID on SUI chain (permanent reference)
  4. Immutable and retrievable forever

### ✅ SIMPLIFIED (No Complex State Machines!)

**Before:**
```python
class StateMachine:
    states = ["IDLE", "COLLECTING", "ANALYZING", "PUBLISHING"]
    def transition(from_state, to_state, reason): ...
```

**After:**
```python
agent_status = {
    "status": "active",  # Simple string: idle/active/error
    "last_update": "2026-03-27T10:00:00Z",
    "metrics": {"processed": 0, "errors": 0},
    "last_trace_blob_id": "7Jqe8Z...ABC123",
    "sui_tx_hash": "0x789abc..."
}
```

### 💰 Cost Breakdown

| Component | Service | Cost | Rate Limit |
|-----------|---------|------|------------|
| Price Data | CoinGecko API | **FREE** | 5-15 calls/min |
| Blockchain | SUI Testnet | **FREE** | Faucet tokens |
| Data Availability | Walrus DA | **FREE** | Testnet storage |
| News Data | CryptoPanic | **FREE** | 100 req/day |
| **TOTAL** | | **$0** | Perfect for demo! |

### ⏱️ Implementation Timeline

| Phase | Tasks | Time Estimate |
|-------|-------|---------------|
| **Phase 1** | Real Data Sources | 3-4 hours |
| **Phase 2** | Agent A + Walrus | 2 hours |
| **Phase 3** | Agent B + RAID | 3-4 hours |
| **Phase 4** | Agent C + Portfolio | 3-4 hours |
| **Phase 5** | Integration | 2 hours |
| **Phase 6** | Testing | 2 hours |
| **TOTAL** | | **15-19 hours** |

---

## Agent Specifications

### Agent A: Sentiment Digestion Agent

**Purpose:** Consume raw news data from CryptoPanic, extract sentiment patterns, and output structured sentiment metrics.

**Input:**
- Real news headlines from CryptoPanic API
- Historical sentiment data (local SQLite)

**Output Signal:**
```json
{
  "signal_type": "sentiment_digest",
  "metrics": {
    "overall_sentiment": 0.65,          // -1.0 to +1.0
    "sentiment_volatility": 0.23,       // 0.0 to 1.0 (stability)
    "news_volume": 47,                  // articles in last hour
    "bullish_ratio": 0.73,              // % bullish articles
    "sentiment_trend": "ACCELERATING",  // ACCELERATING/STABLE/DECELERATING
    "key_topics": ["adoption", "ETF"]   // top keywords
  },
  "confidence": 0.82,
  "timestamp": "2026-03-27T10:00:00Z"
}
```

**Reasoning Trace:**
- Captures: Observing → Planning → Reasoning → Acting
- Uploaded to Walrus DA (returns blob ID)
- **No RAID scoring** (baseline data processor)

**Status Tracking:**
```python
agent_a_status = {
    "status": "active",                  # idle/active/error
    "last_update": "2026-03-27T10:00:00Z",
    "news_processed": 20,
    "current_sentiment": 0.65,
    "volatility": 0.23,
    "trend": "ACCELERATING",
    "last_trace_blob_id": "7Jqe8Z...ABC123"  # Walrus DA reference
}
```

---

### Agent B: Investment Suggestion Agent

**Purpose:** Consume sentiment signal from Agent A + real BTC price from CoinGecko, predict future BTC price.

**Input:**
- Signal from Agent A (sentiment metrics)
- Real BTC price from CoinGecko API
- Historical price data (local cache)

**Output Signal:**
```json
{
  "signal_type": "price_prediction",
  "asset": "BTC",
  "current_price": 70000,
  "predicted_price_24h": 72500,
  "prediction_confidence": 0.78,
  "direction": "BULLISH",              // BULLISH/BEARISH/NEUTRAL
  "expected_return_pct": 3.57,
  "risk_level": "MODERATE",            // LOW/MODERATE/HIGH
  "reasoning_summary": "Strong sentiment + technical breakout",
  "timestamp": "2026-03-27T10:00:00Z"
}
```

**Reasoning Trace:**
- Captures: Observing → Planning → Reasoning → Acting
- Uploaded to Walrus DA (returns blob ID)
- Blob ID stored on SUI chain with prediction

**RAID Scoring Mechanism:**
- **After 24h:** Fetch actual BTC price from CoinGecko
- **Calculate Metrics:**
  - Accuracy: % predictions within 5% of actual
  - Mean Absolute Error (MAE)
  - Direction accuracy: Did price move as predicted?
- **Formula:** Score = 0.5 × accuracy + 0.3 × direction + 0.2 × (1 - normalized_MAE)
- **Update:** Submit RAID score to SUI testnet with blob ID reference

**Status Tracking:**
```python
agent_b_status = {
    "status": "active",
    "last_update": "2026-03-27T10:00:00Z",
    "last_prediction": 72500,
    "confidence": 0.78,
    "accuracy_30d": 0.67,           # From REAL validation!
    "mae_30d": 0.023,               # Mean Absolute Error
    "direction_accuracy": 0.71,
    "raid_score": 0.723,            # Stored on SUI testnet
    "last_trace_blob_id": "8KpD9A...DEF456",  # Walrus DA
    "sui_tx_hash": "0x789abc..."    # On-chain RAID update
}
```

---

### Agent C: Portfolio Management Agent

**Purpose:** Accept predictions from Agent B + real SUI price from CoinGecko, generate optimal asset allocation, execute rebalancing on SUI testnet.

**Input:**
- Signal from Agent B (BTC prediction)
- Real SUI price from CoinGecko API
- Current portfolio state (SQLite)
- Risk parameters (configurable)
- SUI testnet wallet credentials

**Output Signal:**
```json
{
  "signal_type": "portfolio_allocation",
  "actions": [
    {
      "asset": "BTC",
      "action": "BUY",
      "target_allocation_pct": 60,     // Target % of portfolio
      "current_allocation_pct": 45,
      "rebalance_amount_usd": 15000
    },
    {
      "asset": "SUI",
      "action": "HOLD",
      "target_allocation_pct": 30,
      "current_allocation_pct": 30,
      "rebalance_amount_usd": 0
    },
    {
      "asset": "USDC",
      "action": "SELL",
      "target_allocation_pct": 10,
      "current_allocation_pct": 25,
      "rebalance_amount_usd": -15000
    }
  ],
  "portfolio_metrics": {
    "expected_return_24h_pct": 2.8,
    "risk_score": 0.45,
    "diversification_score": 0.82
  },
  "timestamp": "2026-03-27T10:00:00Z"
}
```

**Reasoning Trace:**
- Captures: Observing → Planning → Reasoning → Acting
- Uploaded to Walrus DA (returns blob ID)
- Blob ID stored on SUI chain with portfolio state

**RAID Scoring Mechanism:**
- **Track Metrics:** Sharpe ratio, total return, max drawdown, win rate
- **Formula:** Score = 0.4 × sharpe + 0.3 × return + 0.2 × (1 - drawdown) + 0.1 × win_rate
- **Update:** Submit RAID score to SUI testnet with performance data

**Blockchain Integration:**
- Submit rebalancing transaction to SUI testnet
- Store portfolio state on-chain
- Update RAID score with blob ID reference
- Track gas usage and transaction history

**Status Tracking:**
```python
agent_c_status = {
    "status": "active",
    "last_update": "2026-03-27T10:00:00Z",
    "portfolio_value": 100000,
    "allocation": {"BTC": 0.45, "SUI": 0.30, "USDC": 0.25},
    "performance_30d": {
        "return": 0.125,
        "sharpe_ratio": 1.82,
        "max_drawdown": -0.032,
        "win_rate": 0.73
    },
    "raid_score": 0.856,            # Stored on SUI testnet
    "last_trace_blob_id": "9LqE0B...GHI789",  # Walrus DA
    "sui_address": "0x123abc...",   # SUI testnet agent address
    "last_rebalance_tx": "0x456def...",  # SUI testnet tx hash
    "last_raid_update_tx": "0x789ghi..."
}
```

---

## Implementation Phases

### Phase 1: Real Data Sources (3-4 hours)

#### 1.1 CoinGecko API Integration (`coingecko_client.py`)
- **Endpoint:** `/api/v3/simple/price?ids=bitcoin,sui&vs_currencies=usd`
- **Features:**
  - Fetch real-time BTC/SUI prices
  - Local caching (respect 5-15 calls/min limit)
  - Error handling with exponential backoff
  - No API key required for basic calls
- **Replace:** `price_simulator.py` (delete mock)

#### 1.2 CryptoPanic API Fix (`news_api.py`)
- **Token:** `72101129f9f637bc26a837a8b61ad6bae189ab2f`
- **Tasks:**
  - Debug 404 errors (verify endpoint v1 vs v2)
  - Test with token authentication
  - Implement fallback to mock if needed
  - Store articles in SQLite with deduplication

#### 1.3 SUI Testnet Setup (`sui_testnet_client.py`)
- **RPC:** `https://fullnode.testnet.sui.io:443`
- **Tasks:**
  - Install SDK: `pip install pysui`
  - Get testnet tokens from faucet
  - Create 3 agent addresses (A, B, C)
  - Test transaction submission
  - Implement RAID score storage functions

#### 1.4 Walrus DA Integration (`walrus_client.py`)
- **Installation:** `curl https://install.walrus.xyz | sh`
- **Tasks:**
  - Exchange SUI → WAL tokens (1:1 testnet)
  - Create Python wrapper for CLI commands
  - Test blob upload: `walrus store <file> --epochs 10`
  - Parse blob IDs from responses
  - Implement retrieval function

---

### Phase 2: Agent A - Sentiment Digestion (2 hours)

#### 2.1 Implement `agent_a_sentiment.py`
- Consume real news from CryptoPanic API
- Calculate sentiment metrics:
  - Overall sentiment (-1.0 to +1.0)
  - Volatility (0.0 to 1.0)
  - News volume (count)
  - Bullish ratio (%)
  - Sentiment trend (ACCELERATING/STABLE/DECELERATING)
  - Key topics (keyword extraction)
- Generate reasoning trace (JSON format)
- Upload trace to Walrus DA
- Store blob ID locally
- Output sentiment signal (JSONL)
- **No RAID scoring** (baseline processor)

---

### Phase 3: Agent B - Investment Suggestion (3-4 hours)

#### 3.1 Implement `agent_b_investment.py`
- Consume Agent A signal (JSONL)
- Fetch real BTC price from CoinGecko
- Predict BTC price 24h ahead (simple model)
- Generate reasoning trace with prediction logic
- Upload trace to Walrus DA
- Store prediction with timestamp in SQLite:
  ```sql
  CREATE TABLE predictions (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    current_price REAL,
    predicted_price REAL,
    confidence REAL,
    direction TEXT,
    blob_id TEXT,
    validated BOOLEAN DEFAULT 0,
    actual_price REAL,
    mae REAL,
    correct_direction BOOLEAN
  );
  ```
- Output prediction signal (JSONL)

#### 3.2 Implement Real RAID Validation (`prediction_tracker.py`)
- **Scheduled Task:** Run every hour to check for 24h-old predictions
- **Logic:**
  1. Query unvalidated predictions older than 24h
  2. Fetch actual BTC price from CoinGecko
  3. Calculate MAE: `abs(actual - predicted) / predicted`
  4. Calculate direction accuracy: `(actual > current) == (predicted > current)`
  5. Calculate consistency over 30-day window
  6. Update RAID score: `0.5 × accuracy + 0.3 × direction + 0.2 × (1 - MAE)`
  7. Submit RAID score to SUI testnet with blob ID reference
  8. Mark prediction as validated

#### 3.3 Wire Agent A → Agent B Pipeline
- Read Agent A signal from JSONL
- Signal Agent B on new sentiment data
- Pass signals via local files (no network calls)

---

### Phase 4: Agent C - Portfolio Management (3-4 hours)

#### 4.1 Implement `agent_c_portfolio.py`
- Consume Agent B signal (JSONL)
- Fetch real SUI price from CoinGecko
- Calculate optimal portfolio allocation (BTC/SUI/USDC)
  - Simple mean-variance optimization
  - Risk constraints (configurable)
  - Confidence-weighted allocations
- Generate rebalancing actions
- Generate reasoning trace with allocation logic
- Upload trace to Walrus DA
- Submit rebalancing transaction to SUI testnet
- Submit portfolio state to SUI testnet
- Track portfolio metrics in SQLite

#### 4.2 Implement Portfolio RAID Scoring (`portfolio_tracker.py`)
- **Metrics:**
  - Sharpe Ratio: `(return - risk_free_rate) / std_dev`
  - Total Return: `(final_value - initial_value) / initial_value`
  - Max Drawdown: `max((peak - current) / peak)`
  - Win Rate: `profitable_rebalances / total_rebalances`
- **Formula:** `0.4 × sharpe + 0.3 × return + 0.2 × (1 - drawdown) + 0.1 × win_rate`
- Submit RAID score to SUI testnet
- Link to Walrus blob ID on-chain

#### 4.3 Wire Agent B → Agent C Pipeline
- Read Agent B signal from JSONL
- Signal Agent C on new predictions
- Execute full pipeline: A → B → C

---

### Phase 5: Integration & Orchestration (2 hours)

#### 5.1 Implement `runner.py` - Multi-Agent Coordinator
- Run agents in sequence: A → B → C
- Pass signals between agents (JSONL files)
- Upload all traces to Walrus DA
- Submit trace references to SUI testnet
- Update RAID scores on-chain
- Display real-time metrics:
  - Current prices (CoinGecko)
  - Agent statuses
  - Walrus blob IDs
  - SUI transaction hashes
  - RAID scores

#### 5.2 Seed Historical Data for Demo
- Generate 30 days of fake predictions with validation
- Calculate initial RAID scores
- Store in SQLite for instant demo results
- Use real price history from CoinGecko

#### 5.3 Create Output Directories
- Local: `signals/`, `traces/`, `logs/`
- Track remote: Walrus blob IDs, SUI tx hashes in CSV

---

### Phase 6: Testing & Visualization (2 hours)

#### 6.1 Integration Tests
- Test CoinGecko API calls (rate limiting, errors)
- Test SUI testnet transactions (balance checks, gas)
- Test Walrus DA uploads (blob ID parsing, retrieval)
- Test RAID validation logic (edge cases, accuracy)
- Mock external APIs for unit tests

#### 6.2 Console Visualization
- Real-time dashboard:
  - Live price updates (CoinGecko)
  - Agent statuses (active/idle/error)
  - Latest signals
  - Blockchain confirmations (SUI tx hashes)
  - Walrus blob IDs (clickable if explorer available)
  - RAID score updates

#### 6.3 Performance Reports
- Prediction accuracy over time (CSV export)
- Portfolio returns vs baseline (chart)
- On-chain verification links (SUI explorer)
- Walrus blob retrieval commands

#### 6.4 Update Documentation
- README with setup instructions:
  - CoinGecko API (no key needed!)
  - SUI testnet faucet workflow
  - Walrus CLI installation
  - CryptoPanic API token
- Example outputs and screenshots
- Troubleshooting guide

---

## Directory Structure

```
demo/
├── DESIGN.md (this file - COMPLETE DESIGN!)
├── README.md
├── requirements.txt
├── config/
│   ├── .env.example                 # Template with all API tokens
│   ├── .env                         # Actual credentials (gitignored)
│   └── settings.py                  # Application configuration
│
├── src/
│   ├── data_sources/
│   │   ├── __init__.py
│   │   ├── coingecko_client.py     # REAL: BTC/SUI prices
│   │   ├── news_api.py              # REAL: CryptoPanic news
│   │   └── database.py              # SQLite operations
│   │
│   ├── blockchain/
│   │   ├── __init__.py
│   │   ├── sui_testnet_client.py   # REAL: SUI testnet integration
│   │   └── walrus_client.py         # REAL: Walrus DA uploads
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── agent_a_sentiment.py    # Sentiment (real news)
│   │   ├── agent_b_investment.py   # Investment (real prices)
│   │   └── agent_c_portfolio.py    # Portfolio (real blockchain)
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── signal.py                # Signal data structures
│   │   └── reasoning_trace.py       # Trace JSON formatting
│   │
│   ├── scoring/
│   │   ├── __init__.py
│   │   ├── prediction_tracker.py   # Agent B RAID (real validation!)
│   │   └── portfolio_tracker.py    # Agent C RAID (real returns!)
│   │
│   └── orchestrator/
│       ├── __init__.py
│       └── runner.py                # Multi-agent coordinator
│
├── data/
│   ├── news.db                      # SQLite: News articles
│   ├── predictions.db               # SQLite: Agent B predictions
│   └── portfolio.db                 # SQLite: Agent C state
│
├── output/
│   ├── traces/                      # Local trace copies (also on Walrus)
│   │   ├── agent_a/
│   │   ├── agent_b/
│   │   └── agent_c/
│   ├── signals/
│   │   ├── sentiment_signals.jsonl
│   │   ├── price_predictions.jsonl
│   │   └── allocations.jsonl
│   ├── logs/                        # Application logs
│   └── reports/                     # Performance analysis
│
├── scripts/
│   ├── collect_news.py              # Fetch CryptoPanic news
│   ├── run_single_agent.py          # Test individual agents
│   ├── validate_predictions.py      # Run RAID validation
│   ├── setup_testnet.py             # SUI testnet setup helper
│   └── seed_historical_data.py      # Generate demo data
│
└── tests/
    ├── test_agents.py
    ├── test_scoring.py
    ├── test_blockchain.py           # SUI + Walrus tests
    └── test_integration.py
```

### Module Purposes

#### 🤖 Agents (`src/agents/`)
Three specialized agents forming the pipeline:
- **Agent A**: News → Sentiment (baseline, no RAID)
- **Agent B**: Sentiment → Predictions (RAID: accuracy)
- **Agent C**: Predictions → Portfolio (RAID: Sharpe ratio)

#### 🧠 Core (`src/core/`)
Foundational components used by all agents:
- **Signal**: Structured data passed between agents (JSONL format)
- **Reasoning Trace**: JSON formatting for Walrus DA submission

#### 📊 Scoring (`src/scoring/`)
RAID score calculation for Agents B & C:
- **Prediction Tracker**: Validate predictions after 24h, calculate accuracy
- **Portfolio Tracker**: Track portfolio performance, calculate Sharpe ratio

#### 📡 Data Sources (`src/data_sources/`)
External data integrations (all real!):
- **CoinGecko Client**: Fetch real BTC/SUI prices
- **News API**: Fetch cryptocurrency news from CryptoPanic
- **Database**: SQLite operations for local storage

#### ⛓️ Blockchain (`src/blockchain/`)
Blockchain integration layer (all real!):
- **SUI Testnet Client**: Real transaction submission and querying
- **Walrus Client**: Real blob storage and retrieval

#### 🎯 Orchestrator (`src/orchestrator/`)
Multi-agent coordination:
- **Runner**: Executes agents in sequence (A → B → C), manages pipelines

---

## Data Flow Examples

### Cycle 1: News Arrives

**Step 1: Agent A processes real news**
```
INPUT: Real CryptoPanic news → "Bitcoin ETF sees record $500M inflows"
PROCESSING:
  - Fetch from CryptoPanic API
  - Analyze sentiment using keyword matching
  - Calculate metrics: sentiment, volatility, trend
OUTPUT: {
  "overall_sentiment": +0.82,
  "sentiment_volatility": 0.15,
  "sentiment_trend": "ACCELERATING",
  "news_volume": 47,
  "bullish_ratio": 0.73
}
TRACE: Upload to Walrus DA → Blob ID: 7Jqe8Z...ABC123
```

**Step 2: Agent B makes prediction with real price**
```
INPUT:
  - Agent A signal (sentiment: +0.82)
  - Real BTC price from CoinGecko: $70,000
REASONING:
  - Strong sentiment (+0.82) indicates buying pressure
  - Low volatility (0.15) suggests sustained trend
  - Technical indicators (simulated) confirm breakout
OUTPUT: {
  "predicted_price_24h": $72,100,
  "confidence": 0.78,
  "direction": "BULLISH",
  "expected_return_pct": +3.0%
}
STORAGE:
  - Save prediction to SQLite with timestamp
  - Upload reasoning trace to Walrus DA → Blob ID: 8KpD9A...DEF456
  - Submit blob ID reference to SUI testnet → Tx: 0x789abc...
```

**Step 3: Agent C allocates portfolio with real prices**
```
INPUT:
  - Agent B signal (BTC: +3.0%)
  - Real SUI price from CoinGecko: $2.48
  - Current portfolio: BTC 45%, SUI 30%, USDC 25%
REASONING:
  - BTC high conviction → increase allocation 45% → 60%
  - SUI neutral signal → maintain 30%
  - Reduce USDC cash position 25% → 10%
OUTPUT: {
  "BTC": BUY $15,000,
  "SUI": HOLD,
  "USDC": SELL $15,000
}
BLOCKCHAIN:
  - Upload reasoning trace to Walrus DA → Blob ID: 9LqE0B...GHI789
  - Submit rebalancing tx to SUI testnet → Tx: 0x456def...
  - Store portfolio state on-chain
  - Log RAID score commitment → Tx: 0x789ghi...
```

### 24 Hours Later: Real Validation

**Agent B RAID Scoring:**
```
PREDICTION (T0):
  - Predicted: $72,100
  - Timestamp: 2026-03-27T10:00:00Z
  - Confidence: 0.78

ACTUAL (T0+24h):
  - Real price from CoinGecko: $71,850
  - Error: -0.35%
  - Direction: CORRECT (predicted UP, actual UP)

CALCULATION:
  - Accuracy: 99.65% (within 5% threshold: ✓)
  - MAE: 0.0035
  - Direction: CORRECT
  - RAID Score = 0.5 × 0.9965 + 0.3 × 1.0 + 0.2 × (1 - 0.0035)
               = 0.4983 + 0.3 + 0.1993
               = 0.998 (excellent prediction!)

UPDATE:
  - Store validation results in SQLite
  - Update RAID score: 0.723 → 0.731 (rolling 30-day average)
  - Submit updated RAID score to SUI testnet → Tx: 0xabcdef...
```

**Agent C RAID Scoring:**
```
PORTFOLIO PERFORMANCE (24h):
  - Value before: $100,000
  - Value after: $102,800
  - Return: +2.8%
  - Sharpe Ratio: 1.85
  - Max Drawdown: -0.5%
  - Win Rate: 1/1 (100%)

CALCULATION:
  - RAID Score = 0.4 × 1.85/3.0 + 0.3 × 0.028/0.05 + 0.2 × (1 - 0.005) + 0.1 × 1.0
               = 0.247 + 0.168 + 0.199 + 0.100
               = 0.714

UPDATE:
  - Store performance metrics in SQLite
  - Update RAID score: 0.856 → 0.861 (rolling 30-day average)
  - Submit updated RAID score to SUI testnet → Tx: 0xfedcba...
```

---

## Success Criteria

After implementation, the demo must demonstrate:

- [ ] **Agent A** generates sentiment signals from real CryptoPanic news
- [ ] **Agent B** consumes Agent A signals and predicts BTC price using real CoinGecko data
- [ ] **Agent C** consumes Agent B signals and allocates portfolio using real SUI prices
- [ ] **All agents** generate reasoning traces uploaded to Walrus DA
- [ ] **Agent B** prediction accuracy tracked and validated with real 24h prices
- [ ] **Agent B** RAID score calculated and stored on SUI testnet
- [ ] **Agent C** portfolio performance tracked with real metrics
- [ ] **Agent C** RAID score calculated and stored on SUI testnet
- [ ] **Multi-agent pipeline** runs end-to-end for 20+ cycles
- [ ] **Performance metrics** display correctly in console dashboard
- [ ] **All traces** saved locally AND uploaded to Walrus DA
- [ ] **Blockchain integration** confirmed with real SUI testnet transactions
- [ ] **Zero mocking** except for demo seeding (historical data)

---

## Future Enhancements

### 1. Advanced Scoring
- **Agent A**: Sentiment prediction accuracy (correlate sentiment with price movements)
- **Agent B**: Bayesian prediction intervals, confidence calibration
- **Agent C**: Sortino ratio, Calmar ratio, conditional VaR

### 2. Agent Communication
- Feedback loops (Agent C risk tolerance → Agent B predictions)
- Multi-agent coordination (consensus mechanisms)
- Adversarial agents (challenge predictions for robustness)

### 3. Production Deployment
- Migrate from testnet → SUI mainnet
- Walrus DA mainnet (when available)
- Public reputation API for querying RAID scores
- Real trading execution (with safeguards and legal compliance!)

### 4. Additional Data Sources
- Twitter API for real-time sentiment
- Glassnode for on-chain metrics
- TradingView for technical indicators
- Discord/Telegram for community sentiment

### 5. Advanced Features
- Blind Sequencer for work attestation
- zkTLS proofs of API calls
- Cross-stream validation logic
- Multi-asset portfolio (ETH, SOL, etc.)

---

## Appendix: Quick Reference

### Environment Variables (.env)
```bash
# CryptoPanic API
CRYPTOPANIC_API_TOKEN=72101129f9f637bc26a837a8b61ad6bae189ab2f

# SUI Testnet
SUI_TESTNET_RPC=https://fullnode.testnet.sui.io:443
SUI_AGENT_A_ADDRESS=0x...
SUI_AGENT_B_ADDRESS=0x...
SUI_AGENT_C_ADDRESS=0x...

# Walrus DA
WALRUS_CONTEXT=testnet
WALRUS_EPOCHS=10

# CoinGecko API (no key needed!)
# COINGECKO_API_KEY=optional_for_pro_tier
```

### Quick Start Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Setup SUI testnet
python scripts/setup_testnet.py

# Install Walrus CLI
curl https://install.walrus.xyz | sh

# Get testnet tokens
# Visit: https://faucet.sui.io/

# Seed historical data
python scripts/seed_historical_data.py

# Run full pipeline
python src/orchestrator/runner.py

# Run single agent (testing)
python scripts/run_single_agent.py --agent a

# Validate predictions (manual signal)
python scripts/validate_predictions.py
```

### Useful Links
- **CoinGecko API Docs:** https://www.coingecko.com/en/api/documentation
- **SUI Testnet Faucet:** https://faucet.sui.io/
- **SUI Explorer:** https://suiscan.xyz/testnet/home
- **Walrus Docs:** https://docs.walrus.xyz/
- **CryptoPanic API:** https://cryptopanic.com/developers/api/

---

**Document Version:** 2.0
**Last Updated:** March 27, 2026
**Status:** ✅ Design Complete - Ready for Phase 1 Implementation
**Estimated Total Time:** 15-19 hours
**Total Cost:** $0 (all free tiers!)
