"""Reproduce Phase 2/3 timing and Python-allocation comparisons.

Run from repository root with python3 coursework/benchmark_phase3.py.
Inputs are fictional. CSV and environment metadata go to coursework/phase3_results.
Timing uses five trials, alternating algorithm order, and reports raw samples.
Memory is measured separately with tracemalloc, excluding prebuilt input records.
"""

import csv
import gc
import json
import platform
import random
import statistics
import sys
import time
import tracemalloc
from pathlib import Path

from phase1_data_structures import Driver
from phase2_poc import RaceSession
from phase3_optimized import OptimizedRaceSession

RESULTS = Path(__file__).parent / "phase3_results"
CLASSES = {"Phase 2": RaceSession, "Phase 3": OptimizedRaceSession}
CONFIGS = [(100, 1000), (1000, 10000), (10000, 100000), (1000, 100000), (1000, 500000)]


def dataset(drivers, laps):
    rng = random.Random(2026 + drivers + laps)
    ids = [f"d{i:05}" for i in range(drivers)]
    people = [Driver(driver_id, f"Demo {i}", str(i)) for i, driver_id in enumerate(ids)]
    # Each driver appears at least once. Quantized times deliberately create ties.
    events = [(ids[i % drivers], rng.randrange(15000, 25001) / 1000) for i in range(laps)]
    best = {}
    for driver_id, seconds in events:
        best[driver_id] = min(seconds, best.get(driver_id, seconds))
    expected = sorted((seconds, driver_id) for driver_id, seconds in best.items())
    return people, events, expected


def populate(cls, people, events):
    session = cls()
    for driver in people:
        session.register_driver(driver)
    for driver_id, seconds in events:
        session.record_lap(driver_id, seconds)
    return session


def measured(cls, people, events, expected):
    gc.collect()
    start = time.perf_counter_ns()
    session = populate(cls, people, events)
    ingest_ms = (time.perf_counter_ns() - start) / 1e6

    start = time.perf_counter_ns()
    rankings = session.rankings()
    first_read_ms = (time.perf_counter_ns() - start) / 1e6
    assert rankings == expected
    assert session.fastest_lap() == expected[0]

    # Both sessions are fully populated and have served one initial ranking.
    start = time.perf_counter_ns()
    for _ in range(100):
        session.rankings()
    warm_100_ms = (time.perf_counter_ns() - start) / 1e6
    return ingest_ms, first_read_ms, warm_100_ms


def memory(cls, people, events, expected):
    gc.collect()
    tracemalloc.start()
    try:
        session = populate(cls, people, events)
        assert session.rankings() == expected
        current, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    # This measures additional Python allocations including cache materialization.
    # It excludes existing input objects and does not measure total process RSS.
    return current / 1048576, peak / 1048576


def write_csv(name, rows):
    with (RESULTS / name).open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    RESULTS.mkdir(exist_ok=True)
    metadata = {
        "python": sys.version, "platform": platform.platform(),
        "machine": platform.machine(), "processor": platform.processor(),
        "timing_trials": 5, "memory_trials": 1, "warm_rankings_per_trial": 100,
        "baseline_commit": "76fdb1a2d46c5cf97004c5778847146f621ef5a8",
        "measurement_location": "Assistant execution environment",
        "memory_scope": "tracemalloc additional Python allocations excluding prebuilt input",
    }
    (RESULTS / "environment.json").write_text(json.dumps(metadata, indent=2) + "\n")
    raw = []
    summaries = []
    for drivers, laps in CONFIGS:
        people, events, expected = dataset(drivers, laps)
        for trial in range(5):
            names = list(CLASSES)
            if trial % 2:
                names.reverse()
            for name in names:
                ingest, cold, warm = measured(CLASSES[name], people, events, expected)
                raw.append(dict(drivers=drivers, laps=laps, version=name, trial=trial + 1,
                                ingest_ms=ingest, first_read_ms=cold, warm_100_ms=warm))
        for name, cls in CLASSES.items():
            samples = [row for row in raw if row["drivers"] == drivers and
                       row["laps"] == laps and row["version"] == name]
            current, peak = memory(cls, people, events, expected)
            summary = dict(drivers=drivers, laps=laps, version=name)
            for metric in ("ingest_ms", "first_read_ms", "warm_100_ms"):
                values = [row[metric] for row in samples]
                summary[metric + "_median"] = statistics.median(values)
                summary[metric + "_min"] = min(values)
                summary[metric + "_max"] = max(values)
            summary["retained_mib"] = current
            summary["peak_mib"] = peak
            summaries.append(summary)
        print(f"Verified {drivers:,} drivers / {laps:,} laps", flush=True)
    write_csv("raw_timings.csv", raw)
    write_csv("summary.csv", summaries)
    print("Saved measured results to", RESULTS)


if __name__ == "__main__":
    main()
