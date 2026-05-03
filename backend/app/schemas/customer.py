from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class CustomerBase(BaseModel):
    customer_code: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    country: str
    city: str = "Unknown"
    segment: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    segment: Optional[str] = None


class CustomerRead(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class CustomerSummary(BaseModel):
    customer_id: int
    customer_name: str
    country: str
    orders: int
    total_spent: float
    average_order_value: float


class CustomerWithOrders(CustomerRead):
    total_spent: float = 0.0
    order_count: int = 0


class CustomerSegmentRead(BaseModel):
    customer_id: int
    customer_name: str
    segment: str
    recency_days: int
    frequency: int
    monetary_value: float
