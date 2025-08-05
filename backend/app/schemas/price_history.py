"""
Pydantic schemas for PriceHistory API models.
"""

from pydantic import BaseModel, UUID4, Field, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal


class PriceHistoryBase(BaseModel):
    """Base price history schema."""
    
    product_id: UUID4 = Field(..., description="ID of the product")
    price: Decimal = Field(..., gt=0, description="Product price")
    condition: str = Field("near_mint", description="Card condition")
    source: str = Field(..., description="Price source: tcgplayer, ebay, amazon, etc.")
    source_url: Optional[str] = Field(None, max_length=500, description="URL where price was found")
    seller_count: Optional[int] = Field(None, ge=0, description="Number of sellers")
    available_quantity: Optional[int] = Field(None, ge=0, description="Available quantity")
    shipping_cost: Optional[Decimal] = Field(None, ge=0, description="Shipping cost")
    price_type: str = Field("market", description="Price type: market, low, mid, high")
    is_foil: bool = Field(False, description="Whether this is a foil version")
    confidence_level: str = Field("high", description="Data confidence level")
    data_source_quality: Decimal = Field(1.0, ge=0, le=1, description="Data source quality score")
    
    @validator('condition')
    def validate_condition(cls, v):
        valid_conditions = ['mint', 'near_mint', 'lightly_played', 'moderately_played', 'heavily_played', 'damaged']
        if v not in valid_conditions:
            raise ValueError(f'condition must be one of: {", ".join(valid_conditions)}')
        return v
    
    @validator('source')
    def validate_source(cls, v):
        valid_sources = ['tcgplayer', 'ebay', 'amazon', 'cardmarket', 'coolstuffinc', 'channelfireball', 'manual']
        if v not in valid_sources:
            raise ValueError(f'source must be one of: {", ".join(valid_sources)}')
        return v
    
    @validator('price_type')
    def validate_price_type(cls, v):
        valid_types = ['market', 'low', 'mid', 'high', 'buylist']
        if v not in valid_types:
            raise ValueError(f'price_type must be one of: {", ".join(valid_types)}')
        return v
    
    @validator('confidence_level')
    def validate_confidence_level(cls, v):
        if v not in ['low', 'medium', 'high']:
            raise ValueError('confidence_level must be one of: low, medium, high')
        return v


class PriceHistoryCreate(PriceHistoryBase):
    """Schema for creating a new price history entry."""
    
    recorded_at: Optional[datetime] = Field(None, description="When the price was recorded")


class PriceHistoryUpdate(BaseModel):
    """Schema for updating price history (limited fields)."""
    
    confidence_level: Optional[str] = Field(None, description="Update confidence level")
    data_source_quality: Optional[Decimal] = Field(None, ge=0, le=1, description="Update quality score")


class PriceHistory(PriceHistoryBase):
    """Schema for price history responses."""
    
    id: UUID4
    recorded_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class PriceHistoryInDB(PriceHistory):
    """Schema for price history with additional database fields."""
    pass


class PriceTrend(BaseModel):
    """Schema for price trend analysis."""
    
    product_id: UUID4
    current_price: Decimal
    previous_price: Optional[Decimal] = None
    price_change: Optional[Decimal] = None
    price_change_percentage: Optional[Decimal] = None
    trend_direction: str = Field(..., description="Trend direction: up, down, stable")
    volatility: Decimal = Field(..., description="Price volatility score")
    last_updated: datetime
    
    @validator('trend_direction')
    def validate_trend_direction(cls, v):
        if v not in ['up', 'down', 'stable']:
            raise ValueError('trend_direction must be one of: up, down, stable')
        return v


class PriceComparisonSource(BaseModel):
    """Schema for price comparison across sources."""
    
    source: str
    price: Decimal
    seller_count: Optional[int] = None
    last_updated: datetime
    confidence_level: str


class PriceComparison(BaseModel):
    """Schema for comparing prices across multiple sources."""
    
    product_id: UUID4
    product_name: str
    sources: list[PriceComparisonSource]
    lowest_price: Decimal
    highest_price: Decimal
    average_price: Decimal
    price_spread: Decimal
    recommended_source: str
    last_updated: datetime


class PriceAlert(BaseModel):
    """Schema for price alert configuration."""
    
    product_id: UUID4
    target_price: Decimal = Field(..., gt=0, description="Alert when price reaches this level")
    alert_type: str = Field(..., description="Alert type: below, above, change")
    percentage_change: Optional[Decimal] = Field(None, description="Alert on percentage change")
    is_active: bool = Field(True, description="Whether alert is active")
    
    @validator('alert_type')
    def validate_alert_type(cls, v):
        if v not in ['below', 'above', 'change']:
            raise ValueError('alert_type must be one of: below, above, change')
        return v