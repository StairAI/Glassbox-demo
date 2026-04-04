# Reasoning Ledger SDK - Agent A Integration Analysis

## Overview

The Reasoning Ledger SDK provides a standardized way to store and retrieve agent reasoning traces. This document analyzes Agent A's current implementation and suggests integration points.

## SDK Capabilities

### Core Features
1. **ReasoningTrace** - Structured dataclass for reasoning traces
2. **ReasoningLedger** - Main SDK for store/retrieve operations
3. **ReasoningLedgerHelper** - Utility functions for creating steps

### Key Benefits
- ✅ Standardized trace format across all agents
- ✅ Built-in integrity verification (hash checking)
- ✅ Step-by-step reasoning tracking
- ✅ LLM metadata capture
- ✅ Multi-agent reasoning chain support
- ✅ Simplified API for common operations

---

## Current Agent A Implementation

### What Agent A Does Now (Lines 137-194)

```python
def _process_news_signal(self, signal_data: Dict) -> InsightSignal:
    # Step 1: Fetch news data from Walrus
    news_data = signal_obj.fetch_full_data(walrus_client=self.publisher.walrus_client)

    # Step 2: Analyze sentiment with LLM
    sentiment_scores = self._analyze_sentiment(news_data['articles'])

    # Step 3: Create reasoning trace (MANUAL)
    reasoning_trace = {
        "agent": "agent_a_sentiment",
        "input_signal": signal_data['signal_id'],
        "input_walrus_blob": signal_data['walrus_blob_id'],
        "articles_analyzed": len(news_data['articles']),
        "sentiment_scores": sentiment_scores,
        "target_tokens": self.target_tokens,
        "llm_provider": "anthropic",
        "llm_model": "claude-sonnet-4.5-20250514",
        "timestamp": datetime.utcnow().isoformat()
    }

    # Step 4: Publish signal (which stores trace on Walrus)
    signal_signal = self.publisher.publish_signal_signal(
        signal_type="sentiment",
        signal_value=sentiment_scores,
        confidence=sentiment_scores.get("overall_confidence", 0.8),
        producer="agent_a",
        reasoning_trace=reasoning_trace
    )
```

### Issues with Current Approach

1. **❌ Manual trace construction** - Prone to inconsistency across agents
2. **❌ No step-by-step tracking** - Only captures final result
3. **❌ No LLM prompt/response capture** - Missing important debugging info
4. **❌ No execution time tracking** - Can't analyze performance
5. **❌ Inconsistent format** - Each agent might structure differently
6. **❌ No verification** - No hash checking when retrieving
7. **❌ Coupled to publisher** - Reasoning logic mixed with publishing

---

## Suggested Integration Points

### 1. **Replace Manual Trace Construction** (Lines 154-166)

**Before:**
```python
reasoning_trace = {
    "agent": "agent_a_sentiment",
    "input_signal": signal_data['signal_id'],
    # ... manual dict construction
}
```

**After (with SDK):**
```python
from src.reasoning_ledger.reasoning_ledger_sdk import (
    ReasoningLedger,
    ReasoningLedgerHelper
)

# Initialize ledger (in __init__)
self.reasoning_ledger = ReasoningLedger(self.publisher.walrus_client)

# Store reasoning with structured format
reasoning_result = self.reasoning_ledger.store_reasoning_simple(
    agent_id="agent_a_sentiment",
    agent_version="1.0",
    input_data={
        "signal_id": signal_data['signal_id'],
        "walrus_blob_id": signal_data['walrus_blob_id'],
        "articles_count": len(news_data['articles'])
    },
    output_data=sentiment_scores,
    reasoning_steps=reasoning_steps,  # Collected throughout process
    confidence=sentiment_scores.get("overall_confidence", 0.8),
    llm_provider="anthropic",
    llm_model="claude-sonnet-4.5-20250514",
    input_signals=[signal_data['signal_id']]
)

# Get blob ID for publishing
trace_blob_id = reasoning_result["walrus_blob_id"]
```

### 2. **Add Step-by-Step Reasoning Tracking** (Throughout `_process_news_signal`)

**Current:** No step tracking

