# Tests

Organized test suite for the Glass Box Protocol demo.

## Folder Structure

```
tests/
├── README.md                 # This file
├── __init__.py              # Test package init
├── blockchain/              # Blockchain integration tests
│   ├── __init__.py
│   └── test_blockchain.py   # SUI blockchain publisher tests
├── llm/                     # LLM client tests
│   ├── __init__.py
│   └── test_llm_client.py   # Unified LLM client tests
├── data_sources/            # Data source tests
│   ├── __init__.py
│   ├── test_cryptopanic.py  # CryptoPanic API tests
│   ├── test_cryptopanic_simple.py
│   ├── test_coingecko.py    # CoinGecko API tests
│   ├── debug_cryptopanic.py
│   └── debug_cryptopanic2.py
├── agents/                  # Agent tests
│   ├── __init__.py
│   └── test_agents.py       # Agent A, B, C tests
├── scoring/                 # Scoring module tests
│   ├── __init__.py
│   └── test_scoring.py      # Prediction and portfolio tracker tests
└── integration/             # End-to-end integration tests
    ├── __init__.py
    └── test_integration.py  # Full pipeline tests
```

## Running Tests

### Run All Tests

```bash
# From demo directory
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### Run Specific Test Categories

```bash
# Blockchain tests
pytest tests/blockchain/ -v

# LLM client tests
pytest tests/llm/ -v

# Data source tests
pytest tests/data_sources/ -v

# Agent tests
pytest tests/agents/ -v

# Scoring tests
pytest tests/scoring/ -v

# Integration tests
pytest tests/integration/ -v
```

### Run Individual Test Files

```bash
pytest tests/llm/test_llm_client.py -v
pytest tests/blockchain/test_blockchain.py -v
```

### Run Specific Test Classes or Methods

```bash
# Run specific test class
pytest tests/llm/test_llm_client.py::TestAnthropicCalls -v

# Run specific test method
pytest tests/llm/test_llm_client.py::TestAnthropicCalls::test_simple_call -v
```

## Configuration

Tests use configuration from `config/.env`:

```env
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-...
CRYPTOPANIC_API_TOKEN=...
COINGECKO_API_KEY=...
SUI_NETWORK=testnet
SUI_TESTNET_RPC=https://fullnode.testnet.sui.io:443
```

## Test Categories

### Blockchain Tests

Tests for SUI blockchain integration:
- Publishing signals to SUI
- Transaction verification
- Object creation and queries
- Network connectivity

**Requirements:**
- `SUI_NETWORK` in `.env`
- `SUI_TESTNET_RPC` in `.env`
- `SUI_PRIVATE_KEY` (optional, for write operations)

### LLM Tests

Tests for the unified LLM client:
- Client initialization
- API calls (Anthropic Claude)
- Response parsing
- Error handling
- Usage tracking
- Sentiment analysis use cases

**Requirements:**
- `ANTHROPIC_API_KEY` in `.env` (for Claude tests)
- `OPENAI_API_KEY` in `.env` (for OpenAI tests, optional)

### Data Source Tests

Tests for external data APIs:
- CryptoPanic news fetching
- CoinGecko price data
- API health checks
- Rate limiting
- Error handling

**Requirements:**
- `CRYPTOPANIC_API_TOKEN` in `.env`
- `COINGECKO_API_KEY` in `.env` (optional, free tier available)

### Agent Tests

Tests for the three agents:
- Agent A: Sentiment analysis
- Agent B: Investment recommendations
- Agent C: Portfolio management
- Signal generation
- Reasoning traces

**Requirements:**
- `ANTHROPIC_API_KEY` for Agent A and B
- Test data fixtures

### Scoring Tests

Tests for scoring modules:
- Prediction tracking
- Portfolio performance
- Accuracy metrics
- Database operations

### Integration Tests

End-to-end pipeline tests:
- Full data flow from news → signals → recommendations
- Multi-agent orchestration
- Walrus storage integration
- Signal registry

**Requirements:**
- All configuration from `.env`
- Walrus testnet access

## Test Fixtures

Common test fixtures are defined in `conftest.py` (to be created):
- Mock API responses
- Sample news articles
- Test databases
- Temporary directories

## Best Practices

1. **Use pytest fixtures** for setup and teardown
2. **Skip tests gracefully** when API keys are missing:
   ```python
   if not os.getenv("ANTHROPIC_API_KEY"):
       pytest.skip("ANTHROPIC_API_KEY not found")
   ```
3. **Mock external APIs** where possible to avoid rate limits
4. **Use meaningful test names** that describe what's being tested
5. **Add docstrings** to test classes and methods
6. **Clean up** temporary files and databases in teardown
7. **Parameterize tests** for testing multiple scenarios:
   ```python
   @pytest.mark.parametrize("temperature", [0.0, 0.5, 1.0])
   def test_temperature(temperature):
       ...
   ```

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v
    env:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

## Coverage

Generate test coverage reports:

```bash
# HTML report
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html

# Terminal report
pytest tests/ --cov=src --cov-report=term-missing

# XML report (for CI)
pytest tests/ --cov=src --cov-report=xml
```

## Troubleshooting

### Tests Skip Due to Missing API Keys

Add keys to `config/.env`:
```bash
cp config/.env.example config/.env
# Edit and add your API keys
```

### Import Errors

Ensure you're running tests from the `demo` directory:
```bash
cd demo
pytest tests/
```

### Rate Limiting

If you hit API rate limits:
- Use mock responses for frequent test runs
- Implement test throttling
- Use different API keys for testing

## Contributing

When adding new tests:
1. Place them in the appropriate category folder
2. Follow existing naming conventions (`test_*.py`)
3. Add docstrings explaining what's tested
4. Update this README if adding new test categories
5. Ensure tests pass locally before committing

## License

Part of the Glass Box Protocol demo project.
