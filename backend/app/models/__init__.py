"""
Database models for the arbitrage detection system.
"""

from app.core.database import Base
from .product import Product
from .arbitrage_opportunity import ArbitrageOpportunity, ProductSingle
from .price_history import PriceHistory
from .user_alert import UserAlert
from .system_config import SystemConfig

__all__ = [
    "Base",
    "Product",
    "ArbitrageOpportunity",
    "ProductSingle", 
    "PriceHistory",
    "UserAlert",
    "SystemConfig"
]