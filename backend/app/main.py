from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.api.routes import health, imports, orders, customers, products, analytics, ml


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up %s v%s", settings.APP_NAME, settings.APP_VERSION)
    logger.info("Database schema is managed by Alembic migrations")
    yield
    logger.info("Shutting down %s", settings.APP_NAME)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Sales & Customer Analytics Intelligence Platform API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["Health"])
app.include_router(imports.router, prefix="/api/imports", tags=["Imports"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(customers.router, prefix="/api/customers", tags=["Customers"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(ml.router, prefix="/api/ml", tags=["Machine Learning"])
