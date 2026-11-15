"""TrackSide Live proof of concept for one race session."""

from math import isfinite

from phase1_data_structures import Driver, DriverIndex, FastestLaps, LeaderboardAVL


class RaceSession:
    """Track every valid lap and rank each driver by their personal best."""

    def __init__(self) -> None:
        self._drivers = DriverIndex()
        self._laps = FastestLaps()
        self._leaderboard = LeaderboardAVL()

    def register_driver(self, driver: Driver) -> None:
        if not driver.driver_id.strip():
            raise ValueError("Driver ID is required")
        if self.find_driver(driver.driver_id) is not None:
            raise ValueError(f"Driver already registered: {driver.driver_id}")
        self._drivers.add(driver)

    def find_driver(self, driver_id: str) -> Driver | None:
        return self._drivers.find(driver_id)

    def record_lap(self, driver_id: str, seconds: float) -> None:
        if self.find_driver(driver_id) is None:
            raise ValueError(f"Unknown driver: {driver_id}")
        if not isfinite(seconds) or seconds <= 0:
            raise ValueError("Lap time must be finite and positive")

        self._laps.add(driver_id, seconds)
        previous = self._leaderboard.best_time(driver_id)
        if previous is None or seconds < previous:
            self._leaderboard.update(driver_id, seconds)

    def fastest_lap(self) -> tuple[float, str] | None:
        return self._laps.fastest()

    def rankings(self) -> list[tuple[float, str]]:
        return self._leaderboard.rankings()


def main() -> None:
    session = RaceSession()
    session.register_driver(Driver("d1", "Demo Racer One", "07"))
    session.register_driver(Driver("d2", "Demo Racer Two", "88"))
    print("Driver lookup:", session.find_driver("d1"))
    for driver_id, seconds in [("d1", 17.45), ("d2", 17.21), ("d2", 17.80)]:
        session.record_lap(driver_id, seconds)
        print(f"Recorded lap for {driver_id}: {seconds:.2f} seconds")

    print("Fastest lap:", session.fastest_lap())
    print("Leaderboard (personal bests):")
    for position, (seconds, driver_id) in enumerate(session.rankings(), start=1):
        print(f"{position}. {driver_id} — {seconds:.2f} seconds")


if __name__ == "__main__":
    main()
