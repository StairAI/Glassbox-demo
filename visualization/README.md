# Glass Box Explorer

A blockchain explorer-style visualization for the Glass Box Protocol demo, providing real-time transparency into agent reasoning and data processing.

## Features

### 📊 Processor Output Tab
- View all triggers published to SUI blockchain
- See news triggers (CryptoPanic data) and signal triggers (agent outputs)
- Fetch full data from Walrus decentralized storage
- Real-time statistics and filtering

### 🤖 Agents Tab
- Browse all agents in the system
- View execution statistics (total runs, average confidence)
- Click on any agent to see their complete reasoning traces
- Reasoning traces pulled directly from Walrus blockchain storage

## Architecture

```
┌─────────────────┐
│   Frontend      │  ← HTML/CSS/JS (index.html)
│   (Browser)     │
└────────┬────────┘
         │
         │ HTTP
         ▼
┌─────────────────┐
│   API Server    │  ← Flask REST API (api/server.py)
│   (Python)      │
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
         ▼                 ▼
┌─────────────────┐  ┌─────────────────┐
│  TriggerRegistry│  │  Walrus Client  │
│  (SUI Metadata) │  │  (Full Data)    │
└─────────────────┘  └─────────────────┘
```

## Setup

### Prerequisites

```bash
# Install Python dependencies
pip install flask flask-cors

# Ensure demo environment is set up
cd ../demo
pip install -r requirements.txt
```

### Running the Explorer

#### Option 1: Quick Start (Run Script)

```bash
cd visualization
python run.py
```

Then open http://localhost:8000 in your browser.

#### Option 2: Manual Start

```bash
# Terminal 1: Start API server
cd visualization/api
python server.py

# Terminal 2: Open frontend
# Open visualization/index.html in your browser
# Or use a simple HTTP server:
cd visualization
python -m http.server 3000
# Then visit http://localhost:3000
```

## API Endpoints

### Get All Triggers
```bash
GET http://localhost:8000/api/triggers
GET http://localhost:8000/api/triggers?type=news
GET http://localhost:8000/api/triggers?type=signal&limit=50
```

### Get Full Trigger Data
```bash
GET http://localhost:8000/api/triggers/{trigger_id}/full
```

### Get All Agents
```bash
GET http://localhost:8000/api/agents
```

### Get Agent Reasoning Traces
```bash
GET http://localhost:8000/api/agents/{agent_id}/traces
```

### System Statistics
```bash
GET http://localhost:8000/api/stats
```

### Health Check
```bash
GET http://localhost:8000/api/health
```

## Data Sources

### 1. SUI Blockchain (via TriggerRegistry)
- **What**: Trigger metadata (IDs, timestamps, producers)
- **Where**: `demo/data/trigger_registry.json`
- **Why**: Lightweight, queryable metadata on-chain

### 2. Walrus Decentralized Storage
- **What**: Full data (news articles, reasoning traces)
- **Where**: Walrus testnet (https://aggregator.walrus-testnet.walrus.space)
- **Why**: Large data that's too expensive for blockchain

### 3. Local Database
- **What**: Activity logs (API calls, processing history)
- **Where**: `demo/data/activity.db`
- **Why**: Query optimization and analytics

## Example Usage

### View Latest News Triggers

1. Open http://localhost:8000
2. Click "Processor Output" tab
3. Filter by "News Triggers"
4. Click "View Full Data from Walrus" to see all articles

### Inspect Agent Reasoning

1. Open http://localhost:8000
2. Click "Agents" tab
3. Click on "Agent A - Sentiment Analysis"
4. View complete reasoning traces including:
   - Step-by-step reasoning
   - LLM prompts and responses
   - Confidence scores
   - Execution times

## Development

### Frontend Structure
```
visualization/
├── index.html              # Main UI
├── static/
│   ├── css/
│   │   └── style.css       # Blockchain explorer-style design
│   └── js/
│       └── main.js         # Frontend logic
```

### Backend Structure
```
visualization/
└── api/
    └── server.py           # Flask REST API
```

### Adding New Features

#### Add New Tab
1. Add tab button in `index.html`
2. Add tab panel in `index.html`
3. Add tab switching logic in `static/js/main.js`
4. Create API endpoint in `api/server.py` if needed

#### Add New API Endpoint
1. Add route in `api/server.py`
2. Fetch data from TriggerRegistry, Walrus, or DB
3. Return JSON response
4. Add frontend fetch call in `static/js/main.js`

## Troubleshooting

### API Server Not Starting
- Check Python dependencies: `pip install flask flask-cors`
- Ensure demo data exists: Run `cd ../demo && python scripts/batch_process_btc_sui.py`

### No Triggers Showing
- Run batch processing first: `cd ../demo && python scripts/batch_process_btc_sui.py`
- Check trigger registry: `cat ../demo/data/trigger_registry.json`

### CORS Errors
- Make sure API server is running on localhost:8000
- Check CORS is enabled in `api/server.py`

## Future Enhancements

- [ ] Real-time WebSocket updates
- [ ] Advanced filtering and search
- [ ] Graph visualization of agent chains
- [ ] Performance metrics dashboard
- [ ] Export data to CSV/JSON
- [ ] Dark/light theme toggle
- [ ] Mobile responsive design improvements

## License

MIT License - See main project LICENSE
