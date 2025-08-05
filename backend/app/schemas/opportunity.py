"""
Pydantic schemas for ArbitrageOpportunity API models.
"""

from pydantic import BaseModel, UUID4, Field, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal

from .product import Product


class ArbitrageOpportunityBase(BaseModel):
    """Base arbitrage opportunity schema."""
    
    sealed_product_id: UUID4 = Field(..., description="ID of the sealed product")
    sealed_price: Decimal = Field(..., gt=0, description="Price of the sealed product")
    singles_value: Decimal = Field(..., gt=0, description="Total value of component singles")
    margin_percentage: Decimal = Field(..., description="Profit margin percentage")
    confidence_score: Decimal = Field(..., ge=0, le=1, description="Confidence score (0.0 to 1.0)")
    risk_level: str = Field(..., description="Risk level: 'low', 'medium', 'high'")
    seller_count: Optional[int] = Field(None, ge=0, description="Number of sellers")
    competition_level: Optional[str] = Field("unknown", description="Competition level")
    
    @validator('risk_level')
    def validate_risk_level(cls, v):
        if v not in ['low', 'medium', 'high']:
            raise ValueError('risk_level must be one of: low, medium, high')
        return v
    
    @validator('competition_level')
    def validate_competition_level(cls, v):
        if v not in ['low', 'medium', 'high', 'unknown']:
            raise ValueError('competition_level must be one of: low, medium, high, unknown')
        return v


class ArbitrageOpportunityCreate(ArbitrageOpportunityBase):
    """Schema for creating a new arbitrage opportunity."""
    
    expires_at: Optional[datetime] = Field(None, description="When this opportunity expires")


class ArbitrageOpportunityUpdate(BaseModel):
    """Schema for updating an arbitrage opportunity."""
    
    status: Optional[str] = Field(None, description="Opportunity status")
    execution_quantity: Optional[int] = Field(None, ge=0, description="Quantity executed")
    execution_notes: Optional[str] = Field(None, max_length=500, description="Execution notes")
    
    @validator('status')
    def validate_status(cls, v):
        if v and v not in ['active', 'expired', 'executed', 'cancelled']:
            raise ValueError('status must be one of: active, expired, executed, cancelled')
        return v


class ArbitrageOpportunity(ArbitrageOpportunityBase):
    """Schema for arbitrage opportunity responses."""
    
    id: UUID4
    status: str
    execution_quantity: int = 0
    execution_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    
    # Computed fields
    potential_profit: Optional[Decimal] = Field(None, description="Potential profit in dollars")
    is_active: bool = Field(description="Whether opportunity is still active")
    is_high_confidence: bool = Field(description="Whether confidence score >= 0.8")
    
    class Config:
        from_attributes = True


class ArbitrageOpportunityInDB(ArbitrageOpportunity):
    """Schema for opportunity with additional database fields."""
    pass


class ArbitrageOpportunityWithProduct(ArbitrageOpportunity):
    """Opportunity schema with embedded product information."""
    
    sealed_product: Product = Field(..., description="Sealed product details")


class OpportunityFilters(BaseModel):
    """Schema for filtering arbitrage opportunities."""
    
    min_margin: Optional[Decimal] = Field(None, ge=0, description="Minimum margin percentage")
    max_margin: Optional[Decimal] = Field(None, ge=0, description="Maximum margin percentage")
    min_confidence: Optional[Decimal] = Field(None, ge=0, le=1, description="Minimum confidence score")
    max_risk: Optional[str] = Field(None, description="Maximum risk level")
    status: str = Field("active", description="Opportunity status filter")
    category: Optional[str] = Field(None, description="Product category filter")
    created_after: Optional[datetime] = Field(None, description="Created after this date")
    created_before: Optional[datetime] = Field(None, description="Created before this date")
    expires_after: Optional[datetime] = Field(None, description="Expires after this date")
    expires_before: Optional[datetime] = Field(None, description="Expires before this date")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(50, ge=1, le=200, description="Number of records to return")
    sort_by: str = Field("margin_percentage", description="Sort field")
    sort_order: str = Field("desc", description="Sort order: 'asc' or 'desc'")
    
    @validator('max_risk')
    def validate_max_risk(cls, v):
        if v and v not in ['low', 'medium', 'high']:
            raise ValueError('max_risk must be one of: low, medium, high')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['active', 'expired', 'executed', 'cancelled', 'all']
        if v not in valid_statuses:
            raise ValueError(f'status must be one of: {", ".join(valid_statuses)}')
        return v
    
    @validator('sort_by')
    def validate_sort_by(cls, v):
        valid_fields = ['margin_percentage', 'confidence_score', 'created_at', 'expires_at', 'sealed_price']
        if v not in valid_fields:
            raise ValueError(f'sort_by must be one of: {", ".join(valid_fields)}')
        return v
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v not in ['asc', 'desc']:
            raise ValueError('sort_order must be either "asc" or "desc"')
        return v


class OpportunityExecution(BaseModel):
    """Schema for executing an opportunity."""
    
    quantity: int = Field(..., ge=1, le=100, description="Quantity to execute")
    notes: Optional[str] = Field(None, max_length=500, description="Execution notes")


class OpportunityStats(BaseModel):
    """Schema for opportunity statistics."""
    
    total_opportunities: int = Field(..., description="Total number of opportunities")
    active_opportunities: int = Field(..., description="Number of active opportunities")
    executed_opportunities: int = Field(..., description="Number of executed opportunities")
    expired_opportunities: int = Field(..., description="Number of expired opportunities")
    average_margin: Decimal = Field(..., description="Average margin percentage")
    average_confidence: Decimal = Field(..., description="Average confidence score")
    total_potential_profit: Decimal = Field(..., description="Total potential profit")
    high_confidence_count: int = Field(..., description="Number of high confidence opportunities")
    low_risk_count: int = Field(..., description="Number of low risk opportunities")