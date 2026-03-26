"""
Glass Box Protocol SDK Client
Mock implementation for demo purposes
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict
from pathlib import Path


class GlassBoxSDK:
    """
    Glass Box Protocol SDK Client

    In production, this would make HTTP requests to the actual Glass Box Protocol API.
    For demo purposes, this saves traces locally and simulates API responses.
    """

    def __init__(self, output_dir: str = None):
        """
        Initialize SDK client

        Args:
            output_dir: Directory to save traces (default: ../../output/traces)
        """
        if output_dir is None:
            # Default to demo/output/traces
            current_dir = Path(__file__).parent
            output_dir = current_dir.parent.parent / "output" / "traces"

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.trace_counter = 0
        self.session_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        print(f"[GlassBox SDK] Initialized with output directory: {self.output_dir}")

    def submit_trace(self, trace: Dict) -> Dict:
        """
        Submit reasoning trace to Glass Box Protocol

        Args:
            trace: ReasoningTrace dict conforming to Universal Schema

        Returns:
            dict: {
                "trace_id": str,
                "da_pointer": str,
                "merkle_root": str,
                "status": str
            }
        """
        self.trace_counter += 1

        # Generate trace ID
        agent_id_short = trace['Header']['agent_id'][-8:]
        timestamp = trace['Header']['epoch_timestamp'].replace(':', '').replace('-', '').replace('.', '')[:15]
        trace_id = f"trace_{agent_id_short}_{timestamp}_{self.trace_counter:03d}"

        # Save trace to local file system (simulating DA layer)
        trace_filename = f"{trace_id}.json"
        trace_path = self.output_dir / trace_filename

        with open(trace_path, 'w') as f:
            json.dump(trace, f, indent=2)

        # Simulate DA pointer (in production, this would be Celestia/EigenDA)
        da_pointer = f"local://traces/{trace_filename}"

        # Simulate Merkle root calculation
        merkle_root = self._calculate_mock_merkle_root(trace)

        response = {
            "trace_id": trace_id,
            "da_pointer": da_pointer,
            "merkle_root": merkle_root,
            "status": "confirmed",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        print(f"[GlassBox SDK] Trace submitted: {trace_id}")

        return response

    def get_agent_reputation(self, agent_id: str) -> Dict:
        """
        Query agent reputation (RAID score)

        Args:
            agent_id: Agent's public key / RAID address

        Returns:
            dict: Agent reputation data
        """
        # Mock reputation data
        # In production, this would query the Reputation Engine API
        return {
            "agent_id": agent_id,
            "raid_score": 0.847,
            "breakdown": {
                "reasoning_accuracy": 0.92,
                "data_provenance": 0.88,
                "actuarial_performance": 0.75,
                "state_continuity": 0.91,
                "framework_adherence": 0.95
            },
            "total_traces": 127,
            "total_signals": 23,
            "last_active": datetime.now(timezone.utc).isoformat()
        }

    def _calculate_mock_merkle_root(self, trace: Dict) -> str:
        """
        Calculate mock Merkle root for trace

        In production, this would be a cryptographic hash of the trace data
        """
        import hashlib

        trace_str = json.dumps(trace, sort_keys=True)
        hash_obj = hashlib.sha256(trace_str.encode())
        return f"0x{hash_obj.hexdigest()[:40]}"

    def get_trace_count(self) -> int:
        """Get number of traces submitted in this session"""
        return self.trace_counter

    def list_traces(self) -> list:
        """List all traces in output directory"""
        traces = []
        for trace_file in self.output_dir.glob("*.json"):
            with open(trace_file, 'r') as f:
                trace = json.load(f)
                traces.append({
                    "filename": trace_file.name,
                    "agent_id": trace['Header']['agent_id'],
                    "timestamp": trace['Header']['epoch_timestamp'],
                    "terminal_action": trace['Terminal_Action']['type']
                })
        return traces


if __name__ == "__main__":
    # Test the SDK
    sdk = GlassBoxSDK()

    print("\nGlass Box SDK - Test Output\n")
    print("=" * 80)

    # Create a test trace
    test_trace = {
        "Header": {
            "agent_id": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            "epoch_timestamp": datetime.now(timezone.utc).isoformat(),
            "attestation_type": "framework_v1"
        },
        "Trigger_Event": {
            "source": "test_source",
            "payload": {"test": "data"}
        },
        "Context_Snapshot": "[ENCRYPTED]",
        "Execution_Graph": "[ENCRYPTED]",
        "Terminal_Action": {
            "type": "test_action",
            "payload": {"status": "success"}
        }
    }

    # Submit trace
    response = sdk.submit_trace(test_trace)
    print(f"\nSubmitted trace:")
    print(f"  Trace ID: {response['trace_id']}")
    print(f"  DA Pointer: {response['da_pointer']}")
    print(f"  Merkle Root: {response['merkle_root']}")
    print(f"  Status: {response['status']}")

    # Get reputation
    print(f"\nAgent reputation:")
    reputation = sdk.get_agent_reputation(test_trace['Header']['agent_id'])
    print(f"  RAID Score: {reputation['raid_score']}")
    print(f"  Total Traces: {reputation['total_traces']}")

    print(f"\nSession stats:")
    print(f"  Traces submitted: {sdk.get_trace_count()}")
