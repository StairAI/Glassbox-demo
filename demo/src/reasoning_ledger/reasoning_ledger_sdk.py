#!/usr/bin/env python3
"""
Reasoning Ledger SDK

This SDK provides a unified interface for storing and retrieving reasoning traces
from agents on Walrus (decentralized storage) and registering them on-chain.

Key Features:
- Store reasoning traces with full transparency
- Retrieve and verify reasoning traces
- Link reasoning to triggers (input/output)
- Support for multi-agent reasoning chains
- Immutable audit trail
"""

import hashlib
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict

from src.storage.walrus_client import WalrusClient, WalrusHelper


@dataclass
class ReasoningTrace:
    """
    Represents a reasoning trace from an agent.

    A reasoning trace captures:
    - What input the agent received
    - How the agent reasoned about it
    - What output the agent produced
    - Metadata about the reasoning process
    """
    agent_id: str                           # Agent identifier (e.g., "agent_a_sentiment")
    agent_version: str                      # Agent version
    input_triggers: List[str]               # Input trigger IDs
    output_trigger: Optional[str]           # Output trigger ID (if published)

    # Reasoning content
    reasoning_steps: List[Dict[str, Any]]   # Step-by-step reasoning
    final_output: Dict[str, Any]            # Final decision/output
    confidence: float                       # Overall confidence

    # LLM metadata (if used)
    llm_provider: Optional[str] = None      # e.g., "anthropic"
    llm_model: Optional[str] = None         # e.g., "claude-sonnet-4.5-20250514"
    llm_prompt: Optional[str] = None        # Prompt sent to LLM
    llm_response: Optional[str] = None      # Raw LLM response

    # Metadata
    timestamp: str = None                   # ISO format timestamp
    execution_time_ms: Optional[float] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReasoningTrace':
        """Create from dictionary."""
        return cls(**data)


