# Engineering Architecture Specification: The Glass Box Protocol

**Version:** 1.0
**Last Updated:** March 22, 2026
**Core Objective:** Establish a verifiable, decentralized trust and reputation layer (RAID) for autonomous AI agents via immutable reasoning traces.

---

## 1. System Topology & Data Flow

The Glass Box Protocol operates as a middleware trust layer sitting between agent computation and on-chain financial execution. The architecture strictly limits integration to two perimeter gates (Input and Output) to maintain an agent-agnostic core.

**High-Level Flow:**

```
Trigger Register (Input) → Execution Track (Hosted or Self-Hosted) → Ledger SDK (Output) → DA Layer → Reputation Engine → Marketplace / API
```

---

## 2. Integration Gates (Ingress & Egress)

### 2.1 The Trigger Register (Input Gate)

A standardized event bus that feeds normalized triggers to the agents. This prevents agents from arbitrarily executing without a verifiable catalyst.

- **On-Chain Events:** Smart contract state changes, DEX pool imbalances, DAO votes
- **Off-Chain Events:** Verified Oracle data (e.g., Pyth/Chainlink price feeds), News API webhooks
- **Agent-Generated Events:** Inter-agent communication (e.g., a macro-analysis agent triggering a specialized execution sub-agent)

### 2.2 The Reasoning Ledger SDK (Output Gate)

A lightweight client library (`@glassbox/sdk`) responsible for intercepting the agent's state, compiling the final outcome and the granular execution steps into the Universal Schema, encrypting proprietary alpha, and pushing the payload to the ledger.

---

## 3. Dual-Track Execution & Attestation Layer

To solve the "Cold Start" developer friction while maintaining a path to fully trustless institutional adoption, the protocol routes agents through one of two execution tracks.

### Track A: The Glass Box Framework (MVP / Cold Start)

Designed for rapid onboarding with limited flexibility.

- **Infrastructure:** Agents are built using the official, opinionated Glass Box runtime environment
- **Attestation:** Because the protocol controls the runtime, it serves as the centralized "Trust Source." The framework natively captures the trace, signs it with a protocol session key, and guarantees the logic was executed as claimed

### Track B: Self-Hosted Agents (Trustless Ecosystem)

Designed for proprietary, mature agents (e.g., institutional quant bots) running on external infrastructure.

- **Identity:** Bring Your Own Identity (BYOI). Agents sign payloads with their own cryptographic public key (EVM address, DID), establishing their RAID (Reasoning As Identity)
- **Work Attestation (The Blind Sequencer):** Sits between the Trigger Register and the Agent. It randomly injects synthetic, protocol-generated test events alongside real user data. This creates cryptographic paranoia, making lazy "token-digging" computationally risky and economically irrational
- **Cryptographic Proofs:** Long-term roadmap includes requiring zkTLS (proving web traffic to Anthropic/OpenAI) or TEE (hardware enclave signatures) to cryptographically guarantee the trace matches the runtime execution

---

## 4. The Universal Reasoning Ledger (Data Schema)

The protocol utilizes an agent-agnostic JSON envelope to record computation. The `Execution_Graph` mandates a low-granularity behavioral breakdown, mapping directly to modern LLM Tool Use and XML-tagging mechanics (e.g., Claude `tool_use`, `<thinking>`, `<plan>`).

**`ReasoningTrace` JSON Schema:**

```json
{
  "Header": {
    "agent_id": "0x...",
    "epoch_timestamp": "2026-03-22T12:00:00Z",
    "attestation_type": "framework_v1"
  },
  "Trigger_Event": {
    "source": "chainlink_oracle",
    "payload": { "asset": "ETH", "price": "3200" }
  },
  "Context_Snapshot": "[ENCRYPTED_CREATOR_KEY]",
  "Execution_Graph": [
    {
      "behavior": "Observing",
      "data": "Ingested ETH price drop and current stablecoin balances."
    },
    {
      "behavior": "Planning",
      "data": "1. Verify slippage. 2. Execute rotation to USDC."
    },
    {
      "behavior": "Reasoning",
      "data": "Market volatility exceeds threshold. Capital preservation protocol engaged."
    },
    {
      "behavior": "Acting",
      "tool": "uniswap_router",
      "params": { "action": "swap", "amount": "100_ETH" }
    },
    {
      "behavior": "Self_Refining",
      "data": "Slippage tolerance exceeded. Recalculating route via Curve."
    }
  ],
  "Terminal_Action": {
    "type": "transaction_intent",
    "payload": { "status": "executed", "tx_hash": "0x..." }
  }
}
```

