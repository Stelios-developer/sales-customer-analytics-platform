from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_database_session
from app.schemas.product import ProductRead
from app.services.product_service import get_products, get_product_by_id, get_top_products_service, get_product_categories

router = APIRouter()


@router.get("", response_model=List[ProductRead])
def list_products(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_database_session),
):
    products = get_products(db, search=search, category=category, skip=skip, limit=limit)
    return [ProductRead.model_validate(p) for p in products]


@router.get("/top")
def top_products(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_database_session)):
    rows = get_top_products_service(db, limit=limit)
    return [
        {
            "product_id": r.id,
            "product_name": r.name,
            "category": r.category,
            "quantity_sold": int(r.qty),
            "revenue": round(float(r.revenue), 2),
            "profit": round(float(r.profit), 2),
        }
        for r in rows
    ]


@router.get("/categories")
def product_categories(db: Session = Depends(get_database_session)):
    return get_product_categories(db)


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_database_session)):
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductRead.model_validate(product)
