"""
Mock SUI Blockchain Integration
Simulates SUI blockchain operations locally for testing without real network connection
"""

import json
import hashlib
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


class MockSUIAddress:
    """Generate and validate mock SUI addresses (0x format)"""

    @staticmethod
    def generate() -> str:
        """Generate a mock SUI address"""
        # SUI addresses are 32-byte hex strings with 0x prefix
        random_bytes = secrets.token_bytes(32)
        return "0x" + random_bytes.hex()

    @staticmethod
    def is_valid(address: str) -> bool:
        """Validate SUI address format"""
        if not address.startswith("0x"):
            return False
        try:
            int(address[2:], 16)
            return len(address) == 66  # 0x + 64 hex chars
        except ValueError:
            return False


class MockSUITransaction:
    """Mock SUI transaction"""

    def __init__(self, tx_type: str, sender: str, data: Dict):
        self.tx_type = tx_type
        self.sender = sender
        self.data = data
        self.timestamp = datetime.now(timezone.utc)
        self.tx_hash = self._generate_hash()
        self.block_number = None  # Set when added to block
        self.gas_used = self._calculate_gas()
        self.status = "pending"

    def _generate_hash(self) -> str:
        """Generate transaction hash"""
        tx_data = json.dumps({
            "type": self.tx_type,
            "sender": self.sender,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }, sort_keys=True)

        hash_obj = hashlib.sha256(tx_data.encode())
        return "0x" + hash_obj.hexdigest()

    def _calculate_gas(self) -> float:
        """Calculate mock gas cost in SUI"""
        # Base cost + data size cost
        data_size = len(json.dumps(self.data))
        base_cost = 0.001
        size_cost = (data_size / 1000) * 0.0001
        return round(base_cost + size_cost, 6)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "tx_hash": self.tx_hash,
            "tx_type": self.tx_type,
            "sender": self.sender,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "block_number": self.block_number,
            "gas_used": self.gas_used,
            "status": self.status
        }


