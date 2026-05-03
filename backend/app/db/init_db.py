from app.db.database import Base, engine
from app.models import customer, product, order, order_item, payment, data_import_log, ml_model_run


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
