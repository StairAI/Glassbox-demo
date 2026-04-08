#!/usr/bin/env python3
"""
Download Reasoning Ledgers from Walrus

This script downloads all reasoning traces from Walrus for inspection.
It reads the signal registry, finds all insight signals with reasoning traces,
and downloads the raw JSON data from Walrus.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv('config/.env')

import os
import json
from datetime import datetime
from src.demo.signal_registry import SignalRegistry
from src.storage.walrus_client import WalrusClient, WalrusHelper


def main():
    print("=" * 80)
    print("REASONING LEDGER DOWNLOADER")
    print("=" * 80)
    print()

    # ========================================================================
    # SETUP
    # ========================================================================
    print("[Setup] Initializing components...")

    # Walrus client
    walrus_publisher = os.getenv("WALRUS_PUBLISHER_URL", "https://publisher.walrus-testnet.walrus.space")
    walrus_aggregator = os.getenv("WALRUS_AGGREGATOR_URL", "https://aggregator.walrus-testnet.walrus.space")
    walrus_enabled = os.getenv("WALRUS_ENABLED", "false").lower() == "true"

    walrus_client = WalrusClient(
        publisher_url=walrus_publisher,
        aggregator_url=walrus_aggregator,
        simulated=not walrus_enabled
    )

    # Signal registry
    registry = SignalRegistry(registry_path="data/signal_registry.json")

    # Output directory
    output_dir = Path("output/reasoning_ledgers")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"  ✓ Walrus mode: {'Real' if walrus_enabled else 'Simulated'}")
    print(f"  ✓ Output dir: {output_dir}")
    print()

    # ========================================================================
    # FETCH ALL INSIGHT SIGNALS
    # ========================================================================
    print("=" * 80)
    print("STEP 1: FIND ALL INSIGHT SIGNALS WITH REASONING TRACES")
    print("=" * 80)
    print()

    all_signals = registry.get_signals(signal_type='insight', limit=10000)

    # Filter signals that have reasoning traces
    signals_with_traces = [
        s for s in all_signals
        if s.get('walrus_trace_id')
    ]

    print(f"  ✓ Total insight signals: {len(all_signals)}")
    print(f"  ✓ Signals with reasoning traces: {len(signals_with_traces)}")
    print()

    if not signals_with_traces:
        print("❌ No signals with reasoning traces found!")
        return

    # ========================================================================
    # DOWNLOAD REASONING LEDGERS
    # ========================================================================
    print("=" * 80)
    print("STEP 2: DOWNLOAD REASONING LEDGERS FROM WALRUS")
    print("=" * 80)
    print()

    downloaded = 0
    failed = 0

    for i, signal in enumerate(signals_with_traces, 1):
        signal_id = signal.get('signal_id')
        walrus_trace_id = signal.get('walrus_trace_id')
        producer = signal.get('producer', 'unknown')
        timestamp = signal.get('timestamp', '')

        print(f"[{i}/{len(signals_with_traces)}] Downloading {signal_id} from {producer}...")
        print(f"  Walrus Trace ID: {walrus_trace_id}")

        try:
            # Fetch reasoning trace from Walrus
            trace_data = WalrusHelper.fetch_json(walrus_client, walrus_trace_id)

            # Save to file
            filename = f"{signal_id}_{producer}_{walrus_trace_id[:12]}.json"
            output_path = output_dir / filename

            with open(output_path, 'w') as f:
                json.dump(trace_data, f, indent=2, sort_keys=True)

            print(f"  ✓ Saved to: {output_path}")
            print(f"  ✓ Reasoning steps: {len(trace_data.get('reasoning_steps', []))}")

            downloaded += 1

        except Exception as e:
            print(f"  ✗ Failed: {e}")
            failed += 1

        print()

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"✅ Successfully downloaded {downloaded} reasoning ledgers")
    if failed > 0:
        print(f"❌ Failed to download {failed} reasoning ledgers")
    print()
    print(f"All reasoning ledgers saved to: {output_dir}")
    print()

    # Create a summary file
    summary = {
        "download_timestamp": datetime.now().isoformat(),
        "total_signals": len(all_signals),
        "signals_with_traces": len(signals_with_traces),
        "downloaded": downloaded,
        "failed": failed,
        "output_directory": str(output_dir),
        "signals": [
            {
                "signal_id": s.get('signal_id'),
                "producer": s.get('producer'),
                "walrus_trace_id": s.get('walrus_trace_id'),
                "confidence": s.get('confidence'),
                "timestamp": s.get('timestamp'),
                "filename": f"{s.get('signal_id')}_{s.get('producer')}_{s.get('walrus_trace_id')[:12]}.json"
            }
            for s in signals_with_traces
        ]
    }

    summary_path = output_dir / "download_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"Summary saved to: {summary_path}")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
