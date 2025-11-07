# TallyAI — Comprehensive Full-Stack Implementation Plan

## 1. Project Overview

**Problem:**
Businesses need real-time, secure, multi-tenant access to financial reports (Receivables, Payables, GST liabilities, Stock, Payroll, Income/Expense analytics) from Tally Prime, delivered via a conversational chatbot interface. Tally Prime supports JSON integrations over HTTP, with nested JSON and REST-like workflows via TDL and plugins.

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
- Python 3.11+, FastAPI, src layout, SQLite for PoC.

---

## 2. High-Level Architecture

User (Telegram, future: WhatsApp) → Chatbot Logic (LangChain) → Backend Middleware (FastAPI) → Tally Bridge (JSON API on AWS Windows server)

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

**Improvements:**
- Tally Prime hosted on AWS Windows server.
- Backend is stateless, multi-tenant aware; uses SQLite for PoC.
- Async IO in backend (FastAPI + httpx) for Tally JSON API calls.
- Charts and analytics via Pandas.
- Optional caching for frequently requested reports.

---

## 3. Technology Stack

- Backend: Python 3.11+, FastAPI, httpx, pydantic
- DB: SQLite
- Chatbot: LangChain (LLM routing)
- Messaging: Telegram Bot (python-telegram-bot, webhook mode)
- Reporting: Pandas + WeasyPrint/ReportLab

---

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
│   ├── k8s/
│   └── terraform/
├── scripts/
│   ├── dev_bootstrap.sh
│   └── run_migrations.sh
├── tests/
│   ├── unit/
│   └── integration/
├── src/
│   └── app/
│       ├── __init__.py
│       ├── core/
│       │   ├── config.py
│       │   ├── logging.py
│       │   └── security.py
│       ├── api/
│       │   ├── deps.py
│       │   ├── auth.py
│       │   ├── reports.py
│       │   ├── tenants.py
│       │   └── health.py
│       ├── bots/
│       │   ├── telegram_webhook.py
│       │   └── commands.py
│       ├── llm/
│       │   ├── chains.py
│       │   ├── tools.py
│       │   └── prompts.py
│       ├── tally_bridge/
│       │   ├── client.py
│       │   ├── schemas.py
│       │   └── adapters/
│       ├── services/
│       │   ├── reporting_service.py
│       │   ├── gst_service.py
│       │   └── payroll_service.py
│       ├── repositories/
│       │   ├── base.py
│       │   ├── report_cache.py
│       │   └── tenant_repo.py
│       ├── models/
│       │   ├── tenant.py
│       │   ├── user.py
│       │   └── audit.py
│       ├── schemas/
│       │   ├── auth.py
│       │   ├── reports.py
│       │   └── common.py
│       ├── workers/
│       │   ├── tasks.py
│       │   └── schedule.py
│       ├── utils/
│       │   ├── caching.py
│       │   ├── rate_limiting.py
│       │   └── pagination.py
│       └── main.py
└── alembic/
    ├── env.py
    └── versions/
```

---

## 5. Tally Integration Details

- Tally Prime provides HTTP/JSON API (see https://help.tallysolutions.com/json-integration/) on AWS Windows EC2.
- Build Tally JSON request templates for required reports (ledgers, stock, payroll, tax data).
- Send JSON over HTTP to Tally, parse JSON response.
- Normalize data to internal models (LedgerEntry, StockItem, PayrollRecord).
- Handle authentication headers, retries, error handling (exponential backoff).
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

---

## 6. API Design (focus)

- GET /companies/{id}/reports/payables?min_amount=&status= — outstanding payables
- GET /companies/{id}/reports/receivables
- GET /companies/{id}/reports/{report_id}/download — download PDF/Excel

Requests from chatbot: simple JSON with intent + entities, backend returns natural-language summary + optional attachment link.

---

## 7. Data Models (minimum)

- User(id, name, telegram_id, password_hash)
- Company(id, name, owner_id, tally_host, tally_port, tally_credentials_encrypted)
- Report(id, company_id, user_id, type, params, status, result_path, created_at)
- LedgerEntry / StockItem / PayrollRecord (normalized fields)

Encryption: use environment key (Fernet) to encrypt Tally credentials in SQLite.

---

## 8. Chatbot Flows

- Telegram Bot: user interacts via Telegram (future migration to WhatsApp planned).
- Register bot with BotFather; use webhook mode (HTTPS endpoint).
- Command menu, guardrails (rate limits, cooldowns), user feedback.
- LangChain: intent recognition, entity extraction, API call mapping.
- Conversation memory: last company context, date ranges, filters.
- Response composition: backend returns both structured metrics and human-friendly summary.
- Minimal message flow:
  - User sends command/query
  - Bot webhook receives, validates user
  - LangChain parses intent, calls FastAPI tool
  - FastAPI fetches/caches report, returns summary/chart
  - Bot sends formatted reply (PDF/Excel/chart)
- State handling: session context, last report, filters.

---

## 9. Reporting & Charts

- Use Pandas to compute and render summary tables and simple charts.
- Save charts as PNG/SVG to attach or embed in PDFs.
- Support on-demand exports.

---

## 10. Authentication & Multi-User

- JWT authentication with role-based access (user, admin).
- Per-user company access lists.
- Audit logs for report requests and exports.
- Telegram user verification before exposing tenant data.

---

## 11. Operational Concerns

- Logging & monitoring: structured logs.
- Rate limiting per user/company.
- Retry/backoff for Tally calls.
- Tests: unit tests for connectors + integration tests using a Tally test instance or mocked responses.

---

## 12. Timeline & Milestones (2–4 weeks prototype)

- Week 0–1: Project scaffolding, FastAPI skeleton, Tally JSON templates, simple Tally connector (sync) + local dev docs.
- Week 1–2: Implement core endpoints (payables, receivables), JSON normalization, minimal auth, DB models.
- Week 2–3: Telegram Bot + LangChain integration, basic conversational flows.
- Week 3–4: Reporting exports (PDF/Excel), charts, testing, deployment scripts.

---

## 13. Deliverables (initial PoC)

- FastAPI server with endpoints for payables, receivables
- Tally connector (JSON templates + parser)
- Minimal auth & company management
- Telegram Bot + LangChain demonstrating at least 3 user intents
- Example report exports (PDF/Excel) with charts
- README.md with setup and run instructions

---

## 14. Next Steps

1. Confirm Telegram Bot setup and provide bot token.
2. Provide sample Tally access (host/port) or sample JSON responses for development.
3. Confirm SQLite as DB for PoC.
