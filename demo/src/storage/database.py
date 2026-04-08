#!/usr/bin/env python3
"""
SQLite Database for Glass Box Protocol Demo

This module provides a lightweight database for tracking:
- Signals (key indices only, full data on Walrus)
- Agents (execution metadata)
- Reasoning Traces (references to Walrus blobs)

The database stores only essential indices and metadata.
Full signal data is always fetched from Walrus for integrity verification.
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class GlassBoxDatabase:
    """
    SQLite database for Glass Box Protocol signal tracking.

    Stores lightweight indices and metadata, while full data lives on Walrus.
    """

    def __init__(self, db_path: str = "data/glassbox.db"):
        """
        Initialize database connection and create tables if needed.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize connection
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Return rows as dicts

        # Create tables
        self._create_tables()

    def _create_tables(self):
        """Create database schema if it doesn't exist."""
        cursor = self.conn.cursor()

        # ====================================================================
        # SIGNALS TABLE - Lightweight index of all signals
        # ====================================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id TEXT UNIQUE NOT NULL,
                signal_type TEXT NOT NULL,

                -- Walrus storage references
                walrus_blob_id TEXT NOT NULL,
                data_hash TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,

                -- Signal metadata
                producer TEXT NOT NULL,
                owner TEXT NOT NULL,
                timestamp TEXT NOT NULL,

                -- Type-specific fields (nullable)
                insight_type TEXT,
                confidence REAL,
                symbol TEXT,
                price_usd REAL,
                articles_count INTEGER,

                -- Reasoning trace reference (for insight signals)
                walrus_trace_id TEXT,

                -- Tracking
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indices for signals table
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_signal_type ON signals(signal_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_producer ON signals(producer)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_owner ON signals(owner)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON signals(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_walrus_blob ON signals(walrus_blob_id)")

        # ====================================================================
        # AGENTS TABLE - Agent metadata/definitions
        # ====================================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                agent_name TEXT NOT NULL,
                agent_version TEXT NOT NULL,
                agent_type TEXT,
                description TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ====================================================================
        # AGENTS_RUN TABLE - Track individual agent execution runs
        # ====================================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents_run (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                agent_version TEXT NOT NULL,

                -- Execution metadata
                execution_id TEXT UNIQUE NOT NULL,
                execution_time_ms REAL,

                -- Input/Output signals
                input_signal_ids TEXT,
                output_signal_id TEXT,

                -- Results
                confidence REAL,
                success BOOLEAN NOT NULL,
                error_message TEXT,

                -- Reasoning trace
                walrus_trace_id TEXT,

                -- Tracking
                executed_at TEXT NOT NULL,

                -- Foreign key
                FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
            )
        """)

        # Create indices for agents_run table
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agents_run_agent_id ON agents_run(agent_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agents_run_execution_id ON agents_run(execution_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agents_run_output_signal ON agents_run(output_signal_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agents_run_executed_at ON agents_run(executed_at)")

        # ====================================================================
        # REASONING_TRACES TABLE - Track reasoning ledgers
        # ====================================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reasoning_traces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                -- Reference
                walrus_trace_id TEXT UNIQUE NOT NULL,
                signal_id TEXT NOT NULL,

                -- Agent info
                agent_id TEXT NOT NULL,
                agent_version TEXT NOT NULL,

                -- Trace metadata
                step_count INTEGER NOT NULL,
                execution_time_ms REAL,
                confidence REAL,

                -- LLM info (if applicable)
                llm_provider TEXT,
                llm_model TEXT,

                -- Storage
                data_hash TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,

                -- Tracking
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                -- Foreign key
                FOREIGN KEY (signal_id) REFERENCES signals(signal_id)
            )
        """)

        # Create indices for reasoning_traces table
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_walrus_trace ON reasoning_traces(walrus_trace_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_signal_id ON reasoning_traces(signal_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_id ON reasoning_traces(agent_id)")

        # ====================================================================
        # MOCKED_ACCOUNTS TABLE - Mock wallet addresses for demo
        # ====================================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mocked_accounts (
                address TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()
        cursor.close()

    # ========================================================================
    # SIGNALS - CRUD Operations
    # ========================================================================

    def insert_signal(self, signal_data: Dict[str, Any]) -> int:
        """
        Insert a new signal into the database.

        Args:
            signal_data: Signal metadata dictionary

        Returns:
            Row ID of inserted signal
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO signals (
                signal_id, signal_type, walrus_blob_id, data_hash, size_bytes,
                producer, owner, timestamp, insight_type, confidence,
                symbol, price_usd, articles_count, walrus_trace_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            signal_data.get('signal_id'),
            signal_data['signal_type'],
            signal_data['walrus_blob_id'],
            signal_data['data_hash'],
            signal_data['size_bytes'],
            signal_data['producer'],
            signal_data['owner'],
            signal_data['timestamp'],
            signal_data.get('insight_type'),
            signal_data.get('confidence'),
            signal_data.get('symbol'),
            signal_data.get('price_usd'),
            signal_data.get('articles_count'),
            signal_data.get('walrus_trace_id')
        ))

        self.conn.commit()
        row_id = cursor.lastrowid
        cursor.close()

        return row_id

    def get_signals(
        self,
        signal_type: Optional[str] = None,
        producer: Optional[str] = None,
        owner: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Query signals with optional filters.

        Args:
            signal_type: Filter by signal type ('news', 'price', 'insight')
            producer: Filter by producer/agent
            owner: Filter by owner address
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of signal dictionaries
        """
        cursor = self.conn.cursor()

        # Build query dynamically
        query = "SELECT * FROM signals WHERE 1=1"
        params = []

        if signal_type:
            query += " AND signal_type = ?"
            params.append(signal_type)

        if producer:
            query += " AND producer = ?"
            params.append(producer)

        if owner:
            query += " AND owner = ?"
            params.append(owner)

        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()

        # Convert to dicts
        return [dict(row) for row in rows]

    def get_signal_by_id(self, signal_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single signal by its ID.

        Args:
            signal_id: Signal ID to fetch

        Returns:
            Signal dictionary or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM signals WHERE signal_id = ?", (signal_id,))
        row = cursor.fetchone()
        cursor.close()

        return dict(row) if row else None

    def count_signals(
        self,
        signal_type: Optional[str] = None,
        producer: Optional[str] = None
    ) -> int:
        """
        Count signals with optional filters.

        Args:
            signal_type: Filter by signal type
            producer: Filter by producer

        Returns:
            Number of matching signals
        """
        cursor = self.conn.cursor()

        query = "SELECT COUNT(*) FROM signals WHERE 1=1"
        params = []

        if signal_type:
            query += " AND signal_type = ?"
            params.append(signal_type)

        if producer:
            query += " AND producer = ?"
            params.append(producer)

        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        cursor.close()

        return count

    # ========================================================================
    # AGENTS - CRUD Operations (Agent definitions)
    # ========================================================================

    def insert_agent(self, agent_data: Dict[str, Any]) -> str:
        """
        Register an agent definition.

        Args:
            agent_data: Agent metadata (agent_id, agent_name, agent_version, agent_type, description)

        Returns:
            agent_id
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO agents (
                agent_id, agent_name, agent_version, agent_type, description, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            agent_data['agent_id'],
            agent_data.get('agent_name', agent_data['agent_id']),
            agent_data.get('agent_version', '1.0'),
            agent_data.get('agent_type'),
            agent_data.get('description'),
            datetime.now().isoformat()
        ))

        self.conn.commit()
        cursor.close()

        return agent_data['agent_id']

    def get_agents(self) -> List[Dict[str, Any]]:
        """
        Get all registered agents.

        Returns:
            List of agent definitions
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM agents ORDER BY agent_id")
        rows = cursor.fetchall()
        cursor.close()

        return [dict(row) for row in rows]

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific agent by ID.

        Args:
            agent_id: Agent identifier

        Returns:
            Agent metadata or None
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM agents WHERE agent_id = ?", (agent_id,))
        row = cursor.fetchone()
        cursor.close()

        return dict(row) if row else None

    # ========================================================================
    # AGENTS_RUN - CRUD Operations (Agent execution runs)
    # ========================================================================

    def insert_agent_execution(self, execution_data: Dict[str, Any]) -> int:
        """
        Record an agent execution run.

        Args:
            execution_data: Agent execution metadata

        Returns:
            Row ID of inserted execution
        """
        cursor = self.conn.cursor()

        # Convert input_signal_ids list to JSON string
        import json
        input_signals_json = json.dumps(execution_data.get('input_signal_ids', []))

        cursor.execute("""
            INSERT INTO agents_run (
                agent_id, agent_version, execution_id, execution_time_ms,
                input_signal_ids, output_signal_id, confidence, success,
                error_message, walrus_trace_id, executed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            execution_data['agent_id'],
            execution_data['agent_version'],
            execution_data['execution_id'],
            execution_data.get('execution_time_ms'),
            input_signals_json,
            execution_data.get('output_signal_id'),
            execution_data.get('confidence'),
            execution_data.get('success', True),
            execution_data.get('error_message'),
            execution_data.get('walrus_trace_id'),
            execution_data['executed_at']
        ))

        self.conn.commit()
        row_id = cursor.lastrowid
        cursor.close()

        return row_id

    def get_agent_executions(
        self,
        agent_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get agent execution history.

        Args:
            agent_id: Filter by specific agent
            limit: Maximum results

        Returns:
            List of execution records
        """
        cursor = self.conn.cursor()

        if agent_id:
            cursor.execute(
                "SELECT * FROM agents_run WHERE agent_id = ? ORDER BY executed_at DESC LIMIT ?",
                (agent_id, limit)
            )
        else:
            cursor.execute(
                "SELECT * FROM agents_run ORDER BY executed_at DESC LIMIT ?",
                (limit,)
            )

        rows = cursor.fetchall()
        cursor.close()

        return [dict(row) for row in rows]

    # ========================================================================
    # REASONING TRACES - CRUD Operations
    # ========================================================================

    def insert_reasoning_trace(self, trace_data: Dict[str, Any]) -> int:
        """
        Record a reasoning trace reference.

        Args:
            trace_data: Reasoning trace metadata

        Returns:
            Row ID of inserted trace
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO reasoning_traces (
                walrus_trace_id, signal_id, agent_id, agent_version,
                step_count, execution_time_ms, confidence, llm_provider,
                llm_model, data_hash, size_bytes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trace_data['walrus_trace_id'],
            trace_data['signal_id'],
            trace_data['agent_id'],
            trace_data['agent_version'],
            trace_data.get('step_count', 0),
            trace_data.get('execution_time_ms'),
            trace_data.get('confidence'),
            trace_data.get('llm_provider'),
            trace_data.get('llm_model'),
            trace_data['data_hash'],
            trace_data['size_bytes']
        ))

        self.conn.commit()
        row_id = cursor.lastrowid
        cursor.close()

        return row_id

    def get_reasoning_trace(self, walrus_trace_id: str) -> Optional[Dict[str, Any]]:
        """
        Get reasoning trace metadata by Walrus ID.

        Args:
            walrus_trace_id: Walrus blob ID of the trace

        Returns:
            Trace metadata or None
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM reasoning_traces WHERE walrus_trace_id = ?",
            (walrus_trace_id,)
        )
        row = cursor.fetchone()
        cursor.close()

        return dict(row) if row else None

    def get_traces_by_agent(
        self,
        agent_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all reasoning traces for an agent.

        Args:
            agent_id: Agent identifier
            limit: Maximum results

        Returns:
            List of trace metadata
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM reasoning_traces WHERE agent_id = ? ORDER BY created_at DESC LIMIT ?",
            (agent_id, limit)
        )
        rows = cursor.fetchall()
        cursor.close()

        return [dict(row) for row in rows]

    # ========================================================================
    # MOCKED_ACCOUNTS - CRUD Operations
    # ========================================================================

    def insert_mocked_account(self, address: str, name: str, description: Optional[str] = None) -> str:
        """
        Add a mocked wallet account.

        Args:
            address: Wallet address
            name: Display name
            description: Optional description

        Returns:
            address
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO mocked_accounts (address, name, description)
            VALUES (?, ?, ?)
        """, (address, name, description))

        self.conn.commit()
        cursor.close()

        return address

    def get_mocked_accounts(self) -> List[Dict[str, Any]]:
        """
        Get all mocked accounts.

        Returns:
            List of mocked account dicts
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM mocked_accounts ORDER BY created_at DESC")
        rows = cursor.fetchall()
        cursor.close()

        return [dict(row) for row in rows]

    def get_mocked_account(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific mocked account by address.

        Args:
            address: Wallet address

        Returns:
            Account dict or None
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM mocked_accounts WHERE address = ?", (address,))
        row = cursor.fetchone()
        cursor.close()

        return dict(row) if row else None

    # ========================================================================
    # UTILITY
    # ========================================================================

    def get_unique_owners(self) -> List[Dict[str, Any]]:
        """
        Get list of unique owner addresses from signals.

        Returns:
            List of owner dicts with address and signal count
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT owner, COUNT(*) as signal_count
            FROM signals
            GROUP BY owner
            ORDER BY signal_count DESC
        """)

        owners = [
            {
                'address': row[0],
                'signal_count': row[1]
            }
            for row in cursor.fetchall()
        ]

        cursor.close()

        return owners

    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.

        Returns:
            Dictionary with counts and metrics
        """
        cursor = self.conn.cursor()

        stats = {}

        # Total signals
        cursor.execute("SELECT COUNT(*) FROM signals")
        stats['total_signals'] = cursor.fetchone()[0]

        # Signals by type
        cursor.execute("SELECT signal_type, COUNT(*) FROM signals GROUP BY signal_type")
        stats['signals_by_type'] = {row[0]: row[1] for row in cursor.fetchall()}

        # Agents (definitions)
        cursor.execute("SELECT COUNT(*) FROM agents")
        stats['unique_agents'] = cursor.fetchone()[0]

        # Agent executions
        cursor.execute("SELECT COUNT(*) FROM agents_run")
        stats['total_executions'] = cursor.fetchone()[0]

        # Reasoning traces
        cursor.execute("SELECT COUNT(*) FROM reasoning_traces")
        stats['total_traces'] = cursor.fetchone()[0]

        cursor.close()

        return stats

    def close(self):
        """Close database connection."""
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
