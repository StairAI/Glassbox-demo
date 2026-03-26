# Engineering Architecture Specification: The Glass Box Protocol

**Version:** 1.0
**Core Objective:** Establish a verifiable, decentralized trust and reputation layer (RAID) for autonomous AI agents via immutable reasoning traces.

---

## 1. System Topology & Data Flow

The Glass Box Protocol operates as a middleware trust layer sitting between agent computation and on-chain financial execution. The architecture strictly limits integration to two perimeter gates (Input and Output) to maintain an agent-agnostic core.

**High-Level Flow:**
`Trigger Register (Input)` $\rightarrow$ `Execution Track (Hosted or Self-Hosted)` $\rightarrow$ `Ledger SDK (Output)` $\rightarrow$ `DA Layer` $\rightarrow$ `Reputation Engine` $\rightarrow$ `Marketplace / API`

---

## 2. Integration Gates (Ingress & Egress)

### 2.1 The Trigger Register (Input Gate)

A standardized event bus that feeds normalized triggers to the agents. This prevents agents from arbitrarily executing without a verifiable catalyst.

- **On-Chain Events:** Smart contract state changes, DEX pool imbalances, DAO votes.
- **Off-Chain Events:** Verified Oracle data (e.g., Pyth/Chainlink price feeds), News API webhooks.
- **Agent-Generated Events:** Inter-agent communication (e.g., a macro-analysis agent triggering a specialized execution sub-agent).

### 2.2 The Reasoning Ledger SDK (Output Gate)

A lightweight client library (`@glassbox/sdk`) responsible for intercepting the agent's state, compiling the final outcome and the granular execution steps into the Universal Schema, encrypting proprietary alpha, and pushing the payload to the ledger.

---

## 3. Dual-Track Execution & Attestation Layer

To solve the "Cold Start" developer friction while maintaining a path to fully trustless institutional adoption, the protocol routes agents through one of two execution tracks.

### Track A: The Glass Box Framework (MVP / Cold Start)

Designed for rapid onboarding with limited flexibility.

- **Infrastructure:** Agents are built using the official, opinionated Glass Box runtime environment.
- **Attestation:** Because the protocol controls the runtime, it serves as the centralized "Trust Source." The framework natively captures the trace, signs it with a protocol session key, and guarantees the logic was executed as claimed.

### Track B: Self-Hosted Agents (Trustless Ecosystem)

Designed for proprietary, mature agents (e.g., institutional quant bots) running on external infrastructure.

- **Identity:** Bring Your Own Identity (BYOI). Agents sign payloads with their own cryptographic public key (EVM address, DID), establishing their RAID (Reasoning As Identity).
- **Work Attestation (The Blind Sequencer):** Sits between the Trigger Register and the Agent. It randomly injects synthetic, protocol-generated test events alongside real user data. This creates cryptographic paranoia, making lazy "token-digging" computationally risky and economically irrational.
- **Cryptographic Proofs:** Long-term roadmap includes requiring zkTLS (proving web traffic to Anthropic/OpenAI) or TEE (hardware enclave signatures) to cryptographically guarantee the trace matches the runtime execution.

---

## 4. The Universal Reasoning Ledger (Data Schema)

The protocol utilizes an agent-agnostic JSON envelope to record computation. The `Execution_Graph` mandates a low-granularity behavioral breakdown, mapping directly to modern LLM Tool Use and XML-tagging mechanics (e.g., Claude `tool_use`, `<thinking>`, `<plan>`).

**`ReasoningTrace` JSON Schema:**

```json
{
  "Header": {
    "agent_id": "0x...", // RAID Public Key
    "epoch_timestamp": "2026-03-21T10:00:00Z",
    "attestation_type": "framework_v1"
  },
  "Trigger_Event": {
    "source": "chainlink_oracle",
    "payload": { "asset": "ETH", "price": "3200" }
  },
  "Context_Snapshot": "[ENCRYPTED_CREATOR_KEY]",
  "Execution_Graph": [
    // [ENCRYPTED_CREATOR_KEY]
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
      "behavior": "Self_Refining", // If an error occurs
      "data": "Slippage tolerance exceeded. Recalculating route via Curve."
    }
  ],
  "Terminal_Action": {
    "type": "transaction_intent",
    "payload": { "status": "executed", "tx_hash": "0x..." }
  }
}
```
