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

## Contributing
- Follow style rules: run formatters/linters if configured (black, isort, ruff). Add tests for new features.

## License & contacts
- Project README is intentionally minimal. Add license and maintainer contact details here.
