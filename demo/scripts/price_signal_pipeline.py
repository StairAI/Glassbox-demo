#!/usr/bin/env python3
"""
BTC Price Signal Pipeline

Fetches current BTC price from CoinGecko and publishes as a PriceSignal.
This signal can then be consumed by Agent B for investment predictions.

Usage:
    python scripts/price_signal_pipeline.py [--owner OWNER_ADDRESS]
"""

import sys
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

# Add demo directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv('config/.env')

from src.data_sources.coingecko_source import CoinGeckoSource
from src.storage.walrus_client import WalrusClient
from src.blockchain.sui_publisher import OnChainPublisher
from src.demo.signal_registry import SignalRegistry


class PriceSignalPipeline:
    """
    Price Signal Pipeline - Fetches BTC price and publishes as signal.
    """

    def __init__(self, owner_address: Optional[str] = None):
        """
        Initialize pipeline.

        Args:
            owner_address: Owner address for all published data
        """
        self.owner_address = owner_address or "0xPRICE_PIPELINE_DEFAULT"

        # Initialize CoinGecko source (with Pro API key if available)
        coingecko_api_key = os.getenv("COINGECKO_API_KEY")
        self.price_source = CoinGeckoSource(api_key=coingecko_api_key)

        # Initialize Walrus client
        walrus_publisher = os.getenv("WALRUS_PUBLISHER_URL", "https://publisher.walrus-testnet.walrus.space")
        walrus_aggregator = os.getenv("WALRUS_AGGREGATOR_URL", "https://aggregator.walrus-testnet.walrus.space")
        walrus_enabled = os.getenv("WALRUS_ENABLED", "false").lower() == "true"

        self.walrus_client = WalrusClient(
            publisher_url=walrus_publisher,
            aggregator_url=walrus_aggregator,
            simulated=not walrus_enabled
        )

        # Initialize publisher
        self.publisher = OnChainPublisher(
            walrus_client=self.walrus_client,
            owner_address=owner_address,
            simulated=True
        )

        # Initialize signal registry
        self.registry = SignalRegistry(registry_path="data/signal_registry.json")

    def fetch_and_publish_btc_price(self) -> None:
        """Fetch BTC price from CoinGecko and publish as PriceSignal."""
        print()
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 25 + "BTC PRICE SIGNAL PIPELINE" + " " * 24 + "║")
        print("╚" + "=" * 78 + "╝")
        print()

        try:
            # Step 1: Check CoinGecko availability
            print("[Step 1] Checking CoinGecko API...")
            if not self.price_source.is_available():
                print("  ✗ CoinGecko API is not available")
                return

            print("  ✓ CoinGecko API is available")
            print()

            # Step 2: Fetch BTC price
            print("[Step 2] Fetching BTC current price...")
            btc_price_data = self.price_source.get_price("BTC")

            print(f"  ✓ Fetched BTC price")
            print(f"    Symbol:        {btc_price_data.symbol}")
            print(f"    Price (USD):   ${btc_price_data.price_usd:,.2f}")
            print(f"    Source:        {btc_price_data.source}")
            print(f"    Timestamp:     {btc_price_data.timestamp}")

            if btc_price_data.price_change_24h:
                print(f"    24h Change:    {btc_price_data.price_change_24h:+.2f}%")

            if btc_price_data.volume_24h:
                print(f"    24h Volume:    ${btc_price_data.volume_24h:,.0f}")

            if btc_price_data.market_cap:
                print(f"    Market Cap:    ${btc_price_data.market_cap:,.0f}")

            print()

            # Step 3: Convert to dict for Walrus storage
            print("[Step 3] Converting to dict for Walrus storage...")
            price_dict = btc_price_data.to_dict()
            print(f"  ✓ Size: ~{len(str(price_dict))} bytes")
            print()

            # Step 4: Publish to Walrus + SUI
            print("[Step 4] Publishing price signal...")
            price_signal = self.publisher.publish_price_signal(
                price_data=price_dict,
                producer="coingecko_price_pipeline"
            )

            # Step 5: Register in SignalRegistry
            print("[Step 5] Registering signal in registry...")
            self.registry.register_signal({
                "signal_type": "price",
                "walrus_blob_id": price_signal.walrus_blob_id,
                "data_hash": price_signal.data_hash,
                "size_bytes": price_signal.size_bytes,
                "symbol": price_signal.symbol,
                "price_usd": price_signal.price_usd,
                "producer": "coingecko_price_pipeline",
                "owner": self.owner_address,
                "timestamp": datetime.now().isoformat()
            })

            print(f"  ✓ Signal registered (ID: signal_{price_signal.object_id[-6:]})")
            print()

            # Summary
            print("╔" + "=" * 78 + "╗")
            print("║" + " " * 32 + "SUMMARY" + " " * 34 + "║")
            print("╚" + "=" * 78 + "╝")
            print()
            print(f"  BTC Price:       ${btc_price_data.price_usd:,.2f}")
            print(f"  Signal ID:       {price_signal.object_id}")
            print(f"  Walrus Blob ID:  {price_signal.walrus_blob_id}")
            print(f"  Owner:           {self.owner_address}")
            print()
            print(f"  ✅ Price signal successfully published!")
            print()
            print(f"  This signal can now be consumed by Agent B for BTC price predictions.")
            print()

        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="BTC Price Signal Pipeline")
    parser.add_argument(
        "--owner",
        type=str,
        default=None,
        help="Owner address for published signals (auto-generated if not specified)"
    )

    args = parser.parse_args()

    # Generate owner address if not provided
    owner_address = args.owner or f"0xPRICE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Create and run pipeline
    pipeline = PriceSignalPipeline(owner_address=owner_address)
    pipeline.fetch_and_publish_btc_price()


if __name__ == "__main__":
    main()
