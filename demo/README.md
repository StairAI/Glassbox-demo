# Bitcoin Investment Agent Demo

A demonstration of the **Glass Box Protocol** with a simple Bitcoin investment agent that analyzes news sentiment, generates trading signals, and submits immutable reasoning traces to the protocol.

---

## Overview

This demo showcases the core concepts of the Glass Box Protocol:

1. **Text-Based State Machine**: Agent maintains readable state optimized for LLM processing
2. **Reasoning Trace Generation**: Every decision is logged with behavioral breakdown (Observing → Planning → Reasoning → Acting)
3. **Glass Box SDK Integration**: Traces submitted to mock protocol (simulates real DA layer)
4. **Encrypted Alpha Protection**: Context and execution graphs are encrypted before submission
5. **RAID Scoring**: Agent reputation based on reasoning patterns and outcomes

---

## Architecture

```
News Fetcher → Sentiment Analyzer → Bitcoin Agent → Signal Generator
                                          ↓
                                 Reasoning Trace Generator
                                          ↓
                                   Glass Box SDK
                                          ↓
                          DA Layer (Mock - Local Files)
```

**Components:**

- `data_sources/news_fetcher.py`: Mock Bitcoin news generator
- `data_sources/sentiment_analyzer.py`: Keyword-based sentiment analysis
- `agent/state_machine.py`: Text-based state machine
- `agent/bitcoin_agent.py`: Main decision-making agent
- `sdk/trace_generator.py`: Reasoning trace formatter
- `sdk/glassbox_sdk.py`: Protocol SDK (mock implementation)
- `runner.py`: Main execution loop

---

## Quick Start

### Prerequisites

- Python 3.8+
- No external dependencies (uses standard library only)

### Installation

```bash
cd demo
```

### Run the Demo

```bash
python3 src/runner.py
```

The agent will:
1. Fetch Bitcoin news every 10 seconds (mock data)
2. Analyze sentiment using keyword matching
3. Update internal state machine
4. Generate trading signals when thresholds met (|sentiment| > 0.5 AND confidence > 0.7)
5. Submit reasoning traces to Glass Box Protocol
6. Run for 20 cycles (~3 minutes) then stop

### Sample Output

```
[Cycle 1] -----------------------------------------------------------------
📰 NEWS: Bitcoin surges past $70k as institutions adopt crypto...
📊 SENTIMENT: +0.85 (BULLISH) | Confidence: 0.88
🚨 SIGNAL GENERATED: LONG BTC
   Entry: $70,245 | SL: $66,733 | TP: $75,865
   Position: full position (100%) | R:R = 1.6
   Signal ID: sig_btc_long_20260325_155000
✅ TRACE: trace_595f0bEb_20260325T155000_001
📈 STATE: BTC $70,245 | Market: +0.85 | Trend: RISING
```

---

## Output Files

After running the demo, check these directories:

### 1. Reasoning Traces (`output/traces/`)

JSON files conforming to the Universal Reasoning Ledger schema:

```json
{
  "Header": {
    "agent_id": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "epoch_timestamp": "2026-03-25T15:50:00Z",
    "attestation_type": "framework_v1"
  },
  "Trigger_Event": {
    "source": "news_stream",
    "payload": { ... }
  },
  "Context_Snapshot": "[ENCRYPTED:119 bytes]",
  "Execution_Graph": "[ENCRYPTED:550 bytes]",
  "Terminal_Action": {
    "type": "signal_generated",
    "payload": { ... }
  }
}
```

### 2. Agent State (`output/state/agent_state.txt`)

Human-readable state machine:

```
=== AGENT STATE ===
Timestamp: 2026-03-25T15:50:00Z
Market Sentiment: +0.67 (BULLISH)
Signal Strength: BULLISH
Confidence: 0.82
Current Position: MONITORING

=== NEWS STREAM ===
Last 5 Headlines:
  [1] BULLISH (+0.85) - Bitcoin surges past $70k as institutions adopt crypto
  [2] BEARISH (-0.42) - SEC increases scrutiny on cryptocurrency exchanges
  [3] BULLISH (+0.78) - Major bank announces Bitcoin custody services...
  ...

Average Sentiment: +0.67
Sentiment Trend: RISING

=== SIGNAL HISTORY ===
[2026-03-25T15:50:00Z] LONG signal @ $70,245 (SL: $66,733, TP: $75,865)
```

---

## Configuration

Edit `src/runner.py` to customize:

```python
# Main execution parameters
AGENT_ID = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
CYCLE_INTERVAL = 10  # seconds between news cycles
MAX_CYCLES = 20      # total cycles (None = unlimited)
```

