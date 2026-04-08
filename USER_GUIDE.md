# Glass Box Protocol - User Guide

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js (for frontend visualization)
- Git

### Installation

```bash
# Clone repository
git clone <repository-url>
cd Glassbox-demo/demo

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp config/.env.example config/.env
# Edit config/.env with your Walrus testnet credentials
```

### Running the Demo

#### 1. Initialize Database
```bash
cd demo
python3 scripts/populate_mocked_accounts.py
```

#### 2. Run End-to-End Pipeline
```bash
python3 scripts/E2E_complete_pipeline.py
```

This pipeline:
- Fetches 5 Bitcoin news articles
- Generates sentiment analysis (Agent A)
- Fetches BTC price data
- Creates investment predictions (Agent B)
- Generates portfolio recommendations (Agent C)
- Publishes all signals to Walrus testnet
- Stores metadata in SQLite database

#### 3. Launch Visualization
```bash
cd ../visualization/api
python3 server.py
```

Open browser: http://localhost:8080

### Architecture Overview

```
┌─────────────────┐
│  Data Sources   │  CryptoPanic, CoinGecko
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Agent A        │  Sentiment Analysis
│  (NewsSignal)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Agent B        │  Investment Prediction
│  (PriceSignal)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Agent C        │  Portfolio Management
│  (Insight)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Walrus Storage │  Decentralized blob storage
└─────────────────┘
```

### Key Concepts

**Signals**: Atomic units of data published to Walrus
- `NewsSignal`: News articles
- `PriceSignal`: Market prices
- `InsightSignal`: Agent-generated insights

**Reasoning Ledger**: Step-by-step audit trail of agent decisions
- Stored on Walrus alongside signals
- Viewable in UI by clicking agent nodes

**Signal Registry**: SQLite database tracking all signals
- Maps signal IDs to Walrus blob IDs
- Enables efficient querying and indexing

### Database Schema

```sql
signals           -- Signal metadata index
agents_run        -- Agent execution logs
reasoning_traces  -- Reasoning ledger references
mocked_accounts   -- Demo wallet addresses
```

### Configuration

Edit `demo/config/.env`:

```bash
# Walrus Testnet
WALRUS_ENABLED=true
WALRUS_PUBLISHER_URL=https://publisher.walrus-testnet.walrus.space
WALRUS_AGGREGATOR_URL=https://aggregator.walrus-testnet.walrus.space

# Data Sources
CRYPTOPANIC_API_KEY=your_key_here
COINGECKO_API_KEY=your_key_here
```

### Common Tasks

#### Clean Database
```bash
cd demo
rm -f data/glassbox.db
python3 scripts/populate_mocked_accounts.py
```

#### Download Reasoning Traces
```bash
python3 scripts/download_reasoning_ledgers.py
```

#### View Database Statistics
```bash
sqlite3 data/glassbox.db "SELECT signal_type, COUNT(*) FROM signals GROUP BY signal_type;"
```

### Project Structure

```
demo/
├── config/               # Environment configuration
├── data/                 # SQLite database, Walrus blobs
├── scripts/              # Pipeline scripts
├── src/
│   ├── agents/           # Agent A, B, C implementations
│   ├── data_clients/     # CryptoPanic, CoinGecko clients
│   ├── storage/          # Walrus client, database
│   ├── reasoning_ledger/ # Reasoning trace generation
│   └── demo/             # Signal registry, publisher
└── tests/                # Unit tests

visualization/
├── api/                  # Flask API server
├── static/               # Frontend UI
│   ├── css/
│   ├── js/
│   └── index.html
└── templates/
```

### Troubleshooting

**UI shows old data**
- Hard refresh browser (Cmd+Shift+R or Ctrl+Shift+R)
- Restart visualization server

**Walrus upload fails**
- Check internet connection
- Verify Walrus testnet is online
- Set `WALRUS_ENABLED=false` for local testing

**Database locked**
- Close all running scripts
- Delete `data/glassbox.db-journal` if exists

### API Endpoints

```
GET  /api/signals              - List all signals
GET  /api/signals/{id}/full    - Get signal data from Walrus
GET  /api/owners               - List owner addresses
GET  /api/agents               - List all agents
GET  /api/agents/{id}/traces   - Get reasoning traces
GET  /api/stats                - System statistics
```

### Development Workflow

1. Modify agent logic in `src/agents/`
2. Run pipeline: `python3 scripts/E2E_complete_pipeline.py`
3. Check results in UI at http://localhost:8080
4. View reasoning traces by clicking agent nodes
5. Inspect database: `sqlite3 data/glassbox.db`

### Performance Tips

- Signals are cached by modification time
- Use `limit` parameter in database queries
- Walrus blobs cached for 15 minutes
- Agent executions run sequentially

### Production Deployment

For production use:
1. Replace SQLite with PostgreSQL
2. Deploy smart contracts to SUI mainnet
3. Use production WSGI server (Gunicorn)
4. Enable HTTPS for API endpoints
5. Implement proper authentication

### Support

- Documentation: `documents/tech-design.md`
- Issues: GitHub Issues
- Design: `demo/DESIGN.md`

---

**Version**: v0.7
**Last Updated**: April 2026
