# state_manager.py
import json
import os
from config import STATE_FILE_TEMPLATE, CUMULATIVE_RESULTS_DIR

def _get_state_filepath(username):
    """Generates a state file path for a given initial username."""
    safe_username = "".join(c for c in username if c.isalnum())
    return STATE_FILE_TEMPLATE.format(safe_username)

def load_search_state(initial_username):
    """
    Loads search state (visited users and all found matches) for a given initial username.
    Resumes if state matches, otherwise starts fresh.
    Returns (visited_users, all_found_matches).
    """
    visited_users = set()
    all_found_matches = []
    state_filepath = _get_state_filepath(initial_username)

    try:
        with open(state_filepath, "r", encoding="utf-8") as f:
            state = json.load(f)
            if state.get("initial_username") == initial_username:
                visited_users = set(state.get("visited", []))
                all_found_matches = state.get("found_matches", [])
                print(f"✅ Loaded previous state for '{initial_username}'. Resuming general search...")
                print(f"   Total visited users: {len(visited_users)}")
                print(f"   Total matches found so far: {len(all_found_matches)}")
            else:
                print(f"⚠️ Saved state found at {state_filepath} but for a different initial user. Starting fresh.")

    except FileNotFoundError:
        print(f"ℹ️ No previous search state found at {state_filepath}. Starting fresh for '{initial_username}'.")
    except json.JSONDecodeError:
        print(f"⚠️ Corrupted state file detected at {state_filepath}. Starting fresh.")
        try:
            os.remove(state_filepath)
            print(f"   Removed corrupted state file: {state_filepath}")
        except OSError as e:
            print(f"   Could not remove corrupted state file: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred while loading state from {state_filepath}: {e}. Starting fresh.")

    return visited_users, all_found_matches

def save_search_state(initial_username, visited_users, all_found_matches):
    """Saves the current overall search state."""
    state_filepath = _get_state_filepath(initial_username)
    state = {
        "visited": list(visited_users),
        "found_matches": all_found_matches,
        "initial_username": initial_username
    }
    try:
        with open(state_filepath, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=4, ensure_ascii=False)
        print(f"\n💾 Search state saved to {state_filepath}")
    except Exception as e:
        print(f"❌ Error saving state to {state_filepath}: {e}")

def save_cumulative_results_for_keyword(keyword, all_matches_data):
    """
    Filters and saves matches relevant to a specific keyword
    to its dedicated JSON file within the 'results' directory.
    """
    keyword_matches = [m for m in all_matches_data if m.get("matched_keyword") == keyword]
    if not keyword_matches:
        print(f"ℹ️ No matches found for keyword '{keyword}'. Skipping saving.")
        return

    folder = os.path.join(CUMULATIVE_RESULTS_DIR, keyword.lower())
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, f"{keyword.lower()}_matches.json")

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(keyword_matches, f, indent=4, ensure_ascii=False)
        print(f"✅ Matches for '{keyword}' saved to {filepath}")
    except Exception as e:
        print(f"❌ Error saving cumulative results for '{keyword}' to {filepath}: {e}")

