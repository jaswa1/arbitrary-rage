"""
Product model for storing information about sealed products and singles.
"""

from sqlalchemy import Column, String, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Product(Base):
    """
    Product model for both sealed products and individual cards/singles.
    
    This model stores information about products that can be tracked for pricing.
    Products can be either 'sealed' (booster boxes, commander decks, etc.) or 
    'single' (individual cards).
    """
    
    __tablename__ = "products"
    
    # Primary key
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        index=True
    )
    
    # Product identification
    name = Column(String(255), nullable=False, index=True)
    set_name = Column(String(100), nullable=True, index=True)
    product_type = Column(String(50), nullable=False, index=True)  # 'sealed' or 'single'
    category = Column(String(50), nullable=False, index=True)      # 'mtg', 'pokemon', 'yugioh'
    
    # External references
    tcg_product_id = Column(String(100), unique=True, nullable=True)
    ebay_product_id = Column(String(100), nullable=True)
    amazon_asin = Column(String(20), nullable=True)
    
    # Additional metadata
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    
    # Tracking flags
    is_active = Column(String(10), default="true", nullable=False)  # Track pricing for this product
    is_featured = Column(String(10), default="false", nullable=False)  # Featured product
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    price_history = relationship("PriceHistory", back_populates="product")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_product_type_category', 'product_type', 'category'),
        Index('idx_product_active_type', 'is_active', 'product_type'),
        Index('idx_product_set_category', 'set_name', 'category'),
    )
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', type='{self.product_type}')>"
    
    @property
    def is_sealed(self) -> bool:
        """Check if this product is a sealed product."""
        return self.product_type == "sealed"
    
    @property
    def is_single(self) -> bool:
        """Check if this product is a single card."""
        return self.product_type == "single"