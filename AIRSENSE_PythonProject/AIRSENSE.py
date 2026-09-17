#AIRSENSE: PM2.5 Air Pollution Monitoring & Analysis System

import json
import os
from datetime import datetime

import requests

# GPS coordinates of University of Mindanao - Matina Campus, Davao City
UM_MATINA_LATITUDE = 7.0665
UM_MATINA_LONGITUDE = 125.5968

# Open-Meteo Air Quality API endpoint (no API key required)
AIR_QUALITY_API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

# File used to save/load records (data persistence)
RECORDS_FILE = "airsense_records.json"

# Monitored locations/buildings within UM Matina Campus.
# Edit this list to match the actual building names of your campus map.
CAMPUS_LOCATIONS = [
    "Bulwagan ng Katilingban (Main Building)",
    "College of Engineering Building",
    "College of Computing Education (CCE) Building",
    "College of Nursing Building",
    "College of Arts and Sciences (CAS) Building",
    "University Gymnasium",
    "Learning Resource Center / Library",
    "Canteen / Food Court",
    "Parking Area / Main Gate",
]

# PM2.5 health classification breakpoints (micrograms per cubic meter, ug/m3)
# Based on the US EPA PM2.5 Air Quality Index breakpoints.
PM25_BREAKPOINTS = [
    (0.0, 12.0, "Good", "Air quality is satisfactory; poses little or no risk."),
    (12.1, 35.4, "Moderate", "Acceptable air quality; unusually sensitive people should consider reducing prolonged outdoor exertion."),
    (35.5, 55.4, "Unhealthy for Sensitive Groups", "Sensitive groups (children, elderly, asthmatics) may experience health effects."),
    (55.5, 150.4, "Unhealthy", "Everyone may begin to experience health effects; sensitive groups may experience more serious effects."),
    (150.5, 250.4, "Very Unhealthy", "Health alert: everyone may experience more serious health effects."),
    (250.5, 500.4, "Hazardous", "Health warning of emergency conditions; entire population is more likely to be affected."),
]

# DATA STRUCTURES
# records: a LIST of DICTIONARIES.
# Each record (dictionary) has the following keys:
#   id         -> unique integer ID for the record
#   location   -> name of the building/area monitored (string)
#   pm25       -> PM2.5 concentration in ug/m3 (float)
#   category   -> health classification, e.g. "Moderate" (string)
#   advisory   -> short health advice (string)
#   timestamp  -> when the reading was taken/logged (string)
records = []

# API FUNCTION
def fetch_pm25_from_api():
    """
    Calls the Open-Meteo Air Quality API for UM Matina Campus's
    coordinates and returns the current PM2.5 value (ug/m3).

    Returns:
        float: current PM2.5 concentration.

    Raises:
        ConnectionError, TimeoutError, ValueError -- handled by caller.
    """
    params = {
        "latitude": UM_MATINA_LATITUDE,
        "longitude": UM_MATINA_LONGITUDE,
        "current": "pm2_5",
        "timezone": "Asia/Manila",
    }

    response = requests.get(AIR_QUALITY_API_URL, params=params, timeout=10)
    response.raise_for_status()  # raises HTTPError for bad status codes

    data = response.json()
    pm25_value = data["current"]["pm2_5"]

    if pm25_value is None:
        raise ValueError("API returned no PM2.5 data at this time.")

    return float(pm25_value)


def classify_pm25(pm25_value):
    """
    Classifies a PM2.5 value into a health category using
    PM25_BREAKPOINTS.

    Returns:
        (category, advisory) tuple of strings.
    """
    for low, high, category, advisory in PM25_BREAKPOINTS:
        if low <= pm25_value <= high:
            return category, advisory
    # Value is above the highest defined breakpoint
    return "Hazardous", "Health warning of emergency conditions."

# FILE HANDLING (SAVE / LOAD)
def load_records():
    """
    Loads saved records from RECORDS_FILE into the global `records`
    list when the program starts. Uses try/except to handle a
    missing or corrupted file gracefully.
    """
    global records
    try:
        with open(RECORDS_FILE, "r") as file:
            records = json.load(file)
        print(f"[INFO] Loaded {len(records)} saved record(s) from '{RECORDS_FILE}'.")
    except FileNotFoundError:
        print("[INFO] No saved records found. Starting with an empty log.")
        records = []
    except json.JSONDecodeError:
        print("[WARNING] Saved file was unreadable/corrupted. Starting with an empty log.")
        records = []


def save_records():
    """
    Saves the current `records` list to RECORDS_FILE in JSON format.
    Called automatically after every add/update so data is never lost.
    """
    try:
        with open(RECORDS_FILE, "w") as file:
            json.dump(records, file, indent=4)
    except OSError as error:
        print(f"[ERROR] Could not save records to file: {error}")

