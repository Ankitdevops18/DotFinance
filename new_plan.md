# TallyAI — Comprehensive Full-Stack Implementation Plan

## 1. Project Overview

**Problem:**
Businesses need real-time, secure, multi-tenant access to financial reports (Receivables, Payables, GST liabilities, Stock, Payroll, Income/Expense analytics) from Tally Prime, delivered via a conversational chatbot interface. Tally Prime supports JSON and XML integrations over HTTP, with nested JSON and REST-like workflows via TDL and plugins ([1][2][3][4]).

**Goals:**
- Deliver a chatbot (Telegram, future WhatsApp) for financial queries.
- Backend Tally bridge for JSON/HTTP integration with Tally on AWS Windows server.
- Multi-tenant, secure, scalable reporting (PDF/Excel, charts).
- Modern Python backend, best practices, src layout.

**In-scope reports:**
- Receivables, Payables, GST liabilities, Stock details, Payroll summaries, Income & Expense analytics.

**Multi-tenant needs:**
- Each user/company isolated; credentials, data, and reports per tenant.
- Secure storage, encrypted secrets, audit logs.

**Constraints:**
- Tally Prime runs on AWS Windows EC2, exposes HTTP/JSON API (TDL/plugin).
- Telegram bot (webhook mode, HTTPS) initially; WhatsApp planned.
- Python 3.11+, FastAPI, src layout, PostgreSQL (or SQLite for PoC).

## 2. Architecture

**System Flow:**
User (Telegram, future WhatsApp) → Chatbot Logic (LangChain) → Backend Middleware (FastAPI) → Tally Bridge (JSON API on AWS Windows server)

**Diagram:**
```
User (Telegram/WhatsApp)
   │
   ▼
Telegram Bot Webhook (python-telegram-bot)
   │
   ▼
LangChain Orchestration (intent, tools)
   │
   ▼
FastAPI Middleware (auth, tenancy, rate limits)
   │
   ▼
Tally Bridge (httpx, JSON/HTTP to Tally/TDL)
   │
   ▼
Tally Prime (AWS Windows EC2)
```

**Narrative:**
- Telegram bot receives messages via webhook (HTTPS endpoint).
- LangChain parses intent/entities, routes to FastAPI endpoints/tools.
- FastAPI handles auth, multi-tenancy, rate limiting, caching.
- Tally bridge sends JSON requests to Tally Prime (TDL/plugin) on AWS Windows EC2, parses nested JSON responses.
- Reports are cached, shaped, and returned to user (PDF/Excel, charts).
- Session state, caching, and audit logs stored in Redis/PostgreSQL.

**Best Practices:**
- Separate bot logic from business logic.
- Use webhook mode for Telegram bots ([5][6][7]).
- Extensive caching and rate limiting for scale.
- src layout for clean imports and packaging ([8][9][11]).

## 3. Technology Stack

- **Backend:** Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy, Alembic
- **Async/Queue:** Celery or RQ, Redis (cache/queue)
- **Database:** PostgreSQL (multi-tenant), SQLite for PoC
- **Bot:** python-telegram-bot, webhook mode
- **LLM/Orchestration:** LangChain (tools, chains, RAG)
- **HTTP Client:** httpx (Tally bridge)
- **Reporting:** Pandas (charts, tables), WeasyPrint/ReportLab (PDF/Excel)
- **Packaging:** Poetry or pip-tools, pyproject.toml
- **Server:** uvicorn/gunicorn
- **Infra:** Docker, K8s, Terraform (AWS EC2 for Tally)

**Justification:**
- src layout per Python Packaging User Guide ([9][11][8]) prevents import mistakes, supports packaging, and clean separation of concerns.

## 4. Directory Structure (src layout)

