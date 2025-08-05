"""
User alert model for managing notifications and alerts.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class UserAlert(Base):
    """
    Model for managing user alerts and notifications.
    
    This model stores alert configurations and tracks when alerts
    have been sent to prevent spam.
    """
    
    __tablename__ = "user_alerts"
    
    # Primary key
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    # User identification (for future user system)
    user_id = Column(UUID(as_uuid=True), nullable=True)  # Future: ForeignKey to users table
    user_email = Column(String(255), nullable=True)
    
    # Alert target
    opportunity_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("arbitrage_opportunities.id"), 
        nullable=True
    )
    product_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("products.id"), 
        nullable=True
    )
    
    # Alert configuration
    alert_type = Column(String(50), nullable=False)  # 'email', 'slack', 'webhook', 'sms'
    alert_channel = Column(String(255), nullable=False)  # email address, webhook URL, etc.
    
    # Trigger conditions
    alert_threshold = Column(DECIMAL(5, 2), nullable=True)  # minimum margin % to trigger
    min_confidence = Column(DECIMAL(3, 2), nullable=True)  # minimum confidence score
    max_risk_level = Column(String(20), nullable=True)  # maximum risk level to alert on
    
    # Alert content
    alert_title = Column(String(255), nullable=True)
    alert_message = Column(Text, nullable=True)
    custom_template = Column(Text, nullable=True)
    
    # Status tracking
    status = Column(String(20), default="pending", nullable=False)  # 'pending', 'sent', 'failed', 'disabled'
    sent_count = Column(DECIMAL(10, 0), default=0)
    last_error = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    opportunity = relationship("ArbitrageOpportunity", back_populates="alerts")
    product = relationship("Product")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_alert_status_created', 'status', 'created_at'),
        Index('idx_alert_user_type', 'user_id', 'alert_type'),
        Index('idx_alert_opportunity', 'opportunity_id'),
        Index('idx_alert_pending', 'status'),
    )
    
    def __repr__(self):
        return f"<UserAlert(id={self.id}, type='{self.alert_type}', status='{self.status}')>"
    
    @property
    def is_pending(self) -> bool:
        """Check if alert is pending."""
        return self.status == "pending"
    
    @property
    def is_sent(self) -> bool:
        """Check if alert has been sent."""
        return self.status == "sent"
    
    @property
    def can_send(self) -> bool:
        """Check if alert can be sent."""
        return self.status in ["pending", "failed"]