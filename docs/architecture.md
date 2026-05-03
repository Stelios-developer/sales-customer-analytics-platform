# Architecture Documentation

## System Overview

The Sales & Customer Analytics Intelligence Platform is a modular, 3-tier web application designed for local development and containerized deployment.

---

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Browser                        │
│              (React SPA + Recharts Dashboard)              │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/JSON
┌───────────────────────────▼─────────────────────────────────┐
│                     FastAPI Backend                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ API Routers  │  │   Services   │  │  ML Services     │  │
│  │ (routes)     │──│ (business    │──│ (forecast,       │  │
│  │              │  │  logic)       │  │  segment)        │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│           │                 │                  │             │
│           ▼                 ▼                  ▼             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              SQLAlchemy ORM + Alembic                │   │
│  └──────────────────────────┬───────────────────────────┘   │
└───────────────────────────────┼───────────────────────────────┘
                                │ SQL
┌───────────────────────────────▼───────────────────────────────┐
│                    PostgreSQL Database                          │
│  customers, products, orders, order_items, payments, logs     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
backend/
  app/
    api/routes/       # FastAPI route handlers
    core/             # Config, logging, exceptions
    db/               # Database engine, session, init, seed
    models/           # SQLAlchemy declarative models
    schemas/          # Pydantic request/response models
    services/         # Business logic services
      ml/             # Machine learning modules
    utils/            # Helper utilities (dates, money, pagination)
    main.py           # Application entry point
  alembic/            # Database migrations
  tests/              # pytest suite
  sample_data/        # Seed CSV
  uploads/            # Temporary upload storage
  artifacts/          # ML model persistence

frontend/
  src/
    api/              # Axios client
    components/       # Reusable React components
    pages/            # Route-level page components
    types/            # TypeScript interfaces
    utils/            # Formatters, constants
    App.tsx           # Router and layout
    main.tsx          # Entry point
    styles.css        # Tailwind directives
```

---

## Technology Choices

| Decision | Rationale |
|----------|-----------|
| FastAPI | Modern, async Python framework with automatic API docs and Pydantic integration. |
| SQLAlchemy 2.x | Industry-standard ORM with strong typing and modern query syntax. |
| PostgreSQL | Robust relational database with full ACID compliance and advanced analytics support. |
| React + Vite | Fast development, small bundles, excellent TypeScript support. |
| Recharts | Declarative, React-native charting library with good customization. |
| Tailwind CSS | Rapid UI development with consistent design system. |
| scikit-learn | Battle-tested ML library with excellent documentation for regression and clustering. |
| Docker Compose | Single-command reproducible environment for interviewers and collaborators. |

---

## Scalability Considerations

- **Database**: Connection pooling via SQLAlchemy. Indexes on all filter columns.
- **Backend**: Stateless design allows horizontal scaling behind a load balancer.
- **ML**: Model artifacts are precomputed and loaded on demand. Training is an explicit API call, not on the critical path.
- **Frontend**: Static build can be served from CDN. API calls are the only dynamic content.

---

## Security Notes

- CORS is configured via environment variables.
- File uploads are validated (extension, MIME type, size).
- No secrets are hardcoded in source.
- Database credentials are injected via environment variables.
- (Future) Add authentication middleware and input sanitization for production.
