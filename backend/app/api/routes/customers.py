from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_database_session
from app.schemas.customer import CustomerRead
from app.schemas.order import OrderRead
from app.services.customer_service import get_customers, get_customer_by_id, get_customer_orders, get_top_customers_service, get_customer_segments

router = APIRouter()


@router.get("", response_model=List[CustomerRead])
def list_customers(
    search: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_database_session),
):
    customers = get_customers(db, search=search, country=country, skip=skip, limit=limit)
    return [CustomerRead.model_validate(c) for c in customers]


@router.get("/top")
def top_customers(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_database_session)):
    return get_top_customers_service(db, limit=limit)


@router.get("/segments")
def customer_segments(db: Session = Depends(get_database_session)):
    return get_customer_segments(db)


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: int, db: Session = Depends(get_database_session)):
    customer = get_customer_by_id(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return CustomerRead.model_validate(customer)


@router.get("/{customer_id}/orders", response_model=List[OrderRead])
def customer_orders(customer_id: int, db: Session = Depends(get_database_session)):
    orders = get_customer_orders(db, customer_id)
    return [OrderRead.model_validate(o) for o in orders]
