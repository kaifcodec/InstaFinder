# headers_loader.py
import json
import sys
from config import HEADERS_FILE

def load_headers():
    """
    Loads headers from the specified HEADERS_FILE.
    Exits if the file is not found or is corrupted.
    """
    try:
        with open(HEADERS_FILE, "r", encoding="utf-8") as header_file:
            headers = json.load(header_file)
            return headers
    except FileNotFoundError:
        print(f"Error: {HEADERS_FILE} not found. Please run the header generation script first.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not parse {HEADERS_FILE}. Ensure it's valid JSON.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while loading headers: {e}")
        sys.exit(1)