**Note:** Proprietary logic (Context_Snapshot and Execution_Graph) is encrypted. Only the Header, Trigger_Event, and Terminal_Action remain public for the settlement loop.

---

## 5. Infrastructure & Settlement Stack

### Data Availability (DA) Layer

Heavy JSON `ReasoningTrace` payloads are pushed to high-throughput DA networks (e.g., Celestia, EigenDA) to ensure permanent, low-cost storage.

### Smart Contract Layer (L2)

- **Registry Contract:** Maps the BYOI public key to the agent's historical performance
- **Trace Ledger:** Stores the Merkle Root of the JSON payload and the DA pointer, securing the off-chain data mathematically

---

## 6. The Application Layer (Monetization & Utility)

### 6.1 The Reputation Engine

An off-chain evaluator that pulls the raw Outcomes and Traces from the DA layer. It runs the Measurement Matrix (Execution Determinism, Data Provenance, Actuarial Outcome) to continuously update the agent's RAID score.

### 6.2 The Glass Box Marketplace

The primary B2C and B2B interface built on top of the Reputation Engine.

**Signal Subscriptions (Professionals):** Users pay a subscription fee to stream the verified `Terminal_Action` JSON outputs of top-tier agents into their own execution pipelines.

**Agent Staking (Retail/Degens):** Users stake the native protocol token on specific agents, effectively creating a prediction market for agentic performance and routing liquidity to the best models.

**Smart Vaults:** Automated pools where user capital strictly follows the logic of Skill Modules that maintain a RAID score above a specific threshold.

### 6.3 The Reputation API (Future State)

The ultimate utility of the protocol. It exposes the RAID score as the definitive "Credit Score" for the agent economy. DeFi lending platforms, uncollateralized loan protocols, and DAO treasuries query this API to underwrite risk before granting capital access to an autonomous agent.

---

## 7. Agent State Machine Architecture

### 7.1 Text-Based State Representation

Agents maintain a text-based state machine optimized for LLM processing. Unlike traditional binary state machines, this approach allows the AI model itself to read, reason about, and update its own state.

**State File Format (state.txt):**

```
=== AGENT STATE ===
Timestamp: 2026-03-22T12:30:45Z
Market Sentiment: +0.42 (BULLISH)
Political Risk: MODERATE
Signal Strength: BULLISH
Confidence: 0.78
Current Position: MONITORING

=== DATA STREAMS ===
Stream: elon_musk
  Status: ACTIVE
  Last Value: +0.65
  Last Update: 2026-03-22T12:30:40Z
  Signal: BULLISH

Stream: donald_trump
  Status: ACTIVE
  Last Value: +0.38
  Last Update: 2026-03-22T12:30:35Z
  Signal: BULLISH

=== REASONING HISTORY ===
[2026-03-22T12:30:45Z] Processed elon_musk tweet → Generated BUY signal
[2026-03-22T12:25:12Z] Processed donald_trump tweet → Monitoring
[2026-03-22T12:20:08Z] Market sentiment shifted NEUTRAL → BULLISH
```

### 7.2 State Update Logic

```python
class AgentState:
    """Text-based state machine for LLM agents"""

    def __init__(self, state_file="state.txt"):
        self.state_file = state_file
        self.state = self.load_state()

    def load_state(self) -> str:
        """Load current state as plaintext"""
        with open(self.state_file, 'r') as f:
            return f.read()

    def update_stream(self, stream_name: str, new_data: dict):
        """Update a specific data stream in the state"""
        # LLM processes: current_state + new_data → updated_state
        prompt = f"""
        Current State:
        {self.state}

        New Data from {stream_name}:
        {json.dumps(new_data, indent=2)}

        Update the state file to reflect this new information.
        Maintain the same format and structure.
        """

        updated_state = llm.generate(prompt)
        self.save_state(updated_state)
        return updated_state

    def save_state(self, new_state: str):
        """Persist updated state"""
        with open(self.state_file, 'w') as f:
            f.write(new_state)
        self.state = new_state
```

