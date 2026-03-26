# Multi-Agent Investment System - Implementation Plan

**Objective:** Build a sophisticated 3-agent system (Sentiment Digestion → Investment Suggestion → Portfolio Management) with Glass Box Protocol reasoning trace integration and agent-specific RAID scoring.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                                │
│  [News Feed] [Twitter Sentiment] [BTC Price] [SUI Price (Mock)]    │
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
            │  Suggestion    │   (BTC Price Data)
            └───────┬────────┘
                    │
                    │ Signal B
                    │ (BTC Price
                    │  Prediction)
                    │
                    └──────┬─────────────────┐
                           ▼                 ▼
                   ┌────────────────┐  [SUI Prediction
                   │   AGENT C      │   Mock Signal]
                   │   Portfolio    │◄─────────┘
                   │   Management   │
                   └────────┬───────┘
                            │
                            ▼
                   [Asset Allocation Actions]
                            │
                            ▼
                   [SUI Blockchain Integration]
                     • Agent Identity (SUI addresses)
                     • On-chain trace commitments
                     • RAID score storage
                     • Portfolio rebalancing txs
```

---

## Agent Specifications

### Agent A: Sentiment Digestion Agent

**Purpose:** Consume raw news data, extract sentiment patterns, and output structured sentiment metrics.

**Input:**
- Raw news headlines (from news fetcher)
- Historical sentiment data

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
  "timestamp": "2026-03-25T10:00:00Z"
}
```

**Reasoning Trace:**
- Captures: Observing → Planning → Reasoning → Acting
- **No RAID scoring** (baseline data processor)

**State:**
```
=== SENTIMENT DIGESTION STATE ===
Last 20 News Items Processed
Rolling Sentiment: +0.65 (BULLISH)
Volatility Index: 0.23 (STABLE)
Trend: ACCELERATING
```

---

### Agent B: Investment Suggestion Agent

**Purpose:** Consume sentiment signal from Agent A + BTC price data, predict future BTC price.

**Input:**
- Signal from Agent A (sentiment metrics)
- Current BTC price + historical price data
- Technical indicators (simulated)

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
  "timestamp": "2026-03-25T10:00:00Z"
}
```

**Reasoning Trace:**
- Captures: Observing → Planning → Reasoning → Acting
- **RAID Scoring Mechanism:**
  - Track prediction accuracy over 24-hour windows
  - Metrics:
    - Accuracy (% predictions within 5% of actual)
    - Mean Absolute Error (MAE)
    - Direction accuracy (did price go predicted direction?)
  - Score = 0.5 × accuracy + 0.3 × direction_accuracy + 0.2 × (1 - normalized_MAE)

**State:**
```
=== INVESTMENT SUGGESTION STATE ===
Last Prediction: $72,500 (24h target)
Confidence: 0.78
Historical Accuracy (30d): 67%
MAE (30d): 2.3%
Direction Accuracy: 71%
Current RAID Score: 0.723
```

---

### Agent C: Portfolio Management Agent

**Purpose:** Accept predictions from Agent B (+ mocked SUI prediction), generate optimal asset allocation, and execute rebalancing on SUI blockchain.

**Input:**
- Signal from Agent B (BTC prediction)
- Mocked SUI prediction signal (same format)
- Current portfolio state (BTC/SUI/USDC holdings)
- Risk parameters
- SUI wallet address and credentials

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
  "timestamp": "2026-03-25T10:00:00Z"
}
```

**Reasoning Trace:**
- Captures: Observing → Planning → Reasoning → Acting
- **RAID Scoring Mechanism:**
  - Track portfolio performance metrics over rolling windows
  - Metrics:
    - Sharpe Ratio (risk-adjusted return)
    - Total Return (%)
    - Max Drawdown
    - Win Rate (% of profitable rebalances)
  - Score = 0.4 × normalized_sharpe + 0.3 × normalized_return + 0.2 × (1 - normalized_drawdown) + 0.1 × win_rate

**State:**
```
=== PORTFOLIO MANAGEMENT STATE ===
Total Portfolio Value: $100,000
BTC: 45% ($45,000)
SUI: 30% ($30,000)
USDC: 25% ($25,000)

Performance (30d):
  Return: +12.5%
  Sharpe Ratio: 1.82
  Max Drawdown: -3.2%
  Win Rate: 73%

Current RAID Score: 0.856

SUI Blockchain Status:
  Agent Address: 0x123abc...
  Last Tx: 0x456def... (Block: 12,847,392)
  RAID Score On-Chain: 0.856
  Gas Used: 0.02 SUI
```

---

## Directory Structure

