# LLM Client

Unified interface for calling various Large Language Model (LLM) providers.

## Features

- **Multi-Provider Support**: Anthropic Claude, OpenAI, and custom endpoints
- **Consistent API**: Same interface across all providers
- **Auto-Configuration**: Reads API keys from environment variables
- **Structured Responses**: Standardized response format with usage tracking
- **Type Safety**: Full type hints and dataclasses

## Supported Providers

- **Anthropic Claude**: Sonnet 4.5, Opus, Haiku
- **OpenAI**: GPT-4, GPT-4 Turbo, GPT-3.5
- **Custom**: Bring your own endpoint

## Installation

```bash
# For Anthropic Claude
pip install anthropic

# For OpenAI
pip install openai
```

## Quick Start

### Anthropic Claude

```python
from src.llm_client import LLMClient, LLMProvider

# Initialize client (reads ANTHROPIC_API_KEY from environment)
client = LLMClient(provider=LLMProvider.ANTHROPIC)

# Make a call
response = client.call(
    prompt="What is the capital of France?",
    max_tokens=100,
    temperature=0.7
)

print(response.content)
print(f"Used {response.usage['total_tokens']} tokens")
```

### OpenAI

```python
from src.llm_client import LLMClient, LLMProvider

# Initialize client (reads OPENAI_API_KEY from environment)
client = LLMClient(
    provider=LLMProvider.OPENAI,
    default_model="gpt-4"
)

response = client.call(
    prompt="Explain quantum computing in one sentence.",
    system_prompt="You are a helpful physics teacher."
)

print(response.content)
```

### Factory Function

```python
from src.llm_client import create_llm_client

# Simple creation
client = create_llm_client("anthropic")
response = client.call("Hello, world!")

# With custom config
client = create_llm_client(
    provider="openai",
    model="gpt-4-turbo",
    api_key="sk-..."
)
```

## API Reference

### LLMClient

#### Constructor

```python
LLMClient(
    provider: LLMProvider = LLMProvider.ANTHROPIC,
    api_key: Optional[str] = None,
    default_model: Optional[str] = None,
    **kwargs
)
```

**Parameters:**
- `provider`: LLM provider to use (ANTHROPIC, OPENAI, CUSTOM)
- `api_key`: API key (optional, reads from environment if not provided)
- `default_model`: Default model name to use
- `**kwargs`: Provider-specific configuration

#### Methods

##### `call()`

```python
call(
    prompt: str,
    model: Optional[str] = None,
    max_tokens: int = 2048,
    temperature: float = 0.3,
    system_prompt: Optional[str] = None,
    **kwargs
) -> LLMResponse
```

**Parameters:**
- `prompt`: User prompt to send to LLM
- `model`: Model to use (overrides default_model)
- `max_tokens`: Maximum tokens to generate (default: 2048)
- `temperature`: Sampling temperature 0.0-1.0 (default: 0.3)
- `system_prompt`: Optional system/instruction prompt
- `**kwargs`: Additional provider-specific parameters

**Returns:** `LLMResponse` object with:
- `content`: Generated text
- `model`: Model used
- `provider`: Provider used
- `usage`: Token usage dict (input_tokens, output_tokens, total_tokens)
- `raw_response`: Original provider response

##### `is_available`

```python
@property
def is_available(self) -> bool
```

Check if the LLM client is properly initialized and available.

### LLMResponse

Dataclass containing the LLM response:

```python
@dataclass
class LLMResponse:
    content: str                          # Generated text
    model: str                            # Model name used
    provider: LLMProvider                 # Provider used
    usage: Optional[Dict[str, int]]       # Token usage stats
    raw_response: Optional[Any]           # Raw provider response
```

## Usage Examples

### Sentiment Analysis

```python
from src.llm_client import create_llm_client

client = create_llm_client("anthropic")

prompt = """
Analyze the sentiment of this news article:
"Bitcoin surges to new all-time high as institutional adoption accelerates."

Return JSON: {"sentiment": "positive|negative|neutral", "score": -1.0 to 1.0}
"""

response = client.call(prompt, temperature=0.1)
print(response.content)
```

### With Error Handling

```python
from src.llm_client import LLMClient, LLMProvider

try:
    client = LLMClient(provider=LLMProvider.ANTHROPIC)

    if not client.is_available:
        print("LLM not available, using fallback logic")
        # Use fallback method
    else:
        response = client.call("Analyze this...")
        print(response.content)

except Exception as e:
    print(f"LLM call failed: {e}")
    # Handle error
```

### Custom Model Selection

```python
client = create_llm_client("anthropic")

# Use different models for different tasks
cheap_response = client.call(
    "Simple question?",
    model="claude-3-haiku-20240307",  # Fast and cheap
    max_tokens=100
)

powerful_response = client.call(
    "Complex analysis task...",
    model="claude-sonnet-4.5-20250514",  # Most capable
    max_tokens=4000
)
```

## Environment Variables

The client automatically reads API keys from environment variables:

```bash
# Anthropic Claude
export ANTHROPIC_API_KEY=sk-ant-api03-...

# OpenAI
export OPENAI_API_KEY=sk-...
```

Or set them in your `.env` file:

```env
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-...
```

## Error Handling

The client raises exceptions for various error conditions:

- `ValueError`: Invalid provider or missing API key
- `ImportError`: Required package not installed
- `RuntimeError`: Client not available when calling
- Provider-specific errors from the underlying APIs

## Best Practices

1. **Check Availability**: Always check `client.is_available` before making calls
2. **Handle Errors**: Wrap calls in try-except blocks
3. **Use Appropriate Models**: Choose models based on task complexity and cost
4. **Set Temperature**: Use low temperature (0.1-0.3) for factual tasks, higher (0.7-1.0) for creative tasks
5. **Provide System Prompts**: Use system prompts to set context and behavior
6. **Monitor Usage**: Check `response.usage` to track token consumption

## Integration with Agents

Example: Updating Agent A to use the unified client

```python
from src.llm_client import create_llm_client

class AgentA:
    def __init__(self, api_key: Optional[str] = None):
        # Create unified LLM client
        self.llm_client = create_llm_client(
            provider="anthropic",
            api_key=api_key,
            model="claude-sonnet-4.5-20250514"
        )

    def analyze_sentiment(self, articles):
        if not self.llm_client.is_available:
            return self._fallback_sentiment(articles)

        prompt = self._create_sentiment_prompt(articles)

        response = self.llm_client.call(
            prompt=prompt,
            temperature=0.3,
            max_tokens=2048
        )

        return self._parse_response(response.content)
```

## License

Part of the Glass Box Protocol demo project.