### 7.3 Multi-Stream Processing

The state machine handles multiple concurrent data streams with weighted influence:

```python
def process_multi_stream_update(agent_state, new_tweets):
    """Process tweets from multiple sources with weighted influence"""

    # Stream influence weights
    weights = {
        'elon_musk': 0.7,     # 70% influence
        'donald_trump': 0.5   # 50% influence
    }

    for tweet in new_tweets:
        author = tweet['author']
        sentiment = tweet['sentiment']
        weight = weights.get(author, 0.3)

        # Weighted sentiment integration
        old_sentiment = agent_state.market_sentiment
        new_sentiment = old_sentiment * 0.7 + sentiment * weight * 0.3

        agent_state.market_sentiment = new_sentiment
        agent_state.update_stream(author, tweet)

    return agent_state
```

---

## 8. RAID Scoring System

### 8.1 Measurement Matrix

The RAID (Reasoning As Identity) score is calculated across six dimensions:

| Metric | Weight | Description |
|--------|--------|-------------|
| **Reasoning Accuracy** | 25% | Logical consistency and determinism in execution graphs |
| **Data Provenance** | 25% | Source verification and hallucination detection |
| **Actuarial Performance** | 20% | Real-world outcome tracking (PnL, accuracy) |
| **State Continuity** | 20% | Coherent state transitions across data streams |
| **Framework Adherence** | 10% | Compliance with risk management rules |

### 8.2 Scoring Formula

```python
def calculate_raid_score(agent_traces):
    """Calculate RAID score from reasoning traces"""

    scores = {
        'reasoning_accuracy': measure_logical_consistency(agent_traces),
        'data_provenance': verify_data_sources(agent_traces),
        'actuarial_performance': calculate_pnl_accuracy(agent_traces),
        'state_continuity': validate_state_transitions(agent_traces),
        'framework_adherence': check_rule_compliance(agent_traces)
    }

    weights = {
        'reasoning_accuracy': 0.25,
        'data_provenance': 0.25,
        'actuarial_performance': 0.20,
        'state_continuity': 0.20,
        'framework_adherence': 0.10
    }

    raid_score = sum(scores[k] * weights[k] for k in scores)
    return raid_score  # 0.0 to 1.0
```

### 8.3 State Continuity Validation

New metric ensuring agents maintain coherent reasoning across multiple data streams:

```python
def validate_state_transitions(traces):
    """Validate coherent state transitions"""
    score = 1.0

    for i in range(1, len(traces)):
        prev_state = traces[i-1].final_state
        curr_state = traces[i].initial_state

        # Check for unexplained jumps
        sentiment_delta = abs(curr_state.sentiment - prev_state.sentiment)
        if sentiment_delta > 0.5:  # Large unexplained jump
            score -= 0.1

        # Check for stream consistency
        for stream in ['elon_musk', 'donald_trump']:
            if stream_signals_conflict(prev_state, curr_state, stream):
                score -= 0.05

    return max(0.0, score)
```

---

## 9. Database Schemas

### 9.1 Agent Registry

```sql
CREATE TABLE agents (
    agent_id VARCHAR(66) PRIMARY KEY,  -- 0x... RAID address
    created_at TIMESTAMP,
    framework_version VARCHAR(20),
    raid_score DECIMAL(4,3),           -- 0.000 to 1.000
    total_traces INTEGER,
    total_signals_generated INTEGER,
    last_active TIMESTAMP
);
```

### 9.2 Reasoning Traces

```sql
CREATE TABLE reasoning_traces (
    trace_id VARCHAR(100) PRIMARY KEY,
    agent_id VARCHAR(66) REFERENCES agents(agent_id),
    timestamp TIMESTAMP,
    trigger_source VARCHAR(50),
    encrypted_context TEXT,            -- JSONB encrypted
    encrypted_execution_graph TEXT,    -- JSONB encrypted
    terminal_action JSONB,             -- Public
    da_layer_pointer VARCHAR(200),     -- Celestia/EigenDA pointer
    merkle_root VARCHAR(66)
);
```

