#!/usr/bin/env python3
"""
Abstract Agent Interface

All agents in the Glass Box Protocol should implement this interface.
Agents are reasoning processes that:
1. Accept Signals as input (news, price, or insight signals from other agents)
2. Process signals through internal workflows (reasoning, state updates, tool calls)
3. Generate InsightSignals as output
4. Record all steps in the Reasoning Ledger for transparency

Key principles:
- Agents ALWAYS accept List[Signal] as input
- Agents ALWAYS output InsightSignal
- Agents MUST record reasoning traces using ReasoningLedger SDK
- Agents CAN maintain internal state
- Agents CAN use LLMs, tools, and external APIs
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
import time

from .signal import Signal, InsightSignal
from src.reasoning_ledger.reasoning_ledger_sdk import ReasoningLedger, ReasoningLedgerHelper


class Agent(ABC):
    """
    Abstract base class for all agents in the Glass Box Protocol.

    An agent is responsible for:
    1. Reading signals (input)
    2. Processing signals with reasoning
    3. Optionally updating internal state
    4. Generating insight signals (output)
    5. Recording all steps in reasoning ledger
    """

    def __init__(
        self,
        agent_id: str,
        agent_version: str = "1.0",
        reasoning_ledger: Optional[ReasoningLedger] = None
    ):
        """
        Initialize agent.

        Args:
            agent_id: Unique agent identifier (e.g., "agent_a_sentiment")
            agent_version: Agent version for traceability
            reasoning_ledger: ReasoningLedger instance for recording traces
        """
        self.agent_id = agent_id
        self.agent_version = agent_version
        self.reasoning_ledger = reasoning_ledger

        # Execution tracking
        self._last_run: Optional[datetime] = None
        self._run_count: int = 0
        self._reasoning_steps: List[Dict[str, Any]] = []

    # ==================================================================================
    # CORE INTERFACE - Subclasses MUST implement these
    # ==================================================================================

    @abstractmethod
    def process_signals(self, signals: List[Signal]) -> Dict[str, Any]:
        """
        Process input signals and generate output.

        This is the core reasoning logic of the agent. Subclasses must implement
        this method to define their specific behavior.

        Args:
            signals: List of input signals (NewsSignal, PriceSignal, or InsightSignal)

        Returns:
            Dict with:
                - insight_value: The agent's output/decision
                - confidence: Confidence score (0.0 to 1.0)
                - Additional agent-specific fields

        Example:
            {
                "sentiment_scores": {"BTC": 0.75, "ETH": 0.60},
                "confidence": 0.85,
                "tokens_analyzed": ["BTC", "ETH"]
            }
        """
        pass

    # ==================================================================================
    # OPTIONAL HOOKS - Subclasses CAN override these for custom behavior
    # ==================================================================================

    def validate_input(self, signals: List[Signal]) -> bool:
        """
        Validate input signals before processing.

        Override this to add custom validation logic.

        Args:
            signals: Input signals

        Returns:
            True if valid, False otherwise
        """
        return len(signals) > 0

    def before_process(self, signals: List[Signal]) -> None:
        """
        Hook called before processing signals.

        Use this for:
        - Loading state
        - Initializing resources
        - Pre-processing data

        Args:
            signals: Input signals
        """
        pass

    def after_process(self, output: Dict[str, Any]) -> None:
        """
        Hook called after processing signals.

        Use this for:
        - Saving state
        - Cleanup
        - Post-processing

        Args:
            output: Processing output
        """
        pass

    # ==================================================================================
    # REASONING TRACE HELPERS
    # ==================================================================================

    def record_step(
        self,
        step_name: str,
        description: str,
        input_data: Any = None,
        output_data: Any = None,
        confidence: Optional[float] = None
    ) -> None:
        """
        Record a reasoning step for transparency.

        Use this throughout your agent to track its decision-making process.

        Args:
            step_name: Name of the step (e.g., "fetch_data", "analyze_sentiment")
            description: Human-readable description
            input_data: Input to this step
            output_data: Output from this step
            confidence: Confidence in this step
        """
        step = ReasoningLedgerHelper.create_reasoning_step(
            step_name=step_name,
            description=description,
            input_data=input_data,
            output_data=output_data,
            confidence=confidence
        )
        self._reasoning_steps.append(step)

    def record_llm_call(
        self,
        prompt: str,
        response: str,
        model: str,
        provider: str = "anthropic",
        confidence: Optional[float] = None
    ) -> None:
        """
        Record an LLM call for transparency.

        Args:
            prompt: Prompt sent to LLM
            response: LLM response
            model: Model name
            provider: Provider name
            confidence: Confidence in the response
        """
        step = ReasoningLedgerHelper.create_llm_reasoning_step(
            prompt=prompt,
            response=response,
            model=model,
            provider=provider,
            confidence=confidence
        )
        self._reasoning_steps.append(step)

    def record_tool_call(
        self,
        tool_name: str,
        tool_input: Any,
        tool_output: Any,
        tool_description: Optional[str] = None,
        success: bool = True
    ) -> None:
        """
        Record a tool call for transparency.

        Use this to track when agents call external tools/APIs (price feeds, etc.)

        Args:
            tool_name: Name of the tool (e.g., "get_sui_price", "fetch_oracle_data")
            tool_input: Input parameters to the tool
            tool_output: Output from the tool
            tool_description: Human-readable description of what the tool does
            success: Whether the tool call succeeded
        """
        step = {
            "step_type": "tool_call",
            "tool_name": tool_name,
            "tool_description": tool_description or f"Called tool: {tool_name}",
            "tool_input": tool_input,
            "tool_output": tool_output,
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        }
        self._reasoning_steps.append(step)

    def get_reasoning_steps(self) -> List[Dict[str, Any]]:
        """Get all recorded reasoning steps."""
        return self._reasoning_steps.copy()

    def clear_reasoning_steps(self) -> None:
        """Clear reasoning steps (called after storing to ledger)."""
        self._reasoning_steps = []

    # ==================================================================================
    # MAIN EXECUTION FLOW
    # ==================================================================================

    def run(
        self,
        signals: List[Signal],
        store_reasoning: bool = True
    ) -> InsightSignal:
        """
        Main execution method that orchestrates the agent workflow.

        This method:
        1. Validates input
        2. Calls before_process hook
        3. Executes process_signals (core logic)
        4. Calls after_process hook
        5. Stores reasoning trace
        6. Creates and returns InsightSignal

        Args:
            signals: Input signals
            store_reasoning: Whether to store reasoning trace in ledger

        Returns:
            InsightSignal with agent's output

        Raises:
            AgentError: If processing fails
        """
        start_time = time.time()
        self._run_count += 1

        try:
            print(f"\n{'='*80}")
            print(f"{self.agent_id.upper()}: Starting Agent Execution")
            print(f"{'='*80}")

            # Step 1: Validate input
            print(f"[1/5] Validating input signals...")
            if not self.validate_input(signals):
                raise AgentError(
                    agent_id=self.agent_id,
                    message="Input validation failed"
                )
            print(f"  ✓ Received {len(signals)} signal(s)")

            # Record input signals
            signal_ids = [s.object_id for s in signals]
            self.record_step(
                step_name="input_validation",
                description=f"Validated {len(signals)} input signals",
                input_data={"signal_ids": signal_ids},
                output_data={"valid": True}
            )

            # Step 2: Before processing hook
            print(f"[2/5] Pre-processing...")
            self.before_process(signals)

            # Step 3: Core processing
            print(f"[3/5] Processing signals...")
            output = self.process_signals(signals)
            print(f"  ✓ Processing complete")

            # Step 4: After processing hook
            print(f"[4/5] Post-processing...")
            self.after_process(output)

            # Step 5: Create and store InsightSignal
            print(f"[5/5] Creating and storing insight signal...")
            insight_signal = self._create_and_store_insight_signal(
                output=output,
                input_signal_ids=signal_ids,
                execution_time_ms=(time.time() - start_time) * 1000,
                store_reasoning=store_reasoning
            )

            # Update tracking
            self._last_run = datetime.now()

            print(f"\n{'='*80}")
            print(f"{self.agent_id.upper()}: Execution Complete")
            print(f"  Signal ID: {insight_signal.object_id}")
            print(f"  Walrus Blob ID: {insight_signal.walrus_blob_id}")
            print(f"  Reasoning Trace ID: {insight_signal.walrus_trace_id or 'N/A'}")
            print(f"  Confidence: {insight_signal.confidence:.2f}")
            print(f"  Execution Time: {(time.time() - start_time) * 1000:.0f}ms")
            print(f"{'='*80}\n")

            return insight_signal

        except Exception as e:
            raise AgentError(
                agent_id=self.agent_id,
                message=f"Agent execution failed: {str(e)}",
                original_error=e
            ) from e

    # ==================================================================================
    # INTERNAL HELPERS
    # ==================================================================================

    def _create_and_store_insight_signal(
        self,
        output: Dict[str, Any],
        input_signal_ids: List[str],
        execution_time_ms: float,
        store_reasoning: bool = True
    ) -> InsightSignal:
        """
        Create InsightSignal and store both signal data and reasoning trace on Walrus.

        This implements the unified Walrus storage architecture:
        1. Store signal data on Walrus (signal value + metadata)
        2. Store reasoning trace on Walrus (if enabled)
        3. Create InsightSignal with references to both blobs
        4. Return InsightSignal (metadata to be stored on-chain)

        Args:
            output: Agent's processing output
            input_signal_ids: List of input signal IDs
            execution_time_ms: Execution time in milliseconds
            store_reasoning: Whether to store reasoning trace

        Returns:
            InsightSignal with Walrus blob references
        """
        import hashlib
        import json
        from src.storage.walrus_client import WalrusHelper

        # Extract required fields from output
        confidence = output.get("confidence", 0.8)
        insight_type = self.agent_id.replace("agent_", "").split("_")[0]  # e.g., "sentiment"

        # Generate object ID (in production, this would be a SUI object ID)
        object_id = hashlib.sha256(
            f"{self.agent_id}_{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()

        # Step 1: Store signal data on Walrus
        signal_data = {
            "insight_type": insight_type,
            "signal_value": output,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat(),
            "producer": self.agent_id
        }

        signal_json = json.dumps(signal_data, indent=2, sort_keys=True)
        signal_hash = hashlib.sha256(signal_json.encode()).hexdigest()

        # Use reasoning_ledger's walrus_client if available
        walrus_client = self.reasoning_ledger.walrus_client if self.reasoning_ledger else None

        if walrus_client:
            signal_blob_id = WalrusHelper.store_json(walrus_client, signal_data)
            print(f"  ✓ Signal data stored on Walrus: {signal_blob_id}")
        else:
            # Fallback: create temporary blob ID (for testing without Walrus)
            signal_blob_id = f"mock_{signal_hash[:16]}"
            print(f"  ⚠ Signal data mock storage (no Walrus client): {signal_blob_id}")

        # Step 2: Store reasoning trace on Walrus (if enabled)
        trace_blob_id = None
        if store_reasoning and self.reasoning_ledger:
            trace_result = self.reasoning_ledger.store_reasoning_simple(
                agent_id=self.agent_id,
                input_data={"signal_ids": input_signal_ids},
                output_data=output,
                reasoning_steps=self.get_reasoning_steps(),
                confidence=confidence,
                agent_version=self.agent_version,
                input_signals=input_signal_ids,
                output_signal=object_id,
                execution_time_ms=execution_time_ms
            )
            trace_blob_id = trace_result.get("walrus_blob_id")
            print(f"  ✓ Reasoning trace stored on Walrus: {trace_blob_id}")

            # Clear reasoning steps after storing
            self.clear_reasoning_steps()

        # Step 3: Create InsightSignal with Walrus references
        return InsightSignal(
            object_id=object_id,
            walrus_blob_id=signal_blob_id,
            data_hash=signal_hash,
            size_bytes=len(signal_json),
            insight_type=insight_type,
            confidence=confidence,
            timestamp=datetime.utcnow(),
            producer=self.agent_id,
            walrus_trace_id=trace_blob_id  # Link to reasoning trace
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get agent execution statistics."""
        return {
            "agent_id": self.agent_id,
            "agent_version": self.agent_version,
            "last_run": self._last_run.isoformat() if self._last_run else None,
            "run_count": self._run_count
        }


# === Exceptions ===

class AgentError(Exception):
    """Base exception for agent errors."""

    def __init__(
        self,
        agent_id: str,
        message: str,
        original_error: Optional[Exception] = None
    ):
        self.agent_id = agent_id
        self.message = message
        self.original_error = original_error
        super().__init__(f"[{agent_id}] {message}")


class SignalValidationError(AgentError):
    """Exception raised when signal validation fails."""

    def __init__(self, agent_id: str, reason: str):
        super().__init__(agent_id, f"Signal validation failed: {reason}")


class ProcessingError(AgentError):
    """Exception raised during signal processing."""

    def __init__(self, agent_id: str, message: str, original_error: Optional[Exception] = None):
        super().__init__(agent_id, f"Processing error: {message}", original_error)
