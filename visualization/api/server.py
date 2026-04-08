#!/usr/bin/env python3
"""
Glass Box Explorer API Server

Provides REST API endpoints to fetch data from:
- SUI blockchain (signal metadata)
- Walrus decentralized storage (full data, reasoning traces)
- Local database (activity logs)
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# Add demo directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../demo'))

from src.demo.signal_registry import SignalRegistry
from src.storage.walrus_client import WalrusClient, WalrusHelper
from dotenv import load_dotenv

# Load environment
load_dotenv('../../demo/config/.env')

app = Flask(__name__,
            static_folder='../static',
            static_url_path='/static',
            template_folder='../')
CORS(app)  # Enable CORS for frontend

# Initialize components
# Check environment for Walrus configuration
walrus_enabled = os.getenv("WALRUS_ENABLED", "false").lower() == "true"
publisher_url = os.getenv("WALRUS_PUBLISHER_URL")
aggregator_url = os.getenv("WALRUS_AGGREGATOR_URL")

print(f"[DEBUG] Initializing Walrus client:")
print(f"  Enabled: {walrus_enabled}")
if walrus_enabled:
    print(f"  Mode: REAL WALRUS TESTNET")
    print(f"  Publisher: {publisher_url}")
    print(f"  Aggregator: {aggregator_url}")
else:
    print(f"  Mode: SIMULATED (file-based storage)")
    print(f"  Storage dir: ../../demo/data/walrus_blobs")

walrus_client = WalrusClient(
    publisher_url=publisher_url,
    aggregator_url=aggregator_url,
    simulated=not walrus_enabled,
    storage_dir="../../demo/data/walrus_blobs" if not walrus_enabled else None
)

# IMPORTANT: Use absolute path to database so SignalRegistry connects to correct database
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_ABSOLUTE_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "../../demo/data/glassbox.db"))
registry = SignalRegistry(registry_path="../../demo/data/signal_registry.json", db_path=DB_ABSOLUTE_PATH)

# Simple cache to avoid re-reading database on every request
_cache = {
    'signals': None,
    'last_modified': None
}

def get_database_path():
    """Get absolute path to SQLite database."""
    return DB_ABSOLUTE_PATH

def get_cached_signals():
    """Get signals with simple database modification time caching."""
    import os
    db_path = get_database_path()

    try:
        # Check database modification time
        current_mtime = os.path.getmtime(db_path)

        # Check if cache is valid
        if _cache['signals'] is not None and _cache['last_modified'] == current_mtime:
            return _cache['signals']

        # Cache miss or outdated - reload from database
        news = registry.get_signals(signal_type='news', limit=1000)
        insights = registry.get_signals(signal_type='insight', limit=1000)
        prices = registry.get_signals(signal_type='price', limit=1000)
        all_signals = news + insights + prices

        # Update cache
        _cache['signals'] = all_signals
        _cache['last_modified'] = current_mtime

        return all_signals
    except Exception as e:
        print(f"[ERROR] Cache error: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to direct registry access
        news = registry.get_signals(signal_type='news', limit=1000)
        insights = registry.get_signals(signal_type='insight', limit=1000)
        prices = registry.get_signals(signal_type='price', limit=1000)
        return news + insights + prices


# ============================================================================
# API Endpoints
# ============================================================================

@app.route('/api/signals', methods=['GET'])
def get_signals():
    """
    Get all signals from SUI network (via SignalRegistry).

    Query params:
        - type: Filter by signal type (news, signal)
        - owner: Filter by owner address
        - limit: Max number of signals to return
    """
    try:
        signal_type = request.args.get('type')
        owner = request.args.get('owner')
        limit = int(request.args.get('limit', 100))

        # Use cached signals
        signals = get_cached_signals()

        # Filter by type if specified
        if signal_type:
            signals = [t for t in signals if t.get('signal_type') == signal_type]

        # Filter by owner if specified
        if owner and owner != 'all':
            signals = [t for t in signals if t.get('owner') == owner]

        # Sort by timestamp (newest first)
        signals.sort(key=lambda t: t.get('timestamp', ''), reverse=True)
        signals = signals[:limit]

        return jsonify({
            'success': True,
            'count': len(signals),
            'signals': signals
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/signals/<signal_id>/full', methods=['GET'])
def get_signal_full_data(signal_id: str):
    """
    Get full signal data from Walrus.

    This fetches the complete data stored on Walrus, not just metadata.
    """
    try:
        # Get signal metadata
        signal = registry.get_signal(signal_id)

        if not signal:
            return jsonify({
                'success': False,
                'error': f'Signal {signal_id} not found'
            }), 404

        walrus_blob_id = signal.get('walrus_blob_id')
        if not walrus_blob_id:
            return jsonify({
                'success': False,
                'error': 'No Walrus blob ID found for this signal'
            }), 404

        print(f"[DEBUG] Fetching blob from Walrus: {walrus_blob_id}")

        # Fetch full data from Walrus
        full_data = WalrusHelper.fetch_json(walrus_client, walrus_blob_id)

        print(f"[DEBUG] Successfully fetched data from Walrus")

        return jsonify({
            'success': True,
            'signal_id': signal_id,
            'metadata': signal,
            'full_data': full_data
        })

    except Exception as e:
        print(f"[ERROR] Failed to fetch Walrus data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/agents', methods=['GET'])
def get_agents():
    """
    Get list of all agents with their execution statistics.
    """
    try:
        # Get all signal signals grouped by producer (agent)
        signals = registry.get_signals(signal_type='insight', limit=1000)

        # Group by agent
        agent_stats = {}
        for signal in signals:
            producer = signal.get('producer', 'unknown')

            if producer not in agent_stats:
                agent_stats[producer] = {
                    'agent_id': producer,
                    'name': format_agent_name(producer),
                    'icon': get_agent_icon(producer),
                    'description': get_agent_description(producer),
                    'execution_count': 0,
                    'total_confidence': 0,
                    'avg_confidence': 0,
                    'signal_ids': []
                }

            agent_stats[producer]['execution_count'] += 1
            agent_stats[producer]['total_confidence'] += signal.get('confidence', 0)
            agent_stats[producer]['signal_ids'].append(signal.get('signal_id'))

        # Calculate averages
        for agent in agent_stats.values():
            if agent['execution_count'] > 0:
                agent['avg_confidence'] = agent['total_confidence'] / agent['execution_count']
            del agent['total_confidence']  # Don't send to frontend

        agents_list = list(agent_stats.values())

        return jsonify({
            'success': True,
            'count': len(agents_list),
            'agents': agents_list
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/agents/<agent_id>/traces', methods=['GET'])
def get_agent_reasoning_traces(agent_id: str):
    """
    Get all reasoning traces for a specific agent.

    This fetches the complete reasoning traces from Walrus.
    """
    try:
        # Get all signals from this agent
        signals = registry.get_signals(signal_type='insight', limit=1000)
        agent_signals = [s for s in signals if s.get('producer') == agent_id]

        traces = []

        for signal in agent_signals[:5]:  # Limit to 5 most recent
            trace_blob_id = signal.get('walrus_trace_id')

            if trace_blob_id:
                try:
                    # Fetch reasoning trace from Walrus
                    trace_data = WalrusHelper.fetch_json(walrus_client, trace_blob_id)
                    trace_data['signal_id'] = signal.get('signal_id')
                    trace_data['walrus_blob_id'] = trace_blob_id
                    traces.append(trace_data)
                except Exception as e:
                    print(f"Error fetching trace {trace_blob_id}: {e}")
                    continue

        return jsonify({
            'success': True,
            'agent': {
                'agent_id': agent_id,
                'name': format_agent_name(agent_id),
                'icon': get_agent_icon(agent_id),
                'description': get_agent_description(agent_id)
            },
            'traces_count': len(traces),
            'traces': traces
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/owners', methods=['GET'])
def get_owners():
    """
    Get list of owner addresses from both signals and mocked_accounts tables.

    Query params:
        source (optional): 'signals', 'mocked', or 'all' (default: 'all')

    Returns:
        List of owner addresses with their signal counts and display names
    """
    try:
        source = request.args.get('source', 'all')

        result = {
            'success': True,
            'owners': []
        }

        # Get signal owners
        if source in ['signals', 'all']:
            signal_owners = registry.get_unique_owners()
            for owner in signal_owners:
                result['owners'].append({
                    'address': owner['owner'],
                    'signal_count': owner['signal_count'],
                    'source': 'signals',
                    'name': None  # Will be enriched with mocked account name if exists
                })

        # Get mocked accounts
        if source in ['mocked', 'all']:
            mocked_accounts = registry.get_mocked_accounts()
            for account in mocked_accounts:
                # Check if this account already exists in signal owners
                existing = next((o for o in result['owners'] if o['address'] == account['address']), None)
                if existing:
                    # Enrich existing entry with name
                    existing['name'] = account['name']
                    existing['description'] = account.get('description')
                else:
                    # Add as new entry with zero signals
                    result['owners'].append({
                        'address': account['address'],
                        'signal_count': 0,
                        'source': 'mocked',
                        'name': account['name'],
                        'description': account.get('description')
                    })

        result['count'] = len(result['owners'])
        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Get overall system statistics from glassbox database.
    """
    try:
        # Get stats from glassbox database
        db_stats = registry.get_stats()

        # Get signal counts
        news_signals = registry.get_signals(signal_type='news', limit=10000)
        insight_signals = registry.get_signals(signal_type='insight', limit=10000)
        price_signals = registry.get_signals(signal_type='price', limit=10000)

        return jsonify({
            'success': True,
            'stats': {
                'database': db_stats,
                'signals': {
                    'news': len(news_signals),
                    'insight': len(insight_signals),
                    'price': len(price_signals),
                    'total': len(news_signals) + len(insight_signals) + len(price_signals)
                }
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/walrus/<blob_id>', methods=['GET'])
def get_walrus_blob(blob_id: str):
    """
    Proxy endpoint to fetch raw JSON from Walrus.

    This endpoint exists to avoid CORS issues when fetching directly
    from Walrus aggregator in the browser.

    Args:
        blob_id: Walrus blob ID

    Returns:
        Raw JSON data stored in Walrus
    """
    try:
        print(f"[DEBUG] Proxying Walrus fetch for blob: {blob_id}")

        # Fetch data from Walrus using the helper
        data = WalrusHelper.fetch_json(walrus_client, blob_id)

        print(f"[DEBUG] Successfully fetched blob from Walrus")

        return jsonify({
            'success': True,
            'blob_id': blob_id,
            'data': data
        })

    except Exception as e:
        print(f"[ERROR] Failed to fetch Walrus blob {blob_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'walrus': not walrus_client.simulated,
            'database': True,
            'registry': True
        }
    })


# ============================================================================
# Frontend Routes
# ============================================================================

@app.route('/')
def index():
    """Serve the main frontend page."""
    return send_from_directory('..', 'index.html')


# ============================================================================
# Helper Functions
# ============================================================================

def format_agent_name(agent_id: str) -> str:
    """Format agent ID to human-readable name."""
    name_map = {
        'agent_a': 'Agent A - Sentiment Analysis',
        'agent_b': 'Agent B - Investment Predictions',
        'agent_c': 'Agent C - Portfolio Management'
    }
    return name_map.get(agent_id, agent_id.replace('_', ' ').title())


def get_agent_icon(agent_id: str) -> str:
    """Get emoji icon for agent."""
    icon_map = {
        'agent_a': '📊',
        'agent_b': '💹',
        'agent_c': '💼'
    }
    return icon_map.get(agent_id, '🤖')


def get_agent_description(agent_id: str) -> str:
    """Get agent description."""
    desc_map = {
        'agent_a': 'Analyzes cryptocurrency news sentiment using Claude Sonnet 4.5',
        'agent_b': 'Generates investment predictions based on sentiment and price data',
        'agent_c': 'Manages portfolio allocation based on risk and predictions'
    }
    return desc_map.get(agent_id, 'Multi-agent system component')


# ============================================================================
# Workflow API Endpoints
# ============================================================================

@app.route('/api/workflow/metadata', methods=['GET'])
def get_workflow_metadata():
    """
    Get lightweight workflow metadata for initial load.

    Returns:
        - List of agents with their signal counts
        - List of signal_ids grouped by agent (no full data)
    """
    try:
        # Get all insight signals (agent outputs)
        insights = registry.get_signals(signal_type='insight', limit=1000)

        # Build agent -> signals mapping
        agent_signals = {}
        for signal in insights:
            producer = signal.get('producer', 'unknown')
            if producer not in agent_signals:
                agent_signals[producer] = []

            agent_signals[producer].append({
                'signal_id': signal.get('signal_id'),
                'timestamp': signal.get('timestamp'),
                'insight_type': signal.get('insight_type'),
                'confidence': signal.get('confidence')
            })

        # Build agent list
        agents = []
        for agent_id, signals in agent_signals.items():
            agents.append({
                'agent_id': agent_id,
                'name': format_agent_name(agent_id),
                'signal_count': len(signals),
                'signals': signals
            })

        return jsonify({
            'success': True,
            'agents': agents
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/workflow/lineage/<signal_id>', methods=['GET'])
def get_signal_lineage(signal_id):
    """
    Get complete lineage for a specific signal.

    Returns:
        - Signal details
        - Reasoning trace (if available)
        - Upstream signals (dependencies)
        - Agent that produced it
    """
    try:
        # Find the signal in registry
        all_signals = get_cached_signals()
        target_signal = None
        for s in all_signals:
            if s.get('signal_id') == signal_id:
                target_signal = s
                break

        if not target_signal:
            return jsonify({
                'success': False,
                'error': f'Signal {signal_id} not found'
            }), 404

        # Get reasoning trace if it's an insight signal
        reasoning_trace = None
        if target_signal.get('signal_type') == 'insight':
            walrus_trace_id = target_signal.get('walrus_trace_id')
            if walrus_trace_id:
                try:
                    reasoning_trace = WalrusHelper.fetch_json(walrus_client, walrus_trace_id)
                except Exception as e:
                    print(f"Error fetching reasoning trace: {e}")

        # Determine upstream signals based on agent logic
        # This is hardcoded for now, but could be tracked in a dependency table
        upstream_signals = []
        producer = target_signal.get('producer')

        if producer == 'agent_b_investment':
            # Agent B consumes price signals
            price_signals = [s for s in all_signals
                           if s.get('signal_type') == 'price' and s.get('symbol') == 'BTC']
            if price_signals:
                # Get the most recent price signal before this insight
                target_time = target_signal.get('timestamp')
                valid_prices = [p for p in price_signals if p.get('timestamp') < target_time]
                if valid_prices:
                    upstream_signals.append(max(valid_prices, key=lambda x: x.get('timestamp')))

        elif producer == 'agent_c_portfolio':
            # Agent C consumes price + investment signals
            target_time = target_signal.get('timestamp')

            # Find price signal
            price_signals = [s for s in all_signals
                           if s.get('signal_type') == 'price' and s.get('symbol') == 'BTC'
                           and s.get('timestamp') < target_time]
            if price_signals:
                upstream_signals.append(max(price_signals, key=lambda x: x.get('timestamp')))

            # Find investment signal from Agent B
            investment_signals = [s for s in all_signals
                                if s.get('signal_type') == 'insight'
                                and s.get('producer') == 'agent_b_investment'
                                and s.get('timestamp') < target_time]
            if investment_signals:
                upstream_signals.append(max(investment_signals, key=lambda x: x.get('timestamp')))

        return jsonify({
            'success': True,
            'signal': target_signal,
            'reasoning_trace': reasoning_trace,
            'upstream_signals': upstream_signals
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# Run Server
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("Glass Box Explorer API Server")
    print("=" * 80)
    print()
    print("Frontend: http://localhost:8080")
    print("API Base: http://localhost:8080/api")
    print()
    print("Available Endpoints:")
    print("  GET  /api/signals                   - List all signals")
    print("  GET  /api/signals/{id}/full         - Get full signal data from Walrus")
    print("  GET  /api/walrus/{blob_id}          - Proxy to fetch raw JSON from Walrus (avoids CORS)")
    print("  GET  /api/owners                    - List all owner addresses")
    print("  GET  /api/agents                    - List all agents")
    print("  GET  /api/agents/{id}/traces        - Get agent reasoning traces")
    print("  GET  /api/workflow/metadata         - Get workflow metadata (agents + signals)")
    print("  GET  /api/workflow/lineage/{id}     - Get signal lineage and reasoning trace")
    print("  GET  /api/stats                     - System statistics")
    print("  GET  /api/health                    - Health check")
    print()
    print("=" * 80)

    app.run(host='0.0.0.0', port=8080, debug=True)
