# TallyAI — Comprehensive Full-Stack Implementation Plan

This repository contains a FastAPI-based middleware (TallyAI) that integrates with Tally Prime to fetch financial reports and serve them via HTTP and a chatbot interface.

This README documents how to set up the project locally, create a Python virtual environment, install dependencies from `requirements.txt`, configure environment variables, and run the development server.

## Prerequisites
- macOS or Linux (bash shell)
- Python 3.11 or newer installed and available on PATH
- Git
- curl (for quick API checks)

## Quickstart (local development)

1. Clone the repository

   ```bash
   git clone <repo-url>
   cd DotFinance
   ```

2. Create a Python virtual environment (recommended)

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # bash/zsh
   ```

3. Upgrade pip and install dependencies

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Environment variables

   This project uses environment variables (via pydantic-settings). You can set them directly in your shell or create a `.env` file and load it before running the server.

   Example `.env` (create at project root):

   ```env
   DATABASE_URL=sqlite:///./tallyai.db
   SECRET_KEY=supersecret
   TELEGRAM_BOT_TOKEN=
   TALLY_HOST=65.0.33.244
   TALLY_PORT=9000
   DEBUG=true
   ```

   To export variables into your shell for the current session (bash):

   ```bash
   export TALLY_HOST=65.0.33.244
   export TALLY_PORT=9000
   export SECRET_KEY=supersecret
   ```

5. Run the development server

   From the project root with your venv activated:

   ```bash
   uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at http://127.0.0.1:8000

6. Verify the server is running

   ```bash
   curl http://127.0.0.1:8000/health
   ```

   Expected response:

   ```json
   {"status":"ok"}
   ```

7. Test the ledgers endpoint (example)

   The `/companies/{company_id}/reports/ledgers` endpoint sends XML to Tally. If you want to test without Tally available, expect an error about connection. To call the endpoint locally (company_id = 1):

   ```bash
   curl http://127.0.0.1:8000/companies/1/reports/ledgers
   ```

   If Tally is accessible at `TALLY_HOST:TALLY_PORT` the endpoint will POST XML to that host and return the parsed XML as JSON (or error details).

   Advanced: sending the same XML directly to the Tally HTTP port (debugging)

   ```bash
   curl -X POST "http://$TALLY_HOST:$TALLY_PORT" -H "Content-Type: text/xml" --data-binary @- <<'XML'
   <ENVELOPE>
          <HEADER>
                 <VERSION>1</VERSION>
                 <TALLYREQUEST>EXPORT</TALLYREQUEST>
                 <TYPE>COLLECTION</TYPE>
                 <ID>List of Ledgers</ID>
          </HEADER>
          <BODY>
          <DESC>
                 <STATICVARIABLES>
                        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                 </STATICVARIABLES>
          </DESC>
          </BODY>
   </ENVELOPE>
   XML
   ```

   This is useful when validating the Tally server independent of the FastAPI app.

## Running tests

If tests are present, run:

```bash
pytest
```

## Notes and troubleshooting
- Tally connectivity: ensure the Windows server running Tally is reachable from your machine and the `TALLY_HOST` / `TALLY_PORT` are correct. If Tally is on a remote EC2 instance, verify firewall/security groups and that Tally is listening on the specified port.
- If you get XML parsing errors, the Tally response may not be valid XML — check raw response printed by the client.
- Increase the HTTP client timeout in `src/app/tally_bridge/client.py` if requests need more time.
- To change logging level or other settings, modify `src/app/core/config.py` or set environment variables.

## Useful commands summary

- Create & activate venv:
  ```bash
  python3 -m venv .venv && source .venv/bin/activate
  ```
- Install deps:
  ```bash
  pip install -r requirements.txt
  ```
- Start dev server:
  ```bash
  uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
  ```
- Run tests:
  ```bash
  pytest
  ```

## TallyBridge Program Workflow

Purpose
- Describe how the FastAPI app, routers, and the Tally bridge work together so a new developer can understand the runtime flow and where to make changes.

