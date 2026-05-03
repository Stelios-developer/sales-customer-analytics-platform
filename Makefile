.PHONY: up down build logs test backend frontend migrate seed convert-online-retail

up:
	docker-compose up --build

down:
	docker-compose down -v

build:
	docker-compose build

logs:
	docker-compose logs -f backend

test:
	cd backend && pytest -v

backend:
	cd backend && uvicorn app.main:app --reload

frontend:
	cd frontend && npm run dev

migrate:
	cd backend && alembic upgrade head

seed:
	cd backend && python -m app.db.seed

convert-online-retail:
	cd backend && python -m scripts.convert_online_retail --input ../data/raw/online_retail.xlsx --output ../data/processed/online_retail_sales.csv
