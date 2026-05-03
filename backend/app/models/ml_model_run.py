from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.db.database import Base


class MLModelRun(Base):
    __tablename__ = "ml_model_runs"

    id = Column(Integer, primary_key=True, index=True)
    model_type = Column(String(50), nullable=False, index=True)
    model_name = Column(String(100), nullable=False)
    metrics_json = Column(Text, nullable=True)
    artifact_path = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
