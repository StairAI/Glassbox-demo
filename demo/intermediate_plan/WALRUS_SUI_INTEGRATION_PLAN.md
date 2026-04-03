# Walrus & SUI Testnet Integration Plan

**Date:** 2026-03-28
**Phase:** Phase 1 Extension / Phase 2 Preparation

---

## Overview

Integration plan for connecting the Glass Box Protocol to:
1. **Walrus** - Decentralized data availability layer for storing reasoning traces
2. **SUI Testnet** - Blockchain layer for storing RAID scores and validation results

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Agent Pipeline                          │
│  (Agent A → Agent B → Agent C)                              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├─────────────────────────────────────────┐
                 │                                         │
                 ▼                                         ▼
    ┌────────────────────────┐              ┌────────────────────────┐
    │   Walrus DA Layer      │              │   SUI Testnet          │
    │                        │              │                        │
    │  • Reasoning traces    │              │  • RAID scores         │
    │  • Decision logs       │              │  • Predictions         │
    │  • Signal data         │              │  • Validation results  │
    │  • Immutable storage   │              │  • Smart contracts     │
    └────────────────────────┘              └────────────────────────┘
```

---

## Integration 1: Walrus (Data Availability)

### Purpose

Store **immutable reasoning traces** from agents:
- Agent A: News analysis + sentiment scoring
- Agent B: Investment signal generation
- Agent C: Portfolio rebalancing decisions

### What to Store

**Example Trace Structure:**
```json
{
  "trace_id": "trace_20260328_agent_a_001",
  "agent": "agent_a_sentiment",
  "timestamp": "2026-03-28T10:30:00Z",
  "input_data": {
    "news_articles": [
      {"title": "Bitcoin hits $66k", "sentiment": 0.75},
      {"title": "ETH upgrade delayed", "sentiment": -0.3}
    ],
    "prices": {
      "BTC": 66036.00,
      "ETH": 1984.73
    }
  },
  "reasoning_process": {
    "step_1": "Analyzed 10 news articles",
    "step_2": "Calculated weighted sentiment: BTC=0.65, ETH=0.45",
    "step_3": "Applied momentum indicators",
    "step_4": "Generated signals"
  },
  "output_signal": {
    "BTC": {"action": "buy", "confidence": 0.75, "amount": 0.1},
    "ETH": {"action": "hold", "confidence": 0.55, "amount": 0}
  },
  "metadata": {
    "model_version": "v0.1",
    "execution_time_ms": 245
  }
}
```

### Implementation Plan

**Step 1: Install Walrus Python SDK**
```bash
pip install walrus-python
```

**Step 2: Create Walrus Client**
```python
# src/data_clients/walrus_client.py
from walrus import WalrusClient
import json
from typing import Dict, Optional

class WalrusDAClient:
    """
    Walrus Data Availability Client.

    Stores reasoning traces on Walrus decentralized storage.
    """

    def __init__(self, epochs: int = 10):
        """
        Initialize Walrus client.

        Args:
            epochs: Number of epochs to store data (default: 10)
        """
        # Walrus testnet endpoints
        self.publisher_url = "https://publisher.walrus-testnet.walrus.space"
        self.aggregator_url = "https://aggregator.walrus-testnet.walrus.space"

        self.client = WalrusClient(
            publisher_base_url=self.publisher_url,
            aggregator_base_url=self.aggregator_url
        )
        self.epochs = epochs

    def store_trace(self, trace_data: Dict) -> str:
        """
        Store reasoning trace on Walrus.

        Args:
            trace_data: Trace data dict

        Returns:
            Blob ID (unique identifier for retrieval)
        """
        # Convert to JSON bytes
        trace_json = json.dumps(trace_data, indent=2)
        trace_bytes = trace_json.encode('utf-8')

        # Store on Walrus
        result = self.client.store(
            data=trace_bytes,
            epochs=self.epochs,
            deletable=False  # Immutable
        )

        return result.blob_id

    def retrieve_trace(self, blob_id: str) -> Dict:
        """
        Retrieve trace from Walrus.

        Args:
            blob_id: Blob ID from store_trace

        Returns:
            Trace data dict
        """
        # Retrieve from Walrus
        data_bytes = self.client.read(blob_id)

        # Parse JSON
        trace_json = data_bytes.decode('utf-8')
        return json.loads(trace_json)
