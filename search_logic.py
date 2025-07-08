# search_logic.py
import time
import random
from instagram_api import fetch_chain
from user_id_fetcher import get_user_id # Assuming user_id_fetcher.py exists
from config import MAX_DEPTH

def recursive_chain_search(username, keywords_to_match, visited_users, all_found_matches, depth=0, known_user_id=None):
    """
    Recursively searches Instagram user chains.
    It attempts to match any of the provided keywords within each profile.
    This function updates the visited_users and all_found_matches sets/lists in-place.
    """
    indent = "  " * depth

    if depth > MAX_DEPTH:
        print(f"{indent}⚠️ Reached maximum recursion depth ({MAX_DEPTH}) for @{username}, stopping further exploration.")
        return

    user_id = known_user_id
    if user_id is None:
        user_id = get_user_id(username)

    if not user_id:
        print(f"{indent}⚠️ Could not get user ID for @{username}. Skipping this user.")
        return

    if user_id in visited_users:
        print(f"{indent}🔁 Already visited @{username} (ID: {user_id}), skipping to avoid loops.")
        return

    visited_users.add(user_id)
    print(f"{indent}🔎 Searching chains of @{username} (ID: {user_id})... [Depth: {depth}]")

    users_in_chain = fetch_chain(user_id)

    if not users_in_chain:
        print(f"{indent}🤷 No users found in chain for @{username} or failed to fetch suggestions.")
        return

    for user_data in users_in_chain:
        uname = user_data.get("username", "")
        fname = user_data.get("full_name", "")
        uid = user_data.get("id")

        if not uname or not uid:
            print(f"{indent}⚠️ Skipping user with missing username or ID: {user_data}")
            continue

        print(f"{indent}→ @{uname} - {fname} (ID: {uid})")

        for kw_to_check in keywords_to_match:
            if kw_to_check.lower() in uname.lower() or kw_to_check.lower() in fname.lower():
                match_data = {
                    "username": uname,
                    "full_name": fname,
                    "user_id": uid,
                    "found_via_username": username,
                    "found_via_user_id": user_id,
                    "depth_found": depth,
                    "matched_keyword": kw_to_check
                }
                if match_data not in all_found_matches:
                    all_found_matches.append(match_data)
                    print(f"\n🎯 FOUND MATCH for '{kw_to_check}': @{uname} - {fname} - User ID: {uid} (Found via @{username} at Depth {depth})\n")

    if depth < MAX_DEPTH:
        print(f"{indent}🔍 Exploring deeper chains from @{username}...")
        for user_data in users_in_chain:
            time.sleep(random.uniform(1.0, 2.0))
            recursive_chain_search(user_data["username"], keywords_to_match, visited_users, all_found_matches, depth + 1, known_user_id=user_data.get("id"))
    else:
        print(f"{indent}Maximum recursion depth reached for @{username}. Not going deeper.")

