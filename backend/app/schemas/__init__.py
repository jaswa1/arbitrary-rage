"""
Pydantic schemas for API request/response models.
"""

from .product import Product, ProductCreate, ProductUpdate, ProductInDB
from .opportunity import (
    ArbitrageOpportunity, 
    ArbitrageOpportunityCreate, 
    OpportunityFilters,
    ArbitrageOpportunityInDB
)
from .price_history import PriceHistory, PriceHistoryCreate

__all__ = [
    "Product",
    "ProductCreate", 
    "ProductUpdate",
    "ProductInDB",
    "ArbitrageOpportunity",
    "ArbitrageOpportunityCreate",
    "OpportunityFilters", 
    "ArbitrageOpportunityInDB",
    "PriceHistory",
    "PriceHistoryCreate"
]