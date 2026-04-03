#!/usr/bin/env python3
"""
Tests for LLM Client

Tests the unified LLM client with both Anthropic Claude and OpenAI.
Uses environment variables from config/.env for API keys.
"""

import os
import sys
import pytest
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.llm_client import LLMClient, LLMProvider, LLMResponse, create_llm_client


# Load environment variables
load_dotenv('config/.env')


class TestLLMClientInitialization:
    """Test LLM client initialization"""

    def test_anthropic_client_creation(self):
        """Test creating Anthropic client"""
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            pytest.skip("ANTHROPIC_API_KEY not found in environment")

        client = LLMClient(
            provider=LLMProvider.ANTHROPIC,
            api_key=api_key
        )

        assert client.provider == LLMProvider.ANTHROPIC
        assert client.is_available == True
        assert client.default_model == "claude-sonnet-4.5-20250514"

    def test_anthropic_from_env(self):
        """Test creating Anthropic client from environment"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not found in environment")

        client = LLMClient(provider=LLMProvider.ANTHROPIC)
        assert client.is_available == True

    def test_factory_function(self):
        """Test create_llm_client factory function"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not found in environment")

        client = create_llm_client("anthropic")
        assert isinstance(client, LLMClient)
        assert client.provider == LLMProvider.ANTHROPIC

    def test_missing_api_key(self):
        """Test behavior with missing API key"""
        # Temporarily remove API key from environment
        original_key = os.environ.pop("ANTHROPIC_API_KEY", None)

        try:
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY not found"):
                client = LLMClient(provider=LLMProvider.ANTHROPIC)
        finally:
            # Restore API key
            if original_key:
                os.environ["ANTHROPIC_API_KEY"] = original_key

    def test_custom_model(self):
        """Test setting custom default model"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not found in environment")

        client = LLMClient(
            provider=LLMProvider.ANTHROPIC,
            default_model="claude-3-haiku-20240307"
        )
        assert client.default_model == "claude-3-haiku-20240307"


class TestAnthropicCalls:
    """Test calling Anthropic Claude API"""

    def test_simple_call(self):
        """Test basic LLM call"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not found in environment")

        client = create_llm_client("anthropic")

        response = client.call(
            prompt="What is 2 + 2? Answer with just the number.",
            max_tokens=10,
            temperature=0.0
        )

        assert isinstance(response, LLMResponse)
        assert "4" in response.content
        assert response.model == "claude-sonnet-4.5-20250514"
        assert response.provider == LLMProvider.ANTHROPIC
        assert response.usage is not None
        assert response.usage["total_tokens"] > 0

    def test_with_system_prompt(self):
        """Test call with system prompt"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not found in environment")

        client = create_llm_client("anthropic")

        response = client.call(
            prompt="What is your purpose?",
            system_prompt="You are a helpful math tutor. Always mention mathematics in your responses.",
            max_tokens=100,
            temperature=0.3
        )

        assert isinstance(response, LLMResponse)
        assert len(response.content) > 0
        # System prompt should influence the response to mention math
        assert any(word in response.content.lower() for word in ["math", "mathematics", "calculation"])

    def test_different_model(self):
        """Test using a different model"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not found in environment")

        client = create_llm_client("anthropic")

        # Use Haiku model (faster/cheaper)
        response = client.call(
            prompt="Say 'test'",
            model="claude-3-haiku-20240307",
            max_tokens=10
        )

        assert response.model == "claude-3-haiku-20240307"
        assert "test" in response.content.lower()

    def test_temperature_variation(self):
        """Test different temperature settings"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not found in environment")

        client = create_llm_client("anthropic")

        # Low temperature (more deterministic)
        response_low = client.call(
            prompt="Name one color.",
            temperature=0.0,
            max_tokens=10
        )

        # High temperature (more creative)
        response_high = client.call(
            prompt="Name one color.",
            temperature=1.0,
            max_tokens=10
        )

        assert len(response_low.content) > 0
        assert len(response_high.content) > 0

    def test_json_parsing(self):
        """Test LLM returning JSON"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not found in environment")

        client = create_llm_client("anthropic")

        response = client.call(
            prompt='Return a JSON object with one field "result" set to "success". Only return the JSON, no other text.',
            temperature=0.1,
            max_tokens=50
        )

        import json
        # Should be able to parse JSON from response
        assert "{" in response.content
        # Extract JSON and parse it
        json_start = response.content.find("{")
        json_end = response.content.rfind("}") + 1
        result = json.loads(response.content[json_start:json_end])
        assert "result" in result


