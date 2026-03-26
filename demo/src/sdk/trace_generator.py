"""
Reasoning Trace Generator
Captures agent reasoning and formats for Glass Box Protocol
Based on tech-design.md Section 13.2
"""

import json
from datetime import datetime, timezone
from typing import Dict, Optional
from glassbox_sdk import GlassBoxSDK


class ReasoningTraceGenerator:
    """Generate Glass Box reasoning traces from trading agent decisions"""

    def __init__(self, agent_id: str, sdk_client: GlassBoxSDK):
        """
        Initialize trace generator

        Args:
            agent_id: Agent's RAID address (0x...)
            sdk_client: GlassBoxSDK instance
        """
        self.agent_id = agent_id
        self.sdk = sdk_client
        self.current_trace = None

    def start_trace(self, trigger_event: dict):
        """
        Initialize a new reasoning trace

        Args:
            trigger_event: dict with 'source' and 'payload' keys
        """
        self.current_trace = {
            "Header": {
                "agent_id": self.agent_id,
                "epoch_timestamp": datetime.now(timezone.utc).isoformat(),
                "attestation_type": "framework_v1"
            },
            "Trigger_Event": trigger_event,
            "Context_Snapshot": {},
            "Execution_Graph": [],
            "Terminal_Action": None
        }

    def log_behavior(self, behavior: str, data: str, tool: Optional[str] = None, params: Optional[dict] = None):
        """
        Log a step in the execution graph

        Args:
            behavior: One of: Observing, Planning, Reasoning, Acting, Self_Refining
            data: Human-readable description of this step
            tool: (Optional) Tool name if behavior is Acting
            params: (Optional) Tool parameters if behavior is Acting
        """
        if self.current_trace is None:
            raise RuntimeError("Must call start_trace() before logging behaviors")

        step = {
            "behavior": behavior,
            "data": data
        }

        if tool:
            step["tool"] = tool
        if params:
            step["params"] = params

        self.current_trace["Execution_Graph"].append(step)

    def set_context(self, context: dict):
        """
        Set encrypted context snapshot

        Args:
            context: Agent's internal state (will be encrypted)
        """
        if self.current_trace is None:
            raise RuntimeError("Must call start_trace() before setting context")

        # In production, encrypt with agent's private key
        # For demo, we'll mock encryption
        self.current_trace["Context_Snapshot"] = self._encrypt(context)

    def set_terminal_action(self, action_type: str, payload: dict):
        """
        Set final action outcome

        Args:
            action_type: Type of terminal action (e.g., "signal_generated", "no_action")
            payload: Action-specific data
        """
        if self.current_trace is None:
            raise RuntimeError("Must call start_trace() before setting terminal action")

        self.current_trace["Terminal_Action"] = {
            "type": action_type,
            "payload": payload
        }

    def submit_trace(self) -> dict:
        """
        Encrypt and submit trace to Glass Box Protocol

        Returns:
            dict: Response from SDK with trace_id, da_pointer, etc.
        """
        if self.current_trace is None:
            raise RuntimeError("No trace to submit. Call start_trace() first")

        if self.current_trace["Terminal_Action"] is None:
            raise RuntimeError("Must set terminal action before submitting")

        # Encrypt execution graph (proprietary alpha protection)
        encrypted_graph = self._encrypt(self.current_trace["Execution_Graph"])

        # Create final trace with encrypted execution graph
        final_trace = {
            "Header": self.current_trace["Header"],
            "Trigger_Event": self.current_trace["Trigger_Event"],
            "Context_Snapshot": self.current_trace["Context_Snapshot"],
            "Execution_Graph": encrypted_graph,
            "Terminal_Action": self.current_trace["Terminal_Action"]
        }

        # Submit to Glass Box Protocol
        response = self.sdk.submit_trace(final_trace)

        # Reset for next trace
        self.current_trace = None

        return response

    def _encrypt(self, data) -> str:
        """
        Encrypt proprietary data with agent's private key

        In production: AES-256-GCM encryption with agent's private key
        For demo: Mock encryption (just stringify)
        """
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data)
        else:
            data_str = str(data)

        # Mock encryption - in production this would be proper AES-256
        mock_encrypted = f"[ENCRYPTED:{len(data_str)} bytes]"

        return mock_encrypted

    def get_current_trace(self) -> Optional[dict]:
        """Get current trace (for debugging)"""
        return self.current_trace


if __name__ == "__main__":
    # Test the trace generator
    from datetime import datetime, timezone

    print("\nReasoning Trace Generator - Test Output\n")
    print("=" * 80)

    # Initialize SDK and trace generator
    sdk = GlassBoxSDK()
    agent_id = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
    trace_gen = ReasoningTraceGenerator(agent_id, sdk)

    # Simulate agent decision flow
    print("\n1. Starting trace with trigger event...")
    trigger = {
        "source": "news_stream",
        "payload": {
            "headline": "Bitcoin surges past $70k as institutions adopt crypto",
            "sentiment": 0.85,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }
    trace_gen.start_trace(trigger)

    print("2. Setting context...")
    context = {
        "current_position": "MONITORING",
        "portfolio": {"BTC": 0.5, "USDC": 50000},
        "avg_sentiment": 0.45,
        "btc_price": 70000
    }
    trace_gen.set_context(context)

    print("3. Logging behaviors...")
    trace_gen.log_behavior(
        "Observing",
        "Ingested news: 'Bitcoin surges past $70k'. Sentiment: +0.85"
    )

    trace_gen.log_behavior(
        "Planning",
        "Steps: 1) Update sentiment stream 2) Calculate confidence 3) Check thresholds"
    )

    trace_gen.log_behavior(
        "Reasoning",
        "New avg sentiment: +0.54. Confidence: 0.82. Threshold met → Generate signal"
    )

    trace_gen.log_behavior(
        "Acting",
        "Generating BULLISH signal for subscribers",
        tool="signal_generator",
        params={
            "asset": "BTC",
            "direction": "LONG",
            "entry_price": 70000,
            "stop_loss": 66500,
            "take_profit": 75600
        }
    )

    print("4. Setting terminal action...")
    trace_gen.set_terminal_action(
        "signal_generated",
        {
            "status": "published",
            "signal_id": "sig_btc_long_test",
            "subscribers_notified": 147
        }
    )

    print("5. Submitting trace to Glass Box Protocol...")
    response = trace_gen.submit_trace()

    print(f"\n✓ Trace submitted successfully!")
    print(f"  Trace ID: {response['trace_id']}")
    print(f"  DA Pointer: {response['da_pointer']}")
    print(f"  Merkle Root: {response['merkle_root']}")
    print(f"  Status: {response['status']}")

    print("\n" + "=" * 80)
    print("Test completed successfully!")