High-level flow
1. Developer runs the app: uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
2. Client calls an API endpoint, e.g. GET /companies/{company_id}/reports/ledgers
3. The endpoint (router) builds the required XML payload for the requested report and calls the Tally client: send_tally_request(xml_payload)
4. The Tally client posts the XML to the configured TALLY_HOST:TALLY_PORT with Content-Type: text/xml and returns a parsed representation (or error)
5. The API returns that response to the caller (or an HTTP error if appropriate)

Key components and responsibilities (file-by-file)
- README.md
  - Onboarding, setup, commands, and this workflow documentation.

- src/app/main.py
  - App entrypoint. Creates FastAPI app and includes routers. Change this to add middleware, exception handlers, or dependency injection.

- src/app/core/config.py
  - Centralized settings (pydantic-settings). Edit defaults and environment variable names here. Used throughout the app as `from src.app.core.config import settings`.

- src/app/core/logging.py
  - Logging configuration for the project. Adjust format/level here when debugging or in production.

- src/app/core/security.py
  - Password hashing utilities (passlib). Expand for auth helpers and token logic.

- src/app/api/
  - FastAPI routers that expose HTTP endpoints. Each file is an APIRouter with a logical grouping:
    - auth.py — authentication endpoints
    - health.py — simple health/readiness endpoints
    - reports.py — report endpoints (payables, receivables, ledgers, company-balance). These build XML payloads and call the tally client.
    - tenants.py — tenant management (multi-tenant mapping for different Tally hosts/credentials)

- src/app/tally_bridge/client.py
  - HTTP client to Tally (httpx AsyncClient). Responsible for posting XML, setting headers (text/xml), timeouts, error handling, and parsing XML responses into dict-like structures.
  - Recommendation: if you need per-tenant hosts, make this function accept host/port or build a client instance per tenant.

- src/app/tally_bridge/schemas.py
  - Placeholder for typed payload/response schemas for the Tally bridge. Use this to validate and document expected shapes.

- src/app/tally_bridge/adapters/
  - Mappers to convert raw Tally XML/JSON into internal models or output shapes for the chatbot.

- src/app/services/
  - Domain services that orchestrate business logic. For example, reporting_service should call the tally bridge and transform results for consumers.

- src/app/repositories/
  - Database access and caching abstractions (SQLite/Postgres). report_cache.py for cached responses.

- src/app/models/
  - Domain models (placeholders now). Add SQLAlchemy models here.

- src/app/schemas/
  - Pydantic request/response schemas for API validation.

- src/app/bots/
  - Telegram bot logic and webhook handling; calls API endpoints as tools.

- src/app/llm/
  - LangChain orchestration layer: parses user intent, selects tools (API endpoints), and manages prompt templates.
  - chains.py — intent parsing and high-level orchestration.
  - tools.py — wrappers that call FastAPI endpoints (e.g., reports) as LangChain tools.
  - prompts.py — reusable prompt templates.

- src/app/utils/
  - Small helpers (pagination, rate-limiting, caching).

- src/app/workers/
  - Background task definitions and scheduling (Celery or RQ integration points).

Runtime tips and where to change behavior
- Changing Tally host/port per-company: add tenant model + tenant repo; update routers to load tenant config and pass host/port to the Tally client.
- Improve XML parsing: replace xml.etree.ElementTree with lxml or xmltodict for richer parsing and robust namespace handling.
- Add structured logging: use logger from src/app/core/logging.py instead of print statements.
- Error handling: convert client errors into HTTPException in routers for correct status codes.

Developer checklist when adding a new report
1. Add router method in `src/app/api/reports.py` (validate query params or request body as Pydantic model).
2. Create XML payload or JSON template in `src/app/tally_bridge/schemas.py` or in the router if simple.
3. Call `send_tally_request(xml_payload)` or a higher-level service in `src/app/services/reporting_service.py`.
4. Create adapter in `src/app/tally_bridge/adapters/` to normalize response.
5. Add tests under tests/ and update README if additional setup is required.

Contact & next steps
- Add a `./.env.example` file with the environment variables shown in this README.
- Replace placeholders with real models, tests, and tenant management before production.

## Contributing
- Follow style rules: run formatters/linters if configured (black, isort, ruff). Add tests for new features.

## License & contacts
- Project README is intentionally minimal. Add license and maintainer contact details here.
