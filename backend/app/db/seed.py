from app.db.database import SessionLocal
from app.services.csv_import_service import import_sales_csv
from fastapi import UploadFile
import io
import os


def seed_database() -> None:
    """Seed the database with sample sales data."""
    db = SessionLocal()
    try:
        backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        sample_path = os.path.join(backend_dir, "sample_data", "sample_sales_data.csv")
        if not os.path.exists(sample_path):
            print(f"Sample data not found at {sample_path}")
            return
        with open(sample_path, "rb") as f:
            upload = UploadFile(
                file=io.BytesIO(f.read()),
                filename="sample_sales_data.csv",
                headers={"content-type": "text/csv"},
            )
            result = import_sales_csv(upload, db)
            print(f"Seed result: {result}")
    except Exception as e:
        print(f"Seed failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
