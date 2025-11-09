# Placeholder for Tally XML/HTTP client

import httpx
from src.app.core.config import settings
import xml.etree.ElementTree as ET

async def send_tally_request(xml_payload: str):
    url = f"http://{settings.TALLY_HOST}:{settings.TALLY_PORT}"  # e.g., http://windows-server-ip:9000
    headers = {"Content-Type": "application/xml"}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, content=xml_payload, headers=headers)
            response.raise_for_status()
            # Log raw response for debugging
            print("Tally raw response:", response.text)
            # Parse XML response
            try:
                root = ET.fromstring(response.text)
                # Convert XML to dict (simple version)
                def xml_to_dict(element):
                    return {
                        element.tag: (
                            [xml_to_dict(child) for child in element] if list(element) else element.text
                        )
                    }
                return xml_to_dict(root)
            except ET.ParseError:
                return {"error": "Invalid XML response from Tally", "raw": response.text}
    except httpx.RequestError as e:
        return {"error": f"Tally connection error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
