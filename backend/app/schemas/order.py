from pydantic import BaseModel, ConfigDict
from pydantic import Field
from datetime import datetime, date
from typing import Optional, List


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: float
    discount_amount: float = 0.0
    line_total: float


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemRead(OrderItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class OrderBase(BaseModel):
    order_number: str
    customer_id: int
    order_date: date
    status: str = "completed"
    total_amount: float
    discount_amount: float = 0.0
    shipping_amount: float = 0.0
    country: str
    city: str = "Unknown"


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderRead(OrderBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class OrderDetailRead(OrderRead):
    customer_name: str = ""
    items: List[OrderItemRead] = Field(default_factory=list)
    payment_status: str = ""
    payment_method: str = ""


class OrderListParams(BaseModel):
    search: Optional[str] = None
    status: Optional[str] = None
    country: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    sort_by: str = "order_date"
    sort_order: str = "desc"
    page: int = 1
    page_size: int = 20
