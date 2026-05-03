from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Date, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    order_date = Column(Date, nullable=False, index=True)
    status = Column(String(50), nullable=False, default="completed", index=True)
    total_amount = Column(Numeric(12, 2), nullable=False, default=0)
    discount_amount = Column(Numeric(12, 2), nullable=False, default=0)
    shipping_amount = Column(Numeric(12, 2), nullable=False, default=0)
    country = Column(String(100), nullable=False, index=True)
    city = Column(String(100), nullable=False, default="Unknown")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="order", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_orders_date_status", "order_date", "status"),
        Index("ix_orders_country_date", "country", "order_date"),
    )
