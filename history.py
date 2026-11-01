
"""TrackSide Live: Historical race lookup."""

from datetime import date
from models import RaceSession, Lap


class RaceHistory:
    def __init__(self):
        # Key: (driver ID, track ID, race date)
        self.records = {}

    def add_session(self, session):
        for driver_id in session.laps_by_driver:
            key = (
                driver_id,
                session.track_id,
                session.race_date,
            )
            self.records.setdefault(key, []).append(session)

    def find_races(self, driver_id, track_id, race_date):
        key = (driver_id, track_id, race_date)
        return self.records.get(key, [])

    def show_history(self, driver_id, track_id, race_date):
        sessions = self.find_races(
            driver_id, track_id, race_date
        )

        if not sessions:
            print("No race history found.")
            return

        for session in sessions:
            print(f"\nSession: {session.session_type}")

            laps = session.laps_by_driver[driver_id]

            for lap in laps:
                print(
                    f"Lap {lap.lap_number}: "
                    f"{lap.seconds:.3f} seconds"
                )

            print(
                f"Best lap: "
                f"{session.best_lap(driver_id):.3f} seconds"
            )


if __name__ == "__main__":
    history = RaceHistory()

    # Fictional demonstration race
    race = RaceSession(
        session_id="SALEM-2025-001",
        track_id="salem",
        race_date=date(2025, 10, 6),
        division="Legends",
        session_type="Feature Race",
    )

    race.add_lap(Lap("driver07", 1, 19.120))
    race.add_lap(Lap("driver07", 2, 18.850))
    race.add_lap(Lap("driver07", 3, 18.430))
    race.add_lap(Lap("driver07", 4, 18.210))

    history.add_session(race)

    history.show_history(
        "driver07",
        "salem",
        date(2025, 10, 6),
    )