```

**Step 3: Create Trace Manager**
```python
# src/core/trace_manager.py
from datetime import datetime
from typing import Dict, Optional
import logging
from ..data_clients.walrus_client import WalrusDAClient

logger = logging.getLogger(__name__)

class TraceManager:
    """
    Manages reasoning trace creation and storage.
    """

    def __init__(self, walrus_client: WalrusDAClient):
        self.walrus = walrus_client

    def create_trace(
        self,
        agent_name: str,
        input_data: Dict,
        reasoning_process: Dict,
        output_signal: Dict,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Create and store reasoning trace.

        Returns:
            Blob ID from Walrus
        """
        trace_id = f"trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{agent_name}"

        trace_data = {
            "trace_id": trace_id,
            "agent": agent_name,
            "timestamp": datetime.now().isoformat(),
            "input_data": input_data,
            "reasoning_process": reasoning_process,
            "output_signal": output_signal,
            "metadata": metadata or {}
        }

        # Store on Walrus
        blob_id = self.walrus.store_trace(trace_data)

        logger.info(f"Stored trace {trace_id} on Walrus: {blob_id}")

        return blob_id
```

### Walrus Configuration

Add to `.env`:
```bash
# Walrus DA Configuration
WALRUS_PUBLISHER_URL=https://publisher.walrus-testnet.walrus.space
WALRUS_AGGREGATOR_URL=https://aggregator.walrus-testnet.walrus.space
WALRUS_EPOCHS=10
```

---

## Integration 2: SUI Testnet (Blockchain)

### Purpose

Store **on-chain RAID scores** and **prediction validation**:
- Agent reputation scores
- Prediction outcomes (success/failure)
- Portfolio performance metrics
- Transparent, verifiable history

### What to Store

**Example On-Chain Data:**
```json
{
  "agent_id": "agent_a_sentiment",
  "raid_score": 0.75,
  "predictions": [
    {
      "prediction_id": "pred_001",
      "asset": "BTC",
      "predicted_price": 68000,
      "actual_price": 67500,
      "accuracy": 0.99,
      "timestamp": "2026-03-28T10:30:00Z"
    }
  ],
  "total_predictions": 150,
  "successful_predictions": 112,
  "success_rate": 0.747
}
```

### Implementation Plan

**Step 1: Install PySui**
```bash
pip install pysui
```

**Step 2: Create SUI Client**
```python
# src/data_clients/sui_client.py
from pysui import SuiClient, SuiConfig
from pysui.sui.sui_types import SuiAddress
from pysui.sui.sui_txn import SyncTransaction
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class SuiTestnetClient:
    """
    SUI Testnet Client for RAID scores.

    Handles wallet management and transaction execution.
    """

    def __init__(self, private_key: Optional[str] = None):
        """
        Initialize SUI testnet client.

        Args:
            private_key: Optional private key for wallet (will generate if not provided)
        """
        # Initialize testnet config
        self.config = SuiConfig.testnet_config()
        self.client = SuiClient(self.config)

        # Initialize wallet
        if private_key:
            self.wallet = self.config.active_address
        else:
            # Generate new wallet for testnet
            self.wallet = self._create_wallet()

    def _create_wallet(self) -> SuiAddress:
        """Create new wallet address."""
        # Get new address from config
        address = self.config.active_address
        logger.info(f"Created SUI wallet: {address}")
        return address

    def get_balance(self) -> int:
        """Get wallet balance in MIST (1 SUI = 1_000_000_000 MIST)."""
        result = self.client.get_balance(self.wallet)
        return int(result.total_balance)

    def request_faucet(self) -> bool:
        """
        Request testnet SUI from faucet.

        Returns:
            True if successful
        """
        try:
            result = self.client.request_faucet(self.wallet)
            logger.info(f"Faucet request successful: {result}")
            return True
        except Exception as e:
            logger.error(f"Faucet request failed: {e}")
            return False

    def store_raid_score(
        self,
        agent_id: str,
        raid_score: float,
        prediction_count: int,
        success_rate: float
    ) -> str:
        """
        Store RAID score on-chain.

        Args:
            agent_id: Agent identifier
            raid_score: RAID score (0.0 - 1.0)
            prediction_count: Total predictions made
            success_rate: Prediction success rate

        Returns:
            Transaction digest
        """
        # Create transaction
        txn = SyncTransaction(client=self.client, initial_sender=self.wallet)

        # Store data as Move call (requires deployed smart contract)
        # For now, we'll use object creation as placeholder

        # Execute transaction
        result = txn.execute(gas_budget=10_000_000)  # 0.01 SUI

        logger.info(f"Stored RAID score for {agent_id}: {result.digest}")
        return result.digest
```

**Step 3: Create RAID Score Manager**
```python
# src/core/raid_manager.py
from typing import Dict, List
import logging
from datetime import datetime
from ..data_clients.sui_client import SuiTestnetClient

logger = logging.getLogger(__name__)

class RAIDScoreManager:
    """
    Manages RAID (Reputation, Accuracy, Impact, Diversity) scores.
    """

    def __init__(self, sui_client: SuiTestnetClient):
        self.sui = sui_client
        self.scores = {}  # In-memory cache

    def calculate_raid_score(
        self,
        agent_id: str,
        predictions: List[Dict]
    ) -> float:
        """
        Calculate RAID score for agent.

        Components:
        - Reputation: Historical success rate
        - Accuracy: Prediction accuracy
        - Impact: Size of correct predictions
        - Diversity: Coverage of different assets

        Returns:
            RAID score (0.0 - 1.0)
        """
        if not predictions:
            return 0.0

        # Calculate components
        accuracy = self._calculate_accuracy(predictions)
        impact = self._calculate_impact(predictions)
        diversity = self._calculate_diversity(predictions)
        reputation = accuracy  # Simplified for now

        # Weighted average
        raid_score = (
            0.4 * reputation +
            0.3 * accuracy +
            0.2 * impact +
            0.1 * diversity
        )

        return round(raid_score, 3)

    def _calculate_accuracy(self, predictions: List[Dict]) -> float:
        """Calculate prediction accuracy."""
        if not predictions:
            return 0.0

        successful = sum(1 for p in predictions if p.get("success", False))
        return successful / len(predictions)

    def _calculate_impact(self, predictions: List[Dict]) -> float:
        """Calculate prediction impact (normalized)."""
        if not predictions:
            return 0.0

        total_impact = sum(p.get("impact", 0) for p in predictions)
        max_impact = len(predictions) * 100  # Assuming max impact per prediction is 100
        return min(total_impact / max_impact, 1.0)

    def _calculate_diversity(self, predictions: List[Dict]) -> float:
        """Calculate asset diversity."""
        if not predictions:
            return 0.0

        assets = set(p.get("asset") for p in predictions if p.get("asset"))
        max_assets = 10  # Maximum expected assets
        return min(len(assets) / max_assets, 1.0)

    def store_on_chain(self, agent_id: str, raid_score: float) -> str:
        """
        Store RAID score on SUI blockchain.

        Returns:
            Transaction digest
        """
        prediction_count = len(self.scores.get(agent_id, {}).get("predictions", []))
        success_rate = self._calculate_accuracy(
            self.scores.get(agent_id, {}).get("predictions", [])
        )

        # Store on-chain
        digest = self.sui.store_raid_score(
            agent_id=agent_id,
            raid_score=raid_score,
            prediction_count=prediction_count,
            success_rate=success_rate
        )

        logger.info(f"Stored RAID score on-chain: {agent_id} = {raid_score}")

        return digest
```

### SUI Configuration

Add to `.env`:
```bash
# SUI Testnet Configuration
SUI_TESTNET_RPC=https://fullnode.testnet.sui.io:443
SUI_WALLET_PRIVATE_KEY=  # Will be generated on first run
```

---

## Integration Workflow

### Agent Execution Flow with Walrus + SUI

```python
# Example: Agent A with full integration
from src.data_sources import CoinGeckoSource, CryptoPanicSource
from src.data_clients import WalrusDAClient, SuiTestnetClient
from src.core import TraceManager, RAIDScoreManager

# 1. Initialize data sources
price_source = CoinGeckoSource()
news_source = CryptoPanicSource(api_token)

# 2. Initialize blockchain clients
walrus = WalrusDAClient(epochs=10)
sui = SuiTestnetClient()

# 3. Initialize managers
trace_mgr = TraceManager(walrus)
raid_mgr = RAIDScoreManager(sui)

# 4. Fetch data
prices = price_source.get_prices(["BTC", "ETH", "SUI"])
news = news_source.fetch_news(currencies=["BTC", "ETH", "SUI"], limit=10)

# 5. Agent A processes data
input_data = {
    "prices": {symbol: float(data.price_usd) for symbol, data in prices.items()},
    "news": [{"title": a.title, "kind": a.kind} for a in news]
}

# Agent reasoning (simplified)
reasoning_process = {
    "step_1": f"Analyzed {len(news)} news articles",
    "step_2": "Calculated sentiment scores",
    "step_3": "Generated investment signals"
}

output_signal = {
    "BTC": {"action": "buy", "confidence": 0.75},
    "ETH": {"action": "hold", "confidence": 0.55}
}

# 6. Store reasoning trace on Walrus
blob_id = trace_mgr.create_trace(
    agent_name="agent_a_sentiment",
    input_data=input_data,
    reasoning_process=reasoning_process,
    output_signal=output_signal,
    metadata={"version": "v0.1"}
)

print(f"Trace stored on Walrus: {blob_id}")

# 7. Later: Validate prediction and update RAID score
prediction = {
    "asset": "BTC",
    "predicted_action": "buy",
    "success": True,  # Validated later
    "impact": 85
}

# Calculate and store RAID score
raid_score = raid_mgr.calculate_raid_score("agent_a_sentiment", [prediction])
tx_digest = raid_mgr.store_on_chain("agent_a_sentiment", raid_score)

print(f"RAID score stored on SUI: {tx_digest}")
```

---

## File Structure

```
src/
├── data_clients/
│   ├── walrus_client.py          # NEW: Walrus DA client
│   └── sui_client.py             # NEW: SUI testnet client
│
├── core/
│   ├── trace_manager.py          # NEW: Reasoning trace manager
│   └── raid_manager.py           # NEW: RAID score calculator
│
└── blockchain/                    # NEW: Smart contracts (future)
    └── raid_contract.move        # Move smart contract for RAID
```

---

## Dependencies

Add to `requirements.txt`:
```
walrus-python>=0.1.0
pysui>=0.65.0
```

---

## Setup Steps

### 1. Install Dependencies
```bash
pip install walrus-python pysui
```

### 2. Setup SUI Wallet
```bash
# Request testnet SUI from faucet
python scripts/setup_sui_wallet.py
```

### 3. Test Walrus Connection
```bash
# Test storing and retrieving data
python scripts/test_walrus.py
```

### 4. Deploy RAID Smart Contract (Optional)
```bash
# Deploy Move contract to SUI testnet
sui move publish --network testnet
```

---

## Cost Analysis

### Walrus Testnet
- **Storage Cost**: Free on testnet
- **Duration**: 10 epochs (~configurable)
- **Mainnet Cost**: ~0.001 SUI per KB per epoch

### SUI Testnet
- **Gas Cost**: Free (use faucet)
- **Transaction Cost**: ~0.001-0.01 SUI per transaction
- **Mainnet Cost**: Variable based on network

**Total Demo Cost**: **$0** (using testnets)

---

## Benefits

### Walrus Benefits
✅ **Immutable**: Reasoning traces cannot be altered
✅ **Verifiable**: Anyone can verify agent decisions
✅ **Transparent**: Full audit trail
✅ **Decentralized**: No single point of failure

### SUI Benefits
✅ **On-Chain Reputation**: RAID scores visible to all
✅ **Fast**: <1 second finality
✅ **Low Cost**: Minimal gas fees
✅ **Smart Contracts**: Programmable validation logic

---

## Next Steps

1. ✅ Create Walrus client implementation
2. ✅ Create SUI client implementation
3. ⏭️ Create trace manager
4. ⏭️ Create RAID manager
5. ⏭️ Integrate with Agent A
6. ⏭️ Test full pipeline
7. ⏭️ Deploy RAID smart contract (optional)

---

## References

- **Walrus Docs**: https://docs.wal.app/
- **Walrus Python SDK**: https://github.com/standard-crypto/walrus-python
- **PySui Docs**: https://pysui.readthedocs.io/
- **SUI Testnet**: https://docs.sui.io/
- **Move Language**: https://move-language.github.io/move/

---

**Ready to implement Walrus + SUI integration!** 🚀
