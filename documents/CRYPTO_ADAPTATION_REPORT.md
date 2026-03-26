# Cryptocurrency (Bitcoin) Trading System Adaptation Report

## Executive Summary

This report provides a comprehensive file-by-file analysis of the TradingAgents codebase and details the design considerations, modifications, and additions required to adapt this equity trading framework for cryptocurrency trading, specifically Bitcoin.

**Report Generated**: 2026-03-24
**Original Project**: TradingAgents v0.2.2 (Equity Trading Framework)
**Target Domain**: Cryptocurrency Trading (Bitcoin)

---

## Table of Contents

1. [Core Differences: Stocks vs Cryptocurrency](#core-differences)
2. [Architecture Overview](#architecture-overview)
3. [File-by-File Analysis](#file-by-file-analysis)
4. [New Components Required](#new-components-required)
5. [Data Vendor Recommendations](#data-vendor-recommendations)
6. [Implementation Roadmap](#implementation-roadmap)

---

## Core Differences: Stocks vs Cryptocurrency

Before diving into file-specific adaptations, it's crucial to understand the fundamental differences:

### Market Structure
- **Trading Hours**: Crypto trades 24/7/365 vs stock market business hours
- **Exchanges**: Multiple decentralized exchanges (Binance, Coinbase, Kraken) vs centralized stock exchanges
- **Market Fragmentation**: Price differences across exchanges create arbitrage opportunities
- **Settlement**: Near-instant settlement vs T+2 for stocks

### Data Characteristics
- **Volatility**: Crypto exhibits 3-10x higher volatility than equities
- **Market Cap**: Bitcoin ~$1T vs mature equities; alt-coins much smaller
- **Fundamentals**: No traditional financial statements (P/E, EPS, revenue)
- **On-Chain Metrics**: Unique data sources (hash rate, active addresses, whale movements)

### Regulatory & Sentiment
- **News Sources**: Crypto-native media (CoinDesk, The Block) vs traditional finance
- **Social Media Impact**: Twitter/X, Reddit, Telegram have outsized influence
- **Regulatory News**: Country-level bans/adoptions dramatically affect prices
- **Sentiment Drivers**: Elon Musk tweets, government announcements, ETF approvals

### Technical Analysis
- **Indicators**: Same base indicators (RSI, MACD) but different parameter tuning
- **Support/Resistance**: Psychological levels more important (e.g., $10k, $50k, $100k)
- **Volume Profile**: Exchange-specific volume needs aggregation
- **Derivatives**: Perpetual swaps (unique to crypto) vs traditional futures

---

## Architecture Overview

The adapted system would maintain the multi-agent architecture but with crypto-specific modifications:

```
┌─────────────────────────────────────────────────────────────┐
│                     CryptoAgents System                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Analyst Layer (Data Gathering & Analysis)                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ • Price/Volume Analyst (24/7 markets)                  │ │
│  │ • On-Chain Analyst (NEW - blockchain metrics)          │ │
│  │ • Sentiment Analyst (crypto-native social media)       │ │
│  │ • News Analyst (crypto-specific news sources)          │ │
│  │ • Market Structure Analyst (NEW - exchange dynamics)   │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  Research Layer (Debate-Driven Evaluation)                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ • Bull Researcher (bullish on BTC)                     │ │
│  │ • Bear Researcher (bearish on BTC)                     │ │
│  │ • Research Manager (synthesizes debate)                │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  Trading Layer                                                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ • Crypto Trader (24/7 decision making)                 │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  Risk Layer (Multi-Perspective Risk Assessment)              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ • Aggressive Analyst (high leverage)                   │ │
│  │ • Conservative Analyst (spot only)                     │ │
│  │ • Neutral Analyst (moderate leverage)                  │ │
│  │ • Portfolio Manager (final decision)                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## File-by-File Analysis

### 1. Configuration & Setup Files

#### **File**: `tradingagents/__init__.py`
**Current Function**: Sets UTF-8 encoding for cross-platform compatibility

**Crypto Adaptation Design**:
- **No changes required** - UTF-8 encoding is universal
- This file remains identical for crypto implementation

---

#### **File**: `tradingagents/default_config.py`
**Current Function**: Central configuration for LLM settings, data vendors, debate parameters

**Crypto Adaptation Design**:

```python
CRYPTO_DEFAULT_CONFIG = {
    # Directories
    "project_dir": ".",
    "results_dir": "./results",
    "data_cache_dir": "./cryptoagents/dataflows/data_cache",

    # LLM settings (unchanged)
    "llm_provider": "openai",
    "deep_think_llm": "gpt-5.2",
    "quick_think_llm": "gpt-5-mini",
    "backend_url": "https://api.openai.com/v1",

    # Provider-specific thinking (unchanged)
    "google_thinking_level": None,
    "openai_reasoning_effort": None,
    "anthropic_effort": None,

    # Debate settings (unchanged)
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,

    # NEW: Crypto-specific data vendors
    "data_vendors": {
        "price_volume_data": "cryptocompare",     # Options: binance, coinbase, cryptocompare, coingecko
        "on_chain_metrics": "glassnode",          # Options: glassnode, coinmetrics, blockchain_info
        "technical_indicators": "cryptocompare",   # Calculated from price data
        "news_data": "cryptopanic",               # Options: cryptopanic, coindesk, messari
        "social_sentiment": "lunarcrush",         # Options: lunarcrush, santiment
        "exchange_data": "ccxt",                  # Multi-exchange aggregation
        "derivatives_data": "coinglass",          # Options: coinglass, bybt
    },

    # NEW: Crypto-specific settings
    "crypto_settings": {
        "base_currency": "BTC",                   # Primary crypto asset
        "quote_currency": "USDT",                 # Trading pair (BTC/USDT)
        "exchanges": ["binance", "coinbase", "kraken"],  # Exchanges to monitor
        "include_derivatives": True,              # Include futures/perps data
        "time_interval": "1h",                    # Analysis interval (1m, 5m, 15m, 1h, 4h, 1d)
        "lookback_days": 30,                      # Historical data range
        "market_cap_threshold": 1000000000,       # $1B minimum
    },

    # NEW: Risk parameters for crypto volatility
    "risk_settings": {
        "max_leverage": 3,                        # Maximum leverage allowed
        "stop_loss_pct": 0.05,                    # 5% stop loss (tighter than stocks)
        "position_size_pct": 0.1,                 # 10% of portfolio per position
        "volatility_multiplier": 2.0,             # Adjust for crypto volatility
    },

    # Tool-level overrides (optional)
    "tool_vendors": {},
}
```

**Key Changes**:
1. Replace `core_stock_apis`, `fundamental_data` with crypto-specific categories
2. Add `on_chain_metrics`, `social_sentiment`, `derivatives_data` categories
3. Add `crypto_settings` section for asset-specific configuration
4. Add `risk_settings` for crypto volatility management
5. Change default lookback from years to days (crypto moves faster)

---

### 2. Data State Management

#### **File**: `tradingagents/agents/utils/agent_states.py`
**Current Function**: Defines TypedDict state objects for debate tracking and agent communication

**Crypto Adaptation Design**:

```python
from typing import Annotated, Sequence
from datetime import date, timedelta, datetime
from typing_extensions import TypedDict, Optional
from langchain_openai import ChatOpenAI
from cryptoagents.agents import *
from langgraph.prebuilt import ToolNode
from langgraph.graph import END, StateGraph, START, MessagesState


# Investment debate state (unchanged structure)
class InvestDebateState(TypedDict):
    bull_history: Annotated[str, "Bullish Conversation history"]
    bear_history: Annotated[str, "Bearish Conversation history"]
    history: Annotated[str, "Conversation history"]
    current_response: Annotated[str, "Latest response"]
    judge_decision: Annotated[str, "Final judge decision"]
    count: Annotated[int, "Length of the current conversation"]


# Risk debate state (unchanged structure)
class RiskDebateState(TypedDict):
    aggressive_history: Annotated[str, "Aggressive Agent's Conversation history"]
    conservative_history: Annotated[str, "Conservative Agent's Conversation history"]
    neutral_history: Annotated[str, "Neutral Agent's Conversation history"]
    history: Annotated[str, "Conversation history"]
    latest_speaker: Annotated[str, "Analyst that spoke last"]
    current_aggressive_response: Annotated[str, "Latest response by the aggressive analyst"]
    current_conservative_response: Annotated[str, "Latest response by the conservative analyst"]
    current_neutral_response: Annotated[str, "Latest response by the neutral analyst"]
    judge_decision: Annotated[str, "Judge's decision"]
    count: Annotated[int, "Length of the current conversation"]


# MODIFIED: Agent state for crypto trading
class CryptoAgentState(MessagesState):
    # Changed from "company_of_interest" to "crypto_asset"
    crypto_asset: Annotated[str, "Cryptocurrency asset we are analyzing (e.g., BTC, ETH)"]
    trading_pair: Annotated[str, "Trading pair (e.g., BTC/USDT)"]

    # Changed from "trade_date" to support 24/7 trading
    analysis_timestamp: Annotated[str, "Timestamp for analysis in ISO format (YYYY-MM-DD HH:MM:SS UTC)"]

    sender: Annotated[str, "Agent that sent this message"]

    # Research step - MODIFIED
    price_volume_report: Annotated[str, "Report from the Price/Volume Analyst (replaces market_report)"]
    on_chain_report: Annotated[str, "Report from the On-Chain Analyst (NEW)"]
    sentiment_report: Annotated[str, "Report from the Sentiment Analyst (crypto-native sources)"]
    news_report: Annotated[str, "Report from the News Analyst (crypto news)"]

    # Optional: Market structure analysis
    exchange_report: Annotated[str, "Report on exchange dynamics and arbitrage (OPTIONAL)"]
    derivatives_report: Annotated[str, "Report on futures/perpetual swap data (OPTIONAL)"]

    # Researcher team discussion (unchanged structure)
    investment_debate_state: Annotated[InvestDebateState, "Current state of the debate on if to invest or not"]
    investment_plan: Annotated[str, "Plan generated by the Research Manager"]

    # Trader decision
    trader_investment_plan: Annotated[str, "Plan generated by the Crypto Trader"]

    # Risk management team discussion (unchanged structure)
    risk_debate_state: Annotated[RiskDebateState, "Current state of the debate on evaluating risk"]
    final_trade_decision: Annotated[str, "Final decision made by the Portfolio Manager"]
```

**Key Changes**:
1. Rename `company_of_interest` → `crypto_asset` (semantic clarity)
2. Add `trading_pair` field for quote currency tracking
3. Change `trade_date` → `analysis_timestamp` with full datetime (24/7 markets)
4. Replace `market_report` → `price_volume_report`
5. Remove `fundamentals_report`, add `on_chain_report`
6. Add optional `exchange_report` and `derivatives_report` fields
7. Keep debate state structures unchanged (universal logic)

---

#### **File**: `tradingagents/agents/utils/memory.py`
**Current Function**: BM25-based retrieval system for storing financial situations and recommendations

**Crypto Adaptation Design**:
- **Minimal changes required** - the memory system is domain-agnostic
- BM25 tokenization works equally well for crypto terminology

**Suggested Enhancement**:
```python
class CryptoSituationMemory(FinancialSituationMemory):
    """Extended memory for crypto-specific terminology."""

    def _tokenize(self, text: str) -> List[str]:
        """Enhanced tokenization for crypto terms."""
        # Base tokenization
        tokens = super()._tokenize(text)

        # Preserve crypto-specific terms
        # Example: "BTC/USDT" should stay together, not split
        crypto_patterns = [
            r'BTC', r'ETH', r'USDT', r'USDC',  # Tickers
            r'\w+/\w+',  # Trading pairs (BTC/USDT)
            r'\$\d+[KMB]',  # Price levels ($50K, $1M)
            r'\d+x',  # Leverage (10x, 100x)
        ]

        # Additional preprocessing for crypto terms
        # Implementation would use regex to identify and preserve these patterns

        return tokens
```

**Recommendation**: Start with the base `FinancialSituationMemory` unchanged. Only add crypto-specific tokenization if retrieval quality is poor.

---

### 3. Data Tools & Interfaces

#### **File**: `tradingagents/agents/utils/agent_utils.py`
**Current Function**: Provides `build_instrument_context()` for ticker preservation and imports all tools

**Crypto Adaptation Design**:

```python
from langchain_core.messages import HumanMessage, RemoveMessage

# Import crypto-specific tools
from cryptoagents.agents.utils.price_volume_tools import (
    get_crypto_price_data,
    get_orderbook_data,
    get_volume_profile
)
from cryptoagents.agents.utils.technical_indicators_tools import (
    get_indicators  # Same as stocks, but crypto-tuned
)
from cryptoagents.agents.utils.on_chain_tools import (
    get_network_metrics,
    get_whale_movements,
    get_exchange_flows,
    get_hash_rate
)
from cryptoagents.agents.utils.news_data_tools import (
    get_crypto_news,
    get_regulatory_news,
    get_global_crypto_news
)
from cryptoagents.agents.utils.sentiment_tools import (
    get_social_sentiment,
    get_fear_greed_index,
    get_reddit_sentiment
)


def build_crypto_context(crypto_asset: str, trading_pair: str) -> str:
    """Describe the exact cryptocurrency asset for agent analysis."""
    return (
        f"The cryptocurrency to analyze is `{crypto_asset}`. "
        f"The trading pair is `{trading_pair}`. "
        "Use these exact identifiers in every tool call, report, and recommendation. "
        f"Note that {crypto_asset} trades 24/7 across multiple exchanges. "
        "Timestamps should be in UTC format. "
        f"When referencing prices, always specify the exchange if relevant."
    )


def create_msg_delete():
    """Same as original - no changes needed."""
    def delete_messages(state):
        messages = state["messages"]
        removal_operations = [RemoveMessage(id=m.id) for m in messages]
        placeholder = HumanMessage(content="Continue")
        return {"messages": removal_operations + [placeholder]}
    return delete_messages
```

**Key Changes**:
1. Replace `build_instrument_context()` → `build_crypto_context()`
2. Accept both `crypto_asset` and `trading_pair` parameters
3. Add notes about 24/7 trading and multi-exchange dynamics
4. Import crypto-specific tool sets

---

#### **File**: `tradingagents/agents/utils/core_stock_tools.py`
**Current Function**: Provides `get_stock_data()` tool for OHLCV data

**Crypto Adaptation Design**:
**New File**: `cryptoagents/agents/utils/price_volume_tools.py`

```python
from langchain_core.tools import tool
from typing import Annotated
from cryptoagents.dataflows.interface import route_to_vendor


@tool
def get_crypto_price_data(
    symbol: Annotated[str, "Cryptocurrency symbol (e.g., BTC, ETH)"],
    trading_pair: Annotated[str, "Trading pair (e.g., USDT, USD, EUR)"],
    start_datetime: Annotated[str, "Start datetime in ISO format (YYYY-MM-DD HH:MM:SS UTC)"],
    end_datetime: Annotated[str, "End datetime in ISO format (YYYY-MM-DD HH:MM:SS UTC)"],
    interval: Annotated[str, "Time interval: 1m, 5m, 15m, 1h, 4h, 1d"] = "1h",
    exchange: Annotated[str, "Specific exchange (optional, aggregates if not specified)"] = None,
) -> str:
    """
    Retrieve cryptocurrency price data (OHLCV) for a given symbol and trading pair.
    Uses the configured price_volume_data vendor.

    Args:
        symbol: Crypto symbol (BTC, ETH, etc.)
        trading_pair: Quote currency (USDT, USD, EUR)
        start_datetime: Start timestamp in ISO format (24/7 trading)
        end_datetime: End timestamp in ISO format
        interval: Candlestick interval (1m to 1d)
        exchange: Optional specific exchange, aggregates across exchanges if None

    Returns:
        str: Formatted dataframe with OHLCV data including volume and trade count
    """
    return route_to_vendor(
        "get_crypto_price_data",
        symbol,
        trading_pair,
        start_datetime,
        end_datetime,
        interval,
        exchange
    )


@tool
def get_orderbook_data(
    symbol: Annotated[str, "Cryptocurrency symbol"],
    trading_pair: Annotated[str, "Trading pair"],
    exchange: Annotated[str, "Exchange name (binance, coinbase, kraken)"],
    depth: Annotated[int, "Order book depth (number of price levels)"] = 20,
) -> str:
    """
    Retrieve current order book data showing bid/ask levels.
    Useful for understanding immediate supply/demand and liquidity.

    Returns:
        str: Formatted order book with bid/ask prices and volumes
    """
    return route_to_vendor("get_orderbook_data", symbol, trading_pair, exchange, depth)


@tool
def get_volume_profile(
    symbol: Annotated[str, "Cryptocurrency symbol"],
    trading_pair: Annotated[str, "Trading pair"],
    start_datetime: Annotated[str, "Start datetime"],
    end_datetime: Annotated[str, "End datetime"],
) -> str:
    """
    Retrieve volume profile showing price levels with highest trading activity.
    Identifies support/resistance zones based on volume.

    Returns:
        str: Volume profile data with price levels and volume concentrations
    """
    return route_to_vendor("get_volume_profile", symbol, trading_pair, start_datetime, end_datetime)
```

**Key Changes from `core_stock_tools.py`**:
1. Add `trading_pair` parameter (crypto always trades in pairs)
2. Replace `start_date`/`end_date` → `start_datetime`/`end_datetime` (24/7 precision)
3. Add `interval` parameter (crypto supports minute-level granularity)
4. Add `exchange` parameter (multi-exchange ecosystem)
5. Add `get_orderbook_data()` tool (critical for crypto liquidity)
6. Add `get_volume_profile()` tool (important for crypto support/resistance)

---

#### **File**: `tradingagents/agents/utils/technical_indicators_tools.py`
**Current Function**: Provides `get_indicators()` for RSI, MACD, Bollinger Bands, etc.

**Crypto Adaptation Design**:
**Keep same file, modify parameters**:

```python
from langchain_core.tools import tool
from typing import Annotated
from cryptoagents.dataflows.interface import route_to_vendor

@tool
def get_indicators(
    symbol: Annotated[str, "Cryptocurrency symbol"],
    trading_pair: Annotated[str, "Trading pair"],
    indicator: Annotated[str, "Technical indicator to calculate"],
    curr_datetime: Annotated[str, "Current analysis datetime in ISO format"],
    lookback_hours: Annotated[int, "How many hours to look back"] = 168,  # Default 7 days
    interval: Annotated[str, "Time interval: 1m, 5m, 15m, 1h, 4h, 1d"] = "1h",
) -> str:
    """
    Retrieve a single technical indicator for a cryptocurrency.

    Args:
        symbol: Crypto symbol (BTC, ETH, etc.)
        trading_pair: Quote currency (USDT, USD, EUR)
        indicator: Indicator name (rsi, macd, boll_ub, etc.) - call once per indicator
        curr_datetime: Current analysis timestamp
        lookback_hours: Hours of historical data (crypto moves faster than stocks)
        interval: Candlestick interval

    Returns:
        str: Formatted dataframe with indicator values over time

    Supported indicators (crypto-tuned):
    - RSI (14-period default, overbought 70, oversold 30)
    - MACD (12, 26, 9 - standard but faster reaction in crypto)
    - Bollinger Bands (20-period, 2 std dev)
    - EMA (10, 20, 50, 100, 200)
    - ATR (14-period - critical for volatile crypto markets)
    - Volume Weighted Moving Average (VWMA)
    - MFI (Money Flow Index - 14-period)
    """
    # Split comma-separated indicators (same logic as stocks)
    indicators = [i.strip() for i in indicator.split(",") if i.strip()]
    if len(indicators) > 1:
        results = []
        for ind in indicators:
            results.append(route_to_vendor(
                "get_indicators",
                symbol,
                trading_pair,
                ind,
                curr_datetime,
                lookback_hours,
                interval
            ))
        return "\n\n".join(results)

    return route_to_vendor(
        "get_indicators",
        symbol,
        trading_pair,
        indicator.strip(),
        curr_datetime,
        lookback_hours,
        interval
    )
```

**Key Changes**:
1. Add `trading_pair` parameter
2. Change `curr_date` → `curr_datetime` (24/7 precision)
3. Change `look_back_days` → `lookback_hours` (crypto moves faster)
4. Add `interval` parameter
5. Same indicators, but note crypto-specific tuning in docs
6. Keep multi-indicator split logic (works well)

---

#### **File**: `tradingagents/agents/utils/fundamental_data_tools.py`
**Current Function**: Provides tools for balance sheets, cash flow, income statements

**Crypto Adaptation Design**:
**Replace entire file** with:
**New File**: `cryptoagents/agents/utils/on_chain_tools.py`

```python
from langchain_core.tools import tool
from typing import Annotated
from cryptoagents.dataflows.interface import route_to_vendor


@tool
def get_network_metrics(
    symbol: Annotated[str, "Cryptocurrency symbol (e.g., BTC)"],
    start_datetime: Annotated[str, "Start datetime in ISO format"],
    end_datetime: Annotated[str, "End datetime in ISO format"],
) -> str:
    """
    Retrieve on-chain network metrics for fundamental analysis.

    Metrics include:
    - Active addresses (daily/monthly)
    - Transaction count
    - Transaction volume (USD)
    - Average transaction value
    - Network difficulty
    - Hash rate (for PoW chains like Bitcoin)
    - Fees paid (total and average)

    These metrics serve as "fundamentals" for cryptocurrencies, similar to
    revenue and user growth for companies.

    Uses the configured on_chain_metrics vendor.

    Returns:
        str: Formatted report with network health indicators
    """
    return route_to_vendor("get_network_metrics", symbol, start_datetime, end_datetime)


@tool
def get_whale_movements(
    symbol: Annotated[str, "Cryptocurrency symbol"],
    min_value_usd: Annotated[float, "Minimum transaction value in USD to track"] = 1000000,
    lookback_hours: Annotated[int, "Hours to look back"] = 24,
) -> str:
    """
    Track large transactions (whale movements) that could indicate
    accumulation or distribution by major holders.

    Identifies:
    - Large transfers to/from exchanges (selling pressure indicators)
    - Accumulation by long-term holders
    - Whale wallet behavior patterns
    - Exchange reserves changes

    Uses on_chain_metrics vendor.

    Returns:
        str: Report of significant on-chain movements
    """
    return route_to_vendor("get_whale_movements", symbol, min_value_usd, lookback_hours)


@tool
def get_exchange_flows(
    symbol: Annotated[str, "Cryptocurrency symbol"],
    lookback_hours: Annotated[int, "Hours to look back"] = 168,  # 7 days
) -> str:
    """
    Analyze inflows/outflows to cryptocurrency exchanges.

    Key insights:
    - Net inflow to exchanges = potential selling pressure (bearish)
    - Net outflow from exchanges = accumulation in cold storage (bullish)
    - Exchange reserve levels
    - Velocity of exchange movements

    Uses on_chain_metrics vendor.

    Returns:
        str: Report on exchange flow dynamics
    """
    return route_to_vendor("get_exchange_flows", symbol, lookback_hours)


@tool
def get_hash_rate(
    symbol: Annotated[str, "Cryptocurrency symbol (PoW chains only, e.g., BTC)"],
    start_datetime: Annotated[str, "Start datetime"],
    end_datetime: Annotated[str, "End datetime"],
) -> str:
    """
    Retrieve hash rate data for Proof-of-Work cryptocurrencies.

    Hash rate indicates:
    - Network security strength
    - Miner confidence (higher hash rate = more investment in mining)
    - Difficulty adjustments
    - Mining profitability trends

    Rising hash rate is generally bullish (more security, miner confidence).
    Falling hash rate may indicate miner capitulation (can be bullish if it leads to difficulty adjustment).

    Uses on_chain_metrics vendor.

    Returns:
        str: Hash rate trends and analysis
    """
    return route_to_vendor("get_hash_rate", symbol, start_datetime, end_datetime)


@tool
def get_holder_distribution(
    symbol: Annotated[str, "Cryptocurrency symbol"],
) -> str:
    """
    Analyze distribution of holdings across wallet addresses.

    Metrics:
    - Top 1% holder percentage
    - Top 10% holder percentage
    - Number of addresses holding >$1M
    - Distribution Gini coefficient
    - Long-term holder vs short-term holder ratio

    More decentralized distribution is generally healthier.
    Increasing long-term holder percentage is bullish.

    Uses on_chain_metrics vendor.

    Returns:
        str: Holder distribution analysis
    """
    return route_to_vendor("get_holder_distribution", symbol)
```

**Rationale**:
- Cryptocurrencies have NO traditional fundamentals (no balance sheet, no income statement)
- On-chain metrics serve as the "fundamental analysis" layer
- These metrics are unique to blockchain assets and crucial for informed decisions
- Network health (active addresses, hash rate) = company revenue growth
- Whale movements = insider trading indicators
- Exchange flows = supply/demand pressure

---

#### **File**: `tradingagents/agents/utils/news_data_tools.py`
**Current Function**: Provides `get_news()`, `get_global_news()`, `get_insider_transactions()`

**Crypto Adaptation Design**:

```python
from langchain_core.tools import tool
from typing import Annotated
from cryptoagents.dataflows.interface import route_to_vendor


@tool
def get_crypto_news(
    symbol: Annotated[str, "Cryptocurrency symbol"],
    start_datetime: Annotated[str, "Start datetime in ISO format"],
    end_datetime: Annotated[str, "End datetime in ISO format"],
) -> str:
    """
    Retrieve cryptocurrency-specific news from crypto-native sources.

    Sources include:
    - CoinDesk, CoinTelegraph, The Block
    - Crypto Twitter influencers
    - Project-specific announcements
    - Protocol upgrades/forks
    - Partnership announcements

    Uses the configured news_data vendor.

    Returns:
        str: Formatted news articles with sentiment indicators
    """
    return route_to_vendor("get_crypto_news", symbol, start_datetime, end_datetime)


@tool
def get_regulatory_news(
    start_datetime: Annotated[str, "Start datetime"],
    end_datetime: Annotated[str, "End datetime"],
    regions: Annotated[list, "Geographic regions to focus on"] = None,
) -> str:
    """
    Retrieve regulatory news that impacts cryptocurrency markets.

    Coverage:
    - Government policy changes
    - SEC/CFTC statements and actions
    - Country-level bans or adoptions
    - Exchange regulatory issues
    - ETF approval/rejection news
    - Central bank digital currency (CBDC) developments

    Regulatory news has HUGE impact on crypto prices.

    Uses news_data vendor.

    Returns:
        str: Regulatory news summary with impact analysis
    """
    return route_to_vendor("get_regulatory_news", start_datetime, end_datetime, regions)


@tool
def get_global_crypto_news(
    curr_datetime: Annotated[str, "Current datetime"],
    lookback_hours: Annotated[int, "Hours to look back"] = 24,
    limit: Annotated[int, "Max number of articles"] = 10,
) -> str:
    """
    Retrieve global cryptocurrency market news.

    Covers:
    - Major market movements
    - Exchange hacks/issues
    - Bitcoin ETF news
    - Institutional adoption
    - Macro crypto trends
    - DeFi protocol exploits

    Uses news_data vendor.

    Returns:
        str: Global crypto news summary
    """
    return route_to_vendor("get_global_crypto_news", curr_datetime, lookback_hours, limit)


@tool
def get_social_sentiment(
    symbol: Annotated[str, "Cryptocurrency symbol"],
    lookback_hours: Annotated[int, "Hours to look back"] = 24,
) -> str:
    """
    Analyze social media sentiment from crypto-native platforms.

    Sources:
    - Twitter/X (crypto Twitter is extremely influential)
    - Reddit (r/Bitcoin, r/CryptoCurrency)
    - Telegram groups
    - Discord communities

    Metrics:
    - Sentiment score (-1 to +1)
    - Volume of mentions
    - Engagement rate
    - Influencer sentiment
    - Fear & Greed Index correlation

    Social sentiment has MUCH stronger correlation with crypto prices than stocks.

    Uses social_sentiment vendor.

    Returns:
        str: Comprehensive social sentiment analysis
    """
    return route_to_vendor("get_social_sentiment", symbol, lookback_hours)


@tool
def get_fear_greed_index(
    lookback_days: Annotated[int, "Days to look back"] = 7,
) -> str:
    """
    Retrieve the Crypto Fear & Greed Index.

    This index (0-100) measures market sentiment:
    - 0-24: Extreme Fear (potential buying opportunity)
    - 25-49: Fear
    - 50: Neutral
    - 51-75: Greed
    - 76-100: Extreme Greed (potential selling opportunity)

    Based on:
    - Volatility (25%)
    - Market momentum/volume (25%)
    - Social media (15%)
    - Surveys (15%)
    - Bitcoin dominance (10%)
    - Google Trends (10%)

    This is a crypto-specific sentiment indicator with no stock market equivalent.

    Uses sentiment vendor.

    Returns:
        str: Fear & Greed Index history and current reading
    """
    return route_to_vendor("get_fear_greed_index", lookback_days)
```

**Key Changes**:
1. Replace `get_news()` → `get_crypto_news()` with crypto-native sources
2. Remove `get_insider_transactions()` (no corporate insiders in crypto)
3. Add `get_regulatory_news()` (critical for crypto)
4. Modify `get_global_news()` → `get_global_crypto_news()` with crypto focus
5. Add `get_social_sentiment()` (more important for crypto than stocks)
6. Add `get_fear_greed_index()` (crypto-specific sentiment metric)

---

### 4. Data Retrieval Layer

#### **File**: `tradingagents/dataflows/interface.py`
**Current Function**: Routes data requests to configured vendors (yfinance, Alpha Vantage)

**Crypto Adaptation Design**:

```python
from typing import Annotated

# Import from crypto vendor-specific modules
from .cryptocompare_api import (
    get_crypto_price_data as get_cryptocompare_price,
    get_indicators as get_cryptocompare_indicators,
)
from .binance_api import (
    get_crypto_price_data as get_binance_price,
    get_orderbook_data as get_binance_orderbook,
)
from .glassnode_api import (
    get_network_metrics as get_glassnode_network,
    get_whale_movements as get_glassnode_whales,
    get_exchange_flows as get_glassnode_flows,
    get_hash_rate as get_glassnode_hashrate,
)
from .lunarcrush_api import (
    get_social_sentiment as get_lunarcrush_sentiment,
)
from .cryptopanic_api import (
    get_crypto_news as get_cryptopanic_news,
)
from .coinglass_api import (
    get_derivatives_data as get_coinglass_derivatives,
)

# Configuration and routing logic
from .config import get_config

# Tools organized by category - CRYPTO VERSION
TOOLS_CATEGORIES = {
    "price_volume_data": {
        "description": "OHLCV crypto price and volume data",
        "tools": [
            "get_crypto_price_data",
            "get_orderbook_data",
            "get_volume_profile",
        ]
    },
    "on_chain_metrics": {
        "description": "Blockchain network metrics (crypto fundamentals)",
        "tools": [
            "get_network_metrics",
            "get_whale_movements",
            "get_exchange_flows",
            "get_hash_rate",
            "get_holder_distribution",
        ]
    },
    "technical_indicators": {
        "description": "Technical analysis indicators",
        "tools": [
            "get_indicators",
        ]
    },
    "news_data": {
        "description": "Crypto news and regulatory updates",
        "tools": [
            "get_crypto_news",
            "get_regulatory_news",
            "get_global_crypto_news",
        ]
    },
    "social_sentiment": {
        "description": "Social media sentiment and community analysis",
        "tools": [
            "get_social_sentiment",
            "get_fear_greed_index",
        ]
    },
    "derivatives_data": {
        "description": "Futures and perpetual swap data",
        "tools": [
            "get_open_interest",
            "get_funding_rates",
            "get_liquidations",
        ]
    },
}

VENDOR_LIST = [
    "cryptocompare",
    "binance",
    "coinbase",
    "glassnode",
    "coinmetrics",
    "lunarcrush",
    "cryptopanic",
    "coinglass",
]

# Mapping of methods to their vendor-specific implementations
VENDOR_METHODS = {
    # price_volume_data
    "get_crypto_price_data": {
        "cryptocompare": get_cryptocompare_price,
        "binance": get_binance_price,
    },
    "get_orderbook_data": {
        "binance": get_binance_orderbook,
    },

    # on_chain_metrics
    "get_network_metrics": {
        "glassnode": get_glassnode_network,
    },
    "get_whale_movements": {
        "glassnode": get_glassnode_whales,
    },
    "get_exchange_flows": {
        "glassnode": get_glassnode_flows,
    },
    "get_hash_rate": {
        "glassnode": get_glassnode_hashrate,
    },

    # technical_indicators (calculated from price data)
    "get_indicators": {
        "cryptocompare": get_cryptocompare_indicators,
    },

    # news_data
    "get_crypto_news": {
        "cryptopanic": get_cryptopanic_news,
    },

    # social_sentiment
    "get_social_sentiment": {
        "lunarcrush": get_lunarcrush_sentiment,
    },
}


def get_category_for_method(method: str) -> str:
    """Get the category that contains the specified method."""
    for category, info in TOOLS_CATEGORIES.items():
        if method in info["tools"]:
            return category
    raise ValueError(f"Method '{method}' not found in any category")


def get_vendor(category: str, method: str = None) -> str:
    """Get the configured vendor for a data category or specific tool method."""
    config = get_config()

    # Check tool-level configuration first
    if method:
        tool_vendors = config.get("tool_vendors", {})
        if method in tool_vendors:
            return tool_vendors[method]

    # Fall back to category-level configuration
    return config.get("data_vendors", {}).get(category, "default")


def route_to_vendor(method: str, *args, **kwargs):
    """Route method calls to appropriate crypto data vendor with fallback support."""
    category = get_category_for_method(method)
    vendor_config = get_vendor(category, method)
    primary_vendors = [v.strip() for v in vendor_config.split(',')]

    if method not in VENDOR_METHODS:
        raise ValueError(f"Method '{method}' not supported")

    # Build fallback chain
    all_available_vendors = list(VENDOR_METHODS[method].keys())
    fallback_vendors = primary_vendors.copy()
    for vendor in all_available_vendors:
        if vendor not in fallback_vendors:
            fallback_vendors.append(vendor)

    for vendor in fallback_vendors:
        if vendor not in VENDOR_METHODS[method]:
            continue

        vendor_impl = VENDOR_METHODS[method][vendor]
        impl_func = vendor_impl[0] if isinstance(vendor_impl, list) else vendor_impl

        try:
            return impl_func(*args, **kwargs)
        except Exception as e:
            # For crypto, we might have multiple rate limit errors, API key issues, etc.
            # Log and continue to next vendor
            print(f"Vendor {vendor} failed for {method}: {str(e)}")
            continue

    raise RuntimeError(f"No available vendor for '{method}'")
```

**Key Changes**:
1. Replace stock vendors with crypto vendors
2. New categories: `on_chain_metrics`, `social_sentiment`, `derivatives_data`
3. Remove: `fundamental_data` category
4. Add crypto-specific vendors: Glassnode, CryptoCompare, LunarCrush, CryptoPanic, Coinglass
5. Same fallback logic (works well)

---

#### **File**: `tradingagents/dataflows/y_finance.py`
**Current Function**: Implements yfinance data retrieval for stocks

**Crypto Adaptation Design**:
**New File**: `cryptoagents/dataflows/cryptocompare_api.py`

```python
from typing import Annotated
from datetime import datetime
import requests
import pandas as pd
import os

# CryptoCompare API wrapper (free tier available)

CRYPTOCOMPARE_API_KEY = os.getenv("CRYPTOCOMPARE_API_KEY")
BASE_URL = "https://min-api.cryptocompare.com/data"


def get_crypto_price_data(
    symbol: Annotated[str, "Cryptocurrency symbol (e.g., BTC)"],
    trading_pair: Annotated[str, "Trading pair (e.g., USDT, USD)"],
    start_datetime: Annotated[str, "Start datetime in ISO format"],
    end_datetime: Annotated[str, "End datetime in ISO format"],
    interval: Annotated[str, "Time interval: 1m, 5m, 15m, 1h, 4h, 1d"] = "1h",
    exchange: Annotated[str, "Specific exchange (optional)"] = None,
):
    """Retrieve crypto OHLCV data from CryptoCompare."""

    # Parse datetime strings
    start_dt = datetime.fromisoformat(start_datetime.replace("Z", "+00:00"))
    end_dt = datetime.fromisoformat(end_datetime.replace("Z", "+00:00"))

    # Map interval to CryptoCompare API endpoint
    interval_map = {
        "1m": "histominute",
        "5m": "histominute",
        "15m": "histominute",
        "1h": "histohour",
        "4h": "histohour",
        "1d": "histoday",
    }

    endpoint = interval_map.get(interval, "histohour")

    # Build API request
    params = {
        "fsym": symbol.upper(),
        "tsym": trading_pair.upper(),
        "limit": 2000,  # Max per request
        "toTs": int(end_dt.timestamp()),
        "api_key": CRYPTOCOMPARE_API_KEY,
    }

    if exchange:
        params["e"] = exchange

    url = f"{BASE_URL}/{endpoint}"

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data["Response"] == "Error":
            return f"Error retrieving data for {symbol}/{trading_pair}: {data.get('Message', 'Unknown error')}"

        # Parse OHLCV data
        df = pd.DataFrame(data["Data"])
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df = df.rename(columns={
            "time": "Timestamp",
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volumefrom": "Volume",
        })

        # Filter by date range
        df = df[(df["Timestamp"] >= start_dt) & (df["Timestamp"] <= end_dt)]

        if df.empty:
            return f"No data found for {symbol}/{trading_pair} between {start_datetime} and {end_datetime}"

        # Format output
        csv_string = df.to_csv(index=False)
        header = f"# Crypto price data for {symbol}/{trading_pair} from {start_datetime} to {end_datetime}\n"
        header += f"# Interval: {interval}\n"
        header += f"# Total records: {len(df)}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"

        return header + csv_string

    except Exception as e:
        return f"Error fetching data from CryptoCompare: {str(e)}"


def get_indicators(
    symbol: Annotated[str, "Cryptocurrency symbol"],
    trading_pair: Annotated[str, "Trading pair"],
    indicator: Annotated[str, "Technical indicator"],
    curr_datetime: Annotated[str, "Current datetime"],
    lookback_hours: Annotated[int, "Hours to look back"],
    interval: Annotated[str, "Time interval"] = "1h",
) -> str:
    """Calculate technical indicators from crypto price data."""

    # First, fetch the price data
    from datetime import timedelta
    curr_dt = datetime.fromisoformat(curr_datetime.replace("Z", "+00:00"))
    start_dt = curr_dt - timedelta(hours=lookback_hours)

    price_data_str = get_crypto_price_data(
        symbol,
        trading_pair,
        start_dt.isoformat(),
        curr_dt.isoformat(),
        interval,
    )

    # Parse CSV string back to DataFrame
    from io import StringIO
    # Skip header lines (start with #)
    lines = [line for line in price_data_str.split('\n') if not line.startswith('#')]
    csv_data = '\n'.join(lines)
    df = pd.read_csv(StringIO(csv_data))

    # Calculate indicator using stockstats or ta-lib
    from stockstats import StockDataFrame
    stock_df = StockDataFrame.retype(df.copy())

    # Map indicator names
    indicator_column = indicator.lower()

    try:
        # Trigger calculation
        stock_df[indicator_column]

        # Format output
        result_df = stock_df[["Timestamp", indicator_column]].copy()
        result_df = result_df.rename(columns={indicator_column: indicator.upper()})

        csv_output = result_df.to_csv(index=False)
        header = f"# {indicator.upper()} for {symbol}/{trading_pair}\n"
        header += f"# Interval: {interval}, Lookback: {lookback_hours} hours\n\n"

        return header + csv_output

    except Exception as e:
        return f"Error calculating indicator {indicator}: {str(e)}"
```

**Key Differences from yfinance implementation**:
1. Uses CryptoCompare API instead of yfinance
2. Supports multiple exchanges
3. Timestamp-based queries (24/7 data)
4. No quarterly reports, no fundamentals
5. Same indicator calculation logic (stockstats works for crypto too)

**Additional Vendor Files Needed**:
- `cryptoagents/dataflows/binance_api.py` - Direct exchange API
- `cryptoagents/dataflows/glassnode_api.py` - On-chain metrics
- `cryptoagents/dataflows/lunarcrush_api.py` - Social sentiment
- `cryptoagents/dataflows/cryptopanic_api.py` - Crypto news aggregation
- `cryptoagents/dataflows/coinglass_api.py` - Derivatives data

---

### 5. Agent Implementations

#### **File**: `tradingagents/agents/analysts/market_analyst.py`
**Current Function**: Analyzes technical indicators and price movements for stocks

**Crypto Adaptation Design**:
**New File**: `cryptoagents/agents/analysts/price_volume_analyst.py`

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from cryptoagents.agents.utils.agent_utils import (
    build_crypto_context,
    get_crypto_price_data,
    get_indicators,
    get_orderbook_data,
    get_volume_profile,
)
from cryptoagents.dataflows.config import get_config


def create_price_volume_analyst(llm):

    def price_volume_analyst_node(state):
        current_datetime = state["analysis_timestamp"]
        crypto_asset = state["crypto_asset"]
        trading_pair = state["trading_pair"]
        crypto_context = build_crypto_context(crypto_asset, trading_pair)

        tools = [
            get_crypto_price_data,
            get_indicators,
            get_orderbook_data,
            get_volume_profile,
        ]

        system_message = (
            f"""You are a cryptocurrency price and volume analyst specializing in {crypto_asset}. Your role is to analyze 24/7 market dynamics across multiple exchanges and identify trading opportunities using technical indicators and volume analysis.

Key Considerations for Crypto Markets:
- **24/7 Trading**: Markets never close; analyze intraday patterns differently than stocks
- **Higher Volatility**: Crypto can move 10-20% in hours; adjust risk parameters accordingly
- **Multi-Exchange**: Check for arbitrage opportunities and liquidity differences
- **Psychological Levels**: Round numbers (e.g., $50,000, $100,000) act as strong support/resistance
- **Whale Activity**: Large orders in order books can predict price movements

From the following indicator categories, select up to **8 complementary indicators** that provide diverse insights without redundancy:

**Moving Averages** (Trend Identification):
- close_50_ema: 50 EMA (prefer EMA over SMA for crypto's faster movements)
- close_200_ema: 200 EMA (long-term trend anchor)
- close_10_ema: 10 EMA (short-term momentum)

**MACD Related** (Momentum & Trend Changes):
- macd: MACD line (12, 26, 9 periods)
- macds: MACD signal line
- macdh: MACD histogram (momentum strength)

**Momentum Indicators**:
- rsi: RSI (14-period; overbought >70, oversold <30, but crypto can stay extreme longer)
- mfi: Money Flow Index (volume-weighted RSI; critical for crypto)

**Volatility Indicators** (Critical for Crypto):
- boll: Bollinger Middle (20-period)
- boll_ub: Bollinger Upper Band (expect frequent touches in crypto)
- boll_lb: Bollinger Lower Band
- atr: Average True Range (essential for stop-loss placement in volatile markets)

**Volume-Based Indicators**:
- vwma: Volume Weighted Moving Average (shows where volume accumulates)
- volume_profile: Shows price levels with highest trading activity

**Crypto-Specific Analysis**:
- Order book depth (bid/ask walls, liquidity zones)
- Volume spikes (precede major moves)
- Exchange-specific patterns

Your task:
1. Call get_crypto_price_data first to retrieve OHLCV data
2. Select up to 8 complementary indicators and call get_indicators for each
3. Optionally call get_orderbook_data to assess current liquidity
4. Write a detailed, nuanced report on:
   - Current trend direction (bullish/bearish/neutral)
   - Momentum strength
   - Support/resistance levels
   - Volume analysis (accumulation/distribution)
   - Order book insights
   - Key price levels to watch
5. Provide specific, actionable insights with supporting evidence
6. Append a Markdown table summarizing key findings

Remember: Crypto markets move FAST. Your analysis should be time-sensitive and account for the 24/7 nature of trading."""
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    " For your reference, the current datetime is {current_datetime} (UTC). {crypto_context}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_datetime=current_datetime)
        prompt = prompt.partial(crypto_context=crypto_context)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""
        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "price_volume_report": report,
        }

    return price_volume_analyst_node
```

**Key Changes from `market_analyst.py`**:
1. Rename function → `create_price_volume_analyst()`
2. Add crypto-specific context about 24/7 markets, volatility
3. Emphasize EMA over SMA (faster reaction for crypto)
4. Add order book analysis tools
5. Mention psychological price levels ($50K, $100K)
6. Emphasize ATR and MFI (more important for crypto)
7. Change date → datetime references
8. Add multi-exchange considerations

---

#### **File**: `tradingagents/agents/analysts/fundamentals_analyst.py`
**Current Function**: Analyzes financial statements and company metrics

**Crypto Adaptation Design**:
**New File**: `cryptoagents/agents/analysts/on_chain_analyst.py`

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from cryptoagents.agents.utils.agent_utils import (
    build_crypto_context,
    get_network_metrics,
    get_whale_movements,
    get_exchange_flows,
    get_hash_rate,
    get_holder_distribution,
)
from cryptoagents.dataflows.config import get_config


def create_on_chain_analyst(llm):
    def on_chain_analyst_node(state):
        current_datetime = state["analysis_timestamp"]
        crypto_asset = state["crypto_asset"]
        trading_pair = state["trading_pair"]
        crypto_context = build_crypto_context(crypto_asset, trading_pair)

        tools = [
            get_network_metrics,
            get_whale_movements,
            get_exchange_flows,
            get_hash_rate,
            get_holder_distribution,
        ]

        system_message = (
            f"""You are an on-chain analyst specializing in blockchain data for {crypto_asset}.

On-chain metrics serve as the "fundamental analysis" for cryptocurrencies, replacing traditional financial statements. Your role is to analyze network health, holder behavior, and supply/demand dynamics directly from blockchain data.

Key On-Chain Metrics to Analyze:

**Network Health & Growth**:
- Active Addresses: Proxy for network usage and adoption (like "daily active users")
- Transaction Count & Volume: Network activity level
- Hash Rate (for Bitcoin): Mining security and miner confidence
- Fees Paid: Network demand indicator

**Supply Dynamics**:
- Exchange Reserves: Crypto sitting on exchanges (available supply for selling)
  - Decreasing = accumulation (bullish)
  - Increasing = distribution (bearish)
- Whale Movements: Large transactions >$1M
  - To exchanges = potential selling pressure
  - From exchanges = accumulation
- Holder Distribution: Concentration vs decentralization
  - Increasing long-term holders = bullish

**Behavioral Indicators**:
- HODL Waves: Age of coins (old coins moving = potential sell-off)
- Realized Price: Average acquisition price of all coins
- MVRV Ratio: Market Value vs Realized Value (overvalued/undervalued)

Your Task:
1. Use get_network_metrics to assess overall network health
2. Use get_whale_movements to identify large holder activity
3. Use get_exchange_flows to gauge supply/demand pressure
4. Use get_hash_rate (for Bitcoin) to check miner confidence
5. Use get_holder_distribution to assess decentralization

Write a comprehensive report covering:
- Network growth trends (bullish/bearish)
- Holder behavior patterns (accumulation/distribution)
- Supply pressure indicators
- Comparison to historical norms
- Implications for price action

Provide specific, actionable insights with supporting on-chain evidence.
Append a Markdown table summarizing key on-chain metrics and their signals.

Think of this as analyzing a company's fundamentals, but using blockchain data instead of financial statements."""
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    " For your reference, the current datetime is {current_datetime} (UTC). {crypto_context}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_datetime=current_datetime)
        prompt = prompt.partial(crypto_context=crypto_context)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""
        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "on_chain_report": report,
        }

    return on_chain_analyst_node
```

**Rationale**:
- Completely replaces fundamentals analyst (no financial statements in crypto)
- On-chain data = crypto's "fundamentals"
- Network growth → revenue growth
- Holder behavior → insider/institutional activity
- Exchange flows → supply/demand pressure
- This is the MOST UNIQUE aspect of crypto analysis

---

#### **File**: `tradingagents/agents/analysts/news_analyst.py`
**Current Function**: Analyzes macroeconomic news and global events

**Crypto Adaptation Design**:
**Modify existing file**:

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from cryptoagents.agents.utils.agent_utils import (
    build_crypto_context,
    get_crypto_news,
    get_regulatory_news,
    get_global_crypto_news,
)
from cryptoagents.dataflows.config import get_config


def create_crypto_news_analyst(llm):
    def crypto_news_analyst_node(state):
        current_datetime = state["analysis_timestamp"]
        crypto_asset = state["crypto_asset"]
        trading_pair = state["trading_pair"]
        crypto_context = build_crypto_context(crypto_asset, trading_pair)

        tools = [
            get_crypto_news,
            get_regulatory_news,
            get_global_crypto_news,
        ]

        system_message = (
            f"""You are a cryptocurrency news analyst tracking global crypto market events, regulatory developments, and asset-specific news for {crypto_asset}.

Cryptocurrency markets are HIGHLY sensitive to news events. A single tweet or regulatory announcement can move prices 10-20% within hours.

**Key News Categories to Monitor**:

1. **Regulatory Developments** (CRITICAL):
   - SEC/CFTC actions and statements
   - Country-level bans or legal tender adoption
   - ETF approvals/rejections (major Bitcoin catalyst)
   - Exchange regulatory issues (e.g., Binance investigations)
   - CBDC (Central Bank Digital Currency) announcements

2. **Institutional Adoption**:
   - Corporate treasury Bitcoin purchases (e.g., MicroStrategy, Tesla)
   - Investment fund launches
   - Banking integration announcements
   - Payment processor adoption

3. **Technical/Protocol News**:
   - Network upgrades/forks
   - Security vulnerabilities or exploits
   - Developer activity and GitHub commits
   - Layer 2 scaling solutions

4. **Market Structure**:
   - Exchange hacks or insolvency
   - Stablecoin de-pegging events (USDT, USDC)
   - DeFi protocol exploits
   - Liquidation cascades

5. **Macro Crypto Trends**:
   - Bitcoin ETF inflows/outflows
   - Mining difficulty adjustments
   - Network congestion/fee spikes
   - Competing blockchain developments

**Social Media Influence**:
Crypto markets are heavily influenced by:
- Elon Musk tweets (historically 10-20% moves)
- Crypto influencer sentiment
- Reddit/Twitter trending topics
- FUD (Fear, Uncertainty, Doubt) campaigns

Your Task:
1. Use get_crypto_news to gather {crypto_asset}-specific news
2. Use get_regulatory_news to track government/regulatory developments
3. Use get_global_crypto_news for broader market events

Write a comprehensive report covering:
- Recent news impact on {crypto_asset}
- Regulatory developments and implications
- Market-moving events
- Upcoming catalysts (known events)
- Sentiment assessment (bullish/bearish)

Prioritize high-impact news over routine updates.
Provide specific, actionable insights with supporting evidence.
Append a Markdown table summarizing key news events and their potential impact.

Remember: In crypto, news often moves prices MORE than technical analysis."""
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    " For your reference, the current datetime is {current_datetime} (UTC). {crypto_context}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_datetime=current_datetime)
        prompt = prompt.partial(crypto_context=crypto_context)

        chain = prompt | llm.bind_tools(tools)
        result = chain.invoke(state["messages"])

        report = ""
        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "news_report": report,
        }

    return crypto_news_analyst_node
```

**Key Changes**:
1. Emphasize regulatory news (MUCH more important for crypto)
2. Add sections on institutional adoption, protocol upgrades
3. Highlight exchange risks and stablecoin issues
4. Mention social media influence (Elon Musk, crypto influencers)
5. Note that news > technicals for crypto price impact
6. Same structure, crypto-focused content

---

#### **File**: `tradingagents/agents/analysts/social_media_analyst.py`
**Current Function**: Analyzes sentiment from social media and news

**Crypto Adaptation Design**:
**Significantly enhance**:

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from cryptoagents.agents.utils.agent_utils import (
    build_crypto_context,
    get_social_sentiment,
    get_fear_greed_index,
    get_crypto_news,
)
from cryptoagents.dataflows.config import get_config


def create_crypto_sentiment_analyst(llm):
    def crypto_sentiment_analyst_node(state):
        current_datetime = state["analysis_timestamp"]
        crypto_asset = state["crypto_asset"]
        trading_pair = state["trading_pair"]
        crypto_context = build_crypto_context(crypto_asset, trading_pair)

        tools = [
            get_social_sentiment,
            get_fear_greed_index,
            get_crypto_news,  # News includes sentiment indicators
        ]

        system_message = (
            f"""You are a cryptocurrency sentiment analyst specializing in social media and community analysis for {crypto_asset}.

CRITICAL: Social sentiment has a MUCH STRONGER correlation with crypto prices than with stock prices. Crypto markets are highly retail-driven and sentiment-sensitive.

**Key Sentiment Sources**:

1. **Crypto Twitter (Most Important)**:
   - Elon Musk, Michael Saylor, Cathie Wood tweets
   - Crypto influencers (100K+ followers)
   - Trending hashtags (#Bitcoin, #BTC, #crypto)
   - Volume of mentions and engagement

2. **Reddit Communities**:
   - r/Bitcoin, r/CryptoCurrency
   - Post frequency and sentiment
   - Upvote/downvote ratios
   - Quality of discussions (memes vs analysis)

3. **Telegram/Discord**:
   - Community size and activity
   - Developer engagement
   - Whale wallet announcements

4. **Crypto Fear & Greed Index** (0-100):
   - <25: Extreme Fear (contrarian buy signal)
   - 25-49: Fear
   - 50: Neutral
   - 51-75: Greed
   - >75: Extreme Greed (contrarian sell signal)

**Sentiment Indicators**:
- Sentiment Score: -1 (very bearish) to +1 (very bullish)
- Volume of Mentions: Spikes precede major moves
- Sentiment Velocity: Rate of change in sentiment
- Influencer Sentiment: Weighted by follower count
- Retail vs Institutional Sentiment: Different behaviors

**Contrarian Indicators**:
- Extreme Fear = Potential buying opportunity
- Extreme Greed = Potential topping signal
- "This time is different" narratives = Major top warning
- Mainstream media FOMO = Late-stage rally

Your Task:
1. Use get_social_sentiment to analyze {crypto_asset} social media
2. Use get_fear_greed_index to assess overall market sentiment
3. Use get_crypto_news for sentiment-laden news coverage

Write a comprehensive report covering:
- Current sentiment reading (bullish/bearish/neutral)
- Sentiment trend (improving/deteriorating)
- Volume and quality of discussions
- Influencer sentiment
- Fear & Greed Index interpretation
- Contrarian signals (if any)
- Correlation with price action

Provide specific, actionable insights with supporting evidence.
Append a Markdown table summarizing key sentiment metrics.

Remember: Sentiment often leads price in crypto markets. Pay attention to sentiment CHANGES more than absolute levels."""
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    " For your reference, the current datetime is {current_datetime} (UTC). {crypto_context}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_datetime=current_datetime)
        prompt = prompt.partial(crypto_context=crypto_context)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""
        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "sentiment_report": report,
        }

    return crypto_sentiment_analyst_node
```

**Key Changes**:
1. **HUGE emphasis** on crypto-native social media (Twitter > everything)
2. Add Fear & Greed Index (crypto-specific metric)
3. Mention specific influencers (Elon, Saylor)
4. Emphasize contrarian indicators (extreme fear/greed)
5. Note that sentiment LEADS price in crypto
6. Reddit, Telegram, Discord are more important than for stocks

---

#### **Files**: `tradingagents/agents/researchers/bull_researcher.py`, `bear_researcher.py`, `managers/research_manager.py`
**Current Function**: Debate-driven investment evaluation

**Crypto Adaptation Design**:
- **Minimal changes** - debate structure is domain-agnostic
- Update prompts to reference:
  - "cryptocurrency" instead of "stock"
  - "price_volume_report", "on_chain_report" instead of "market_report", "fundamentals_report"
  - Higher volatility and 24/7 nature
  - Regulatory risks specific to crypto

Example modification for `bull_researcher.py`:

```python
prompt = f"""You are a Bull Analyst advocating for investing in {crypto_asset}.

Key points to focus on:
- **Adoption Growth**: Network activity, active addresses, institutional inflows
- **On-Chain Strength**: Decreasing exchange reserves, long-term holder accumulation
- **Technical Momentum**: Breaking resistance, positive momentum indicators
- **Narrative Strength**: Regulatory clarity, ETF approvals, macro tailwinds
- **Counter Bear Arguments**: Address volatility concerns, regulatory risks with data

Remember: Crypto markets are 24/7 and highly volatile. Your arguments should account for this environment.

Resources available:
Price/Volume Report: {price_volume_report}
On-Chain Report: {on_chain_report}
Sentiment Report: {sentiment_report}
News Report: {news_report}
Debate History: {history}
Last Bear Argument: {current_response}
Past Reflections: {past_memory_str}

Deliver a compelling bull argument emphasizing growth potential and competitive advantages in the crypto ecosystem."""
```

---

#### **Files**: `tradingagents/agents/trader/trader.py`, `managers/portfolio_manager.py`
**Current Function**: Final decision making

**Crypto Adaptation Design**:

**trader.py modification**:
```python
context = {
    "role": "user",
    "content": f"""Based on comprehensive analysis by a team of crypto specialists, here is an investment plan for {crypto_asset}. {crypto_context}

This plan incorporates:
- 24/7 price action and volume analysis
- On-chain metrics (network health, holder behavior)
- Crypto-native sentiment indicators
- Regulatory and news developments

IMPORTANT: Crypto markets trade 24/7 with high volatility. Position sizing and risk management are CRITICAL.

Proposed Investment Plan: {investment_plan}

Consider:
- Current market regime (bull/bear/sideways)
- Volatility levels (ATR, Bollinger Band width)
- Liquidity conditions
- Leverage implications (if any)
- Stop-loss levels appropriate for crypto volatility

Leverage these insights to make an informed trading decision.""",
}
```

**portfolio_manager.py modification**:
```python
prompt = f"""As the Portfolio Manager for crypto assets, synthesize the risk debate and deliver the final decision for {crypto_asset}.

{crypto_context}

**Rating Scale** (use exactly one):
- **Buy**: Strong conviction, aggressive entry
- **Overweight**: Favorable, gradual accumulation
- **Hold**: Maintain position
- **Underweight**: Reduce exposure, partial profit-taking
- **Sell**: Exit or avoid

**Crypto-Specific Risk Considerations**:
- Volatility: Crypto can move 10-20% daily
- Liquidity: Assess depth across exchanges
- Regulatory: Country-level bans can happen overnight
- Leverage: If using leverage, 2-3x max recommended
- Stop-Loss: Tighter stops needed (5-10% vs 15-20% for stocks)

**Required Output**:
1. **Rating**: Buy / Overweight / Hold / Underweight / Sell
2. **Executive Summary**: Entry strategy, position size, risk levels, timeframe
3. **Investment Thesis**: Grounded in analyst debate

Consider lessons from past decisions: {past_memory_str}

Risk Debate History:
{history}

Be decisive and specific. Account for crypto's unique risk profile."""
```

---

### 6. Graph Orchestration

#### **File**: `tradingagents/graph/trading_graph.py`
**Current Function**: Main orchestrator for the multi-agent system

**Crypto Adaptation Design**:

```python
# Main changes:
class CryptoAgentsGraph:
    """Main class that orchestrates the crypto trading agents framework."""

    def __init__(
        self,
        selected_analysts=["price_volume", "on_chain", "sentiment", "news"],
        debug=False,
        config: Dict[str, Any] = None,
        callbacks: Optional[List] = None,
    ):
        # ... initialization same as original ...

        # Initialize memories (same structure)
        self.bull_memory = FinancialSituationMemory("bull_memory", self.config)
        self.bear_memory = FinancialSituationMemory("bear_memory", self.config)
        self.trader_memory = FinancialSituationMemory("trader_memory", self.config)
        self.invest_judge_memory = FinancialSituationMemory("invest_judge_memory", self.config)
        self.portfolio_manager_memory = FinancialSituationMemory("portfolio_manager_memory", self.config)

        # Create tool nodes for CRYPTO
        self.tool_nodes = self._create_crypto_tool_nodes()

        # ... rest same as original ...

    def _create_crypto_tool_nodes(self) -> Dict[str, ToolNode]:
        """Create tool nodes for crypto data sources."""
        return {
            "price_volume": ToolNode([
                get_crypto_price_data,
                get_indicators,
                get_orderbook_data,
                get_volume_profile,
            ]),
            "on_chain": ToolNode([
                get_network_metrics,
                get_whale_movements,
                get_exchange_flows,
                get_hash_rate,
                get_holder_distribution,
            ]),
            "sentiment": ToolNode([
                get_social_sentiment,
                get_fear_greed_index,
            ]),
            "news": ToolNode([
                get_crypto_news,
                get_regulatory_news,
                get_global_crypto_news,
            ]),
        }

    def propagate(self, crypto_asset, trading_pair, analysis_timestamp):
        """Run the crypto agents graph for an asset at a specific timestamp.

        Args:
            crypto_asset: Cryptocurrency symbol (e.g., 'BTC', 'ETH')
            trading_pair: Quote currency (e.g., 'USDT', 'USD')
            analysis_timestamp: ISO format timestamp (e.g., '2024-03-20 14:30:00')
        """
        self.crypto_asset = crypto_asset
        self.trading_pair = trading_pair

        # Initialize state for CRYPTO
        init_agent_state = self.propagator.create_initial_crypto_state(
            crypto_asset, trading_pair, analysis_timestamp
        )

        # ... rest same as original ...

        return final_state, self.process_signal(final_state["final_trade_decision"])
```

**Key Changes**:
1. Rename class → `CryptoAgentsGraph`
2. Default analysts: `price_volume`, `on_chain`, `sentiment`, `news`
3. Tool nodes organized for crypto data categories
4. `propagate()` accepts `crypto_asset`, `trading_pair`, `analysis_timestamp`

---

#### **File**: `tradingagents/graph/setup.py`
**Current Function**: Constructs the LangGraph workflow

**Crypto Adaptation Design**:
- **Minimal changes** - same graph structure
- Update analyst node names:
  - "Market Analyst" → "Price/Volume Analyst"
  - "Fundamentals Analyst" → "On-Chain Analyst"
  - "Social Media Analyst" → "Sentiment Analyst"
  - "News Analyst" → "Crypto News Analyst"

Same workflow: Analysts → Bull/Bear → Research Manager → Trader → Risk Debate → Portfolio Manager

---

#### **File**: `tradingagents/graph/reflection.py`
**Current Function**: Post-decision reflection and memory updates

**Crypto Adaptation Design**:
- **No changes required** - reflection logic is domain-agnostic
- Memory system works identically for crypto
- Only update field names in `_extract_current_situation()`:

```python
def _extract_current_situation(self, current_state: Dict[str, Any]) -> str:
    """Extract the current crypto market situation from state."""
    curr_price_volume_report = current_state["price_volume_report"]
    curr_on_chain_report = current_state["on_chain_report"]
    curr_sentiment_report = current_state["sentiment_report"]
    curr_news_report = current_state["news_report"]

    return f"{curr_price_volume_report}\n\n{curr_on_chain_report}\n\n{curr_sentiment_report}\n\n{curr_news_report}"
```

---

### 7. LLM Clients

#### **Files**: `tradingagents/llm_clients/*.py`
**Current Function**: Unified interface for multiple LLM providers

**Crypto Adaptation Design**:
- **NO CHANGES REQUIRED**
- LLM client layer is completely domain-agnostic
- Same providers, same factory pattern
- Works identically for crypto analysis

---

## New Components Required

### 1. Additional Analyst (Optional but Recommended)

**File**: `cryptoagents/agents/analysts/derivatives_analyst.py`

```python
def create_derivatives_analyst(llm):
    """Analyzes futures, perpetual swaps, funding rates, open interest."""

    tools = [
        get_open_interest,
        get_funding_rates,
        get_liquidations,
        get_options_flow,
    ]

    system_message = (
        """You are a crypto derivatives analyst tracking futures and perpetual swap markets.

Key Metrics:
- **Open Interest**: Total outstanding derivative contracts
  - Rising OI + rising price = bullish (new longs)
  - Rising OI + falling price = bearish (new shorts)
  - Falling OI = position closures (potential reversal)

- **Funding Rates**: Perpetual swap interest payments
  - Positive funding = longs pay shorts (overcrowded longs, bearish)
  - Negative funding = shorts pay longs (overcrowded shorts, bullish)
  - Extreme funding = contrarian signal

- **Liquidations**: Forced position closures
  - Long liquidation cascade = capitulation bottom (bullish)
  - Short liquidation cascade = blow-off top (bearish)

- **Leverage Ratio**: Average leverage across market
  - High leverage = fragile, risk of cascades

Derivatives data often leads spot price action. Large liquidations create buying/selling pressure."""
    )
```

### 2. New Data Vendor Implementations

**Required Vendor Files**:
1. `cryptoagents/dataflows/binance_api.py` - Direct exchange integration
2. `cryptoagents/dataflows/cryptocompare_api.py` - Price aggregation
3. `cryptoagents/dataflows/glassnode_api.py` - Premium on-chain metrics
4. `cryptoagents/dataflows/lunarcrush_api.py` - Social sentiment
5. `cryptoagents/dataflows/cryptopanic_api.py` - Crypto news aggregation
6. `cryptoagents/dataflows/coinglass_api.py` - Derivatives data
7. `cryptoagents/dataflows/coinmetrics_api.py` - Alternative on-chain provider

### 3. Utility Modules

**File**: `cryptoagents/dataflows/exchange_aggregator.py`
```python
"""Aggregate price data across multiple exchanges to find arbitrage and average price."""

def get_aggregated_price(symbol, trading_pair, timestamp):
    """Fetch prices from multiple exchanges and compute average."""
    exchanges = ["binance", "coinbase", "kraken", "ftx"]
    prices = []
    for exchange in exchanges:
        price = get_exchange_price(exchange, symbol, trading_pair, timestamp)
        if price:
            prices.append(price)
    return {
        "average": sum(prices) / len(prices),
        "highest": max(prices),
        "lowest": min(prices),
        "spread_pct": ((max(prices) - min(prices)) / min(prices)) * 100,
        "arbitrage_opportunity": max(prices) - min(prices) > threshold,
    }
```

**File**: `cryptoagents/utils/crypto_indicators.py`
```python
"""Crypto-specific indicator calculations and parameter tuning."""

def calculate_rsi_crypto(prices, period=14):
    """RSI with crypto-appropriate parameters."""
    # Standard RSI, but note that crypto can stay overbought/oversold longer
    pass

def calculate_liquidation_levels(current_price, leverage_map):
    """Calculate where liquidations will occur based on leverage distribution."""
    pass

def calculate_fear_greed(volatility, momentum, social, dominance, trends):
    """Composite fear & greed index calculation."""
    pass
```

---

## Data Vendor Recommendations

### Free Tier (Hobbyist/Testing)
1. **CryptoCompare** (free tier: 100k calls/month)
   - Price data: ✓
   - Technical indicators: Calculate from price
   - News: Limited

2. **CoinGecko API** (free tier: 10-50 calls/min)
   - Price data: ✓
   - Market cap rankings: ✓
   - Basic exchange data: ✓

3. **Blockchain.info** (Bitcoin only, free)
   - Basic on-chain metrics: ✓
   - Hash rate, difficulty: ✓

4. **CryptoPanic** (free tier: limited)
   - News aggregation: ✓
   - Community votes: ✓

### Paid Tier (Professional)
1. **Glassnode** ($29-799/month)
   - ⭐ **Best-in-class on-chain metrics**
   - Comprehensive Bitcoin/Ethereum data
   - Advanced holder analysis

2. **LunarCrush** ($49+/month)
   - ⭐ **Best social sentiment data**
   - Twitter, Reddit, news aggregation
   - Influencer tracking

3. **CoinMetrics** (Enterprise pricing)
   - Alternative to Glassnode
   - More assets covered
   - Research-grade data

4. **Coinglass** (Free + Pro $29/month)
   - ⭐ **Best derivatives data**
   - Liquidations, funding rates
   - Open interest

5. **Messari** (Free + Pro $25+/month)
   - Research reports
   - On-chain snapshots
   - Protocol metrics

### Exchange APIs (Free with API key)
1. **Binance** - Highest liquidity, most pairs
2. **Coinbase Pro** - US institutional favorite
3. **Kraken** - Good for EUR pairs
4. **CCXT Library** - Unified API for 100+ exchanges

---

## Implementation Roadmap

### Phase 1: Core Infrastructure (2-3 weeks)
1. ✅ Set up project structure (`cryptoagents/` directory)
2. ✅ Implement configuration system (`crypto_default_config.py`)
3. ✅ Update state management (`CryptoAgentState` with new fields)
4. ✅ Implement data vendor interface (`interface.py` with crypto vendors)
5. ✅ Set up one price data vendor (recommend CryptoCompare free tier)

### Phase 2: Core Agents (3-4 weeks)
1. ✅ Implement Price/Volume Analyst (adapt from market analyst)
2. ✅ Implement On-Chain Analyst (NEW - most complex)
3. ✅ Implement Sentiment Analyst (enhance social media analyst)
4. ✅ Implement Crypto News Analyst (adapt news analyst)
5. ✅ Test each analyst independently with real data

### Phase 3: Workflow & Decision Making (2 weeks)
1. ✅ Adapt Bull/Bear researchers (minimal changes)
2. ✅ Update Research Manager prompts
3. ✅ Update Trader and Portfolio Manager for crypto context
4. ✅ Implement graph orchestration (`CryptoAgentsGraph`)
5. ✅ Test end-to-end workflow

### Phase 4: Data Vendors (2-3 weeks)
1. ✅ Implement Glassnode API integration (on-chain data)
2. ✅ Implement LunarCrush API integration (sentiment)
3. ✅ Implement CryptoPanic API integration (news)
4. ✅ Implement fallback chain for each data category
5. ✅ Add caching layer (Redis) for API rate limit management

### Phase 5: Testing & Validation (2-3 weeks)
1. ✅ Historical backtesting framework
2. ✅ Compare decisions to actual Bitcoin price movements
3. ✅ Validate on-chain metrics provide signal
4. ✅ Tune indicator parameters for crypto volatility
5. ✅ Test memory/reflection system

### Phase 6: Advanced Features (Optional, 2-4 weeks)
1. ✅ Implement Derivatives Analyst
2. ✅ Multi-exchange arbitrage detection
3. ✅ Real-time monitoring (24/7 operation)
4. ✅ Risk management automation (stop-loss execution)
5. ✅ Portfolio tracking across multiple crypto assets

---

## Summary: Key Differences Stock → Crypto

| Aspect | Stocks | Crypto | Impact |
|--------|--------|--------|--------|
| **Trading Hours** | 9:30am-4pm ET (Mon-Fri) | 24/7/365 | Change: date → datetime |
| **Fundamentals** | Financial statements (P/E, EPS, revenue) | On-chain metrics (active addresses, hash rate) | Change: New analyst type |
| **Volatility** | 1-3% daily moves | 5-20% daily moves | Change: Risk parameters |
| **Sentiment Impact** | Moderate correlation | Strong correlation | Change: Sentiment weight↑ |
| **Regulatory** | Established, predictable | Rapidly evolving, country-specific | Change: News focus↑ |
| **Data Sources** | yfinance, Alpha Vantage | Glassnode, CryptoCompare, Binance | Change: New vendors |
| **Technical Indicators** | Standard parameters | Faster-reacting parameters | Change: Tune parameters |
| **Social Media** | Moderate influence | Extreme influence (Elon tweets) | Change: Tool importance↑ |
| **Market Structure** | Centralized exchanges | Decentralized + centralized | Change: Multi-exchange |
| **Derivatives** | Futures, options | + Perpetual swaps (unique) | Change: New data type |

---

## Conclusion

Adapting the TradingAgents framework for cryptocurrency (Bitcoin) trading requires **moderate architectural changes** focused on:

1. **Data Layer** (40% effort): Replace stock vendors with crypto vendors, add on-chain metrics
2. **Analyst Layer** (30% effort): New on-chain analyst, enhanced sentiment analyst, crypto-tuned technical analysis
3. **State Management** (10% effort): Rename fields, add trading pair tracking, datetime precision
4. **Prompts & Context** (15% effort): Update all agent prompts for crypto characteristics
5. **Configuration** (5% effort): New vendor categories, crypto-specific settings

The **core multi-agent architecture remains unchanged**:
- Debate-driven evaluation (Bull/Bear) ✓
- Risk management team discussion ✓
- Memory and reflection system ✓
- LangGraph workflow ✓
- LLM provider abstraction ✓

The most **unique additions** for crypto:
1. ✅ **On-Chain Analyst** - No stock market equivalent
2. ✅ **Enhanced Sentiment Analyst** - Social media much more important
3. ✅ **Regulatory News Focus** - Critical for crypto
4. ✅ **24/7 Timestamp Handling** - No market close
5. ✅ **Multi-Exchange Aggregation** - Fragmented liquidity

**Estimated total adaptation effort**: 10-15 weeks for a team of 2-3 developers with crypto domain knowledge.

---

**Report End**
