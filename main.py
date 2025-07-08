# main.py
import signal
import sys
import os # Keep os for os.makedirs, or move it to cli_interface.py init
import time # For the random sleep, which might be in search_logic now

from cli_interface import initialize_search_environment, get_user_inputs
from state_manager import load_search_state, save_search_state, save_cumulative_results_for_keyword
from search_logic import recursive_chain_search
from config import CUMULATIVE_RESULTS_DIR # For the signal handler to access

# Global variables to manage the search state across all keyword searches for a given target.
current_visited_users = set()
current_all_found_matches = []
initial_target_username_global = ""
search_keywords_global = [] # To be populated by get_user_inputs

def signal_handler(sig, frame):
    """Handles Ctrl+C to gracefully save overall state before exiting."""
    print("\n🛑 Ctrl+C detected. Saving current state and exiting gracefully...")
    save_search_state(initial_target_username_global, current_visited_users, current_all_found_matches)
    for kw in search_keywords_global:
        save_cumulative_results_for_keyword(kw, current_all_found_matches)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def run_search():
    global current_visited_users, current_all_found_matches, initial_target_username_global, search_keywords_global

    initialize_search_environment()
    initial_target_username, search_keywords = get_user_inputs()

    initial_target_username_global = initial_target_username # Set global for signal handler
    search_keywords_global = search_keywords # Set global for signal handler

    current_visited_users, current_all_found_matches = load_search_state(initial_target_username)

    try:
        print(f"\nStarting general search from @{initial_target_username} for keywords: {', '.join(search_keywords)}...")
        recursive_chain_search(
            initial_target_username,
            search_keywords,
            current_visited_users,
            current_all_found_matches,
            depth=0
        )
        print("\n🎉 Overall search completed successfully (or exhausted all accessible paths).")
    except Exception as e:
        print(f"\n🚨 An unhandled error occurred during search: {e}")
    finally:
        print("\n--- Finalizing search results and state ---")
        save_search_state(initial_target_username, current_visited_users, current_all_found_matches)
        for kw in search_keywords:
            save_cumulative_results_for_keyword(kw, current_all_found_matches)
        print("✨ Script finished.")

if __name__ == "__main__":
    run_search()
