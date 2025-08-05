"""
Price history model for tracking product prices over time.
"""

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class PriceHistory(Base):
    """
    Model for storing historical price data for products.
    
    This model tracks price changes over time from various sources
    to enable trend analysis and margin calculations.
    """
    
    __tablename__ = "price_history"
    
    # Primary key
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    # Foreign key to product
    product_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("products.id"), 
        nullable=False,
        index=True
    )
    
    # Price information
    price = Column(DECIMAL(10, 2), nullable=False, index=True)
    condition = Column(String(20), default="near_mint", nullable=False)
    
    # Source information
    source = Column(String(50), nullable=False)  # 'tcgplayer', 'ebay', 'amazon', 'cardmarket'
    source_url = Column(String(500), nullable=True)
    
    # Market data
    seller_count = Column(Integer, nullable=True, index=True)
    available_quantity = Column(Integer, nullable=True)
    shipping_cost = Column(DECIMAL(10, 2), nullable=True)
    
    # Price type indicators
    price_type = Column(String(20), default="market", nullable=False)  # 'market', 'low', 'mid', 'high'
    is_foil = Column(String(10), default="false", nullable=False)
    
    # Data quality indicators
    confidence_level = Column(String(20), default="high", nullable=False)  # 'high', 'medium', 'low'
    data_source_quality = Column(DECIMAL(3, 2), default=1.0)  # 0.0 to 1.0
    
    # Timestamps
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="price_history")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_price_product_source_time', 'product_id', 'source', 'recorded_at'),
        Index('idx_price_source_recorded', 'source', 'recorded_at'),
        Index('idx_price_product_recorded', 'product_id', 'recorded_at'),
        Index('idx_price_recorded_desc', 'recorded_at'),
    )
    
    def __repr__(self):
        return f"<PriceHistory(product={self.product_id}, price=${self.price}, source='{self.source}')>"
    
    @property
    def price_float(self) -> float:
        """Get price as float."""
        return float(self.price)
    
    @property
    def is_recent(self) -> bool:
        """Check if price data is from the last 24 hours."""
        from datetime import datetime, timedelta
        return self.recorded_at > datetime.utcnow() - timedelta(days=1)