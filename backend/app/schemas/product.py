"""
Pydantic schemas for Product API models.
"""

from pydantic import BaseModel, UUID4, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class ProductBase(BaseModel):
    """Base product schema with common fields."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    set_name: Optional[str] = Field(None, max_length=100, description="Set or collection name")
    product_type: str = Field(..., description="Product type: 'sealed' or 'single'")
    category: str = Field(..., description="Product category: 'mtg', 'pokemon', 'yugioh'")
    tcg_product_id: Optional[str] = Field(None, max_length=100, description="TCGPlayer product ID")
    ebay_product_id: Optional[str] = Field(None, max_length=100, description="eBay product ID")
    amazon_asin: Optional[str] = Field(None, max_length=20, description="Amazon ASIN")
    description: Optional[str] = Field(None, description="Product description")
    image_url: Optional[str] = Field(None, max_length=500, description="Product image URL")
    is_active: bool = Field(True, description="Whether to track pricing for this product")
    is_featured: bool = Field(False, description="Whether this is a featured product")
    
    @validator('product_type')
    def validate_product_type(cls, v):
        if v not in ['sealed', 'single']:
            raise ValueError('product_type must be either "sealed" or "single"')
        return v
    
    @validator('category')
    def validate_category(cls, v):
        valid_categories = ['mtg', 'pokemon', 'yugioh', 'lego', 'sports']
        if v not in valid_categories:
            raise ValueError(f'category must be one of: {", ".join(valid_categories)}')
        return v


class ProductCreate(ProductBase):
    """Schema for creating a new product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating an existing product."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    set_name: Optional[str] = Field(None, max_length=100)
    tcg_product_id: Optional[str] = Field(None, max_length=100)
    ebay_product_id: Optional[str] = Field(None, max_length=100)
    amazon_asin: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


class Product(ProductBase):
    """Schema for product responses."""
    
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProductInDB(Product):
    """Schema for product with additional database fields."""
    pass


class ProductWithPricing(Product):
    """Product schema with current pricing information."""
    
    current_price: Optional[Decimal] = Field(None, description="Current market price")
    last_price_update: Optional[datetime] = Field(None, description="Last price update timestamp")
    seller_count: Optional[int] = Field(None, description="Number of sellers")
    price_trend: Optional[str] = Field(None, description="Price trend: 'up', 'down', 'stable'")


class ProductSearch(BaseModel):
    """Schema for product search parameters."""
    
    query: Optional[str] = Field(None, description="Search query")
    category: Optional[str] = Field(None, description="Filter by category")
    product_type: Optional[str] = Field(None, description="Filter by product type")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    is_featured: Optional[bool] = Field(None, description="Filter by featured status")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(50, ge=1, le=1000, description="Number of records to return")


class ProductBulkCreate(BaseModel):
    """Schema for bulk product creation."""
    
    products: List[ProductCreate] = Field(..., min_items=1, max_items=100, description="List of products to create")