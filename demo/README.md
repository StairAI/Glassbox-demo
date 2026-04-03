# Multi-Agent Investment System Demo

A demonstration of the **Glass Box Protocol** with a sophisticated 3-agent investment system (Sentiment → Investment → Portfolio) that uses **100% real data sources** and submits immutable reasoning traces to the Walrus DA layer on SUI Testnet.

---

## Overview

This demo showcases a production-quality implementation with:

1. **Real Data Integration**: CoinGecko prices, CryptoPanic news, SUI Testnet, Walrus DA
2. **Multi-Agent Pipeline**: Agent A (Sentiment) → Agent B (Predictions) → Agent C (Portfolio)
3. **Real RAID Scoring**: 24-hour validation with actual price data
4. **Immutable Reasoning Traces**: Stored on Walrus DA, referenced on SUI blockchain
5. **Zero Cost**: All services use free tiers ($0 total!)

**See [DESIGN.md](DESIGN.md) for complete system specification (all 3 docs merged!).**

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install Walrus CLI
curl https://install.walrus.xyz | sh

# 3. Setup environment
cp config/.env.example config/.env
# Edit config/.env with your API tokens

# 4. Get SUI testnet tokens
# Visit: https://faucet.sui.io/

# 5. Run the pipeline
python src/orchestrator/runner.py
```

**For detailed setup instructions, see [DESIGN.md](DESIGN.md).**

---

## Documentation

📘 **[DESIGN.md](DESIGN.md)** - Complete system specification with:
- Architecture diagrams
- Real data integration details (CoinGecko, SUI, Walrus)
- Agent specifications (A, B, C)
- Implementation phases (15-19 hours)
- Cost breakdown ($0 total!)
- Directory structure
- Success criteria

---

## Key Features

✅ **100% Real Data** - CoinGecko API, CryptoPanic, SUI Testnet, Walrus DA
✅ **Zero Cost** - All services use free tiers
✅ **Real Blockchain** - SUI Testnet with actual transactions
✅ **Real Validation** - 24-hour price predictions verified
✅ **Immutable Traces** - Walrus DA blob storage

---

## License

This demo is part of the Glass Box Protocol project.
