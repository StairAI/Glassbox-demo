#!/usr/bin/env python3
"""
Glass Box Explorer API Server

Provides REST API endpoints to fetch data from:
- SUI blockchain (trigger metadata)
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

from src.demo.trigger_registry import TriggerRegistry
from src.storage.walrus_client import WalrusClient, WalrusHelper
from src.storage.activity_db import ActivityDB
from dotenv import load_dotenv

# Load environment
load_dotenv('../../demo/config/.env')

app = Flask(__name__,
            static_folder='../static',
            static_url_path='/static',
            template_folder='../')
CORS(app)  # Enable CORS for frontend

# Initialize components
# Use simulated Walrus with persistent file storage
print(f"[DEBUG] Initializing Walrus client:")
print(f"  Mode: SIMULATED (file-based storage)")
print(f"  Storage dir: ../../demo/data/walrus_blobs")

walrus_client = WalrusClient(
    simulated=True,
    storage_dir="../../demo/data/walrus_blobs"
)

db = ActivityDB(db_path="../../demo/data/activity.db")
registry = TriggerRegistry(registry_path="../../demo/data/trigger_registry.json")

# Simple cache to avoid re-reading JSON on every request
_cache = {
    'triggers': None,
    'last_modified': None
}

def get_registry_path():
    return "../../demo/data/trigger_registry.json"

def get_cached_triggers():
    """Get triggers with simple file modification time caching."""
    import os
    registry_path = get_registry_path()

    try:
        current_mtime = os.path.getmtime(registry_path)

        # Check if cache is valid
        if _cache['triggers'] is not None and _cache['last_modified'] == current_mtime:
            return _cache['triggers']

        # Cache miss or outdated - reload
        news = registry.get_triggers(trigger_type='news', limit=1000)
        signals = registry.get_triggers(trigger_type='signal', limit=1000)
        all_triggers = news + signals

        # Update cache
        _cache['triggers'] = all_triggers
        _cache['last_modified'] = current_mtime

        return all_triggers
    except Exception as e:
        print(f"Cache error: {e}")
        # Fallback to direct registry access
        news = registry.get_triggers(trigger_type='news', limit=1000)
        signals = registry.get_triggers(trigger_type='signal', limit=1000)
        return news + signals


# ============================================================================
# API Endpoints
# ============================================================================

@app.route('/api/triggers', methods=['GET'])
def get_triggers():
    """
    Get all triggers from SUI network (via TriggerRegistry).

    Query params:
        - type: Filter by trigger type (news, signal)
        - owner: Filter by owner address
        - limit: Max number of triggers to return
    """
    try:
        trigger_type = request.args.get('type')
        owner = request.args.get('owner')
        limit = int(request.args.get('limit', 100))

        # Use cached triggers
        triggers = get_cached_triggers()

        # Filter by type if specified
        if trigger_type:
            triggers = [t for t in triggers if t.get('trigger_type') == trigger_type]

        # Filter by owner if specified
        if owner and owner != 'all':
            triggers = [t for t in triggers if t.get('owner') == owner]

        # Sort by timestamp (newest first)
        triggers.sort(key=lambda t: t.get('timestamp', ''), reverse=True)
        triggers = triggers[:limit]

        return jsonify({
            'success': True,
            'count': len(triggers),
            'triggers': triggers
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/triggers/<trigger_id>/full', methods=['GET'])
def get_trigger_full_data(trigger_id: str):
    """
    Get full trigger data from Walrus.

    This fetches the complete data stored on Walrus, not just metadata.
    """
    try:
        # Get trigger metadata
        trigger = registry.get_trigger(trigger_id)

        if not trigger:
            return jsonify({
                'success': False,
                'error': f'Trigger {trigger_id} not found'
            }), 404

        walrus_blob_id = trigger.get('walrus_blob_id')
        if not walrus_blob_id:
            return jsonify({
                'success': False,
                'error': 'No Walrus blob ID found for this trigger'
            }), 404

        print(f"[DEBUG] Fetching blob from Walrus: {walrus_blob_id}")

        # Fetch full data from Walrus
        full_data = WalrusHelper.fetch_json(walrus_client, walrus_blob_id)

        print(f"[DEBUG] Successfully fetched data from Walrus")

        return jsonify({
            'success': True,
            'trigger_id': trigger_id,
            'metadata': trigger,
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
        # Get all signal triggers grouped by producer (agent)
        signals = registry.get_triggers(trigger_type='signal', limit=1000)

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
            agent_stats[producer]['signal_ids'].append(signal.get('trigger_id'))

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
        signals = registry.get_triggers(trigger_type='signal', limit=1000)
        agent_signals = [s for s in signals if s.get('producer') == agent_id]

        traces = []

        for signal in agent_signals[:10]:  # Limit to 10 most recent
            trace_blob_id = signal.get('walrus_trace_id')

            if trace_blob_id:
                try:
                    # Fetch reasoning trace from Walrus
                    trace_data = WalrusHelper.fetch_json(walrus_client, trace_blob_id)
                    trace_data['signal_id'] = signal.get('trigger_id')
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
    Get list of all owner addresses from mocked_accounts table.

    Returns:
        List of owner addresses with their project names
    """
    try:
        # Get all mocked accounts from database
        accounts = db.list_mocked_accounts(active_only=True)

        # Format for frontend
        owners = [
            {
                'address': acc['account_address'],
                'project_name': acc['project_name'],
                'description': acc['description']
            }
            for acc in accounts
        ]

        return jsonify({
            'success': True,
            'count': len(owners),
            'owners': owners
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Get overall system statistics.
    """
    try:
        db_stats = db.get_stats()

        # Get trigger counts
        news_triggers = registry.get_triggers(trigger_type='news', limit=10000)
        signal_triggers = registry.get_triggers(trigger_type='signal', limit=10000)

        return jsonify({
            'success': True,
            'stats': {
                'database': db_stats,
                'triggers': {
                    'news': len(news_triggers),
                    'signal': len(signal_triggers),
                    'total': len(news_triggers) + len(signal_triggers)
                }
            }
        })

    except Exception as e:
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
    print("  GET  /api/triggers           - List all triggers")
    print("  GET  /api/triggers/{id}/full - Get full trigger data from Walrus")
    print("  GET  /api/owners             - List all owner addresses")
    print("  GET  /api/agents             - List all agents")
    print("  GET  /api/agents/{id}/traces - Get agent reasoning traces")
    print("  GET  /api/stats              - System statistics")
    print("  GET  /api/health             - Health check")
    print()
    print("=" * 80)

    app.run(host='0.0.0.0', port=8080, debug=True)
