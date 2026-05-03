from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import StaticPool
from app.core.config import settings


def _engine_kwargs(database_url: str) -> dict:
    if database_url.startswith("sqlite"):
        return {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
        }
    return {
        "pool_pre_ping": True,
        "echo": False,
    }


engine = create_engine(
    settings.DATABASE_URL,
    **_engine_kwargs(settings.DATABASE_URL),
)

TestEngine = None
if settings.ENVIRONMENT == "testing":
    TestEngine = create_engine(
        settings.SQLITE_DATABASE_URL,
        **_engine_kwargs(settings.SQLITE_DATABASE_URL),
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TestEngine) if TestEngine else None

Base = declarative_base()


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
