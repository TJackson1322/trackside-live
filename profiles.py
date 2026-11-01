
"""TrackSide Live - Driver Profile System."""

import json
from pathlib import Path


DATA_FILE = Path(__file__).with_name("drivers.json")


class DriverProfiles:
    def __init__(self):
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        self.drivers = {
            driver["driver_id"]: driver
            for driver in data["drivers"]
        }

    def show_all_drivers(self):
        print("\n🏁 TRACKSIDE LIVE - DRIVER PROFILES")
        print("-" * 45)

        for driver in self.drivers.values():
            print(
                f"#{driver['car_number']} "
                f"{driver['name']}"
            )
            print(
                f"Division: {', '.join(driver['divisions'])}"
            )
            print("-" * 45)

    def show_profile(self, driver_id):
        driver = self.drivers.get(driver_id)

        if driver is None:
            print("Driver not found.")
            return

        print(f"\n🏎️ {driver['name']}")
        print(f"Car Number: #{driver['car_number']}")
        print(f"Divisions: {', '.join(driver['divisions'])}")
        print(f"Photo: {driver['profile_photo']}")

        achievements = driver["achievements"]

        if achievements:
            print("\n🏆 Career Achievements:")
            for achievement in achievements:
                print(
                    f"{achievement['year']} - "
                    f"{achievement['title']}"
                )
                print(achievement["location"])

        else:
            print("\nCareer achievements coming soon!")


if __name__ == "__main__":
    profiles = DriverProfiles()

    profiles.show_all_drivers()

    profiles.show_profile("chase-bohanon-88")
