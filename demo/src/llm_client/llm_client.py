#!/usr/bin/env python3
"""
Unified LLM Client

Provides a consistent interface for calling various LLM providers:
- Anthropic Claude (Sonnet, Opus, Haiku)
- OpenAI (GPT-4, GPT-3.5)
- Custom endpoints
"""

import os
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass


class LLMProvider(Enum):
    """Supported LLM providers"""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    CUSTOM = "custom"


@dataclass
class LLMResponse:
    """Standardized LLM response"""
    content: str
    model: str
    provider: LLMProvider
    usage: Optional[Dict[str, int]] = None
    raw_response: Optional[Any] = None


class LLMClient:
    """
    Unified LLM client supporting multiple providers.

    Usage:
        # Anthropic Claude
        client = LLMClient(provider=LLMProvider.ANTHROPIC, api_key=api_key)
        response = client.call("Analyze this text...", model="claude-sonnet-4.5-20250514")

        # OpenAI
        client = LLMClient(provider=LLMProvider.OPENAI, api_key=api_key)
        response = client.call("Analyze this text...", model="gpt-4")
    """

    def __init__(
        self,
        provider: LLMProvider = LLMProvider.ANTHROPIC,
        api_key: Optional[str] = None,
        default_model: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize LLM client.

        Args:
            provider: LLM provider to use
            api_key: API key (or will read from environment)
            default_model: Default model to use if not specified in call()
            **kwargs: Additional provider-specific configuration
        """
        self.provider = provider
        self.api_key = api_key
        self.default_model = default_model
        self.kwargs = kwargs
        self._client = None
        self._available = False

        # Initialize the provider
        self._init_provider()

    def _init_provider(self):
        """Initialize the specific provider client"""
        try:
            if self.provider == LLMProvider.ANTHROPIC:
                self._init_anthropic()
            elif self.provider == LLMProvider.OPENAI:
                self._init_openai()
            elif self.provider == LLMProvider.CUSTOM:
                self._init_custom()
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except Exception as e:
            print(f"WARNING: Failed to initialize {self.provider.value} client: {e}")
            self._available = False

    def _init_anthropic(self):
        """Initialize Anthropic Claude client"""
        try:
            import anthropic

            # Get API key from parameter or environment
            api_key = self.api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found")

            self._client = anthropic.Anthropic(api_key=api_key)
            self.default_model = self.default_model or "claude-sonnet-4.5-20250514"
            self._available = True

        except ImportError:
            raise ImportError(
                "Anthropic package not installed. Install with: pip install anthropic"
            )

    def _init_openai(self):
        """Initialize OpenAI client"""
        try:
            import openai

            # Get API key from parameter or environment
            api_key = self.api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found")

            self._client = openai.OpenAI(api_key=api_key)
            self.default_model = self.default_model or "gpt-4"
            self._available = True

        except ImportError:
            raise ImportError(
                "OpenAI package not installed. Install with: pip install openai"
            )

    def _init_custom(self):
        """Initialize custom LLM endpoint"""
        # For custom endpoints, user must provide their own client
        self._client = self.kwargs.get('client')
        self.default_model = self.default_model or "custom-model"
        self._available = self._client is not None

    @property
    def is_available(self) -> bool:
        """Check if LLM client is available"""
        return self._available

    def call(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.3,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Call the LLM with a prompt.

        Args:
            prompt: User prompt to send to LLM
            model: Model to use (defaults to self.default_model)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            system_prompt: Optional system prompt
            **kwargs: Additional provider-specific parameters

        Returns:
            LLMResponse with generated content

        Raises:
            RuntimeError: If client is not available
            Exception: Provider-specific errors
        """
        if not self._available:
            raise RuntimeError(f"{self.provider.value} client is not available")

        model = model or self.default_model

        if self.provider == LLMProvider.ANTHROPIC:
            return self._call_anthropic(prompt, model, max_tokens, temperature, system_prompt, **kwargs)
        elif self.provider == LLMProvider.OPENAI:
            return self._call_openai(prompt, model, max_tokens, temperature, system_prompt, **kwargs)
        elif self.provider == LLMProvider.CUSTOM:
            return self._call_custom(prompt, model, max_tokens, temperature, system_prompt, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _call_anthropic(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str],
        **kwargs
    ) -> LLMResponse:
        """Call Anthropic Claude API"""
        messages = [{"role": "user", "content": prompt}]

        # Build request parameters
        request_params = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }

        # Add system prompt if provided
        if system_prompt:
            request_params["system"] = system_prompt

        # Make API call
        response = self._client.messages.create(**request_params)

        # Extract content
        content = response.content[0].text

        # Extract usage info
        usage = {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "total_tokens": response.usage.input_tokens + response.usage.output_tokens
        }

        return LLMResponse(
            content=content,
            model=model,
            provider=LLMProvider.ANTHROPIC,
            usage=usage,
            raw_response=response
        )

    def _call_openai(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str],
        **kwargs
    ) -> LLMResponse:
        """Call OpenAI API"""
        messages = []

        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        # Make API call
        response = self._client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )

        # Extract content
        content = response.choices[0].message.content

        # Extract usage info
        usage = {
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }

        return LLMResponse(
            content=content,
            model=model,
            provider=LLMProvider.OPENAI,
            usage=usage,
            raw_response=response
        )

    def _call_custom(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str],
        **kwargs
    ) -> LLMResponse:
        """
        Call custom LLM endpoint.

        User must provide a callable client that accepts:
        (prompt, model, max_tokens, temperature, system_prompt, **kwargs)
        and returns a dict with at least {'content': str}
        """
        if not callable(self._client):
            raise ValueError("Custom client must be callable")

        result = self._client(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system_prompt=system_prompt,
            **kwargs
        )

        return LLMResponse(
            content=result.get('content', ''),
            model=model,
            provider=LLMProvider.CUSTOM,
            usage=result.get('usage'),
            raw_response=result
        )


def create_llm_client(
    provider: str = "anthropic",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
) -> LLMClient:
    """
    Factory function to create an LLM client.

    Args:
        provider: Provider name ("anthropic", "openai", "custom")
        api_key: API key (optional, will read from env)
        model: Default model to use
        **kwargs: Additional provider-specific config

    Returns:
        Configured LLMClient instance

    Example:
        client = create_llm_client("anthropic")
        response = client.call("What is 2+2?")
        print(response.content)
    """
    provider_enum = LLMProvider(provider.lower())
    return LLMClient(
        provider=provider_enum,
        api_key=api_key,
        default_model=model,
        **kwargs
    )
