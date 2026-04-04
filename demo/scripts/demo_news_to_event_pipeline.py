#!/usr/bin/env python3
"""
Complete Example: Real News Data → SUI Event → Agent Signal

Demonstrates the full pipeline:
1. Fetch real news from CryptoPanic
2. Store in local DB
3. Emit SUI event with reference
4. Watch for event and retrieve full data
5. Signal agent with real data
"""

import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_sources import CryptoPanicSource
from dotenv import load_dotenv
import json
from datetime import datetime
import sqlite3

# Load environment
load_dotenv("config/.env")


def fetch_real_news():
    """Step 1: Fetch real news from CryptoPanic."""
    print("=" * 80)
    print("STEP 1: Fetching Real News from CryptoPanic")
    print("=" * 80)

    api_token = os.getenv("CRYPTOPANIC_API_TOKEN")
    source = CryptoPanicSource(api_token)

    # Fetch real BTC news
    articles = source.fetch_news(currencies=["BTC"], limit=5)

    print(f"\n✓ Fetched {len(articles)} real articles")
    print()

    return articles


def analyze_sentiment(text: str) -> str:
    """Simple keyword-based sentiment analysis."""
    text_lower = text.lower()

    bullish = ["surge", "rally", "bullish", "moon", "pump", "gains", "up", "rise"]
    bearish = ["crash", "dump", "bearish", "drop", "fall", "plunge", "down"]

    bullish_count = sum(1 for word in bullish if word in text_lower)
    bearish_count = sum(1 for word in bearish if word in text_lower)

    if bullish_count > bearish_count:
        return "bullish"
    elif bearish_count > bullish_count:
        return "bearish"
    else:
        return "neutral"


def store_in_local_db(articles):
    """Step 2: Store articles in local SQLite database."""
    print("=" * 80)
    print("STEP 2: Storing in Local Database")
    print("=" * 80)

    # Create data directory if not exists
    Path("data").mkdir(exist_ok=True)

    # Create DB
    conn = sqlite3.connect("data/news.db")
    cursor = conn.cursor()

    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS news_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            source TEXT,
            published_at TEXT,
            sentiment TEXT,
            raw_data TEXT,
            created_at TEXT
        )
    """)

    db_ids = []

    for article in articles:
        # Simple sentiment analysis
        sentiment = analyze_sentiment(article.title)

        cursor.execute("""
            INSERT INTO news_articles
            (title, source, published_at, sentiment, raw_data, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            article.title,
            article.source,
            article.published_at.isoformat(),
            sentiment,
            json.dumps(article.raw_data),
            datetime.now().isoformat()
        ))

        db_id = cursor.lastrowid
        db_ids.append(db_id)

        print(f"✓ Stored article {db_id}: {article.title[:60]}...")
        print(f"  Sentiment: {sentiment}")

    conn.commit()
    conn.close()

    print(f"\n✓ Stored {len(db_ids)} articles in database")
    print()

    return db_ids


def simulate_sui_event_emission(db_ids, articles):
    """Step 3: Simulate emitting SUI events (would be on-chain)."""
    print("=" * 80)
    print("STEP 3: Simulating SUI Event Emission")
    print("=" * 80)
    print()
    print("NOTE: In production, these would be actual SUI blockchain transactions")
    print()

    events = []

    for db_id, article in zip(db_ids, articles):
        sentiment = analyze_sentiment(article.title)

        # This is what would go on-chain (lightweight!)
        event_data = {
            "db_id": db_id,
            "title_preview": article.title[:100],  # Truncated
            "source": article.source,
            "sentiment": sentiment,
            "timestamp": int(datetime.now().timestamp()),
        }

        events.append(event_data)

        print(f"📡 Event Emitted:")
        print(f"   DB ID: {db_id}")
        print(f"   Title: {event_data['title_preview']}")
        print(f"   Sentiment: {sentiment}")
        print()

    return events


def simulate_event_watcher(events):
    """Step 4: Simulate event watcher detecting events."""
    print("=" * 80)
    print("STEP 4: Event Watcher Detecting Events")
    print("=" * 80)
    print()

    for event in events:
        print(f"👁️  Event Detected:")
        print(f"   Title Preview: {event['title_preview']}")
        print(f"   Sentiment: {event['sentiment']}")
        print(f"   DB ID: {event['db_id']}")

        # Filter: Only signal on bullish/bearish news
        if event['sentiment'] in ['bullish', 'bearish']:
            print(f"   ✓ Signaling agent (sentiment: {event['sentiment']})")

            # Fetch full data from DB
            retrieve_and_signal_agent(event['db_id'])
        else:
            print(f"   ⊘ Skipping neutral news")

        print()


def retrieve_and_signal_agent(db_id: int):
    """Step 5: Retrieve full data and signal agent."""
    print("   " + "-" * 60)
    print(f"   RETRIEVING FULL DATA FROM DB (ID: {db_id})")

    conn = sqlite3.connect("data/news.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM news_articles WHERE id = ?", (db_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        article = dict(row)

        print(f"   ✓ Full Article Retrieved:")
        print(f"     Title: {article['title']}")
        print(f"     Source: {article['source']}")
        print(f"     Published: {article['published_at']}")
        print(f"     Sentiment: {article['sentiment']}")
        print(f"     Raw Data Size: {len(article['raw_data'])} bytes")

        print()
        print(f"   🤖 TRIGGERING AGENT A with full article data...")
        print(f"   Agent A would now process:")
        print(f"     - Analyze sentiment: {article['sentiment']}")
        print(f"     - Generate investment signal")
        print(f"     - Store reasoning trace")


def main():
    """Run complete pipeline."""
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "REAL NEWS DATA → SUI EVENT → AGENT TRIGGER" + " " * 15 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    # Step 1: Fetch real news
    articles = fetch_real_news()

    if not articles:
        print("❌ No articles fetched. Check API token.")
        return

    # Step 2: Store in DB
    db_ids = store_in_local_db(articles)

    # Step 3: Emit SUI events (simulated)
    events = simulate_sui_event_emission(db_ids, articles)

    # Step 4: Event watcher detects
    simulate_event_watcher(events)

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✓ Fetched {len(articles)} real articles from CryptoPanic")
    print(f"✓ Stored in local database")
    print(f"✓ Emitted {len(events)} SUI events (simulated)")
    print(f"✓ Event watcher signaled agents for relevant news")
    print()
    print("Key Insight:")
    print("  • SUI Events = Lightweight signals (200 bytes)")
    print("  • Real Data = Stored in DB/Walrus (can be 10KB+)")
    print("  • Agents fetch full data when signaled")
    print()
    print("Data Storage Options:")
    print("  1. Local DB (SQLite) - For demo/development")
    print("  2. Walrus DA - For production (immutable, decentralized)")
    print("  3. Hybrid - Metadata on SUI, full data on Walrus")
    print()


if __name__ == "__main__":
    main()
