from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


class ProductBase(BaseModel):
    product_code: str
    name: str
    category: str
    unit_price: float
    cost_price: float


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    unit_price: Optional[float] = None
    cost_price: Optional[float] = None


class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class ProductSummary(BaseModel):
    product_id: int
    product_name: str
    category: str
    quantity_sold: int
    revenue: float
    profit: float


class ProductTopRead(BaseModel):
    product_id: int
    product_name: str
    category: str
    quantity_sold: int
    revenue: float
    profit: float
