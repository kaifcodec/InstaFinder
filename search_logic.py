# search_logic.py (Modified for Async - cleaner output)
import asyncio
import random
from instagram_api import fetch_chain_async
from user_id_fetcher import get_user_id
from config import MAX_DEPTH

async def recursive_chain_search_async(username, keywords_to_match, visited_users, all_found_matches, depth=0, known_user_id=None):
    """
    Recursively searches Instagram user chains asynchronously.
    It attempts to match any of the provided keywords within each profile.
    This function updates the visited_users and all_found_matches sets/lists in-place.
    """
    indent = "  " * depth

    if depth > MAX_DEPTH:
        # Suppress this message for cleaner output unless it's a critical path
        # print(f"{indent}⚠️ Reached maximum recursion depth ({MAX_DEPTH}) for @{username}, stopping further exploration.")
        return

    user_id = known_user_id
    if user_id is None:
        # get_user_id might also need to be async if it makes network calls
        user_id = get_user_id(username) # Assume get_user_id is blocking for now

    if not user_id:
        print(f"{indent}⚠️ Could not get user ID for @{username}. Skipping this user.")
        return

    if user_id in visited_users:
        # Suppress this message for cleaner output
        # print(f"{indent}🔁 Already visited @{username} (ID: {user_id}), skipping to avoid loops.")
        return

    visited_users.add(user_id)
    print(f"{indent}🔎 Searching chains of @{username} (ID: {user_id})... [Depth: {depth}]")

    users_in_chain = await fetch_chain_async(user_id)

    if not users_in_chain:
        print(f"{indent}🤷 No users found in chain for @{username} or failed to fetch suggestions.")
        return

    # --- Reduced output for individual users in chain ---
    # No longer printing each user by default, only matches or summary.
    # print(f"{indent}  Found {len(users_in_chain)} suggestions. Checking for keywords...")


    for user_data in users_in_chain:
        uname = user_data.get("username", "")
        fname = user_data.get("full_name", "")
        uid = user_data.get("id")

        if not uname or not uid:
            # Suppress this message for cleaner output
            # print(f"{indent}⚠️ Skipping user with missing username or ID: {user_data}")
            continue

        # Check for ALL provided keywords in the current user's data
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
                    # --- Prominent Match Output ---
                    print("\n" + "="*60)
                    print(f"🎯 FOUND MATCH for '{kw_to_check}'!")
                    print(f"   User: @{uname} - {fname}")
                    print(f"   ID: {uid}")
                    print(f"   Found via: @{username} (Depth {depth})")
                    print("="*60 + "\n")

    if depth < MAX_DEPTH:
        # Suppress this message for cleaner output
        # print(f"{indent}🔍 Exploring deeper chains from @{username}...")
        tasks = []
        for user_data in users_in_chain:
            # Random sleep for each recursive call to avoid overwhelming
            await asyncio.sleep(random.uniform(0.1, 0.2)) # Reduced sleep for speed
            tasks.append(
                recursive_chain_search_async(
                    user_data["username"],
                    keywords_to_match,
                    visited_users,
                    all_found_matches,
                    depth + 1,
                    known_user_id=user_data.get("id")
                )
            )
        await asyncio.gather(*tasks)
    # else:
        # Suppress this message for cleaner output
        # print(f"{indent}Maximum recursion depth reached for @{username}. Not going deeper.")
