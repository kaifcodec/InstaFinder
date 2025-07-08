# cli_interface.py
import os
import sys
from config import CUMULATIVE_RESULTS_DIR

def initialize_search_environment():
    """Initializes the necessary directories."""
    os.makedirs(CUMULATIVE_RESULTS_DIR, exist_ok=True)

def get_user_inputs():
    """Prompts the user for initial username and search keywords."""
    print("--- Instagram Chain Search ---")
    print("This script searches for keywords within Instagram's suggested user chains.")
    print("To search for users likely known by a specific 'victim', enter their username.")
    print("Do NOT enter your own username if you wish to avoid searching your personal network.")

    initial_target_username = input("\nEnter Instagram username to start searching from (e.g., the 'victim'): ").strip()
    keywords_input = input("Enter keywords/names to search in suggestions (comma-separated, e.g., 'tech, john doe, coding'): ").strip()
    search_keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]

    if not search_keywords:
        print("❌ No keywords provided. Exiting.")
        sys.exit(1)
    if not initial_target_username:
        print("❌ No initial username provided. Exiting.")
        sys.exit(1)

    return initial_target_username, search_keywords
