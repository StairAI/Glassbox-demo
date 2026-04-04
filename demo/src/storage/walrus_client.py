#!/usr/bin/env python3
"""
Walrus Client: Interface for Walrus decentralized storage

Walrus is a decentralized data availability layer built on SUI.
It provides cost-efficient storage for large data that doesn't fit on-chain.

Documentation: https://docs.walrus.site/
"""

import hashlib
import logging
from typing import Optional
import json

logger = logging.getLogger(__name__)


class WalrusError(Exception):
    """Base exception for Walrus errors."""
    pass


class WalrusClient:
    """
    Client for Walrus decentralized storage.

    Walrus is used for storing large data (like news articles) that would be
    too expensive to store directly on SUI blockchain.

    Architecture:
        - Full data → Walrus (cheap, immutable)
        - Metadata + blob_id → SUI (expensive but queryable)

    Example:
        client = WalrusClient(simulated=True)

        # Store data
        blob_id = client.store(b"large data here")

        # Fetch data
        data = client.fetch(blob_id)
    """

    def __init__(
        self,
        publisher_url: Optional[str] = None,
        aggregator_url: Optional[str] = None,
        simulated: bool = True,
        storage_dir: Optional[str] = None
    ):
        """
        Initialize Walrus client.

        Args:
            publisher_url: Walrus publisher endpoint (for storing)
            aggregator_url: Walrus aggregator endpoint (for fetching)
            simulated: If True, simulate Walrus operations locally
            storage_dir: Directory for simulated blob storage (default: data/walrus_blobs)
        """
        self.publisher_url = publisher_url or "https://publisher.walrus-testnet.walrus.space"
        self.aggregator_url = aggregator_url or "https://aggregator.walrus-testnet.walrus.space"
        self.simulated = simulated

        # For simulated mode, use file-based storage
        if simulated:
            import os
            self.storage_dir = storage_dir or "data/walrus_blobs"
            os.makedirs(self.storage_dir, exist_ok=True)
            logger.info(f"WalrusClient initialized in SIMULATED mode (storage: {self.storage_dir})")
        else:
            self.storage_dir = None
            logger.info(f"WalrusClient initialized: publisher={self.publisher_url}")

    def store(self, data: bytes) -> str:
        """
        Store data on Walrus.

        Args:
            data: Raw bytes to store

        Returns:
            blob_id: Walrus blob identifier (hash-based)

        Raises:
            WalrusError: If storage fails
        """
        # Compute blob_id (deterministic hash)
        blob_id = self._compute_blob_id(data)

        if self.simulated:
            return self._simulate_store(data, blob_id)
        else:
            return self._real_store(data, blob_id)

    def fetch(self, blob_id: str) -> bytes:
        """
        Fetch data from Walrus.

        Args:
            blob_id: Walrus blob identifier

        Returns:
            data: Raw bytes

        Raises:
            WalrusError: If blob not found or fetch fails
        """
        if self.simulated:
            return self._simulate_fetch(blob_id)
        else:
            return self._real_fetch(blob_id)

    def exists(self, blob_id: str) -> bool:
        """
        Check if blob exists on Walrus.

        Args:
            blob_id: Walrus blob identifier

        Returns:
            True if blob exists, False otherwise
        """
        if self.simulated:
            import os
            blob_path = os.path.join(self.storage_dir, f"{blob_id}.blob")
            return os.path.exists(blob_path)
        else:
            try:
                self._real_fetch(blob_id)
                return True
            except WalrusError:
                return False

    def get_blob_info(self, blob_id: str) -> dict:
        """
        Get information about a blob.

        Returns:
            Dict with blob metadata (size, timestamp, etc.)
        """
        if self.simulated:
            import os
            blob_path = os.path.join(self.storage_dir, f"{blob_id}.blob")

            if not os.path.exists(blob_path):
                raise WalrusError(f"Blob not found: {blob_id}")

            size = os.path.getsize(blob_path)
            return {
                "blob_id": blob_id,
                "size_bytes": size,
                "storage": "simulated",
                "path": blob_path
            }
        else:
            # Real implementation would query Walrus
            raise NotImplementedError("Real Walrus info query not implemented")

    # === Private Methods ===

    def _compute_blob_id(self, data: bytes) -> str:
        """
        Compute deterministic blob ID from data.

        Walrus uses content-addressable storage, so blob_id is derived from
        the data itself (similar to IPFS).
        """
        return hashlib.sha256(data).hexdigest()

    def _simulate_store(self, data: bytes, blob_id: str) -> str:
        """Simulate storing data locally to file."""
        import os

        # Write blob to file
        blob_path = os.path.join(self.storage_dir, f"{blob_id}.blob")
        with open(blob_path, 'wb') as f:
            f.write(data)

        logger.info(
            f"[Walrus Simulated] Stored {len(data)} bytes\n"
            f"  Blob ID: {blob_id[:16]}...\n"
            f"  Size: {len(data):,} bytes\n"
            f"  Path: {blob_path}"
        )

        return blob_id

    def _simulate_fetch(self, blob_id: str) -> bytes:
        """Simulate fetching data from local file storage."""
        import os

        blob_path = os.path.join(self.storage_dir, f"{blob_id}.blob")

        if not os.path.exists(blob_path):
            raise WalrusError(f"Blob not found in simulated storage: {blob_id}")

        with open(blob_path, 'rb') as f:
            data = f.read()

        logger.info(
            f"[Walrus Simulated] Fetched {len(data)} bytes\n"
            f"  Blob ID: {blob_id[:16]}...\n"
            f"  Path: {blob_path}"
        )

        return data

    def _real_store(self, data: bytes, blob_id: str) -> str:
        """
        Store data on real Walrus network with retry logic.

        This uses the Walrus publisher API:
        PUT /v1/blobs
        Body: raw bytes
        Returns: {newlyCreated: {blobObject: {blobId: ...}}}

        Implements exponential backoff for retries on timeout/network errors.
        """
        import requests
        import time

        max_retries = 3
        base_timeout = 30

        for attempt in range(max_retries):
            try:
                # Increase timeout with each retry
                timeout = base_timeout * (attempt + 1)

                if attempt > 0:
                    # Exponential backoff: wait 2^attempt seconds before retry
                    wait_time = 2 ** attempt
                    logger.info(f"[Walrus] Retry {attempt}/{max_retries} after {wait_time}s wait (timeout={timeout}s)")
                    time.sleep(wait_time)

                response = requests.put(
                    f"{self.publisher_url}/v1/blobs",
                    data=data,
                    headers={"Content-Type": "application/octet-stream"},
                    timeout=timeout
                )

                if response.status_code != 200:
                    raise WalrusError(
                        f"Walrus storage failed: {response.status_code} {response.text}"
                    )

                result = response.json()
                certified_blob_id = result.get("newlyCreated", {}).get("blobObject", {}).get("blobId")

                if not certified_blob_id:
                    # Blob might already exist
                    certified_blob_id = result.get("alreadyCertified", {}).get("blobId")

                if not certified_blob_id:
                    raise WalrusError(f"Unexpected Walrus response: {result}")

                if attempt > 0:
                    logger.info(f"[Walrus] ✓ Succeeded on retry {attempt}")
                logger.info(f"[Walrus] Stored {len(data)} bytes, blob_id={certified_blob_id}")

                return certified_blob_id

            except requests.Timeout as e:
                if attempt == max_retries - 1:
                    # Final attempt failed
                    raise WalrusError(
                        f"Walrus storage timeout after {max_retries} attempts: {e}"
                    ) from e
                else:
                    logger.warning(f"[Walrus] Timeout on attempt {attempt + 1}/{max_retries}: {e}")
                    continue

            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    # Final attempt failed
                    raise WalrusError(
                        f"Walrus storage request failed after {max_retries} attempts: {e}"
                    ) from e
                else:
                    logger.warning(f"[Walrus] Request error on attempt {attempt + 1}/{max_retries}: {e}")
                    continue

    def _real_fetch(self, blob_id: str) -> bytes:
        """
        Fetch data from real Walrus network with retry logic.

        This uses the Walrus aggregator API:
        GET /v1/blobs/{blob_id}
        Returns: raw bytes

        Implements exponential backoff for retries on timeout/network errors.
        """
        import requests
        import time

        max_retries = 3
        base_timeout = 30

        for attempt in range(max_retries):
            try:
                # Increase timeout with each retry
                timeout = base_timeout * (attempt + 1)

                if attempt > 0:
                    # Exponential backoff: wait 2^attempt seconds before retry
                    wait_time = 2 ** attempt
                    logger.info(f"[Walrus] Fetch retry {attempt}/{max_retries} after {wait_time}s wait (timeout={timeout}s)")
                    time.sleep(wait_time)

                response = requests.get(
                    f"{self.aggregator_url}/v1/blobs/{blob_id}",
                    timeout=timeout
                )

                if response.status_code == 404:
                    raise WalrusError(f"Blob not found: {blob_id}")

                if response.status_code != 200:
                    raise WalrusError(
                        f"Walrus fetch failed: {response.status_code} {response.text}"
                    )

                if attempt > 0:
                    logger.info(f"[Walrus] ✓ Fetch succeeded on retry {attempt}")
                logger.info(f"[Walrus] Fetched {len(response.content)} bytes")

                return response.content

            except requests.Timeout as e:
                if attempt == max_retries - 1:
                    # Final attempt failed
                    raise WalrusError(
                        f"Walrus fetch timeout after {max_retries} attempts: {e}"
                    ) from e
                else:
                    logger.warning(f"[Walrus] Fetch timeout on attempt {attempt + 1}/{max_retries}: {e}")
                    continue

            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    # Final attempt failed
                    raise WalrusError(
                        f"Walrus fetch request failed after {max_retries} attempts: {e}"
                    ) from e
                else:
                    logger.warning(f"[Walrus] Fetch request error on attempt {attempt + 1}/{max_retries}: {e}")
                    continue


class WalrusHelper:
    """
    Helper utilities for working with Walrus.
    """

    @staticmethod
    def store_json(client: WalrusClient, data: dict) -> str:
        """
        Store JSON data on Walrus.

        Args:
            client: WalrusClient instance
            data: Python dict to store

        Returns:
            blob_id: Walrus blob identifier
        """
        json_str = json.dumps(data, sort_keys=True, indent=2)
        json_bytes = json_str.encode('utf-8')
        return client.store(json_bytes)

    @staticmethod
    def fetch_json(client: WalrusClient, blob_id: str) -> dict:
        """
        Fetch JSON data from Walrus.

        Args:
            client: WalrusClient instance
            blob_id: Walrus blob identifier

        Returns:
            data: Python dict
        """
        json_bytes = client.fetch(blob_id)
        json_str = json_bytes.decode('utf-8')
        return json.loads(json_str)

    @staticmethod
    def compute_blob_id(data: bytes) -> str:
        """Compute blob ID without storing."""
        return hashlib.sha256(data).hexdigest()
