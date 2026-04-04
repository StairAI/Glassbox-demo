#!/usr/bin/env python3
"""
SuiPricePipeline: Pipeline to read price data from on-chain oracles

KEY DIFFERENCE from NewsPipeline:
- This READS from SUI blockchain (oracles like Pyth/Switchboard already post prices)
- Does NOT fetch from off-chain APIs
- Creates PriceSignal from on-chain data

This is a lighter pipeline that abstracts 3rd-party oracle data into our Signal format.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from src.blockchain.sui_publisher import OnChainPublisher
from src.abstract import PriceSignal


class SuiPricePipeline:
    """
    Pipeline to read price data from on-chain oracles.

    Unlike NewsPipeline (which fetches from off-chain APIs), this pipeline:
    1. READS price data from SUI blockchain oracles (Pyth, Switchboard, etc.)
    2. TRANSFORMS to our standardized PriceSignal format
    3. PUBLISHES signal to SUI (no Walrus needed - data is small)

    This is a "lighter" pipeline that abstracts 3rd-party posted data.

    Example:
        pipeline = SuiPricePipeline(
            sui_client=sui_client,
            publisher=OnChainPublisher(),
            oracle_type="pyth"
        )
        signal = pipeline.read_and_publish_signal(symbol="BTC")
    """

    # Oracle package IDs on SUI testnet
    ORACLE_PACKAGES = {
        "pyth": "0x...pyth_package_id...",
        "switchboard": "0x...switchboard_package_id...",
        "custom": None  # For custom oracles
    }

    def __init__(
        self,
        sui_client=None,  # pysui.SuiClient
        publisher: OnChainPublisher = None,
        oracle_type: str = "pyth",
        simulated: bool = True
    ):
        """
        Initialize SUI price pipeline.

        Args:
            sui_client: pysui SuiClient for reading from blockchain
            publisher: OnChainPublisher for creating signals
            oracle_type: Oracle to use ("pyth", "switchboard", "custom")
            simulated: If True, simulate oracle reads (for demo/testing)
        """
        self.sui_client = sui_client
        self.publisher = publisher
        self.oracle_type = oracle_type
        self.simulated = simulated
        self.oracle_package_id = self.ORACLE_PACKAGES.get(oracle_type)

        if not simulated and not sui_client:
            raise ValueError("sui_client required when simulated=False")

    def read_and_publish_signal(
        self,
        symbol: str
    ) -> PriceSignal:
        """
        Read price from on-chain oracle and create signal.

        This is the complete pipeline flow:
        1. READ: Fetch price from on-chain oracle
        2. TRANSFORM: Convert to standardized format
        3. PUBLISH: Create PriceSignal on SUI

        Args:
            symbol: Asset symbol (e.g., "BTC", "ETH", "SUI")

        Returns:
            PriceSignal instance
        """
        print(f"\n{'='*80}")
        print(f"SUI PRICE PIPELINE: Processing {symbol}")
        print(f"{'='*80}")

        # Step 1: READ - Fetch from on-chain oracle
        print(f"\n[1/3] READ: Fetching {symbol} price from {self.oracle_type} oracle")

        oracle_data = self._read_oracle_price(symbol)

        print(f"  ✓ Price: ${oracle_data['price_usd']:,.2f}")
        print(f"  ✓ Oracle: {oracle_data['oracle_source']}")
        print(f"  ✓ Confidence: {oracle_data.get('confidence', 'N/A')}")
        print(f"  ✓ Timestamp: {oracle_data['timestamp'].isoformat()}")

        # Step 2: TRANSFORM - Already in standardized format
        print(f"\n[2/3] TRANSFORM: Data already standardized (on-chain oracle)")
        print(f"  ✓ No transformation needed")

        # Step 3: PUBLISH - Create signal on SUI
        print(f"\n[3/3] PUBLISH: Creating PriceSignal on SUI")

        signal = self.publisher.publish_price_signal(
            symbol=symbol,
            price_usd=oracle_data['price_usd'],
            oracle_source=oracle_data['oracle_source'],
            confidence=oracle_data.get('confidence'),
            producer="sui_price_pipeline"
        )

        print(f"{'='*80}")
        print(f"SUI PRICE PIPELINE: Complete")
        print(f"{'='*80}")
        print(f"✓ Price signal published: {signal.object_id[:16]}...")
        print(f"✓ Symbol: {signal.symbol}")
        print(f"✓ Price: ${signal.price_usd:,.2f}")
        print()

        return signal

    def read_and_publish_multiple(
        self,
        symbols: List[str]
    ) -> List[PriceSignal]:
        """
        Read and publish multiple price signals.

        Args:
            symbols: List of asset symbols (e.g., ["BTC", "ETH", "SUI"])

        Returns:
            List of PriceSignal instances
        """
        signals = []

        for symbol in symbols:
            try:
                signal = self.read_and_publish_signal(symbol)
                signals.append(signal)
            except Exception as e:
                print(f"✗ Failed to process {symbol}: {e}")

        return signals

    # === Private Methods ===

    def _read_oracle_price(self, symbol: str) -> Dict[str, Any]:
        """
        Read price from on-chain oracle.

        This is a READ operation from SUI blockchain, not a write.
        Oracles like Pyth/Switchboard regularly post prices on-chain.

        Args:
            symbol: Asset symbol

        Returns:
            Dict with price data
        """
        if self.simulated:
            return self._simulate_oracle_read(symbol)
        else:
            return self._real_oracle_read(symbol)

    def _simulate_oracle_read(self, symbol: str) -> Dict[str, Any]:
        """
        Simulate reading from oracle for demo purposes.

        In reality, this would query actual price feeds on SUI.
        """
        # Simulated prices for demo
        SIMULATED_PRICES = {
            "BTC": 66434.0,
            "ETH": 2543.12,
            "SUI": 1.23,
            "SOL": 142.67,
            "AVAX": 28.45
        }

        price = SIMULATED_PRICES.get(symbol, 100.0)

        return {
            "symbol": symbol,
            "price_usd": price,
            "oracle_source": self.oracle_type,
            "confidence": 0.01,  # ±1% confidence interval
            "timestamp": datetime.now()
        }

    def _real_oracle_read(self, symbol: str) -> Dict[str, Any]:
        """
        Read price from real on-chain oracle.

        This would query Pyth or Switchboard price feeds on SUI blockchain.

        Example for Pyth:
            from pysui.sui.sui_types.scalars import ObjectID

            # Get price feed object ID for symbol
            price_feed_id = SYMBOL_TO_FEED_ID[symbol]

            # Read price feed object
            result = self.sui_client.get_object(ObjectID(price_feed_id))
            price_obj = result.data

            # Parse price from object
            price = parse_pyth_price(price_obj)

            return {
                "symbol": symbol,
                "price_usd": price['price'],
                "oracle_source": "pyth",
                "confidence": price['confidence'],
                "timestamp": datetime.fromtimestamp(price['publish_time'])
            }
        """
        raise NotImplementedError(
            "Real oracle reading requires pysui SDK and oracle integration. "
            "Use simulated=True for demo purposes."
        )


class PriceScheduler:
    """
    Scheduler for periodic price signal creation.

    Reads prices from oracle and creates signals on schedule (e.g., every 1 minute).

    Example:
        scheduler = PriceScheduler(pipeline=price_pipeline)
        scheduler.run_periodic(symbols=["BTC", "ETH"], interval_seconds=60)
    """

    def __init__(self, pipeline: SuiPricePipeline):
        self.pipeline = pipeline

    def run_once(self, symbols: List[str]) -> List[PriceSignal]:
        """Run pipeline once for multiple symbols."""
        return self.pipeline.read_and_publish_multiple(symbols)

    def run_periodic(self, symbols: List[str], interval_seconds: int = 60):
        """
        Run pipeline periodically.

        In production, this would use a proper scheduler like APScheduler.
        """
        import time

        print(f"Starting periodic price signal creation (every {interval_seconds}s)")
        print(f"Symbols: {symbols}")
        print()

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


# === Helper: Oracle Integration ===

class OracleHelper:
    """
    Helper class for working with different oracle types.

    Provides utilities for parsing oracle data and mapping symbols to feed IDs.
    """

    # Map symbols to Pyth price feed IDs
    PYTH_FEED_IDS = {
        "BTC": "0xe62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43",
        "ETH": "0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace",
        "SUI": "0x23d7315113f5b1d3ba7a83604c44b94d79f4fd69af77f804fc7f920a6dc65744",
        "SOL": "0xef0d8b6fda2ceba41da15d4095d1da392a0d2f8ed0c6c7bc0f4cfac8c280b56d",
        "AVAX": "0x93da3352f9f1d105fdfe4971cfa80e9dd777bfc5d0f683ebb6e1294b92137bb7"
    }

    @staticmethod
    def get_pyth_feed_id(symbol: str) -> Optional[str]:
        """Get Pyth price feed ID for symbol."""
        return OracleHelper.PYTH_FEED_IDS.get(symbol.upper())

    @staticmethod
    def parse_pyth_price(price_obj: Any) -> Dict[str, Any]:
        """
        Parse Pyth price object.

        This would parse the actual Pyth price feed object from SUI.
        """
        # Pseudocode for parsing Pyth data
        # price_info = price_obj.content.fields.price_info
        # return {
        #     'price': price_info.price / (10 ** price_info.expo),
        #     'confidence': price_info.conf / (10 ** price_info.expo),
        #     'publish_time': price_info.publish_time
        # }
        raise NotImplementedError("Pyth parsing requires actual oracle integration")
