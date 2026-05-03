from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, unique=True)
    payment_method = Column(String(50), nullable=False, index=True)
    payment_status = Column(String(50), nullable=False, default="pending", index=True)
    paid_amount = Column(Numeric(12, 2), nullable=False, default=0)
    payment_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship("Order", back_populates="payment")
