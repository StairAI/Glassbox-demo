"""Quick test of the demo with 3 cycles"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src" / "data_sources"))
sys.path.append(str(Path(__file__).parent / "src" / "agent"))
sys.path.append(str(Path(__file__).parent / "src" / "sdk"))

from src.data_sources.news_fetcher import NewsFetcher
from src.data_sources.sentiment_analyzer import SentimentAnalyzer
from src.agent.bitcoin_agent import BitcoinAgent
from src.sdk.glassbox_sdk import GlassBoxSDK
from src.sdk.trace_generator import ReasoningTraceGenerator

async def test_demo():
    print("=" * 80)
    print("Bitcoin Investment Agent Demo - Quick Test (3 cycles)")
    print("=" * 80)
    print()

    # Initialize
    AGENT_ID = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"

    fetcher = NewsFetcher()
    analyzer = SentimentAnalyzer()
    agent = BitcoinAgent(AGENT_ID)
    sdk = GlassBoxSDK()
    trace_gen = ReasoningTraceGenerator(AGENT_ID, sdk)

    print()

    for cycle in range(1, 4):
        print(f"[Cycle {cycle}] {'-' * 65}")

        # Fetch and analyze
        news = fetcher.fetch()
        sentiment = analyzer.analyze(news)

        print(f"📰 NEWS: {news['headline'][:70]}...")
        print(f"📊 SENTIMENT: {sentiment['sentiment']:+.2f} ({sentiment['signal']})")

        # Start trace
        trace_gen.start_trace({
            "source": "news_stream",
            "payload": news
        })

        # Process
        context = agent.get_context_snapshot()
        trace_gen.set_context(context)

        signal = agent.process_news(news, sentiment)

        # Log reasoning
        steps = agent.generate_reasoning_steps(news, sentiment, signal)
        for behavior, data, tool, params in steps:
            trace_gen.log_behavior(behavior, data, tool, params)

        # Terminal action
        if signal:
            trace_gen.set_terminal_action("signal_generated", signal)
            print(f"🚨 SIGNAL: {signal['direction']} @ ${signal['entry_price']:,.0f}")
        else:
            trace_gen.set_terminal_action("no_action", {"status": "monitoring"})
            print(f"⏳ MONITORING")

        # Submit
        response = trace_gen.submit_trace()
        print(f"✅ TRACE: {response['trace_id']}")
        print()

        await asyncio.sleep(1)

    print("=" * 80)
    print(f"✓ Test completed successfully!")
    print(f"  Traces submitted: {sdk.get_trace_count()}")
    print(f"  Signals generated: {agent.signal_count}")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_demo())
