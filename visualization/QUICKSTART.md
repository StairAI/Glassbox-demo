# Glass Box Explorer - Quick Start Guide

## Overview

The Glass Box Explorer is a blockchain explorer-style web interface for visualizing agent reasoning and data processing in the Glass Box Protocol demo. It provides **complete transparency** by pulling data directly from the SUI blockchain and Walrus decentralized storage.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Browser (Frontend)                     │
│  • Processor Output Tab (view triggers from SUI)         │
│  • Agents Tab (view reasoning traces from Walrus)        │
└────────────────────┬─────────────────────────────────────┘
                     │
                     │ HTTP REST API
                     ▼
┌──────────────────────────────────────────────────────────┐
│              Flask API Server (Backend)                   │
│  • /api/triggers - Get triggers from SUI                 │
│  • /api/agents - Get agent list                          │
│  • /api/agents/{id}/traces - Get reasoning from Walrus   │
└────────────────────┬─────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
┌──────────────┐ ┌────────┐ ┌──────────┐
│TriggerRegistry│ │ Walrus │ │ActivityDB│
│  (SUI Meta)   │ │(Full   │ │ (Logs)   │
│               │ │ Data)  │ │          │
└──────────────┘ └────────┘ └──────────┘
```

## Prerequisites

1. **Run batch processing** to generate data:
   ```bash
   cd ../demo
   python scripts/batch_process_btc_sui.py
   ```

2. **Install Python dependencies**:
   ```bash
   pip install flask flask-cors
   ```

## Quick Start (2 Methods)

### Method 1: Automatic (Recommended)

```bash
cd visualization
python api/server.py
```

Then open your browser to: **http://localhost:8000**

### Method 2: Using Run Script

```bash
cd visualization
python run.py
```

This will automatically:
- Check dependencies
- Verify demo data exists
- Start API server
- Open browser to http://localhost:8000

## Features

### 📊 Processor Output Tab

**What you see:**
- All triggers published to SUI blockchain
- News triggers (100+ articles from CryptoPanic)
- Signal triggers (Agent A sentiment outputs)

**What you can do:**
- Filter by trigger type (news/signal)
- Search by ID, producer, or token
- Click "View Full Data from Walrus" to see complete articles
- See metadata: timestamps, confidence scores, data sizes

**Data source:**
- Metadata: `demo/data/trigger_registry.json` (simulates SUI blockchain)
- Full data: Walrus testnet via blob IDs

### 🤖 Agents Tab

**What you see:**
- All agents in the system (Agent A, B, C)
- Execution statistics (run count, avg confidence)
- Agent descriptions and capabilities

**What you can do:**
- Click any agent to view complete reasoning traces
- See step-by-step reasoning from Walrus
- View LLM prompts and responses
- Inspect confidence scores and execution times

**Data source:**
- Reasoning traces pulled directly from Walrus decentralized storage
- Each trace includes:
  - Input data and triggers
  - Reasoning steps with descriptions
  - LLM provider/model metadata
  - Output confidence scores

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Get All Triggers
```bash
# All triggers
curl http://localhost:8000/api/triggers

# Filter by type
curl http://localhost:8000/api/triggers?type=news
curl http://localhost:8000/api/triggers?type=signal

# Limit results
curl http://localhost:8000/api/triggers?limit=10
```

### Get Full Trigger Data from Walrus
```bash
curl http://localhost:8000/api/triggers/trigger_000000/full
```

### Get All Agents
```bash
curl http://localhost:8000/api/agents
```

### Get Agent Reasoning Traces
```bash
curl http://localhost:8000/api/agents/agent_a/traces
```

### System Statistics
```bash
curl http://localhost:8000/api/stats
```

## Example Workflow

### 1. View Latest News

1. Start server: `python api/server.py`
2. Open http://localhost:8000
3. You'll see "Processor Output" tab by default
4. Filter by "News Triggers"
5. Click any trigger
6. Click "View Full Data from Walrus"
7. See all 100 articles fetched from CryptoPanic

### 2. Inspect Agent Reasoning

1. Click "Agents" tab
2. Click "Agent A - Sentiment Analysis"
3. See all reasoning traces
4. Each trace shows:
   - What input the agent received
   - How it analyzed the data (step-by-step)
   - What sentiment scores it generated
   - Confidence levels and reasoning

### 3. Verify Transparency

All data is **verifiable on-chain**:

```bash
# View trigger registry (simulates SUI blockchain)
cat ../demo/data/trigger_registry.json

# View activity database
sqlite3 ../demo/data/activity.db "SELECT * FROM triggers LIMIT 5"

# Reasoning traces are stored on Walrus testnet
# Each trace has a blob_id that can be verified independently
```

## File Structure

```
visualization/
├── index.html                  # Main UI (2 tabs)
├── static/
│   ├── css/
│   │   └── style.css           # Blockchain explorer design
│   └── js/
│       └── main.js             # Frontend logic (fetches API)
├── api/
│   └── server.py               # Flask REST API
├── README.md                   # Full documentation
├── QUICKSTART.md               # This file
└── run.py                      # Launcher script
```

## Troubleshooting

### "No triggers found"
Run batch processing first:
```bash
cd ../demo
python scripts/batch_process_btc_sui.py
```

### "Error loading triggers"
Check that trigger registry exists:
```bash
ls ../demo/data/trigger_registry.json
```

### "Flask not found"
Install dependencies:
```bash
pip install flask flask-cors
```

### Port 8000 already in use
Change port in `api/server.py` line 325:
```python
app.run(host='0.0.0.0', port=8001, debug=True)  # Use 8001 instead
```

### CORS errors
Make sure you're accessing via http://localhost:8000 (not file://)

## Next Steps

1. **Run batch processing** to populate with fresh data
2. **Start the server** and explore the UI
3. **Click through agents** to see reasoning traces
4. **Verify data** by checking Walrus blob IDs
5. **Extend** by adding new agents or data sources

## Technical Details

### How Data Flows

1. **Batch Script** → CryptoPanic API → Walrus → SUI
2. **Agent A** → Reads from SUI → Processes → Outputs to SUI
3. **Explorer** → Reads from SUI → Fetches from Walrus → Displays

### Why This Design?

- **SUI**: Lightweight metadata, queryable, on-chain
- **Walrus**: Large data (articles, traces), cheap storage
- **Local DB**: Activity logs, analytics, caching

### Transparency Guarantees

Every reasoning trace includes:
- ✅ Walrus blob ID (verifiable)
- ✅ Data hash (integrity check)
- ✅ Timestamp (audit trail)
- ✅ Agent version (reproducibility)
- ✅ LLM model (transparency)
- ✅ Complete reasoning steps (explainability)

## Demo URLs

- **Main UI**: http://localhost:8000
- **API Health**: http://localhost:8000/api/health
- **All Triggers**: http://localhost:8000/api/triggers
- **All Agents**: http://localhost:8000/api/agents

Enjoy exploring the Glass Box Protocol! 🔍
