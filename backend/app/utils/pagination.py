from typing import TypeVar, Generic, List, Type
from sqlalchemy.orm import Session, Query
from sqlalchemy import func

T = TypeVar("T")


def paginate_query(db: Session, query, page: int, page_size: int) -> dict:
    """Paginate a SQLAlchemy query and return standardized pagination dict."""
    total = db.execute(func.count()).select_from(query.subquery()).scalar()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }
