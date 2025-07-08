# instagram_api.py
import httpx
import json
from user_id_fetcher import get_user_id # Assuming user_id_fetcher.py exists
from headers_loader import load_headers

# Load headers once when this module is imported
HEADERS = load_headers()

def fetch_chain(user_id):
    """Fetches chaining suggestions (suggested users) for a given Instagram user ID."""
    url = f"https://i.instagram.com/api/v1/discover/chaining/?module=profile&target_id={user_id}&profile_chaining_check=false"
    try:
        with httpx.Client(http2=True, headers=HEADERS, timeout=20.0) as client:
            r = client.get(url)
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