```
demo/
├── PLAN.md (this file)
├── README.md
├── requirements.txt
├── src/
│   ├── data_sources/
│   │   ├── __init__.py
│   │   ├── news_fetcher.py          # Bitcoin news generator
│   │   ├── price_fetcher.py         # BTC/SUI price simulator
│   │   └── sui_predictor_mock.py    # Mock SUI prediction generator
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── agent_a_sentiment.py     # Sentiment Digestion Agent
│   │   ├── agent_b_investment.py    # Investment Suggestion Agent
│   │   └── agent_c_portfolio.py     # Portfolio Management Agent
│   ├── state/
│   │   ├── __init__.py
│   │   └── state_machine.py         # Text-based state machine (shared)
│   ├── scoring/
│   │   ├── __init__.py
│   │   ├── prediction_tracker.py    # Track Agent B predictions
│   │   └── portfolio_tracker.py     # Track Agent C performance
│   ├── sdk/
│   │   ├── __init__.py
│   │   ├── glassbox_sdk.py          # Glass Box Protocol SDK
│   │   └── trace_generator.py       # Reasoning trace generator
│   └── runner.py                     # Multi-agent orchestration
├── output/
│   ├── traces/
│   │   ├── agent_a/                 # Sentiment traces
│   │   ├── agent_b/                 # Investment traces
│   │   └── agent_c/                 # Portfolio traces
│   ├── signals/
│   │   ├── sentiment_signals.jsonl  # Agent A outputs
│   │   ├── price_predictions.jsonl  # Agent B outputs
│   │   └── allocations.jsonl        # Agent C outputs
│   ├── state/
│   │   ├── agent_a_state.txt
│   │   ├── agent_b_state.txt
│   │   └── agent_c_state.txt
│   └── performance/
│       ├── agent_b_predictions.csv  # Prediction accuracy tracking
│       └── agent_c_portfolio.csv    # Portfolio performance tracking
└── tests/
    ├── test_agent_a.py
    ├── test_agent_b.py
    ├── test_agent_c.py
    └── test_integration.py
```

---

## Implementation Phases

### Phase 1: Core Infrastructure (60 min)
1. Update `price_fetcher.py` - BTC/SUI price simulator
2. Create `sui_predictor_mock.py` - Mock SUI predictions
3. Create `sui_integration.py` - SUI blockchain interaction layer
4. Update `state_machine.py` - Generic state for all agents
5. Create `prediction_tracker.py` - Agent B scoring
6. Create `portfolio_tracker.py` - Agent C scoring

### Phase 2: Agent A - Sentiment Digestion (45 min)
6. Implement `agent_a_sentiment.py`
   - Consume news from news_fetcher
   - Calculate sentiment metrics (overall, volatility, trend)
   - Output structured sentiment signal
   - Generate reasoning trace (no scoring)

### Phase 3: Agent B - Investment Suggestion (60 min)
7. Implement `agent_b_investment.py`
   - Consume Agent A signal + BTC price data
   - Predict BTC price 24h ahead
   - Generate reasoning trace with prediction logic
   - Submit to prediction tracker for scoring
8. Wire Agent A → Agent B pipeline

### Phase 4: Agent C - Portfolio Management (60 min)
9. Implement `agent_c_portfolio.py`
   - Consume Agent B signal + mock SUI signal
   - Calculate optimal portfolio allocation (BTC/SUI/USDC)
   - Generate rebalancing actions
   - Submit rebalancing transactions to SUI blockchain
   - Generate reasoning trace with allocation logic
   - Submit to portfolio tracker for scoring
10. Wire Agent B → Agent C pipeline

### Phase 5: Integration & Orchestration (45 min)
11. Implement `runner.py` - Multi-agent coordinator
    - Run agents in sequence: A → B → C
    - Pass signals between agents
    - Submit all traces to Glass Box Protocol
    - Display performance metrics
12. Create output directories and logging

### Phase 6: Testing & Visualization (30 min)
13. Create integration tests
14. Add console visualization for multi-agent flow
15. Generate performance reports
16. Update README with multi-agent documentation

**Total Estimated Time:** 5 hours

---

## Data Flow Example

### Cycle 1: News Arrives

**Step 1: Agent A processes news**
```
INPUT: "Bitcoin ETF sees record $500M inflows"
OUTPUT: {
  "overall_sentiment": +0.82,
  "sentiment_volatility": 0.15,
  "sentiment_trend": "ACCELERATING"
}
```

**Step 2: Agent B makes prediction**
```
INPUT: Agent A signal + BTC price $70,000
REASONING:
  - Strong sentiment (+0.82) indicates buying pressure
  - Low volatility (0.15) suggests sustained trend
  - Technical indicators confirm breakout
OUTPUT: {
  "predicted_price_24h": $72,100,
  "confidence": 0.78,
  "expected_return_pct": +3.0%
}
```

