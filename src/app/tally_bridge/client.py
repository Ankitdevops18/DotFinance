# Placeholder for Tally JSON/HTTP client

import httpx
from app.core.config import settings

async def send_tally_request(payload):
    url = f"http://{settings.TALLY_HOST}:{settings.TALLY_PORT}"  # e.g., http://windows-server-ip:9000
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        return {"error": f"Tally connection error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