Edit `src/agent/bitcoin_agent.py` for trading logic:

```python
# Signal generation thresholds
def should_generate_signal(self):
    return abs(self.market_sentiment) > 0.5 and self.confidence > 0.7

# Risk management
stop_loss_pct = 0.95  # -5%
take_profit_pct = 1.08  # +8%
```

---

## Key Concepts Demonstrated

### 1. Text-Based State Machine

Unlike traditional binary state machines, the agent maintains plaintext state that LLMs can directly read and reason about:

```python
state = AgentState()
state.update_from_news(news, sentiment_analysis, news_history)
if state.should_generate_signal():
    signal = agent.generate_signal()
```

### 2. Reasoning Trace Lifecycle

Every decision follows the Glass Box behavioral taxonomy:

1. **Observing**: Ingest external data
2. **Planning**: Outline analysis steps
3. **Reasoning**: Execute decision logic
4. **Acting**: Generate signal or take action
5. **Self_Refining**: (Optional) Error correction

### 3. Confidence Calibration

Signals only generated when both conditions met:
- **Sentiment threshold**: |market_sentiment| > 0.5
- **Confidence threshold**: confidence > 0.7

This prevents low-quality signals from polluting the agent's RAID score.

### 4. Encrypted Alpha Protection

Proprietary logic is encrypted before submission:
- `Context_Snapshot`: Agent's internal state
- `Execution_Graph`: Detailed reasoning steps

Only `Header`, `Trigger_Event`, and `Terminal_Action` remain public.

---

## Testing Individual Components

### Test News Fetcher

```bash
cd src/data_sources
python3 news_fetcher.py
```

### Test Sentiment Analyzer

```bash
cd src/data_sources
python3 sentiment_analyzer.py
```

### Test State Machine

```bash
cd src/agent
python3 state_machine.py
```

### Test Bitcoin Agent

```bash
cd src/agent
python3 bitcoin_agent.py
```

### Test SDK

```bash
cd src/sdk
python3 trace_generator.py
```

---

## Architecture Highlights

### Multi-Stream State Management

The agent accumulates sentiment from multiple news items:

```python
# Rolling average of last 5 news items
recent_sentiments = [item['sentiment'] for item in news_history[-5:]]
avg_sentiment = sum(recent_sentiments) / len(recent_sentiments)
```

### Position Sizing

Confidence-based position sizing:

- Confidence > 0.9: Full position (100%)
- Confidence > 0.8: Large position (75%)
- Confidence > 0.7: Medium position (50%)
- Confidence ≤ 0.7: Small position (25%)

### Risk Management

Every signal includes:
- **Stop-loss**: -5% for longs, +5% for shorts
- **Take-profit**: +8% for longs, -8% for shorts
- **Risk/Reward Ratio**: Automatically calculated

---

## Future Enhancements

This demo can be extended to include:

1. **Real Data Sources**:
   - Twitter API for live sentiment
   - CoinGecko/CoinMarketCap for prices
   - Glassnode for on-chain metrics

2. **Actuarial Performance Tracking**:
   - 24-hour outcome validation
   - Win rate calculation
   - RAID score updates based on real PnL

3. **Multiple Data Streams**:
   - Social sentiment (Twitter, Reddit)
   - On-chain metrics (exchange flows, whale movements)
   - Technical indicators (RSI, MACD)

4. **Real Glass Box Protocol Integration**:
   - Connect to testnet/mainnet
   - Submit to Celestia/EigenDA
   - Query reputation API

5. **Advanced Features**:
   - Blind Sequencer for work attestation
   - zkTLS proofs of API calls
   - Cross-stream validation logic

---

## Troubleshooting

### Permission Errors

If you see file permission errors:

```bash
chmod +x src/runner.py
```

### Import Errors

Make sure you're running from the `demo/` directory:

```bash
cd /path/to/Glassbox-demo/demo
python3 src/runner.py
```

### Clean Output Files

To reset the demo:

```bash
rm -rf output/traces/*.json
rm -f output/state/agent_state.txt
```

---

## Learn More

- **Technical Design**: See `../documents/tech-design.md` for full protocol specification
- **Whitepaper**: See `../documents/whitepaper.md` for conceptual overview
- **Crypto Adaptation**: See `../documents/CRYPTO_ADAPTATION_REPORT.md` for crypto-specific considerations

---

## License

This demo is part of the Glass Box Protocol project.

---

## Support

For questions or issues:
- Create an issue on GitHub: https://github.com/StairAI/Glassbox-demo
- Review the technical design document: `documents/tech-design.md`

---

**Built with Glass Box Protocol v1.1**
