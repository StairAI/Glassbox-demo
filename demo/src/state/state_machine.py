"""
Generic Text-Based State Machine for LLM Agents

Optimized for LLM reasoning over state transitions using plaintext representation
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path
import json


class StateMachine:
    """
    Text-based state machine for agent decision-making

    Design principles:
    1. Human-readable state representation (plaintext)
    2. Clear state transition rules
    3. Automatic state history tracking
    4. LLM-optimized state descriptions
    """

    def __init__(
        self,
        agent_id: str,
        initial_state: str,
        valid_states: List[str],
        transition_rules: Dict[str, List[str]],
        state_dir: Optional[Path] = None
    ):
        """
        Initialize state machine

        Args:
            agent_id: Agent identifier
            initial_state: Starting state
            valid_states: List of all valid states
            transition_rules: Dict mapping state -> list of allowed next states
            state_dir: Directory to persist state
        """
        self.agent_id = agent_id
        self.current_state = initial_state
        self.valid_states = valid_states
        self.transition_rules = transition_rules

        # Persistence (must be set before _record_state)
        if state_dir is None:
            state_dir = Path(__file__).parent.parent.parent / "output" / "state"
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # State history
        self.state_history = []

        # Metadata
        self.metadata = {}  # Store arbitrary context per state

        # Record initial state (after state_dir is set)
        self._record_state(initial_state, "initialized")

    def transition(self, new_state: str, reason: str, metadata: Optional[Dict] = None) -> bool:
        """
        Attempt state transition

        Args:
            new_state: Target state
            reason: Human-readable reason for transition
            metadata: Optional metadata to attach to this state

        Returns:
            bool: True if transition successful, False if invalid
        """
        # Validate new state
        if new_state not in self.valid_states:
            print(f"[{self.agent_id}] Invalid state: {new_state}")
            return False

        # Check transition rules
        allowed_next_states = self.transition_rules.get(self.current_state, [])
        if new_state not in allowed_next_states and new_state != self.current_state:
            print(f"[{self.agent_id}] Invalid transition: {self.current_state} -> {new_state}")
            print(f"  Allowed transitions from {self.current_state}: {allowed_next_states}")
            return False

        # Record transition
        old_state = self.current_state
        self.current_state = new_state
        self._record_state(new_state, reason, metadata)

        print(f"[{self.agent_id}] State: {old_state} -> {new_state} ({reason})")

        return True

    def get_current_state(self) -> str:
        """Get current state"""
        return self.current_state

    def get_state_description(self) -> str:
        """
        Get human-readable state description (for LLM consumption)

        Returns:
            str: Plaintext description of current state and history
        """
        description = f"=== {self.agent_id.upper()} STATE ===\n"
        description += f"Current State: {self.current_state}\n"

        if self.metadata:
            description += "\nState Metadata:\n"
            for key, value in self.metadata.items():
                description += f"  {key}: {value}\n"

        description += f"\nState History (last 5 transitions):\n"
        for record in self.state_history[-5:]:
            ts = record["timestamp"]
            state = record["state"]
            reason = record["reason"]
            description += f"  [{ts}] {state}: {reason}\n"

        return description

    def can_transition_to(self, target_state: str) -> bool:
        """
        Check if transition to target state is allowed

        Args:
            target_state: Proposed next state

        Returns:
            bool: True if transition is allowed
        """
        if target_state not in self.valid_states:
            return False

        allowed_next_states = self.transition_rules.get(self.current_state, [])
        return target_state in allowed_next_states or target_state == self.current_state

    def get_allowed_transitions(self) -> List[str]:
        """Get list of allowed transitions from current state"""
        return self.transition_rules.get(self.current_state, [])

    def update_metadata(self, key: str, value: Any):
        """Update metadata for current state"""
        self.metadata[key] = value

    def _record_state(self, state: str, reason: str, metadata: Optional[Dict] = None):
        """Record state transition in history"""
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "state": state,
            "reason": reason,
            "metadata": metadata or {}
        }

        self.state_history.append(record)

        # Update metadata
        if metadata:
            self.metadata.update(metadata)

        # Persist state
        self._save_state()

    def _save_state(self):
        """Persist state to disk"""
        state_file = self.state_dir / f"{self.agent_id}_state.json"

        state_data = {
            "agent_id": self.agent_id,
            "current_state": self.current_state,
            "metadata": self.metadata,
            "state_history": self.state_history[-100:]  # Keep last 100 transitions
        }

        with open(state_file, 'w') as f:
            json.dump(state_data, f, indent=2)

    def load_state(self):
        """Load persisted state from disk"""
        state_file = self.state_dir / f"{self.agent_id}_state.json"

        if not state_file.exists():
            return

        try:
            with open(state_file, 'r') as f:
                state_data = json.load(f)

            self.current_state = state_data.get("current_state", self.current_state)
            self.metadata = state_data.get("metadata", {})
            self.state_history = state_data.get("state_history", [])

            print(f"[{self.agent_id}] Loaded state: {self.current_state}")

        except Exception as e:
            print(f"[{self.agent_id}] Warning: Could not load state: {e}")


# Example state machines for each agent type

def create_agent_a_state_machine(agent_id: str = "agent_a") -> StateMachine:
    """Create state machine for Agent A (Sentiment Digestion)"""

    states = [
        "IDLE",           # Waiting for news
        "COLLECTING",     # Gathering news articles
        "ANALYZING",      # Processing sentiment
        "PUBLISHING"      # Emitting sentiment signal
    ]

    transitions = {
        "IDLE": ["COLLECTING"],
        "COLLECTING": ["ANALYZING"],
        "ANALYZING": ["PUBLISHING"],
        "PUBLISHING": ["IDLE"]
    }

    return StateMachine(
        agent_id=agent_id,
        initial_state="IDLE",
        valid_states=states,
        transition_rules=transitions
    )


def create_agent_b_state_machine(agent_id: str = "agent_b") -> StateMachine:
    """Create state machine for Agent B (Investment Suggestion)"""

    states = [
        "MONITORING",        # Waiting for signals
        "ANALYZING",         # Processing sentiment + price data
        "PREDICTING",        # Generating BTC prediction
        "VALIDATING",        # Checking previous predictions
        "PUBLISHING"         # Emitting prediction + RAID score
    ]

    transitions = {
        "MONITORING": ["ANALYZING"],
        "ANALYZING": ["PREDICTING"],
        "PREDICTING": ["VALIDATING"],
        "VALIDATING": ["PUBLISHING"],
        "PUBLISHING": ["MONITORING"]
    }

    return StateMachine(
        agent_id=agent_id,
        initial_state="MONITORING",
        valid_states=states,
        transition_rules=transitions
    )


def create_agent_c_state_machine(agent_id: str = "agent_c") -> StateMachine:
    """Create state machine for Agent C (Portfolio Management)"""

    states = [
        "MONITORING",        # Waiting for predictions
        "ANALYZING",         # Processing BTC/SUI predictions
        "ALLOCATING",        # Determining portfolio allocation
        "REBALANCING",       # Executing trades on SUI blockchain
        "TRACKING",          # Updating RAID score
        "PUBLISHING"         # Emitting portfolio signal
    ]

    transitions = {
        "MONITORING": ["ANALYZING"],
        "ANALYZING": ["ALLOCATING"],
        "ALLOCATING": ["REBALANCING"],
        "REBALANCING": ["TRACKING"],
        "TRACKING": ["PUBLISHING"],
        "PUBLISHING": ["MONITORING"]
    }

    return StateMachine(
        agent_id=agent_id,
        initial_state="MONITORING",
        valid_states=states,
        transition_rules=transitions
    )


if __name__ == "__main__":
    # Test state machines
    print("\nState Machine - Test Output\n")
    print("=" * 80)

    print("\n1. Testing Agent A State Machine:")
    agent_a = create_agent_a_state_machine()
    print(agent_a.get_state_description())

    agent_a.transition("COLLECTING", "Received news update")
    agent_a.update_metadata("news_count", 5)
    agent_a.transition("ANALYZING", "Processing 5 news articles")
    agent_a.transition("PUBLISHING", "Sentiment analysis complete")

    print("\nAgent A Final State:")
    print(agent_a.get_state_description())

    print("\n" + "-" * 80)

    print("\n2. Testing Agent B State Machine:")
    agent_b = create_agent_b_state_machine()
    print(f"Current State: {agent_b.get_current_state()}")
    print(f"Allowed Transitions: {agent_b.get_allowed_transitions()}")

    agent_b.transition("ANALYZING", "Received sentiment signal (+0.7)")
    agent_b.transition("PREDICTING", "Generating 24h BTC prediction")
    agent_b.update_metadata("predicted_price", 71500)
    agent_b.update_metadata("confidence", 0.78)
    agent_b.transition("VALIDATING", "Checking previous prediction accuracy")
    agent_b.update_metadata("previous_mae", 0.024)
    agent_b.transition("PUBLISHING", "Prediction ready with RAID score 0.731")

    print("\nAgent B Final State:")
    print(agent_b.get_state_description())

    print("\n" + "-" * 80)

    print("\n3. Testing Agent C State Machine:")
    agent_c = create_agent_c_state_machine()

    agent_c.transition("ANALYZING", "Received BTC and SUI predictions")
    agent_c.transition("ALLOCATING", "Calculating optimal portfolio")
    agent_c.update_metadata("btc_allocation_pct", 55)
    agent_c.update_metadata("sui_allocation_pct", 20)
    agent_c.update_metadata("usdc_allocation_pct", 25)
    agent_c.transition("REBALANCING", "Submitting transactions to SUI chain")
    agent_c.transition("TRACKING", "Portfolio rebalanced, updating performance")
    agent_c.update_metadata("sharpe_ratio", 1.82)
    agent_c.transition("PUBLISHING", "Portfolio update complete with RAID score 0.856")

    print("\nAgent C Final State:")
    print(agent_c.get_state_description())

    print("\n" + "-" * 80)

    print("\n4. Testing Invalid Transitions:")
    # Try invalid transition
    result = agent_a.transition("MONITORING", "Invalid jump")
    print(f"Invalid transition result: {result}")

    # Try valid self-transition
    result = agent_a.transition("PUBLISHING", "Staying in current state")
    print(f"Self-transition result: {result}")

    print("\n" + "=" * 80)
    print("Test completed successfully!")
