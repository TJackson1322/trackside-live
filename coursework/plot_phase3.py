"""Create the report graph from the measured CSV (requires matplotlib)."""

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).parent / "phase3_results"


def main():
    with (ROOT / "summary.csv").open() as source:
        rows = list(csv.DictReader(source))
    fig, axes = plt.subplots(2, 2, figsize=(9, 5.0), constrained_layout=True)
    colors = {"Phase 2": "#555555", "Phase 3": "#176389"}
    for version, color in colors.items():
        scaled = [r for r in rows if r["version"] == version and
                  int(r["laps"]) == 10 * int(r["drivers"])]
        history = [r for r in rows if r["version"] == version and int(r["drivers"]) == 1000]
        drivers = [int(r["drivers"]) for r in scaled]
        axes[0, 0].plot(drivers, [float(r["ingest_ms_median"]) for r in scaled],
                        "o-", color=color, label=version)
        axes[0, 1].plot(drivers, [float(r["warm_100_ms_median"]) for r in scaled],
                        "o-", color=color, label=version)
        axes[1, 0].plot(drivers, [float(r["peak_mib"]) for r in scaled],
                        "o-", color=color, label=version)
        axes[1, 1].plot([int(r["laps"]) for r in history],
                        [float(r["peak_mib"]) for r in history],
                        "o-", color=color, label=version)
    labels = [
        ("Registration and lap recording", "Drivers (10 laps per driver)", "Median milliseconds"),
        ("100 unchanged leaderboard reads", "Drivers (10 laps per driver)", "Median milliseconds"),
        ("Peak traced allocations", "Drivers (10 laps per driver)", "MiB"),
        ("Longer session with 1,000 drivers", "Recorded laps", "Peak traced MiB"),
    ]
    for ax, (title, xlabel, ylabel) in zip(axes.flat, labels):
        ax.set_title(title, fontsize=10)
        ax.set_xlabel(xlabel, fontsize=9)
        ax.set_ylabel(ylabel, fontsize=9)
        ax.set_xscale("log")
        ax.tick_params(labelsize=8)
        ax.grid(alpha=.2)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(fontsize=8)
    fig.savefig(ROOT / "phase3_performance.png", dpi=220)
    plt.close(fig)


if __name__ == "__main__":
    main()
