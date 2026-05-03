# GitHub Publishing Guide

Use this checklist before pushing the repository publicly.

## Repository Settings

Recommended repository name:

```text
sales-customer-analytics-platform
```

Recommended description:

```text
Full-stack sales analytics platform with FastAPI, React, ETL, SQL analytics, XGBoost forecasting, and Gaussian Mixture customer segmentation.
```

Recommended topics:

```text
fastapi
react
typescript
postgresql
sqlalchemy
data-engineering
etl
analytics-dashboard
machine-learning
xgboost
customer-segmentation
sales-analytics
```

## Files That Should Not Be Committed

Confirm these are absent from `git status --short`:

```text
backend/.env
frontend/.env
backend/.venv/
frontend/node_modules/
frontend/dist/
backend/sales_dev.db
backend/artifacts/
backend/uploads/
data/raw/
data/processed/
```

## Final Commands

```powershell
git init
git branch -M main
git add .
git status --short
git commit -m "Initial sales customer analytics platform"
git remote add origin https://github.com/Stelios-developer/sales-customer-analytics-platform.git
git push -u origin main
```

## After Push

1. Open the GitHub Actions tab and confirm CI passes.
2. Add screenshots to `docs/screenshots/`.
3. Update `docs/screenshots.md` with image links.
4. Enable Dependabot alerts in repository settings.
5. Pin the repository on your GitHub profile.
