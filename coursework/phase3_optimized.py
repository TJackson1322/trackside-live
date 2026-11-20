"""TrackSide Live Phase 3 standings summary.

The public Phase 2 lookup, registration, lap, and ranking methods are preserved.
This session keeps personal bests and the session minimum. It does not retain
individual lap history. Use separate persistent storage if an audit is needed.
"""

from math import isfinite

from phase1_data_structures import Driver, DriverIndex, LeaderboardAVL


class OptimizedRaceSession:
    """Maintain standings using O(D) session state for D registered drivers."""

    def __init__(self) -> None:
        self._drivers = DriverIndex()
        self._leaderboard = LeaderboardAVL()
        self._fastest: tuple[float, str] | None = None
        self._rankings_cache: tuple[tuple[float, str], ...] | None = None

    def register_driver(self, driver: Driver) -> None:
        if not driver.driver_id.strip():
            raise ValueError("Driver ID is required")
        if self.find_driver(driver.driver_id) is not None:
            raise ValueError(f"Driver already registered: {driver.driver_id}")
        self._drivers.add(driver)

    def find_driver(self, driver_id: str) -> Driver | None:
        return self._drivers.find(driver_id)

    def record_lap(self, driver_id: str, seconds: float) -> None:
        # Validate before changing any session results.
        if self.find_driver(driver_id) is None:
            raise ValueError(f"Unknown driver: {driver_id}")
        if not isfinite(seconds) or seconds <= 0:
            raise ValueError("Lap time must be finite and positive")

        previous = self._leaderboard.best_time(driver_id)
        if previous is not None and seconds >= previous:
            # A slower or equal lap cannot change best-lap standings.
            return

        self._leaderboard.update(driver_id, seconds)
        # Only a first or faster lap invalidates the saved standings.
        self._rankings_cache = None
        candidate = (seconds, driver_id)
        # Compare the whole tuple to preserve the Phase 2 driver-ID tie rule.
        if self._fastest is None or candidate < self._fastest:
            self._fastest = candidate

    def fastest_lap(self) -> tuple[float, str] | None:
        return self._fastest

    def rankings(self) -> list[tuple[float, str]]:
        if self._rankings_cache is None:
            self._rankings_cache = tuple(self._leaderboard.rankings())
        # Return a fresh list so a caller cannot modify our cached state.
        # This copy is still O(D), even when tree traversal is avoided.
        return list(self._rankings_cache)


def main() -> None:
    session = OptimizedRaceSession()
    session.register_driver(Driver("d1", "Demo Racer One", "07"))
    session.register_driver(Driver("d2", "Demo Racer Two", "88"))
    for driver_id, seconds in [("d1", 17.45), ("d2", 17.21), ("d2", 17.80)]:
        session.record_lap(driver_id, seconds)
    print("Driver lookup:", session.find_driver("d1"))
    print("Fastest lap:", session.fastest_lap())
    print("Leaderboard:", session.rankings())


if __name__ == "__main__":
    main()