**After (with SDK):**
```python
def _process_news_signal(self, signal_data: Dict) -> InsightSignal:
    reasoning_steps = []  # Collect steps
    start_time = time.time()

    # Step 1: Fetch news data
    print("  [1/5] Fetching news data from Walrus...")
    signal_obj = NewsSignal(...)
    news_data = signal_obj.fetch_full_data(...)

    # Track this step
    reasoning_steps.append(
        ReasoningLedgerHelper.create_reasoning_step(
            step_name="fetch_news_data",
            description=f"Fetched {len(news_data['articles'])} articles from Walrus",
            input_data={"walrus_blob_id": signal_data['walrus_blob_id']},
            output_data={"articles_count": len(news_data['articles'])}
        )
    )

    # Step 2: Analyze sentiment
    print("  [2/5] Analyzing sentiment with LLM...")
    sentiment_scores = self._analyze_sentiment(news_data['articles'])

    # Track this step (with LLM details if used)
    if self.llm_available:
        reasoning_steps.append(
            ReasoningLedgerHelper.create_llm_reasoning_step(
                prompt=self.last_llm_prompt,  # Store this in _call_claude
                response=self.last_llm_response,
                model="claude-sonnet-4.5-20250514",
                provider="anthropic",
                confidence=sentiment_scores.get("overall_confidence")
            )
        )
    else:
        reasoning_steps.append(
            ReasoningLedgerHelper.create_reasoning_step(
                step_name="analyze_sentiment_fallback",
                description="Used rule-based sentiment analysis",
                output_data=sentiment_scores
            )
        )

    # ... continue with more steps

    execution_time = (time.time() - start_time) * 1000  # ms

    # Store complete reasoning trace
    reasoning_result = self.reasoning_ledger.store_reasoning_simple(
        agent_id="agent_a_sentiment",
        input_data={...},
        output_data=sentiment_scores,
        reasoning_steps=reasoning_steps,
        confidence=sentiment_scores.get("overall_confidence", 0.8),
        execution_time_ms=execution_time,
        ...
    )
```

### 3. **Capture LLM Prompt/Response** (In `_call_claude`, line 268)

**Before:**
```python
def _call_claude(self, prompt: str) -> str:
    response = self.llm_client.messages.create(...)
    return response.content[0].text
```

**After:**
```python
def _call_claude(self, prompt: str) -> str:
    # Store for reasoning trace
    self.last_llm_prompt = prompt

    response = self.llm_client.messages.create(...)
    response_text = response.content[0].text

    # Store for reasoning trace
    self.last_llm_response = response_text

    return response_text
```

### 4. **Decouple from OnChainPublisher** (Lines 168-176)

**Current:** Agent A relies on `publisher.publish_signal_signal()` to store reasoning

**After:**
```python
# Step 1: Store reasoning independently
reasoning_result = self.reasoning_ledger.store_reasoning_simple(...)
trace_blob_id = reasoning_result["walrus_blob_id"]

# Step 2: Publish signal with reference to reasoning
signal_signal = self.publisher.publish_signal_signal(
    signal_type="sentiment",
    signal_value=sentiment_scores,
    confidence=sentiment_scores.get("overall_confidence", 0.8),
    producer="agent_a",
    reasoning_trace_blob_id=trace_blob_id  # Just reference, not full trace
)
```

**Benefit:** Reasoning storage is independent of publishing mechanism

### 5. **Add Reasoning Verification** (New method)

**Add to Agent A:**
```python
def verify_past_reasoning(self, signal_signal_id: str) -> bool:
    """
    Verify the integrity of a past reasoning trace.

    Args:
        signal_signal_id: Signal signal to verify

    Returns:
        True if reasoning trace is valid
    """
    # Get signal from registry
    signal_data = self.registry.get_signal(signal_signal_id)

    if not signal_data or not signal_data.get('walrus_trace_id'):
        print("No reasoning trace found")
        return False

    # Retrieve and verify
    try:
        trace = self.reasoning_ledger.retrieve_reasoning(
            walrus_blob_id=signal_data['walrus_trace_id'],
            verify_hash=signal_data.get('reasoning_hash')  # If stored
        )
        print(f"✓ Reasoning verified: {trace.agent_id}")
        print(f"  Steps: {len(trace.reasoning_steps)}")
        print(f"  Confidence: {trace.confidence}")
        return True
    except ValueError as e:
        print(f"✗ Verification failed: {e}")
        return False
```

---

## Complete Integration Example

Here's what Agent A would look like with full SDK integration:

