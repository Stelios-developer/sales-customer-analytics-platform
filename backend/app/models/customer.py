from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Text, Date, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_code = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True)
    country = Column(String(100), nullable=False, index=True)
    city = Column(String(100), nullable=False, default="Unknown")
    segment = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_customers_name", "first_name", "last_name"),
        Index("ix_customers_country_city", "country", "city"),
    )
