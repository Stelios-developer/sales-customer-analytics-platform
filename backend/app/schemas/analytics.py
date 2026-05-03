from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class KPISummary(BaseModel):
    total_revenue: float
    total_profit: float
    number_of_orders: int
    number_of_customers: int
    number_of_products: int
    average_order_value: float
    conversion_proxy: float
    paid_revenue: float
    pending_revenue: float
    top_product: Optional[str] = None
    top_customer: Optional[str] = None
    best_country: Optional[str] = None


class MonthlySales(BaseModel):
    month: str
    revenue: float
    profit: float
    orders: int


class TopProduct(BaseModel):
    product_id: int
    product_name: str
    category: str
    quantity_sold: int
    revenue: float
    profit: float


class TopCustomer(BaseModel):
    customer_id: int
    customer_name: str
    country: str
    orders: int
    total_spent: float
    average_order_value: float


class SalesByCountry(BaseModel):
    country: str
    revenue: float
    orders: int
    customers: int


class SalesByCategory(BaseModel):
    category: str
    revenue: float
    profit: float
    orders: int
    quantity_sold: int


class PaymentMethodSummary(BaseModel):
    payment_method: str
    total: float
    count: int


class OrderStatusSummary(BaseModel):
    status: str
    count: int
    revenue: float


class ProfitSummary(BaseModel):
    total_revenue: float
    total_cost: float
    total_profit: float
    profit_margin_pct: float


class RecentOrder(BaseModel):
    order_id: int
    order_number: str
    customer_name: str
    total_amount: float
    status: str
    order_date: str
