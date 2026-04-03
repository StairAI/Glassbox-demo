#!/usr/bin/env python3
"""
Glass Box Explorer - Quick Start Launcher

Starts both the API server and opens the frontend in your default browser.
"""

import os
import sys
import time
import webbrowser
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")

    try:
        import flask
        import flask_cors
        print("  ✓ Flask installed")
    except ImportError:
        print("  ✗ Flask not installed")
        print("\nInstalling dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "flask", "flask-cors"])

def check_data():
    """Check if demo data exists."""
    print("\nChecking demo data...")

    registry_path = Path("../demo/data/trigger_registry.json")
    db_path = Path("../demo/data/activity.db")

    if not registry_path.exists():
        print("  ⚠️  No trigger registry found")
        print("  Run: cd ../demo && python scripts/batch_process_btc_sui.py")
        return False

    if not db_path.exists():
        print("  ⚠️  No activity database found")
        print("  Run: cd ../demo && python scripts/batch_process_btc_sui.py")
        return False

    print("  ✓ Demo data found")
    return True

def start_server():
    """Start the API server."""
    print("\n" + "=" * 80)
    print("STARTING GLASS BOX EXPLORER")
    print("=" * 80)
    print()

    # Change to api directory
    os.chdir('api')

    # Import and run server
    import server
    # Server will run in server.py's __main__ block

def main():
    """Main launcher."""
    print("=" * 80)
    print("Glass Box Explorer - Launcher")
    print("=" * 80)
    print()

    # Check dependencies
    check_dependencies()

    # Check data
    data_exists = check_data()

    if not data_exists:
        print("\n❌ Missing demo data. Please run batch processing first:")
        print("   cd ../demo && python scripts/batch_process_btc_sui.py")
        sys.exit(1)

    # Open browser after short delay
    print("\n📱 Opening browser in 2 seconds...")
    time.sleep(2)
    webbrowser.open('http://localhost:8000')

    # Start server (this will block)
    start_server()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down Glass Box Explorer...")
        sys.exit(0)
