#!/usr/bin/env python3
"""
Activity Database - Index all API and blockchain interactions

This database tracks:
- CryptoPanic API requests/responses
- Walrus storage operations
- SUI blockchain transactions
- Agent processing activities
- Trigger creations and signal outputs
"""

import sqlite3
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path


class ActivityDB:
    """
    Local SQLite database for indexing all system activities.

    Provides a queryable audit trail of:
    - External API calls (CryptoPanic, etc.)
    - Blockchain operations (SUI testnet)
    - Decentralized storage (Walrus)
    - Agent processing (sentiment analysis, predictions, portfolio)
    """

    def __init__(self, db_path: str = "data/activity.db"):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path

        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Return rows as dicts

        self._init_schema()

    def _init_schema(self):
        """Initialize database schema."""
        cursor = self.conn.cursor()

        # API Calls Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            api_name TEXT NOT NULL,
            endpoint TEXT,
            method TEXT DEFAULT 'GET',
            request_params TEXT,
            response_status INTEGER,
            response_data TEXT,
            error_message TEXT,
            duration_ms REAL
        )
        """)

        # Walrus Storage Operations
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS walrus_operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            operation_type TEXT NOT NULL,
            blob_id TEXT,
            data_hash TEXT,
            size_bytes INTEGER,
            content_type TEXT,
            metadata TEXT,
            success INTEGER DEFAULT 1,
            error_message TEXT
        )
        """)

        # SUI Blockchain Transactions
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sui_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            transaction_digest TEXT,
            object_id TEXT,
            sender TEXT,
            gas_used INTEGER,
            status TEXT,
            metadata TEXT,
            error_message TEXT
        )
        """)

        # Trigger Processing
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS trigger_processing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            trigger_id TEXT NOT NULL,
            trigger_type TEXT NOT NULL,
            agent_id TEXT,
            input_data TEXT,
            output_data TEXT,
            confidence REAL,
            reasoning_blob_id TEXT,
            processing_time_ms REAL,
            success INTEGER DEFAULT 1,
            error_message TEXT
        )
        """)

        # News Articles Cache
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS news_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            article_id TEXT UNIQUE,
            source TEXT,
            title TEXT,
            url TEXT,
            published_at TEXT,
            tokens TEXT,
            sentiment TEXT,
            content_hash TEXT,
            raw_data TEXT
        )
        """)

        # Mocked Account Addresses (for indexing/organization)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mocked_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            account_address TEXT UNIQUE NOT NULL,
            project_name TEXT NOT NULL,
            description TEXT,
            is_active INTEGER DEFAULT 1,
            enabled INTEGER DEFAULT 1,
            metadata TEXT
        )
        """)

        # Create indexes for common queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_calls_timestamp ON api_calls(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_calls_api_name ON api_calls(api_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_walrus_blob_id ON walrus_operations(blob_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sui_tx_digest ON sui_transactions(transaction_digest)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trigger_id ON trigger_processing(trigger_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_article_id ON news_articles(article_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_article_url ON news_articles(url)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mocked_account_address ON mocked_accounts(account_address)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mocked_account_project ON mocked_accounts(project_name)")

        # Migration: Add 'enabled' column to existing mocked_accounts table if not exists
        try:
            cursor.execute("SELECT enabled FROM mocked_accounts LIMIT 1")
        except sqlite3.OperationalError:
            # Column doesn't exist, add it
            cursor.execute("ALTER TABLE mocked_accounts ADD COLUMN enabled INTEGER DEFAULT 1")
            print("[ActivityDB] Migration: Added 'enabled' column to mocked_accounts table")

        self.conn.commit()

    # ==================================================================================
    # API CALLS
    # ==================================================================================

    def log_api_call(
        self,
        api_name: str,
        endpoint: str,
        method: str = "GET",
        request_params: Optional[Dict] = None,
        response_status: Optional[int] = None,
        response_data: Optional[Any] = None,
        error_message: Optional[str] = None,
        duration_ms: Optional[float] = None
    ) -> int:
        """
        Log an API call.

        Args:
            api_name: Name of API (e.g., "CryptoPanic", "CoinGecko")
            endpoint: API endpoint
            method: HTTP method
            request_params: Request parameters
            response_status: HTTP status code
            response_data: Response data (will be JSON serialized)
            error_message: Error message if failed
            duration_ms: Request duration in milliseconds

        Returns:
            Record ID
        """
        cursor = self.conn.cursor()

        cursor.execute("""
        INSERT INTO api_calls (
            timestamp, api_name, endpoint, method,
            request_params, response_status, response_data,
            error_message, duration_ms
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.utcnow().isoformat(),
            api_name,
            endpoint,
            method,
            json.dumps(request_params) if request_params else None,
            response_status,
            json.dumps(response_data) if response_data else None,
            error_message,
            duration_ms
        ))

        self.conn.commit()
        return cursor.lastrowid

    def get_api_calls(
        self,
        api_name: Optional[str] = None,
        since: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Query API calls.

        Args:
            api_name: Filter by API name
            since: Filter by timestamp (ISO format)
            limit: Max records to return

        Returns:
            List of API call records
        """
        cursor = self.conn.cursor()

        query = "SELECT * FROM api_calls WHERE 1=1"
        params = []

        if api_name:
            query += " AND api_name = ?"
            params.append(api_name)

        if since:
            query += " AND timestamp >= ?"
            params.append(since)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    # ==================================================================================
    # WALRUS OPERATIONS
    # ==================================================================================

    def log_walrus_operation(
        self,
        operation_type: str,
        blob_id: Optional[str] = None,
        data_hash: Optional[str] = None,
        size_bytes: Optional[int] = None,
        content_type: str = "application/json",
        metadata: Optional[Dict] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> int:
        """
        Log a Walrus storage operation.

        Args:
            operation_type: "store" or "retrieve"
            blob_id: Walrus blob ID
            data_hash: SHA-256 hash of data
            size_bytes: Data size
            content_type: MIME type
            metadata: Additional metadata
            success: Whether operation succeeded
            error_message: Error message if failed

        Returns:
            Record ID
        """
        cursor = self.conn.cursor()

        cursor.execute("""
        INSERT INTO walrus_operations (
            timestamp, operation_type, blob_id, data_hash,
            size_bytes, content_type, metadata, success, error_message
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.utcnow().isoformat(),
            operation_type,
            blob_id,
            data_hash,
            size_bytes,
            content_type,
            json.dumps(metadata) if metadata else None,
            1 if success else 0,
            error_message
        ))

        self.conn.commit()
        return cursor.lastrowid

    def get_walrus_operations(
        self,
        operation_type: Optional[str] = None,
        blob_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Query Walrus operations."""
        cursor = self.conn.cursor()

        query = "SELECT * FROM walrus_operations WHERE 1=1"
        params = []

        if operation_type:
            query += " AND operation_type = ?"
            params.append(operation_type)

        if blob_id:
            query += " AND blob_id = ?"
            params.append(blob_id)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    # ==================================================================================
    # SUI TRANSACTIONS
    # ==================================================================================

    def log_sui_transaction(
        self,
        transaction_type: str,
        transaction_digest: Optional[str] = None,
        object_id: Optional[str] = None,
        sender: Optional[str] = None,
        gas_used: Optional[int] = None,
        status: str = "success",
        metadata: Optional[Dict] = None,
        error_message: Optional[str] = None
    ) -> int:
        """
        Log a SUI blockchain transaction.

        Args:
            transaction_type: Type of transaction (e.g., "publish_trigger", "publish_signal")
            transaction_digest: SUI transaction digest
            object_id: Created/modified object ID
            sender: Sender address
            gas_used: Gas consumed
            status: Transaction status
            metadata: Additional metadata
            error_message: Error message if failed

        Returns:
            Record ID
        """
        cursor = self.conn.cursor()

        cursor.execute("""
        INSERT INTO sui_transactions (
            timestamp, transaction_type, transaction_digest,
            object_id, sender, gas_used, status, metadata, error_message
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.utcnow().isoformat(),
            transaction_type,
            transaction_digest,
            object_id,
            sender,
            gas_used,
            status,
            json.dumps(metadata) if metadata else None,
            error_message
        ))

        self.conn.commit()
        return cursor.lastrowid

    def get_sui_transactions(
        self,
        transaction_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Query SUI transactions."""
        cursor = self.conn.cursor()

        query = "SELECT * FROM sui_transactions WHERE 1=1"
        params = []

        if transaction_type:
            query += " AND transaction_type = ?"
            params.append(transaction_type)

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    # ==================================================================================
    # TRIGGER PROCESSING
    # ==================================================================================

    def log_trigger_processing(
        self,
        trigger_id: str,
        trigger_type: str,
        agent_id: Optional[str] = None,
        input_data: Optional[Dict] = None,
        output_data: Optional[Dict] = None,
        confidence: Optional[float] = None,
        reasoning_blob_id: Optional[str] = None,
        processing_time_ms: Optional[float] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> int:
        """
        Log agent trigger processing.

        Args:
            trigger_id: Trigger ID
            trigger_type: Trigger type (e.g., "news", "signal")
            agent_id: Agent that processed it
            input_data: Input data
            output_data: Output data
            confidence: Processing confidence
            reasoning_blob_id: Walrus blob ID for reasoning trace
            processing_time_ms: Processing time
            success: Whether processing succeeded
            error_message: Error message if failed

        Returns:
            Record ID
        """
        cursor = self.conn.cursor()

        cursor.execute("""
        INSERT INTO trigger_processing (
            timestamp, trigger_id, trigger_type, agent_id,
            input_data, output_data, confidence, reasoning_blob_id,
            processing_time_ms, success, error_message
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.utcnow().isoformat(),
            trigger_id,
            trigger_type,
            agent_id,
            json.dumps(input_data) if input_data else None,
            json.dumps(output_data) if output_data else None,
            confidence,
            reasoning_blob_id,
            processing_time_ms,
            1 if success else 0,
            error_message
        ))

        self.conn.commit()
        return cursor.lastrowid

    # ==================================================================================
    # NEWS ARTICLES
    # ==================================================================================

    def store_news_article(
        self,
        article_id: str,
        source: str,
        title: str,
        url: str,
        published_at: str,
        tokens: List[str],
        raw_data: Dict
    ) -> int:
        """
        Store a news article.

        Args:
            article_id: Unique article ID
            source: News source
            title: Article title
            url: Article URL
            published_at: Publication timestamp
            tokens: Associated tokens (BTC, SUI, etc.)
            raw_data: Full article data

        Returns:
            Record ID (or existing ID if duplicate)
        """
        cursor = self.conn.cursor()

        try:
            cursor.execute("""
            INSERT INTO news_articles (
                timestamp, article_id, source, title, url,
                published_at, tokens, raw_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.utcnow().isoformat(),
                article_id,
                source,
                title,
                url,
                published_at,
                json.dumps(tokens),
                json.dumps(raw_data)
            ))

            self.conn.commit()
            return cursor.lastrowid

        except sqlite3.IntegrityError:
            # Article already exists
            cursor.execute("SELECT id FROM news_articles WHERE article_id = ?", (article_id,))
            return cursor.fetchone()[0]

    def get_news_articles(
        self,
        tokens: Optional[List[str]] = None,
        source: Optional[str] = None,
        since: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Query news articles.

        Args:
            tokens: Filter by tokens (e.g., ["BTC", "SUI"])
            source: Filter by source
            since: Filter by timestamp
            limit: Max records

        Returns:
            List of news articles
        """
        cursor = self.conn.cursor()

        query = "SELECT * FROM news_articles WHERE 1=1"
        params = []

        if source:
            query += " AND source = ?"
            params.append(source)

        if since:
            query += " AND timestamp >= ?"
            params.append(since)

        # Token filtering (simple LIKE match)
        if tokens:
            token_conditions = " OR ".join(["tokens LIKE ?" for _ in tokens])
            query += f" AND ({token_conditions})"
            params.extend([f"%{token}%" for token in tokens])

        query += " ORDER BY published_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_article_by_url(self, url: str) -> Optional[Dict]:
        """
        Check if an article with this URL already exists.

        Args:
            url: Article URL

        Returns:
            Article record if exists, None otherwise
        """
        cursor = self.conn.cursor()

        cursor.execute("SELECT * FROM news_articles WHERE url = ?", (url,))
        row = cursor.fetchone()

        return dict(row) if row else None

    # ==================================================================================
    # MOCKED ACCOUNTS
    # ==================================================================================

    def register_mocked_account(
        self,
        account_address: str,
        project_name: str,
        description: Optional[str] = None,
        enabled: bool = True,
        metadata: Optional[Dict] = None
    ) -> int:
        """
        Register a new mocked account address for indexing/organization.

        Args:
            account_address: Account address (e.g., 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1)
            project_name: Project identifier (e.g., "ProjectA", "BTC-News-Pipeline")
            description: Optional description
            enabled: Whether account is enabled in visualization (default True)
            metadata: Optional metadata dict

        Returns:
            Record ID (or existing ID if duplicate)
        """
        cursor = self.conn.cursor()

        try:
            cursor.execute("""
            INSERT INTO mocked_accounts (
                created_at, account_address, project_name,
                description, is_active, enabled, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.utcnow().isoformat(),
                account_address,
                project_name,
                description,
                1,  # is_active = True
                1 if enabled else 0,
                json.dumps(metadata) if metadata else None
            ))

            self.conn.commit()
            return cursor.lastrowid

        except sqlite3.IntegrityError:
            # Account already exists
            cursor.execute("SELECT id FROM mocked_accounts WHERE account_address = ?", (account_address,))
            return cursor.fetchone()[0]

    def get_mocked_account(self, account_address: str) -> Optional[Dict]:
        """
        Get mocked account details by address.

        Args:
            account_address: Account address to look up

        Returns:
            Account record if exists, None otherwise
        """
        cursor = self.conn.cursor()

        cursor.execute("SELECT * FROM mocked_accounts WHERE account_address = ?", (account_address,))
        row = cursor.fetchone()

        return dict(row) if row else None

    def list_mocked_accounts(
        self,
        project_name: Optional[str] = None,
        active_only: bool = True,
        enabled_only: bool = True
    ) -> List[Dict]:
        """
        List all mocked accounts, optionally filtered.

        Args:
            project_name: Filter by project name
            active_only: Only return active accounts (default True)
            enabled_only: Only return enabled accounts (default True)

        Returns:
            List of account records
        """
        cursor = self.conn.cursor()

        query = "SELECT * FROM mocked_accounts WHERE 1=1"
        params = []

        if active_only:
            query += " AND is_active = 1"

        if enabled_only:
            query += " AND enabled = 1"

        if project_name:
            query += " AND project_name = ?"
            params.append(project_name)

        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def update_mocked_account(
        self,
        account_address: str,
        project_name: Optional[str] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None,
        enabled: Optional[bool] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Update mocked account details.

        Args:
            account_address: Account address to update
            project_name: New project name (optional)
            description: New description (optional)
            is_active: New active status (optional)
            enabled: New enabled status for visualization (optional)
            metadata: New metadata (optional)

        Returns:
            True if account was updated, False if not found
        """
        cursor = self.conn.cursor()

        # Build dynamic UPDATE query
        updates = []
        params = []

        if project_name is not None:
            updates.append("project_name = ?")
            params.append(project_name)

        if description is not None:
            updates.append("description = ?")
            params.append(description)

        if is_active is not None:
            updates.append("is_active = ?")
            params.append(1 if is_active else 0)

        if enabled is not None:
            updates.append("enabled = ?")
            params.append(1 if enabled else 0)

        if metadata is not None:
            updates.append("metadata = ?")
            params.append(json.dumps(metadata))

        if not updates:
            return False  # No updates provided

        params.append(account_address)
        query = f"UPDATE mocked_accounts SET {', '.join(updates)} WHERE account_address = ?"

        cursor.execute(query, params)
        self.conn.commit()

        return cursor.rowcount > 0

    def deactivate_mocked_account(self, account_address: str) -> bool:
        """
        Mark mocked account as inactive.

        Args:
            account_address: Account address to deactivate

        Returns:
            True if account was deactivated, False if not found
        """
        return self.update_mocked_account(account_address, is_active=False)

    # ==================================================================================
    # UTILITY
    # ==================================================================================

    def get_stats(self) -> Dict[str, int]:
        """Get database statistics."""
        cursor = self.conn.cursor()

        stats = {}

        for table in ["api_calls", "walrus_operations", "sui_transactions",
                      "trigger_processing", "news_articles", "mocked_accounts"]:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table] = cursor.fetchone()[0]

        return stats

    def close(self):
        """Close database connection."""
        self.conn.close()
