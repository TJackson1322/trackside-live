"""Create the report graph from measured CSV using 12-point Times New Roman."""

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path(__file__).parent / "phase3_results"


def main():
    # Refresh available fonts so newly installed Times fonts are recognized.
    for font in font_manager.findSystemFonts():
        if Path(font).name.lower().startswith("times"):
            font_manager.fontManager.addfont(font)
    font_manager.findfont("Times New Roman", fallback_to_default=False)
    plt.rcParams.update({
        "font.family": "Times New Roman", "font.size": 12,
        "axes.titlesize": 12, "axes.labelsize": 12,
        "xtick.labelsize": 12, "ytick.labelsize": 12,
        "legend.fontsize": 12,
    })
    with (ROOT / "summary.csv").open() as source:
        rows = list(csv.DictReader(source))
    # The figure is inserted at this exact width so labels remain 12 points.
    fig, axes = plt.subplots(1, 2, figsize=(6.5, 3.0), layout="constrained")
    colors = {"Phase 2": "#555555", "Phase 3": "#176389"}
    for index, (version, color) in enumerate(colors.items()):
        scaled = [r for r in rows if r["version"] == version and
                  int(r["laps"]) == 10 * int(r["drivers"])]
        history = [r for r in rows if r["version"] == version and int(r["drivers"]) == 1000]
        positions = [x + (index - .5) * .34 for x in range(3)]
        axes[0].bar(positions, [float(r["warm_100_ms_median"]) for r in scaled],
                    width=.34, color=color, label=version)
        axes[1].bar(positions, [float(r["peak_mib"]) for r in history],
                    width=.34, color=color, label=version)
    axes[0].set_title("100 unchanged reads")
    axes[0].set_ylabel("Median milliseconds")
    axes[0].set_xlabel("Drivers (10 laps each)")
    axes[0].set_xticks(range(3), ["100", "1,000", "10,000"])
    axes[1].set_title("Long-session memory")
    axes[1].set_ylabel("Peak traced MiB")
    axes[1].set_xlabel("Laps (1,000 drivers)")
    axes[1].set_xticks(range(3), ["10k", "100k", "500k"])
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=.2)
        ax.set_axisbelow(True)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside upper center", ncol=2, frameon=False)
    fig.savefig(ROOT / "phase3_performance.png", dpi=220)
    plt.close(fig)


if __name__ == "__main__":
    main()
