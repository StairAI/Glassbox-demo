# Agent A Updates - Token-Flexible Sentiment Analysis

## Changes Made

### 1. Switched to Claude Sonnet 4.5 Only
- **Removed**: OpenAI support
- **Using**: Claude Sonnet 4.5 (`claude-sonnet-4.5-20250514`)
- **Configuration**: Single `ANTHROPIC_API_KEY` in `.env`

### 2. Flexible Token Structure

**Old Format** (hardcoded BTC/ETH):
```json
{
  "btc_sentiment": -0.2,
  "eth_sentiment": -0.2,
  "overall_sentiment": -0.4,
  "confidence": 0.6,
  "reasoning": "..."
}
```

**New Format** (flexible tokens):
```json
{
  "tokens": [
    {
      "target_token": "BTC",
      "target_token_sentiment": -0.25,
      "confidence": 0.5,
      "reasoning": "..."
    },
    {
      "target_token": "ETH",
      "target_token_sentiment": -1.0,
      "confidence": 0.5,
      "reasoning": "..."
    }
  ],
  "overall_confidence": 0.5
}
```

### 3. Updated Constructor

**Old**:
```python
AgentA(
    registry=registry,
    publisher=publisher,
    llm_provider="openai",  # or "anthropic"
    api_key=api_key
)
```

**New**:
```python
AgentA(
    registry=registry,
    publisher=publisher,
    target_tokens=["BTC", "ETH", "SUI"],  # Flexible token list
    api_key=api_key  # Anthropic API key
)
```

### 4. Updated Prompt

The prompt now dynamically generates the JSON structure based on `target_tokens`:

```python
# Example for ["BTC", "ETH", "SUI"]
"""
Analyze sentiment for BTC, ETH, SUI.

Return a JSON array with one object per token:
[
  {
    "target_token": "BTC",
    "target_token_sentiment": <-1.0 to 1.0>,
    "confidence": <0.0 to 1.0>,
    "reasoning": "..."
  },
  ...
]
"""
```

### 5. Updated Fallback Sentiment

The rule-based fallback also uses the new token structure:
- Analyzes each token in `target_tokens` independently
- Returns array format matching Claude's output
- Supports custom token search terms (BTC → ["btc", "bitcoin"])

## Usage Examples

### Basic Usage (BTC/ETH)
```python
agent_a = AgentA(
    registry=registry,
    publisher=publisher
    # Defaults to target_tokens=["BTC", "ETH"]
)
```

### Custom Tokens
```python
agent_a = AgentA(
    registry=registry,
    publisher=publisher,
    target_tokens=["BTC", "ETH", "SUI", "SOL"]
)
```

### With Claude API Key
```python
agent_a = AgentA(
    registry=registry,
    publisher=publisher,
    target_tokens=["BTC", "ETH"],
    api_key="sk-ant-..."
)
```

## Configuration

In `config/.env`:
```bash
# =============================================================================
# LLM Configuration (Agent A & B)
# =============================================================================
# Using Claude Sonnet 4.5 for sentiment analysis
# Get key from: https://console.anthropic.com/
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## Benefits

1. **Flexible**: Can analyze any number of tokens
2. **Scalable**: Easy to add new tokens without code changes
3. **Consistent**: Same structure from LLM and fallback
4. **Future-proof**: Single LLM provider (Claude) with latest model
5. **Traceable**: Each token has individual confidence and reasoning

## Test Results

✅ Successfully tested with fallback mode:
- BTC: -0.25 sentiment (4 mentions)
- ETH: -1.0 sentiment (1 mention)
- Structure correctly stored in Walrus
- Reasoning traces captured

## Next Steps

To use with real Claude API:
1. Get API key from https://console.anthropic.com/
2. Add to `config/.env`: `ANTHROPIC_API_KEY=your_key`
3. Install anthropic: `pip install anthropic`
4. Run demo to see Claude-powered sentiment analysis
