import httpx
import json

# Load mobile API headers
def load_headers():
    with open("headers.json", "r", encoding="utf-8") as f:
        return json.load(f)

def get_user_id(username):
    headers = load_headers()

    url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"

    try:
        res = httpx.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            user_id = data["data"]["user"]["id"]
            print(f"✅ Username: @{username} → User ID: {user_id}")
            return user_id
        else:
            print(f"❌ Failed ({res.status_code}) - Username may not exist or you're rate limited.")
            print(res.text)
            return None
    except Exception as e:
        print(f"❌ Exception occurred while fetching user ID: {e}")
        return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python user_id_fetcher.py <username>")
    else:
        get_user_id(sys.argv[1])