# CORE FEATURES
def choose_location():
    """Displays the list of campus locations and returns the chosen one."""
    print("\nSelect a location at UM Matina Campus:")
    for index, location in enumerate(CAMPUS_LOCATIONS, start=1):
        print(f"  {index}. {location}")

    while True:
        choice = input("Enter location number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(CAMPUS_LOCATIONS):
            return CAMPUS_LOCATIONS[int(choice) - 1]
        print("Invalid choice. Please enter a valid number from the list.")

def add_record():
    """
    ADD PRODUCT RECORD (equivalent feature):
    Fetches a live PM2.5 reading from the API for a chosen building,
    classifies it, and appends it to `records`. Saves to file right after.
    """
    print("\n--- ADD NEW AIR QUALITY RECORD ---")
    location = choose_location()

    print(f"Fetching live PM2.5 data for UM Matina Campus ({location})...")
    try:
        pm25_value = fetch_pm25_from_api()
    except requests.exceptions.ConnectionError:
        print("[ERROR] No internet connection. Could not reach the air quality API.")
        return
    except requests.exceptions.Timeout:
        print("[ERROR] The API took too long to respond. Please try again.")
        return
    except requests.exceptions.HTTPError as error:
        print(f"[ERROR] The API returned an error: {error}")
        return
    except (KeyError, ValueError) as error:
        print(f"[ERROR] Unexpected API response: {error}")
        return

    category, advisory = classify_pm25(pm25_value)
    timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")

    new_id = (records[-1]["id"] + 1) if records else 1
    new_record = {
        "id": new_id,
        "location": location,
        "pm25": round(pm25_value, 2),
        "category": category,
        "advisory": advisory,
        "timestamp": timestamp,
    }
    records.append(new_record)
    save_records()

    print("\n[SUCCESS] Record added and saved:")
    print_record(new_record)


def view_records():
    """
    VIEW EXISTING PRODUCTS (equivalent feature):
    Displays every saved air quality record in a readable table.
    """
    print("\n--- ALL AIR QUALITY RECORDS (UM MATINA CAMPUS) ---")
    if not records:
        print("No records found yet. Use 'Add Record' first.")
        return

    header = f"{'ID':<4}{'Location':<40}{'PM2.5':<10}{'Category':<32}{'Logged At':<20}"
    print(header)
    print("-" * len(header))
    for record in records:
        print(
            f"{record['id']:<4}"
            f"{record['location']:<40}"
            f"{record['pm25']:<10}"
            f"{record['category']:<32}"
            f"{record['timestamp']:<20}"
        )

def search_records():
    """
    SEARCH FOR A PRODUCT (equivalent feature):
    Lets the user search saved records by building/location name
    or by health category (e.g. "Moderate", "Unhealthy").
    """
    print("\n--- SEARCH RECORDS ---")
    if not records:
        print("No records found yet. Use 'Add Record' first.")
        return

    keyword = input("Enter a location name or category keyword to search: ").strip().lower()
    if not keyword:
        print("[ERROR] Search keyword cannot be empty.")
        return

    results = [
        record for record in records
        if keyword in record["location"].lower() or keyword in record["category"].lower()
    ]

    if not results:
        print(f"No records matched '{keyword}'.")
        return

    print(f"\nFound {len(results)} matching record(s):")
    for record in results:
        print_record(record)

def update_record():
    """
    UPDATE PRODUCT INFORMATION (equivalent feature):
    Lets the user pick a record by ID and either:
      1. Re-fetch a fresh PM2.5 reading from the API for it, or
      2. Manually change which building/location it belongs to.
    """
    print("\n--- UPDATE A RECORD ---")
    if not records:
        print("No records found yet. Use 'Add Record' first.")
        return

    view_records()
    record_id_input = input("\nEnter the ID of the record to update: ").strip()

    if not record_id_input.isdigit():
        print("[ERROR] Please enter a valid numeric ID.")
        return

    record_id = int(record_id_input)
    target = next((record for record in records if record["id"] == record_id), None)

    if target is None:
        print(f"[ERROR] No record found with ID {record_id}.")
        return

    print("\nWhat would you like to update?")
    print("  1. Refresh PM2.5 reading from the API")
    print("  2. Change the building/location")
    sub_choice = input("Enter choice (1 or 2): ").strip()

    if sub_choice == "1":
        print("Fetching a fresh reading...")
        try:
            pm25_value = fetch_pm25_from_api()
        except (requests.exceptions.RequestException, KeyError, ValueError) as error:
            print(f"[ERROR] Could not refresh reading: {error}")
            return
        category, advisory = classify_pm25(pm25_value)
        target["pm25"] = round(pm25_value, 2)
        target["category"] = category
        target["advisory"] = advisory
        target["timestamp"] = datetime.now().strftime("%Y-%m-%d %I:%M %p")

    elif sub_choice == "2":
        new_location = choose_location()
        target["location"] = new_location

    else:
        print("[ERROR] Invalid choice.")
        return

    save_records()
    print("\n[SUCCESS] Record updated and saved:")
    print_record(target)

def print_record(record):
    """Utility function: neatly prints a single record."""
    print(
        f"  ID {record['id']} | {record['location']}\n"
        f"    PM2.5: {record['pm25']} ug/m3  |  Category: {record['category']}\n"
        f"    Advisory: {record['advisory']}\n"
        f"    Logged at: {record['timestamp']}"
    )

# MAIN MENU / PROGRAM FLOW
def display_menu():
    print("\n" + "=" * 60)
    print(" AIRSENSE: PM2.5 Monitoring - University of Mindanao (Matina)")
    print("=" * 60)
    print("  1. Add Air Quality Record   (fetch live PM2.5 from API)")
    print("  2. View All Records")
    print("  3. Search Records")
    print("  4. Update a Record")
    print("  5. Exit")

def main():
    print("Starting AIRSENSE...")
    load_records()

    while True:
        display_menu()
        choice = input("Select an option (1-5): ").strip()

        if choice == "1":
            add_record()
        elif choice == "2":
            view_records()
        elif choice == "3":
            search_records()
        elif choice == "4":
            update_record()
        elif choice == "5":
            print("Saving records and exiting AIRSENSE. Goodbye!")
            save_records()
            break
        else:
            print("[ERROR] Invalid option. Please choose a number from 1 to 5.")

if __name__ == "__main__":
    main()