class TestSentimentAnalysis:
    """Test LLM client for sentiment analysis tasks (real use case)"""

    def test_crypto_sentiment_analysis(self):
        """Test analyzing cryptocurrency news sentiment"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not found in environment")

        client = create_llm_client("anthropic")

        prompt = """
Analyze the sentiment of this cryptocurrency news:
"Bitcoin surges to new all-time high as institutional adoption accelerates."

Return JSON with this structure:
{
  "sentiment": "positive" or "negative" or "neutral",
  "score": -1.0 to 1.0,
  "confidence": 0.0 to 1.0
}
Only return the JSON, no other text.
"""

        response = client.call(
            prompt=prompt,
            temperature=0.2,
            max_tokens=100
        )

        import json
        json_start = response.content.find("{")
        json_end = response.content.rfind("}") + 1
        result = json.loads(response.content[json_start:json_end])

        assert "sentiment" in result
        assert result["sentiment"] in ["positive", "negative", "neutral"]
        assert "score" in result
        assert -1.0 <= result["score"] <= 1.0
        assert "confidence" in result
        assert 0.0 <= result["confidence"] <= 1.0

    def test_multi_token_sentiment(self):
        """Test sentiment analysis for multiple tokens"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not found in environment")

        client = create_llm_client("anthropic")

        prompt = """
Analyze sentiment for BTC and ETH from this news:
"Bitcoin rallies while Ethereum faces regulatory concerns."

Return JSON array:
[
  {"token": "BTC", "sentiment": -1.0 to 1.0},
  {"token": "ETH", "sentiment": -1.0 to 1.0}
]
Only return the JSON array.
"""

        response = client.call(
            prompt=prompt,
            temperature=0.2,
            max_tokens=150
        )

        import json
        import re
        # Extract JSON array
        json_match = re.search(r'\[.*\]', response.content, re.DOTALL)
        result = json.loads(json_match.group())

        assert len(result) == 2
        assert result[0]["token"] == "BTC"
        assert result[1]["token"] == "ETH"
        # BTC should be more positive
        assert result[0]["sentiment"] > result[1]["sentiment"]


class TestErrorHandling:
    """Test error handling"""

    def test_unavailable_client(self):
        """Test calling unavailable client"""
        # Create client with invalid API key
        client = LLMClient(
            provider=LLMProvider.ANTHROPIC,
            api_key="invalid_key"
        )

        # Client should still be marked as available (validation happens on call)
        assert client.is_available == True

        # But the call should fail
        with pytest.raises(Exception):
            client.call("test")

    def test_empty_prompt(self):
        """Test with empty prompt"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not found in environment")

        client = create_llm_client("anthropic")

        # Empty prompt should still work (LLM will handle it)
        response = client.call("", max_tokens=10)
        assert isinstance(response, LLMResponse)


class TestUsageTracking:
    """Test token usage tracking"""

    def test_usage_info(self):
        """Test that usage information is captured"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not found in environment")

        client = create_llm_client("anthropic")

        response = client.call(
            prompt="Count from 1 to 5.",
            max_tokens=50
        )

        assert response.usage is not None
        assert "input_tokens" in response.usage
        assert "output_tokens" in response.usage
        assert "total_tokens" in response.usage
        assert response.usage["total_tokens"] > 0
        assert response.usage["total_tokens"] == (
            response.usage["input_tokens"] + response.usage["output_tokens"]
        )

    def test_raw_response_available(self):
        """Test that raw response is available"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not found in environment")

        client = create_llm_client("anthropic")

        response = client.call("test", max_tokens=10)

        assert response.raw_response is not None
        # Should have Anthropic-specific attributes
        assert hasattr(response.raw_response, "content")
        assert hasattr(response.raw_response, "usage")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
