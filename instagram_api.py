# instagram_api.py (Modified for Async)
import httpx
import json
import asyncio # <--- IMPORTANT: New import for async
from user_id_fetcher import get_user_id # Assuming user_id_fetcher.py exists
from headers_loader import load_headers

# Load headers once when this module is imported
HEADERS = load_headers()

# Use a global async client to enable connection pooling across calls
# This client should be managed by the main application's lifecycle
async_client = None # <--- IMPORTANT: Define async client globally

async def init_async_client(): # <--- IMPORTANT: New async function to initialize client
    """Initializes the global async httpx client."""
    global async_client
    if async_client is None:
        async_client = httpx.AsyncClient(http2=True, headers=HEADERS, timeout=20.0)

async def close_async_client(): # <--- IMPORTANT: New async function to close client
    """Closes the global async httpx client."""
    global async_client
    if async_client:
        await async_client.aclose()
        async_client = None

async def fetch_chain_async(user_id): # <--- IMPORTANT: This function must be async
    """Fetches chaining suggestions asynchronously for a given Instagram user ID."""
    if async_client is None:
        # This should ideally be called once at the start of the application
        # but added as a fallback to prevent errors if not initialized.
        await init_async_client()

    url = f"https://i.instagram.com/api/v1/discover/chaining/?module=profile&target_id={user_id}&profile_chaining_check=false"
    try:
        # Use the global async client and await the get request
        r = await async_client.get(url) # <--- IMPORTANT: Use await
        print(f"[+] Status for User ID {user_id}: {r.status_code}")
        r.raise_for_status()
        return r.json().get("users", [])
    except httpx.RequestError as e:
        print(f"❌ Network or request error while fetching chain for ID {user_id}: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON response for ID {user_id}: {e}.")
        # Use r.text only if r is defined (request was successful enough to get a response)
        print(f"   Raw response content: {r.text if 'r' in locals() else 'No response received.'}")
        return []
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP error {e.response.status_code} while fetching chain for ID {user_id}: {e.response.text}")
        return []
    except Exception as e:
        print(f"❌ An unexpected error occurred while fetching chain for ID {user_id}: {e}")
        return []