```python
class AgentA:
    def __init__(self, registry, publisher, target_tokens=None, api_key=None):
        self.registry = registry
        self.publisher = publisher
        self.target_tokens = target_tokens or ["BTC", "ETH"]

        # Initialize Reasoning Ledger SDK
        self.reasoning_ledger = ReasoningLedger(publisher.walrus_client)

        # For LLM tracking
        self.last_llm_prompt = None
        self.last_llm_response = None

        self._init_llm()

    def _process_news_signal(self, signal_data: Dict) -> InsightSignal:
        reasoning_steps = []
        start_time = time.time()

        # Step 1: Fetch data
        signal_obj = NewsSignal(...)
        news_data = signal_obj.fetch_full_data(...)

        reasoning_steps.append(
            ReasoningLedgerHelper.create_reasoning_step(
                step_name="fetch_news_data",
                description=f"Fetched {len(news_data['articles'])} articles",
                input_data={"walrus_blob_id": signal_data['walrus_blob_id']},
                output_data={"articles_count": len(news_data['articles'])}
            )
        )

        # Step 2: Analyze sentiment
        sentiment_scores = self._analyze_sentiment(news_data['articles'])

        if self.llm_available and self.last_llm_prompt:
            reasoning_steps.append(
                ReasoningLedgerHelper.create_llm_reasoning_step(
                    prompt=self.last_llm_prompt,
                    response=self.last_llm_response,
                    model="claude-sonnet-4.5-20250514",
                    provider="anthropic"
                )
            )

        # Step 3: Parse results
        reasoning_steps.append(
            ReasoningLedgerHelper.create_reasoning_step(
                step_name="generate_sentiment_scores",
                description="Generated sentiment scores for target tokens",
                output_data=sentiment_scores,
                confidence=sentiment_scores.get("overall_confidence")
            )
        )

        execution_time = (time.time() - start_time) * 1000

        # Store reasoning with SDK
        reasoning_result = self.reasoning_ledger.store_reasoning_simple(
            agent_id="agent_a_sentiment",
            agent_version="1.0",
            input_data={
                "signal_id": signal_data['signal_id'],
                "articles_analyzed": len(news_data['articles'])
            },
            output_data=sentiment_scores,
            reasoning_steps=reasoning_steps,
            confidence=sentiment_scores.get("overall_confidence", 0.8),
            llm_provider="anthropic" if self.llm_available else None,
            llm_model="claude-sonnet-4.5-20250514" if self.llm_available else None,
            llm_prompt=self.last_llm_prompt,
            llm_response=self.last_llm_response,
            input_signals=[signal_data['signal_id']],
            execution_time_ms=execution_time
        )

        trace_blob_id = reasoning_result["walrus_blob_id"]

        # Publish signal
        signal_signal = self.publisher.publish_signal_signal(
            signal_type="sentiment",
            signal_value=sentiment_scores,
            confidence=sentiment_scores.get("overall_confidence", 0.8),
            producer="agent_a",
            reasoning_trace_blob_id=trace_blob_id
        )

        # Register
        signal_id = self.registry.register_signal({
            "signal_type": "insight",
            "signal_type": "sentiment",
            "signal_value": sentiment_scores,
            "confidence": sentiment_scores.get("overall_confidence", 0.8),
            "producer": "agent_a",
            "walrus_trace_id": trace_blob_id,
            "reasoning_hash": reasoning_result["data_hash"],  # For verification
            "timestamp": datetime.utcnow().isoformat()
        })

        return signal_signal
```

---

## Benefits of Integration

### 1. **Consistency Across Agents**
- All agents use the same ReasoningTrace format
- Easier to compare reasoning from different agents
- Standardized tooling for analysis

### 2. **Better Debugging**
- Step-by-step trace shows where issues occur
- LLM prompt/response captured for analysis
- Execution time helps identify bottlenecks

### 3. **Auditability**
- Hash verification ensures traces haven't been tampered with
- Complete audit trail from input → reasoning → output
- Can trace back through multi-agent chains

### 4. **Cleaner Code**
- SDK handles complexity of storage/retrieval
- Agent code focuses on logic, not infrastructure
- Reusable across Agent B, C, etc.

### 5. **Future Features**
- Query reasoning by agent, confidence, time range
- Compare reasoning approaches
- Build multi-agent reasoning chains
- Generate reasoning reports

---

## Implementation Priority

### Phase 1: Basic Integration (Recommended First)
1. Add `ReasoningLedger` initialization to `__init__`
2. Replace manual trace dict with `store_reasoning_simple()`
3. Add `reasoning_hash` to SignalRegistry

### Phase 2: Step Tracking
4. Add `reasoning_steps` list to `_process_news_signal`
5. Use `ReasoningLedgerHelper.create_reasoning_step()` for each step
6. Capture LLM prompt/response in `_call_claude`

### Phase 3: Advanced Features
7. Add `verify_past_reasoning()` method
8. Implement reasoning chain retrieval
9. Add performance tracking (execution time)

---

## Summary

The Reasoning Ledger SDK provides a production-ready solution for transparent, verifiable agent reasoning. Integration with Agent A involves:

- **Minimal changes** (~20 lines of code)
- **Immediate benefits** (standardization, verification)
- **Foundation for advanced features** (chains, comparison, analysis)

The SDK decouples reasoning storage from publishing logic, making agents more maintainable and testable.
