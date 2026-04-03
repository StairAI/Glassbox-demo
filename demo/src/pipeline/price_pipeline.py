#!/usr/bin/env python3
"""
PricePipeline: ETL pipeline for price data (NOT an agent)

This is a data pipeline that performs pure ETL operations:
1. Extract: Fetch prices from CoinGecko API
2. Transform: Convert to standardized format
3. Load: Publish to SUI blockchain

IMPORTANT: This is NOT an agent. It does not use LLMs or perform reasoning.
It simply moves data from off-chain (CoinGecko) to on-chain (SUI).
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from src.data_clients.coingecko_client import CoinGeckoClient
from src.data_sources.coingecko_source import CoinGeckoSource
from src.blockchain.sui_publisher import OnChainPublisher


class PricePipeline:
    """
    Price ETL Pipeline (NOT an agent).

    Responsibilities:
    - Fetch prices from CoinGecko API
    - Transform to standardized format
    - Publish raw data to SUI blockchain
    - Emit events to trigger agents

    Does NOT:
    - Use LLMs
    - Perform reasoning
    - Analyze price trends (that's for agents)
    - Store reasoning traces

    Example:
        pipeline = PricePipeline(
            api_key=None,  # Free tier
            publisher=OnChainPublisher(simulated=True)
        )
        object_id = pipeline.fetch_and_publish(symbols=["BTC", "ETH", "SUI"])
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        publisher: OnChainPublisher = None
    ):
        """
        Initialize price pipeline.

        Args:
            api_key: CoinGecko API key (optional, can use free tier)
            publisher: OnChainPublisher instance for storing data
        """
        # Layer 1: API Client (raw HTTP requests)
        self.client = CoinGeckoClient(api_key=api_key)

        # Layer 2: Data Source (transformation to dataclasses)
        self.source = CoinGeckoSource(api_key=api_key)

        # Layer 3: On-chain publisher
        self.publisher = publisher

    def fetch_and_publish(
        self,
        symbols: List[str],
        vs_currency: str = "usd"
    ) -> str:
        """
        Fetch prices from API and publish to blockchain.

        This is the main ETL flow:
        1. Fetch from CoinGecko API
        2. Transform to standardized format
        3. Publish to SUI blockchain
        4. (Optional) Emit event to trigger agents

        Args:
            symbols: List of crypto symbols (e.g., ["BTC", "ETH", "SUI"])
            vs_currency: Currency to price against (default: "usd")

        Returns:
            Object ID where data was stored on-chain
        """
        print(f"\n{'='*80}")
        print("PRICE PIPELINE: Starting ETL Process")
        print(f"{'='*80}")

        # Step 1: Extract - Fetch from API
        print(f"\n[1/4] EXTRACT: Fetching from CoinGecko API")
        print(f"  Symbols: {symbols}")
        print(f"  VS Currency: {vs_currency}")

        prices = []
        for symbol in symbols:
            try:
                price_data = self.source.get_price(symbol, vs_currency)
                prices.append(price_data)
                print(f"  ✓ {symbol}: ${float(price_data.price_usd):,.2f}")
            except Exception as e:
                print(f"  ✗ {symbol}: Error - {e}")

        print(f"  ✓ Fetched {len(prices)} prices")

        # Step 2: Transform - Convert to on-chain format
        print(f"\n[2/4] TRANSFORM: Converting to on-chain format")

        price_data = self._transform_for_onchain(prices, vs_currency)
        print(f"  ✓ Prepared {len(price_data['prices'])} price records")
        print(f"  ✓ Data size: {len(str(price_data))} bytes")

        # Step 3: Load - Publish to blockchain
        print(f"\n[3/4] LOAD: Publishing to SUI blockchain")

        object_id = self.publisher.publish_raw_data(
            data=price_data,
            producer="price_pipeline",
            data_type="price_raw"
        )
        print(f"  ✓ Published to blockchain")
        print(f"  ✓ Object ID: {object_id}")

        # Step 4: (Optional) Emit event to trigger agents
        if self.event_emitter:
            print(f"\n[4/4] EMIT: Triggering agent events")
            self._emit_events(object_id, price_data)

        print(f"\n{'='*80}")
        print("PRICE PIPELINE: ETL Complete")
        print(f"{'='*80}\n")

        return object_id

    def fetch_historical_and_publish(
        self,
        symbol: str,
        days: int = 30,
        vs_currency: str = "usd"
    ) -> str:
        """
        Fetch historical price data and publish to blockchain.

        Args:
            symbol: Crypto symbol (e.g., "BTC")
            days: Number of days of history (default: 30)
            vs_currency: Currency to price against (default: "usd")

        Returns:
            Object ID where data was stored on-chain
        """
        print(f"\n{'='*80}")
        print("PRICE PIPELINE: Fetching Historical Data")
        print(f"{'='*80}")

        # Extract historical data
        print(f"\n[1/3] EXTRACT: Fetching {days} days of {symbol} history")
        historical_data = self.source.get_historical_price(symbol, days, vs_currency)
        print(f"  ✓ Fetched {len(historical_data.prices)} data points")

        # Transform for on-chain
        print(f"\n[2/3] TRANSFORM: Converting to on-chain format")
        data = {
            "symbol": historical_data.symbol,
            "vs_currency": historical_data.vs_currency,
            "prices": historical_data.prices,
            "market_caps": historical_data.market_caps,
            "total_volumes": historical_data.total_volumes,
            "fetch_timestamp": datetime.now().isoformat()
        }

        # Publish to blockchain
        print(f"\n[3/3] LOAD: Publishing to SUI blockchain")
        object_id = self.publisher.publish_raw_data(
            data=data,
            producer="price_pipeline",
            data_type="price_historical"
        )
        print(f"  ✓ Published to blockchain")
        print(f"  ✓ Object ID: {object_id}")

        return object_id

    def _transform_for_onchain(self, prices, vs_currency: str) -> Dict[str, Any]:
        """
        Transform price data to on-chain format.

        This is pure data transformation - no reasoning, no LLM.
        """
        prices_data = []

        for price in prices:
            prices_data.append({
                "symbol": price.symbol,
                "price_usd": float(price.price_usd),
                "source": price.source,
                "market_cap": float(price.market_cap) if price.market_cap else None,
                "volume_24h": float(price.volume_24h) if price.volume_24h else None,
                "price_change_24h": float(price.price_change_24h) if price.price_change_24h else None,
                "timestamp": price.timestamp.isoformat(),
                "raw_data": price.raw_data
            })

        return {
            "prices": prices_data,
            "vs_currency": vs_currency,
            "fetch_timestamp": datetime.now().isoformat(),
            "total_count": len(prices_data)
        }

    def _emit_events(self, object_id: str, price_data: Dict[str, Any]):
        """
        Emit lightweight events to trigger agents.

        Events contain minimal data (just price previews and object_id).
        Agents will fetch full data from blockchain using object_id.
        """
        for price in price_data["prices"]:
            # Lightweight event data (< 200 bytes)
            metadata = {
                "symbol": price["symbol"],
                "price_usd": price["price_usd"],
                "price_change_24h": price.get("price_change_24h"),
                "object_id": object_id  # Reference to full data
            }

            self.event_emitter.emit_event(
                event_type="price_updated",
                object_id=object_id,
                metadata=metadata
            )


class PriceScheduler:
    """
    Scheduler for periodic price fetching.

    This would run on a schedule (e.g., every 1 minute) to fetch
    latest prices and publish to blockchain.

    Example:
        scheduler = PriceScheduler(pipeline=price_pipeline)
        scheduler.run_periodic(interval_seconds=60)  # Every 1 minute
    """

    def __init__(self, pipeline: PricePipeline):
        self.pipeline = pipeline

    def run_once(self, symbols: List[str]) -> str:
        """Run pipeline once."""
        return self.pipeline.fetch_and_publish(symbols=symbols)

    def run_periodic(self, symbols: List[str], interval_seconds: int = 60):
        """
        Run pipeline periodically.

        In production, this would use a proper scheduler like APScheduler.
        """
        import time

        print(f"Starting periodic price fetching (every {interval_seconds}s)")

        while True:
            try:
                self.run_once(symbols=symbols)
                print(f"Sleeping for {interval_seconds} seconds...")
                time.sleep(interval_seconds)
            except KeyboardInterrupt:
                print("\nScheduler stopped by user")
                break
            except Exception as e:
                print(f"Error in scheduler: {e}")
                time.sleep(interval_seconds)