```
.
├── pyproject.toml
├── README.md
├── .env.example
├── .gitignore
├── docker/
│   ├── api.Dockerfile
│   ├── worker.Dockerfile
│   └── nginx.conf
├── deploy/
│   ├── k8s/ # manifests/helm
│   └── terraform/ # AWS infra including Windows EC2 for Tally
├── scripts/
│   ├── dev_bootstrap.sh
│   └── run_migrations.sh
├── tests/
│   ├── unit/
│   └── integration/
├── src/
│   └── app/
│       ├── __init__.py
│       ├── core/ # settings, logging, security, tenancy
│       │   ├── config.py
│       │   ├── logging.py
│       │   └── security.py
│       ├── api/ # FastAPI routers
│       │   ├── deps.py
│       │   ├── auth.py
│       │   ├── reports.py
│       │   ├── tenants.py
│       │   └── health.py
│       ├── bots/ # Telegram (WhatsApp later)
│       │   ├── telegram_webhook.py
│       │   └── commands.py
│       ├── llm/ # LangChain chains/tools/prompts
│       │   ├── chains.py
│       │   ├── tools.py
│       │   └── prompts.py
│       ├── tally_bridge/ # Tally JSON/HTTP integration
│       │   ├── client.py # httpx, retries, auth to Tally/TDL
│       │   ├── schemas.py # JSON payloads
│       │   └── adapters/ # report-specific mappers
│       ├── services/ # domain services
│       │   ├── reporting_service.py
│       │   ├── gst_service.py
│       │   └── payroll_service.py
│       ├── repositories/
│       │   ├── base.py
│       │   ├── report_cache.py
│       │   └── tenant_repo.py
│       ├── models/ # SQLAlchemy models
│       │   ├── tenant.py
│       │   ├── user.py
│       │   └── audit.py
│       ├── schemas/ # Pydantic request/response
│       │   ├── auth.py
│       │   ├── reports.py
│       │   └── common.py
│       ├── workers/ # Celery/RQ tasks
│       │   ├── tasks.py
│       │   └── schedule.py
│       ├── utils/
│       │   ├── caching.py
│       │   ├── rate_limiting.py
│       │   └── pagination.py
│       └── main.py # FastAPI app factory
└── alembic/
    ├── env.py
    └── versions/
```

**Notes:**
- src layout prevents import path mistakes, supports packaging, and clean separation of concerns ([9][11][8]).
- Each module is isolated for testability and maintainability.

## 5. Integration with Tally Prime

- Tally bridge uses httpx to send JSON requests to Tally Prime (TDL/plugin) on AWS Windows EC2 ([1][2][3][4]).
- Tally supports JSON-style integrations, nested JSON, and REST-like workflows via TDL and plugins.
- Handle authentication headers, retries, and error handling (exponential backoff).
- Example JSON payload for Receivables:
```python
payload = {
    "Request": {
        "Type": "Receivables",
        "Params": {"FromDate": "2025-01-01", "ToDate": "2025-01-31"}
    }
}
```
- Endpoints for Receivables, Payables, GST, Stock, Payroll; adapters shape results for chatbot and reporting.
- Third-party plugins may expose GET/POST APIs for masters, vouchers, and reports ([12][4][1]).

## 6. Chatbot Flows

- Register Telegram bot with BotFather; use webhook mode (HTTPS endpoint).
- Command menu, guardrails (rate limits, cooldowns), user feedback.
- Scalable command routing; separate bot logic from business logic ([6][5]).
- RAG for FAQs/policy text with LangChain ([5][7]).
- Minimal message flow:
  - User sends command/query
  - Bot webhook receives, validates user
  - LangChain parses intent, calls FastAPI tool
  - FastAPI fetches/caches report, returns summary/chart
  - Bot sends formatted reply (PDF/Excel/chart)
- State handling: session context, last report, filters.

## 7. LangChain Orchestration

- Tools for each report type (Receivables, Payables, GST, etc.) calling FastAPI endpoints ([13][14][5]).
- RetrievalQA or tools routing for RAG/FAQ.
- Prompt templates with function/tool call boundaries.
- Latency/relevance monitoring; reduce hallucinations with structured tool outputs.

