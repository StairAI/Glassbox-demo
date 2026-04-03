"""
Data Pipelines (NOT Agents)

This module contains data pipelines that perform pure ETL operations:
- Extract: Fetch data from external APIs
- Transform: Convert to standardized format
- Load: Publish to SUI blockchain

IMPORTANT: Pipelines are NOT agents. They do not use LLMs or perform reasoning.
They simply move data from off-chain sources to on-chain storage.
"""

from .news_pipeline import NewsPipeline
from .price_pipeline import PricePipeline

__all__ = ["NewsPipeline", "PricePipeline"]
