# main.py (Modified for Async - clarity on depth)
import signal
import sys
import asyncio

from cli_interface import initialize_search_environment, get_user_inputs
from state_manager import load_search_state, save_search_state, save_cumulative_results_for_keyword
from search_logic import recursive_chain_search_async
from instagram_api import init_async_client, close_async_client
from config import MAX_DEPTH # Import MAX_DEPTH for printing

# Global variables for state management (needed for signal handler)
current_visited_users = set()
current_all_found_matches = []
initial_target_username_global = ""
search_keywords_global = []

# Modified signal handler to properly manage async client shutdown
def signal_handler(sig, frame):
    """Handles Ctrl+C to gracefully save overall state and exit."""
    print("\n🛑 Ctrl+C detected. Saving current state and exiting gracefully...")
    # Run a synchronous cleanup function
    asyncio.create_task(cleanup_on_exit())
    sys.exit(0)

async def cleanup_on_exit():
    """Performs final state and result saving, and closes async client."""
    print("\n--- Finalizing search results and state ---")
    save_search_state(initial_target_username_global, current_visited_users, current_all_found_matches)
    for kw in search_keywords_global:
        save_cumulative_results_for_keyword(kw, current_all_found_matches)
    await close_async_client() # Close the async client
    print("✨ Script finished.")


# Re-register signal handler
signal.signal(signal.SIGINT, signal_handler)

async def run_search_async():
    global current_visited_users, current_all_found_matches, initial_target_username_global, search_keywords_global

    initialize_search_environment()
    initial_target_username, search_keywords = get_user_inputs()

    initial_target_username_global = initial_target_username
    search_keywords_global = search_keywords

    current_visited_users, current_all_found_matches = load_search_state(initial_target_username)

    await init_async_client() # Initialize the async client at the start

    try:
        print(f"\nStarting general search from @{initial_target_username} for keywords: {', '.join(search_keywords)}...")
        # Clarify MAX_DEPTH to the user
        print(f"Search will explore up to {MAX_DEPTH} level(s) deep into suggested user chains.")
        await recursive_chain_search_async(
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
        # Cleanup will be handled by the signal handler or the main process if no error
        # For normal completion, call cleanup_on_exit directly
        if not sys.exc_info()[0]: # Check if an exception occurred
            await cleanup_on_exit()

if __name__ == "__main__":
    asyncio.run(run_search_async())