### 9.3 Performance Metrics

```sql
CREATE TABLE agent_metrics (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(66) REFERENCES agents(agent_id),
    measurement_date DATE,
    reasoning_accuracy DECIMAL(4,3),
    data_provenance DECIMAL(4,3),
    actuarial_performance DECIMAL(4,3),
    state_continuity DECIMAL(4,3),
    framework_adherence DECIMAL(4,3),
    composite_raid_score DECIMAL(4,3)
);
```

---

## 10. API Specifications

### 10.1 Submit Reasoning Trace

```http
POST /api/v1/traces
Authorization: Bearer <agent_session_key>
Content-Type: application/json

{
  "agent_id": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "trace": {
    "header": {...},
    "trigger_event": {...},
    "encrypted_context": "...",
    "encrypted_execution_graph": "...",
    "terminal_action": {...}
  }
}
```

**Response:**

```json
{
  "trace_id": "trace_abc123_1234567890",
  "da_pointer": "celestia://block/12345/tx/67890",
  "merkle_root": "0xabcd...",
  "status": "pending_validation"
}
```

### 10.2 Query Agent Reputation

```http
GET /api/v1/agents/{agent_id}/reputation
```

**Response:**

```json
{
  "agent_id": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "raid_score": 0.847,
  "breakdown": {
    "reasoning_accuracy": 0.92,
    "data_provenance": 0.88,
    "actuarial_performance": 0.75,
    "state_continuity": 0.91,
    "framework_adherence": 0.95
  },
  "total_traces": 1247,
  "total_signals": 89,
  "last_active": "2026-03-22T12:30:45Z"
}
```

### 10.3 Subscribe to Agent Signals

```http
POST /api/v1/subscriptions
Authorization: Bearer <user_api_key>

{
  "agent_id": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "subscription_tier": "premium",
  "webhook_url": "https://myservice.com/webhook"
}
```

---

## 11. Security Considerations

### 11.1 Encryption

- **Context_Snapshot** and **Execution_Graph** are encrypted with the agent's private key
- Only the Reputation Engine (with authorized access) can decrypt for scoring
- Public fields (Header, Trigger_Event, Terminal_Action) remain visible for transparency

### 11.2 Attestation Verification

**Framework Track (MVP):**
- Protocol session key signs all traces
- Centralized but rapid onboarding

**Self-Hosted Track (Future):**
- zkTLS proofs of API calls to LLM providers
- TEE hardware signatures (AWS Nitro, Intel SGX)
- Optimistic fraud proofs with slashing

### 11.3 The Blind Sequencer

Prevents "token-digging" by randomly injecting test events:

```python
def blind_sequencer(real_events, test_events, mix_ratio=0.3):
    """Mix real and synthetic events randomly"""
    total_events = len(real_events)
    num_tests = int(total_events * mix_ratio)

    # Randomly sample test events
    selected_tests = random.sample(test_events, num_tests)

    # Merge and shuffle
    mixed = real_events + selected_tests
    random.shuffle(mixed)

    return mixed
```

Agents cannot know which events are tests, forcing honest computation on all inputs.

---

## 12. Development Roadmap

### Phase 1: MVP (Current)
- Framework-level attestation
- Trading agent focus
- Centralized Reputation Engine
- Manual RAID scoring

### Phase 2: Decentralization (6-12 months)
- Self-hosted agent support
- Blind Sequencer implementation
- zkTLS/TEE attestation
- Automated RAID calculation

### Phase 3: Ecosystem Expansion (12-24 months)
- Multi-domain agent support (not just trading)
- Reputation API marketplace
- Cross-chain deployment
- DAO governance for measurement matrix

---

## 13. References

- **Celestia:** https://celestia.org
- **EigenDA:** https://www.eigenlayer.xyz/eigenda
- **Chainlink:** https://chain.link
- **Pyth Network:** https://pyth.network
- **zkTLS:** https://blog.opacity.network/zktls-the-future-of-private-data-verification
- **AWS Nitro Enclaves:** https://aws.amazon.com/ec2/nitro/nitro-enclaves

---

**Document Version:** 1.0
**Last Updated:** March 22, 2026
**Status:** Active Development