## 8. Security and Multi-Tenancy

- JWT/OAuth for end users and bot verification.
- Tenant isolation via schema or tenant_id column.
- Per-tenant rate limiting and quotas.
- Encrypted secrets (Fernet, environment key).
- Audit logs for access to financial data.
- Telegram user verification before exposing tenant data ([11][6]).

## 9. Data Model and Persistence

- Tables: tenants, users, api_keys, telegram_links, report_cache, audit_events.
- Migrations via Alembic.
- Caching keys by tenant+report+params with TTL.

## 10. API Design

- FastAPI endpoints: auth, /reports/{type}, /tenants, /health.
- Typed schemas (Pydantic).
- Pagination and filters.
- Idempotency keys for report requests.
- Consistent error model.
- Health/readiness probes for ops ([11]).

## 11. Background Jobs and Performance

- Queue long-running report generations (Celery/RQ).
- Retry with exponential backoff.
- Webhook handler quick-ack, defer heavy work.
- Caching of frequently requested reports.
- Rate limiting on bot and API.
- Use webhook mode for scale ([6][11]).

## 12. Ops, CI/CD, and Observability

- GitHub Actions pipeline: lint (ruff/flake8), format (black, isort), type-check (mypy), tests (pytest), build images, scan, deploy.
- Structured logging, request ids, metrics for DAU/commands, error rates, latency.
- Health checks for API and bot endpoints ([8][11]).

## 13. Testing Strategy

- Unit tests for services/adapters.
- Contract tests for Tally bridge (recorded fixtures).
- Integration tests for API and bot webhooks.
- Load tests for report-heavy endpoints ([11]).

## 14. Compliance and Audit

- Immutable audit logs for report fetches, admin actions, permission changes.
- Retain logs per tenant for statutory periods.
- Mask PII in logs.
- Adhere to financial data handling norms ([11]).

## 15. Rollout Plan

- **Phase 1:** Telegram + core reports via FastAPI + Tally bridge (read-only, caching).
- **Phase 2:** Admin UI/dashboard, WhatsApp channel, advanced analytics.
- **Phase 3:** Multi-tenant billing, SLOs, autoscaling, Windows host hardening ([1][6]).

---

**References:**
[1] https://help.tallysolutions.com/integrate-with-tallyprime/
[2] https://help.tallysolutions.com/json-based-export-import/
[3] https://help.tallysolutions.com/integration-methods-and-technologies/
[4] https://help.tallysolutions.com/integration-with-tallyprime/
[5] https://www.linkedin.com/posts/luis-oria-seidel-%F0%9F%87%BB%F0%9F%87%AA-301a758a_rag-langchain-telegrambot-activity-7384940907583787008-a3Of
[6] https://wnexus.io/the-complete-guide-to-telegram-bot-development-in-2025/
[7] https://python.langchain.com/docs/integrations/document_loaders/telegram/
[8] https://www.clariontech.com/blog/python-development-practices
[9] https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/
[10] https://python.langchain.com/docs/integrations/chat_loaders/telegram/
[11] https://dagster.io/blog/python-project-best-practices
[12] https://api2books.com
[13] https://latenode.com/blog/ai-frameworks-technical-infrastructure/langchain-setup-tools-agents-memory/langchain-tools-complete-guide-creating-using-custom-llm-tools-code-examples-2025
[14] https://www.youtube.com/watch?v=GLpitbsSJtw
[15] https://stackoverflow.com/questions/49766143/how-can-we-integrate-rest-api-with-tally
[16] https://tallyexperts.co.in/services/tally-api-intergration/
[17] https://www.youtube.com/watch?v=QU9XivPOSWU
[18] https://www.rootfi.dev/integrations/tally-prime
[19] https://stackoverflow.com/questions/193161/what-is-the-best-project-structure-for-a-python-application
[20] https://www.youtube.com/watch?v=mFyE9xgeKcA
