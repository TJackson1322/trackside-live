
from dataclasses import dataclass, field
from datetime import date


@dataclass
class Driver:
    driver_id: str
    name: str
    car_number: str
    division: str
    transponder_id: str = ""


@dataclass
class Track:
    track_id: str
    name: str
    location: str


@dataclass
class Lap:
    driver_id: str
    lap_number: int
    seconds: float


@dataclass
class RaceSession:
    session_id: str
    track_id: str
    race_date: date
    division: str
    session_type: str
    laps_by_driver: dict = field(default_factory=dict)

    def add_lap(self, lap):
        if lap.lap_number < 1 or lap.seconds <= 0:
            raise ValueError("Invalid lap data")

        laps = self.laps_by_driver.setdefault(
            lap.driver_id, []
        )
        if laps and lap.lap_number <= laps[-1].lap_number:
            raise ValueError("Lap numbers must increase")

        laps.append(lap)

    def best_lap(self, driver_id):
        laps = self.laps_by_driver.get(driver_id, [])
        if not laps:
            return None
        return min(lap.seconds for lap in laps)


@dataclass
class SetupNote:
    owner_id: str
    session_id: str
    air_temp_f: float | None = None
    track_temp_f: float | None = None
    tire_psi_before: dict = field(default_factory=dict)
    tire_psi_after: dict = field(default_factory=dict)
    notes: str = ""