**Step 3: Agent C allocates portfolio**
```
INPUT: Agent B (BTC: +3.0%) + Mock SUI (-1.2%)
REASONING:
  - BTC high conviction → increase allocation 45% → 60%
  - SUI weak signal → maintain 30%
  - Reduce USDC cash position 25% → 10%
OUTPUT: {
  "BTC": BUY $15,000,
  "SUI": HOLD,
  "USDC": SELL $15,000
}
BLOCKCHAIN:
  - Submit rebalancing tx to SUI chain
  - Store RAID score on-chain
  - Log portfolio state commitment
```

### 24 Hours Later: Scoring

**Agent B Scoring:**
```
Predicted: $72,100
Actual: $71,850
Error: -0.35%
Direction: CORRECT (predicted UP, actual UP)
→ Prediction added to history
→ RAID score updated: 0.723 → 0.731
```

**Agent C Scoring:**
```
Portfolio Value Before: $100,000
Portfolio Value After: $102,800
24h Return: +2.8%
Sharpe Ratio: 1.85
→ Performance added to history
→ RAID score updated: 0.856 → 0.861
```

---

## Key Metrics to Display

### Real-time Dashboard (Console)
```
╔════════════════════════════════════════════════════════════════════╗
║           MULTI-AGENT INVESTMENT SYSTEM - Cycle 47                 ║
╠════════════════════════════════════════════════════════════════════╣
║ AGENT A - Sentiment Digestion                                     ║
║   Sentiment: +0.82 (BULLISH) | Volatility: 0.15 (STABLE)         ║
║   Trend: ACCELERATING | Confidence: 0.89                          ║
║   Trace: trace_agentA_20260325_100000_047                         ║
╠────────────────────────────────────────────────────────────────────╣
║ AGENT B - Investment Suggestion                                    ║
║   BTC Prediction: $72,100 (+3.0%) | Confidence: 0.78             ║
║   Risk Level: MODERATE                                             ║
║   RAID Score: 0.731 (Accuracy: 67% | MAE: 2.1%)                  ║
║   Trace: trace_agentB_20260325_100005_047                         ║
╠────────────────────────────────────────────────────────────────────╣
║ AGENT C - Portfolio Management                                     ║
║   Action: BUY BTC $15k | Target Alloc: 60%                        ║
║   Expected Return: +2.8% | Risk: 0.45                             ║
║   RAID Score: 0.861 (Sharpe: 1.85 | Return: +12.5%)              ║
║   Trace: trace_agentC_20260325_100010_047                         ║
╠────────────────────────────────────────────────────────────────────╣
║ PORTFOLIO STATUS                                                   ║
║   Total Value: $102,800 | 24h Change: +2.8%                       ║
║   BTC: 60% ($61,680) | SUI: 30% ($30,840) | USDC: 10% ($10,280)  ║
╠────────────────────────────────────────────────────────────────────╣
║ SUI BLOCKCHAIN STATUS                                              ║
║   Agent Addresses: A(0xabc..), B(0xdef..), C(0x123..)            ║
║   Last Tx: Portfolio rebalance (0x456..) | Block: 12,847,392     ║
║   RAID Scores Stored On-Chain: B(0.731), C(0.861)                ║
╚════════════════════════════════════════════════════════════════════╝
```

---

## Success Criteria

- [ ] Agent A generates sentiment signals from news
- [ ] Agent B consumes Agent A signals and predicts BTC price
- [ ] Agent C consumes Agent B + mock ETH signals and allocates portfolio
- [ ] All agents generate reasoning traces with Glass Box Protocol
- [ ] Agent B prediction accuracy tracked and RAID score calculated
- [ ] Agent C portfolio performance tracked and RAID score calculated
- [ ] Multi-agent pipeline runs end-to-end for 20+ cycles
- [ ] Performance metrics display correctly
- [ ] All traces saved to appropriate directories

---

## Future Enhancements

1. **Real Data Integration:**
   - Twitter API for real-time sentiment
   - CoinGecko for actual BTC/ETH prices
   - Real ETH prediction model (not mocked)

2. **Advanced Scoring:**
   - Agent A: Sentiment prediction accuracy (if prices move as sentiment suggests)
   - Agent B: Bayesian prediction intervals
   - Agent C: Risk-adjusted metrics (Sortino, Calmar ratios)

3. **Agent Communication:**
   - Feedback loops (Agent C can influence Agent B's risk tolerance)
   - Multi-agent coordination (consensus mechanisms)

4. **Production Deployment:**
   - Deploy to Glass Box Protocol testnet
   - Real DA layer submission (Celestia/EigenDA)
   - Public reputation API queries