class ReasoningLedger:
    """
    Reasoning Ledger SDK for storing and retrieving agent reasoning traces.

    This provides a clean interface for agents to:
    1. Store their reasoning process transparently
    2. Link reasoning to specific triggers
    3. Retrieve and verify past reasoning
    4. Build audit trails for multi-agent systems
    """

    def __init__(self, walrus_client: WalrusClient):
        """
        Initialize Reasoning Ledger.

        Args:
            walrus_client: WalrusClient for decentralized storage
        """
        self.walrus_client = walrus_client

    # ==================================================================================
    # STORE REASONING
    # ==================================================================================

    def store_reasoning(
        self,
        trace: ReasoningTrace
    ) -> Dict[str, str]:
        """
        Store a reasoning trace on Walrus.

        Args:
            trace: ReasoningTrace object

        Returns:
            Dict with:
                - walrus_blob_id: Blob ID on Walrus
                - data_hash: SHA-256 hash of the trace
                - size_bytes: Size of stored data
        """
        # Convert to JSON
        trace_dict = trace.to_dict()
        trace_json = json.dumps(trace_dict, indent=2, sort_keys=True)

        # Compute hash
        data_hash = hashlib.sha256(trace_json.encode()).hexdigest()

        # Store on Walrus
        blob_id = WalrusHelper.store_json(self.walrus_client, trace_dict)

        return {
            "walrus_blob_id": blob_id,
            "data_hash": data_hash,
            "size_bytes": len(trace_json)
        }

    def store_reasoning_simple(
        self,
        agent_id: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        reasoning_steps: List[Dict[str, Any]],
        confidence: float,
        **kwargs
    ) -> Dict[str, str]:
        """
        Simplified interface to store reasoning without creating ReasoningTrace manually.

        Args:
            agent_id: Agent identifier
            input_data: Input data (triggers, etc.)
            output_data: Output data (signals, etc.)
            reasoning_steps: List of reasoning steps
            confidence: Overall confidence
            **kwargs: Additional metadata (llm_provider, llm_model, etc.)

        Returns:
            Dict with walrus_blob_id, data_hash, size_bytes
        """
        trace = ReasoningTrace(
            agent_id=agent_id,
            agent_version=kwargs.get("agent_version", "1.0"),
            input_triggers=kwargs.get("input_triggers", []),
            output_trigger=kwargs.get("output_trigger"),
            reasoning_steps=reasoning_steps,
            final_output=output_data,
            confidence=confidence,
            llm_provider=kwargs.get("llm_provider"),
            llm_model=kwargs.get("llm_model"),
            llm_prompt=kwargs.get("llm_prompt"),
            llm_response=kwargs.get("llm_response"),
            execution_time_ms=kwargs.get("execution_time_ms")
        )

        return self.store_reasoning(trace)

    # ==================================================================================
    # RETRIEVE REASONING
    # ==================================================================================

    def retrieve_reasoning(
        self,
        walrus_blob_id: str,
        verify_hash: Optional[str] = None
    ) -> ReasoningTrace:
        """
        Retrieve a reasoning trace from Walrus.

        Args:
            walrus_blob_id: Blob ID on Walrus
            verify_hash: Optional hash to verify integrity

        Returns:
            ReasoningTrace object

        Raises:
            ValueError: If hash verification fails
        """
        # Fetch from Walrus
        trace_dict = WalrusHelper.fetch_json(self.walrus_client, walrus_blob_id)

        # Verify hash if provided
        if verify_hash:
            trace_json = json.dumps(trace_dict, indent=2, sort_keys=True)
            computed_hash = hashlib.sha256(trace_json.encode()).hexdigest()

            if computed_hash != verify_hash:
                raise ValueError(
                    f"Reasoning trace integrity check failed! "
                    f"Expected: {verify_hash}, Got: {computed_hash}"
                )

        # Convert to ReasoningTrace
        return ReasoningTrace.from_dict(trace_dict)

    # ==================================================================================
    # QUERY & ANALYSIS
    # ==================================================================================

    def compare_reasoning(
        self,
        blob_id_1: str,
        blob_id_2: str
    ) -> Dict[str, Any]:
        """
        Compare two reasoning traces (useful for analyzing agent decisions).

        Args:
            blob_id_1: First trace blob ID
            blob_id_2: Second trace blob ID

        Returns:
            Dict with comparison results
        """
        trace_1 = self.retrieve_reasoning(blob_id_1)
        trace_2 = self.retrieve_reasoning(blob_id_2)

        return {
            "agents": {
                "trace_1": trace_1.agent_id,
                "trace_2": trace_2.agent_id
            },
            "confidence_diff": abs(trace_1.confidence - trace_2.confidence),
            "same_llm": (
                trace_1.llm_provider == trace_2.llm_provider and
                trace_1.llm_model == trace_2.llm_model
            ),
            "reasoning_steps_count": {
                "trace_1": len(trace_1.reasoning_steps),
                "trace_2": len(trace_2.reasoning_steps)
            },
            "timestamps": {
                "trace_1": trace_1.timestamp,
                "trace_2": trace_2.timestamp
            }
        }

    def get_reasoning_chain(
        self,
        trigger_id: str,
        registry
    ) -> List[ReasoningTrace]:
        """
        Get the chain of reasoning traces that led to a specific trigger.

        This traces back through multiple agents to understand how a decision was made.

        Args:
            trigger_id: Final trigger ID to trace back from
            registry: TriggerRegistry to query triggers

        Returns:
            List of ReasoningTrace objects in chronological order
        """
        chain = []
        current_trigger_id = trigger_id

        # TODO: Implement recursive trace-back through triggers
        # This would follow input_triggers -> output_trigger links

        return chain


class ReasoningLedgerHelper:
    """
    Helper functions for common reasoning ledger operations.
    """

    @staticmethod
    def create_reasoning_step(
        step_name: str,
        description: str,
        input_data: Any = None,
        output_data: Any = None,
        confidence: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Create a standardized reasoning step.

        Args:
            step_name: Name of the step (e.g., "fetch_data", "analyze_sentiment")
            description: Human-readable description
            input_data: Input to this step
            output_data: Output from this step
            confidence: Confidence in this step

        Returns:
            Dict representing the step
        """
        step = {
            "step_name": step_name,
            "description": description,
            "timestamp": datetime.utcnow().isoformat()
        }

        if input_data is not None:
            step["input"] = input_data
        if output_data is not None:
            step["output"] = output_data
        if confidence is not None:
            step["confidence"] = confidence

        return step

    @staticmethod
    def create_llm_reasoning_step(
        prompt: str,
        response: str,
        model: str,
        provider: str = "anthropic",
        confidence: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Create a reasoning step for LLM calls.

        Args:
            prompt: Prompt sent to LLM
            response: LLM response
            model: Model name
            provider: Provider name
            confidence: Confidence in the response

        Returns:
            Dict representing the LLM step
        """
        return ReasoningLedgerHelper.create_reasoning_step(
            step_name="llm_call",
            description=f"Called {provider} {model}",
            input_data={"prompt": prompt[:500] + "..." if len(prompt) > 500 else prompt},
            output_data={"response": response[:500] + "..." if len(response) > 500 else response},
            confidence=confidence
        )