class MockSUIBlockchain:
    """
    Mock SUI blockchain that simulates on-chain operations locally

    Features:
    - Agent identity registration (SUI addresses)
    - Transaction submission and storage
    - RAID score storage on-chain
    - Portfolio state commitments
    - Block creation and history
    """

    def __init__(self, storage_dir: str = None):
        """
        Initialize mock SUI blockchain

        Args:
            storage_dir: Directory to persist blockchain state
        """
        if storage_dir is None:
            storage_dir = Path(__file__).parent.parent.parent / "output" / "blockchain"

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Blockchain state
        self.current_block_number = 12_847_000  # Start from realistic block number
        self.blocks = []
        self.pending_transactions = []
        self.agent_registry = {}  # agent_id -> SUI address
        self.raid_scores = {}  # agent_id -> score history
        self.portfolio_states = {}  # agent_id -> portfolio state

        # Load persisted state if exists
        self._load_state()

        print(f"[Mock SUI Blockchain] Initialized at block {self.current_block_number:,}")

    def register_agent(self, agent_name: str) -> str:
        """
        Register an agent and assign SUI address

        Args:
            agent_name: Agent identifier (e.g., "agent_a", "agent_b")

        Returns:
            str: Assigned SUI address
        """
        if agent_name in self.agent_registry:
            return self.agent_registry[agent_name]

        sui_address = MockSUIAddress.generate()
        self.agent_registry[agent_name] = sui_address

        # Create registration transaction
        tx = MockSUITransaction(
            tx_type="agent_registration",
            sender=sui_address,
            data={
                "agent_name": agent_name,
                "registered_at": datetime.now(timezone.utc).isoformat()
            }
        )

        self.pending_transactions.append(tx)
        self._create_block_if_needed()

        print(f"[Mock SUI] Registered {agent_name}: {sui_address[:10]}...")

        return sui_address

    def submit_raid_score(self, agent_name: str, raid_score: float, metrics: Dict) -> str:
        """
        Submit RAID score to blockchain

        Args:
            agent_name: Agent identifier
            raid_score: RAID score (0.0 to 1.0)
            metrics: Score breakdown

        Returns:
            str: Transaction hash
        """
        if agent_name not in self.agent_registry:
            raise ValueError(f"Agent {agent_name} not registered")

        sender = self.agent_registry[agent_name]

        # Create RAID score transaction
        tx = MockSUITransaction(
            tx_type="raid_score_update",
            sender=sender,
            data={
                "agent_name": agent_name,
                "raid_score": raid_score,
                "metrics": metrics,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

        self.pending_transactions.append(tx)

        # Store in local state
        if agent_name not in self.raid_scores:
            self.raid_scores[agent_name] = []

        self.raid_scores[agent_name].append({
            "score": raid_score,
            "metrics": metrics,
            "tx_hash": tx.tx_hash,
            "timestamp": tx.timestamp
        })

        self._create_block_if_needed()

        return tx.tx_hash

    def submit_portfolio_rebalance(
        self,
        agent_name: str,
        actions: List[Dict],
        portfolio_value: float
    ) -> str:
        """
        Submit portfolio rebalancing transaction

        Args:
            agent_name: Agent identifier
            actions: List of rebalancing actions
            portfolio_value: Total portfolio value in USD

        Returns:
            str: Transaction hash
        """
        if agent_name not in self.agent_registry:
            raise ValueError(f"Agent {agent_name} not registered")

        sender = self.agent_registry[agent_name]

        # Create rebalancing transaction
        tx = MockSUITransaction(
            tx_type="portfolio_rebalance",
            sender=sender,
            data={
                "agent_name": agent_name,
                "actions": actions,
                "portfolio_value": portfolio_value,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

        self.pending_transactions.append(tx)

        # Store portfolio state
        self.portfolio_states[agent_name] = {
            "actions": actions,
            "value": portfolio_value,
            "tx_hash": tx.tx_hash,
            "timestamp": tx.timestamp
        }

        self._create_block_if_needed()

        return tx.tx_hash

    def submit_trace_commitment(
        self,
        agent_name: str,
        trace_id: str,
        merkle_root: str
    ) -> str:
        """
        Submit reasoning trace commitment (hash) to blockchain

        Args:
            agent_name: Agent identifier
            trace_id: Trace identifier
            merkle_root: Merkle root of trace data

        Returns:
            str: Transaction hash
        """
        if agent_name not in self.agent_registry:
            raise ValueError(f"Agent {agent_name} not registered")

        sender = self.agent_registry[agent_name]

        # Create trace commitment transaction
        tx = MockSUITransaction(
            tx_type="trace_commitment",
            sender=sender,
            data={
                "agent_name": agent_name,
                "trace_id": trace_id,
                "merkle_root": merkle_root,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

        self.pending_transactions.append(tx)
        self._create_block_if_needed()

        return tx.tx_hash

    def _create_block_if_needed(self):
        """Create new block if pending transactions exist"""
        if not self.pending_transactions:
            return

        # Create block every 3 transactions or force create
        if len(self.pending_transactions) >= 3:
            self._create_block()

    def _create_block(self):
        """Create new block with pending transactions"""
        if not self.pending_transactions:
            return

        self.current_block_number += 1

        # Mark transactions as confirmed
        for tx in self.pending_transactions:
            tx.block_number = self.current_block_number
            tx.status = "confirmed"

        block = {
            "block_number": self.current_block_number,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "transactions": [tx.to_dict() for tx in self.pending_transactions],
            "tx_count": len(self.pending_transactions)
        }

        self.blocks.append(block)
        self.pending_transactions = []

        # Persist state
        self._save_state()

    def force_create_block(self):
        """Force creation of block with pending transactions"""
        self._create_block()

    def get_agent_address(self, agent_name: str) -> Optional[str]:
        """Get SUI address for agent"""
        return self.agent_registry.get(agent_name)

    def get_raid_score(self, agent_name: str) -> Optional[Dict]:
        """Get latest RAID score for agent"""
        if agent_name not in self.raid_scores or not self.raid_scores[agent_name]:
            return None
        return self.raid_scores[agent_name][-1]

    def get_portfolio_state(self, agent_name: str) -> Optional[Dict]:
        """Get latest portfolio state for agent"""
        return self.portfolio_states.get(agent_name)

    def get_transaction(self, tx_hash: str) -> Optional[Dict]:
        """Get transaction by hash"""
        # Search in confirmed blocks
        for block in self.blocks:
            for tx in block["transactions"]:
                if tx["tx_hash"] == tx_hash:
                    return tx

        # Search in pending
        for tx in self.pending_transactions:
            if tx.tx_hash == tx_hash:
                return tx.to_dict()

        return None

    def get_latest_block(self) -> Optional[Dict]:
        """Get latest block"""
        return self.blocks[-1] if self.blocks else None

    def get_blockchain_status(self) -> Dict:
        """Get blockchain status summary"""
        total_txs = sum(block["tx_count"] for block in self.blocks)

        return {
            "current_block": self.current_block_number,
            "total_blocks": len(self.blocks),
            "total_transactions": total_txs,
            "pending_transactions": len(self.pending_transactions),
            "registered_agents": len(self.agent_registry),
            "agents": {
                name: {
                    "address": addr[:10] + "...",
                    "raid_score": self.get_raid_score(name)["score"] if self.get_raid_score(name) else None
                }
                for name, addr in self.agent_registry.items()
            }
        }

    def _save_state(self):
        """Persist blockchain state to disk"""
        state_file = self.storage_dir / "blockchain_state.json"

        state = {
            "current_block_number": self.current_block_number,
            "blocks": self.blocks[-100:],  # Keep last 100 blocks
            "agent_registry": self.agent_registry,
            "raid_scores": {
                agent: scores[-10:] if scores else []  # Keep last 10 scores
                for agent, scores in self.raid_scores.items()
            },
            "portfolio_states": self.portfolio_states
        }

        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2, default=str)

    def _load_state(self):
        """Load persisted blockchain state"""
        state_file = self.storage_dir / "blockchain_state.json"

        if not state_file.exists():
            return

        try:
            with open(state_file, 'r') as f:
                state = json.load(f)

            self.current_block_number = state.get("current_block_number", 12_847_000)
            self.blocks = state.get("blocks", [])
            self.agent_registry = state.get("agent_registry", {})

            # Reconstruct raid_scores with datetime objects
            self.raid_scores = {}
            for agent, scores in state.get("raid_scores", {}).items():
                self.raid_scores[agent] = [
                    {**s, "timestamp": datetime.fromisoformat(s["timestamp"]) if isinstance(s["timestamp"], str) else s["timestamp"]}
                    for s in scores
                ]

            self.portfolio_states = state.get("portfolio_states", {})

            print(f"[Mock SUI] Loaded state: Block {self.current_block_number:,}, {len(self.agent_registry)} agents")

        except Exception as e:
            print(f"[Mock SUI] Warning: Could not load state: {e}")


if __name__ == "__main__":
    # Test mock SUI blockchain
    print("\nMock SUI Blockchain - Test Output\n")
    print("=" * 80)

    # Initialize blockchain
    blockchain = MockSUIBlockchain()

    print("\n1. Registering agents...")
    agent_a_addr = blockchain.register_agent("agent_a")
    agent_b_addr = blockchain.register_agent("agent_b")
    agent_c_addr = blockchain.register_agent("agent_c")

    print(f"   Agent A: {agent_a_addr}")
    print(f"   Agent B: {agent_b_addr}")
    print(f"   Agent C: {agent_c_addr}")

    print("\n2. Submitting RAID scores...")
    tx1 = blockchain.submit_raid_score(
        "agent_b",
        raid_score=0.731,
        metrics={
            "accuracy": 0.67,
            "mae": 0.021,
            "direction_accuracy": 0.71
        }
    )
    print(f"   Agent B RAID score tx: {tx1[:16]}...")

    tx2 = blockchain.submit_raid_score(
        "agent_c",
        raid_score=0.856,
        metrics={
            "sharpe_ratio": 1.82,
            "return_pct": 12.5,
            "max_drawdown": 3.2,
            "win_rate": 0.73
        }
    )
    print(f"   Agent C RAID score tx: {tx2[:16]}...")

    print("\n3. Submitting portfolio rebalance...")
    tx3 = blockchain.submit_portfolio_rebalance(
        "agent_c",
        actions=[
            {"asset": "BTC", "action": "BUY", "amount_usd": 15000},
            {"asset": "SUI", "action": "HOLD", "amount_usd": 0},
            {"asset": "USDC", "action": "SELL", "amount_usd": -15000}
        ],
        portfolio_value=102800
    )
    print(f"   Portfolio rebalance tx: {tx3[:16]}...")

    # Force block creation
    blockchain.force_create_block()

    print("\n4. Blockchain Status:")
    status = blockchain.get_blockchain_status()
    print(f"   Current Block: {status['current_block']:,}")
    print(f"   Total Transactions: {status['total_transactions']}")
    print(f"   Registered Agents: {status['registered_agents']}")

    print("\n5. Agent Details:")
    for agent, details in status['agents'].items():
        print(f"   {agent}: {details['address']} | RAID: {details['raid_score']}")

    print("\n6. Latest Block:")
    latest = blockchain.get_latest_block()
    if latest:
        print(f"   Block #{latest['block_number']:,}")
        print(f"   Transactions: {latest['tx_count']}")
        print(f"   Time: {latest['timestamp']}")

    print("\n" + "=" * 80)
    print("Test completed successfully!")
    print(f"State saved to: {blockchain.storage_dir}")
