# AIRSENSE: PM2.5 Air Pollution Monitoring System
import requests

UM_MATINA_LATITUDE = 7.0665
UM_MATINA_LONGITUDE = 125.5968

AIR_QUALITY_API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

CAMPUS_LOCATIONS = [
    "Bulwagan ng Katilingban (Main Building)",
    "College of Engineering Building",
    "College of Computing Education (CCE) Building",
    "College of Nursing Building",
    "College of Arts and Sciences (CAS) Building",
    "University Gymnasium",
    "Learning Resource Center / Library",
    "Canteen / Food Court",
    "Parking Area / Main Gate"
]

print("=" * 60)
print("       AIRSENSE: PM2.5 AIR QUALITY MONITOR")
print("       University of Mindanao - Matina Campus")
print("=" * 60)

print("\nSelect a campus location:")

for index, location in enumerate(CAMPUS_LOCATIONS, start=1):
    print(f"{index}. {location}")

while True:
    choice = input("\nEnter location number (1-9): ").strip()

    if choice.isdigit():
        choice = int(choice)

        if 1 <= choice <= len(CAMPUS_LOCATIONS):
            selected_location = CAMPUS_LOCATIONS[choice - 1]
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 9.")
    else:
        print("Invalid input. Please enter a number.")

print(f"\nSelected Location: {selected_location}")
print("Fetching current PM2.5 data...")

try:
    parameters = {
        "latitude": UM_MATINA_LATITUDE,
        "longitude": UM_MATINA_LONGITUDE,
        "current": "pm2_5",
        "timezone": "Asia/Manila"
    }

    response = requests.get(
        AIR_QUALITY_API_URL,
        params=parameters,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    pm25 = data["current"]["pm2_5"]

    # sa API para i check if nag return ba value
    if pm25 is None:
        print("\nNo PM2.5 data is currently available.")

    else:
        pm25 = float(pm25)

        if pm25 <= 12.0:
            category = "Good"
            advisory = "Air quality is satisfactory."

        elif pm25 <= 35.4:
            category = "Moderate"
            advisory = "Air quality is acceptable."

        elif pm25 <= 55.4:
            category = "Unhealthy for Sensitive Groups"
            advisory = "Sensitive individuals should take caution."

        elif pm25 <= 150.4:
            category = "Unhealthy"
            advisory = "Health effects may occur."

        elif pm25 <= 250.4:
            category = "Very Unhealthy"
            advisory = "Health alert: reduce exposure."

        else:
            category = "Hazardous"
            advisory = "Health warning: avoid exposure."

        print("\n" + "=" * 60)
        print("              AIR QUALITY RESULT")
        print("=" * 60)
        print(f"Location : {selected_location}")
        print(f"PM2.5    : {pm25:.2f} µg/m³")
        print(f"Category : {category}")
        print(f"Advisory : {advisory}")
        print("=" * 60)

except requests.exceptions.ConnectionError:
    print("\nERROR: No internet connection.")

except requests.exceptions.Timeout:
    print("\nERROR: The API request timed out.")

except requests.exceptions.RequestException as error:
    print(f"\nERROR: Unable to retrieve air quality data.")
    print(f"Details: {error}")

except (KeyError, ValueError):
    print("\nERROR: The API returned unexpected data.")
