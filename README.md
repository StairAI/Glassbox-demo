# Glass Box Protocol

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A decentralized trust and reputation layer for autonomous AI agents in finance, enabling transparent reasoning and verifiable decision-making.

## Overview

The Glass Box Protocol provides a framework for AI agents to operate with complete transparency, where every decision is cryptographically traceable back to its reasoning process and data sources. Unlike traditional "black box" AI systems, Glass Box enables:

- **Transparent Reasoning**: Every agent decision generates a detailed reasoning trace
- **RAID (Reasoning As Identity)**: Reputation tied to reasoning patterns, not agent identity
- **Multi-Stream Analysis**: Real-time correlation of multiple data sources
- **Verifiable Decisions**: Cryptographically signed execution paths with confidence scoring

## Live Demo

An interactive demonstration showcasing political risk analysis for Bitcoin price prediction:

🚀 **[View Demo](http://localhost:5174)** (run locally)

### Demo Features

- **Real-time Data Streams**: Mock tweet feeds from Elon Musk and Donald Trump
- **Reasoning Agent**: Professional quantitative trading analysis with:
  - Multi-stream correlation and divergence detection
  - Confidence-weighted position sizing
  - Risk management with specific price levels (entry, stop-loss, take-profit)
  - Cross-stream validation logic
- **Trading Signals**: Threshold-based signal generation (75% confidence, 0.5 sentiment strength)
- **Interactive Visualization**: React Flow graph with animated data flow

### Running the Demo

```bash
cd demo/frontend
npm install
npm run dev
```

The demo will be available at `http://localhost:5173` (or 5174 if 5173 is in use).

## Key Concepts

### 1. Reasoning Traces

Every agent action generates a structured reasoning trace containing:
- **Input Analysis**: Data source evaluation and sentiment scoring
- **Cross-Stream Correlation**: Multi-source validation and conflict detection
- **Risk Assessment**: Political risk and volatility analysis
- **Decision Logic**: Threshold analysis and execution criteria
- **Position Management**: Confidence-weighted sizing and risk parameters

Example reasoning output:
```
📊 MARKET SIGNAL ANALYSIS: New input from Elon Musk (high-influence tech leader)
✓ Cross-stream validation: Both sources bullish - high confidence correlation
💭 Weighted sentiment integration (70% influence): 0.300 → 0.452 (+0.152)
Risk environment: MODERATE - moderate exposure acceptable
Confidence score: 82.5% (threshold: 75%) | Sentiment strength: 0.52 (threshold: 0.50)
✅ EXECUTION CRITERIA MET - BULLISH SIGNAL CONFIRMED
Position sizing: 75% position (confidence-weighted) | Entry: $68,450
Risk management: Stop-loss $65,027 | Take-profit $73,926
```

### 2. State Machine Architecture

Agents maintain text-based state representations optimized for LLM processing:

```python
class AgentState:
    """Text-based state machine for LLM agents"""
    timestamp: datetime
    market_sentiment: float  # -1 to +1
    political_risk: 'LOW' | 'MODERATE' | 'HIGH'
    signal_strength: 'BEARISH' | 'NEUTRAL' | 'BULLISH'
    confidence: float  # 0 to 1
    stream_states: dict  # Per-source signal tracking
    reasoning_history: list  # Recent decision log
```

### 3. RAID Score

Reputation is calculated based on:
- **Reasoning Accuracy** (25%): Logical consistency and determinism
- **Data Provenance** (25%): Source verification and hallucination detection
- **Actuarial Performance** (20%): Real-world outcome tracking
- **Adherence to Framework** (10%): Rule compliance and risk management
- **State Continuity** (20%): Coherent state transitions across streams

## Documentation

- **[Whitepaper](documents/whitepaper.md)**: Complete protocol specification
- **[Technical Design](documents/tech-design.md)**: Architecture and implementation details
- **[Frontend Spec](demo/design/frontend-spec.md)**: UI/UX design documentation

## Architecture

### Layer 1: Identity Layer
- Bring Your Own Identity (BYOI) - any cryptographic identifier
- RAID (Reasoning As Identity) - reputation tied to reasoning patterns
- Flexible identity management across model upgrades

### Layer 2: Runtime Attestation
**Phase 1 (MVP)**: Framework-level attestation via official SDK
**Phase 2 (Roadmap)**:
- zkTLS (Zero-Knowledge TLS) proofs
- TEE (Trusted Execution Environments)
- Optimistic fraud proofs with slashing

### Data Layer
- **Reasoning Ledger**: Universal schema for agent computation
- **Data Availability**: Celestia/EigenDA for immutable trace storage
- **Smart Contracts**: Base/Arbitrum/Solana for registry and settlement

## Technology Stack

### Frontend Demo
- **React** + **TypeScript** + **Vite**
- **React Flow** - Graph visualization with custom nodes
- **Zustand** - Lightweight state management
- **Tailwind CSS** - Utility-first styling with cyberpunk theme

### Core Components
- Mock data generators with sentiment analysis
- Multi-stream reasoning engine with confidence calibration
- Real-time edge animations showing data flow
- Professional quantitative trading logic

## Project Structure

```
glassbox-demo/
├── documents/
│   ├── whitepaper.md           # Protocol specification
│   └── tech-design.md          # Technical architecture
├── demo/
│   ├── design/
│   │   └── frontend-spec.md    # UI/UX specification
│   └── frontend/               # Interactive React demo
│       ├── src/
│       │   ├── components/     # React Flow nodes and UI
│       │   ├── data/           # Mock generators and reasoning engine
│       │   ├── store/          # Zustand state management
│       │   └── types/          # TypeScript definitions
│       └── package.json
└── README.md
```

## Development

### Prerequisites
- Node.js 18+ (demo requires 20+ for Vite)
- npm or yarn

### Setup

```bash
# Clone the repository
git clone https://github.com/StairAI/Glassbox-demo.git
cd Glassbox-demo

# Install demo dependencies
cd demo/frontend
npm install

# Start development server
npm run dev
```

### Building for Production

```bash
cd demo/frontend
npm run build
npm run preview
```

## Demo Controls

- **Play/Pause**: Control automatic tweet generation
- **Speed**: Adjust tweet generation rate (1x, 2x, 4x)
- **Reset**: Clear all data and restart demo

## Reasoning Engine

The demo implements a sophisticated reasoning engine with:

### Input Processing
- Sentiment analysis with reach weighting
- Author influence factors (Elon: 70%, Trump: 50%)
- Bitcoin mention detection

### Multi-Stream Analysis
- Cross-stream validation (alignment boost: +0.2 confidence)
- Divergence detection (conflict penalty: -0.15 confidence)
- Sentiment integration with weighted moving average

### Risk Management
- Political risk calculation based on sentiment volatility
- Position sizing: 50% / 75% / Full based on confidence
- Stop-loss: 5% from entry | Take-profit: 8% from entry

### Signal Generation
Signals only generated when:
- Confidence > 75%
- |Sentiment| > 0.5

## Contributing

This is a demonstration project. For production implementation or contributions, please contact the team.

## License

MIT License - see LICENSE file for details

## Contact

For questions about the Glass Box Protocol:
- Website: [Coming Soon]
- Twitter: [@GlassBoxAI](https://twitter.com/GlassBoxAI)
- Discord: [Join Community](https://discord.gg/glassbox)

---

**Built with transparency. Powered by reasoning.**

*🤖 Demo generated with Claude Code*
