"""Figures for the report from the CSV files of loadgen.py.

    python -m bench.plot latency results/phase2 --out results/figures/phase2
    python -m bench.plot timeline results/failover-lc/rate100_1.csv --stop 20 --start 40 --out results/figures/failover-lc
"""

import argparse
import collections
import csv
import glob
import os
import re

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter, LogLocator


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def latency_per_rate(directory):
    """{rate: [(mean, p99) of every run]}. Failed requests are left out."""
    runs = collections.defaultdict(list)
    for path in sorted(glob.glob(os.path.join(directory, "rate*_*.csv"))):
        rate = float(re.search(r"rate([\d.]+)_", os.path.basename(path)).group(1))
        latencies = np.array([float(r["latency_ms"]) for r in read_csv(path) if not r["error"]])
        runs[rate].append((latencies.mean(), np.percentile(latencies, 99)))
    return dict(sorted(runs.items()))


def plot_latency(directories, labels, out):
    """Every point is the median of the runs at that rate, the bar goes from the lowest to the highest run."""
    data = [latency_per_rate(d) for d in directories]
    for label, values in zip(labels, data):
        print(label)
        for rate, runs in values.items():
            means = ", ".join(f"{mean:.2f}" for mean, _ in runs)
            p99s = ", ".join(f"{p99:.2f}" for _, p99 in runs)
            print(f"  {rate:g} req/s: mean {np.median([r[0] for r in runs]):.2f} ms (runs: {means}), "
                  f"p99 {np.median([r[1] for r in runs]):.2f} ms (runs: {p99s})")

    for index, name, title in [(0, "mean", "Average execution latency"), (1, "p99", "99th-percentile execution latency")]:
        plt.figure(figsize=(4.5, 3))
        for i, (label, values) in enumerate(zip(labels, data)):
            runs = [np.array([run[index] for run in values[rate]]) for rate in values]
            median = np.array([np.median(r) for r in runs])
            low = median - np.array([r.min() for r in runs])
            high = np.array([r.max() for r in runs]) - median
            # shift the lines a little so their bars do not cover each other
            x = np.array(list(values)) + (i - (len(data) - 1) / 2) * 3
            plt.errorbar(x, median, yerr=[low, high], marker="o", markersize=4, capsize=3, label=label)
        # log scale, because an overloaded server is a hundred times slower than the other points
        plt.yscale("log")
        plt.gca().yaxis.set_major_locator(LogLocator(subs=(1, 2, 5)))  # 10, 20, 50, 100, ...
        plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:g}"))
        plt.xticks(list(data[0]))
        plt.xlabel("Keyword requests per second")
        plt.ylabel("Execution latency (ms)")
        plt.title(title)
        plt.grid(alpha=0.3)
        plt.grid(alpha=0.1, which="minor")
        if len(data) > 1:
            plt.legend()
        plt.tight_layout()
        plt.savefig(f"{out}_{name}.png", dpi=200)
        plt.close()


def plot_timeline(path, out, stop, start):
    """Requests answered per second by each server, and failed requests per second."""
    rows = read_csv(path)
    seconds = int(float(rows[-1]["time_s"])) + 1
    answered = collections.defaultdict(lambda: [0] * seconds)
    failed = [0] * seconds
    for r in rows:
        second = int(float(r["time_s"]))
        if r["error"]:
            failed[second] += 1
        else:
            answered[r["server"]][second] += 1

    if stop is not None and start is not None:
        for period, lo, hi in [("before", 0, stop), ("stopped", stop, start), ("after", start, seconds)]:
            part = [r for r in rows if lo <= float(r["time_s"]) < hi]
            counts = collections.Counter(r["server"] or "failed" for r in part)
            print(period, {k: f"{v / max(len(part), 1):.0%}" for k, v in sorted(counts.items())})

    plt.figure(figsize=(4.5, 3))
    for (server, counts), style in zip(sorted(answered.items()), ["-", "--", "-."]):
        plt.plot(range(seconds), counts, style, label=server)
    plt.plot(range(seconds), failed, "r:", linewidth=2, label="failed")
    for x in (stop, start):
        if x is not None:
            plt.axvline(x, color="gray", linewidth=0.8)
    plt.xlabel("Time since the start of the run (s)")
    plt.ylabel("Requests per second")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out + ".png", dpi=200)
    plt.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=["latency", "timeline"])
    parser.add_argument("inputs", nargs="+", help="result directories, or one CSV file for timeline")
    parser.add_argument("--labels", nargs="+", help="one legend label per directory")
    parser.add_argument("--out", required=True, help="file name without extension")
    parser.add_argument("--stop", type=float, help="second at which the server was stopped")
    parser.add_argument("--start", type=float, help="second at which it was started again")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    if args.kind == "latency":
        plot_latency(args.inputs, args.labels or args.inputs, args.out)
    else:
        plot_timeline(args.inputs[0], args.out, args.stop, args.start)


if __name__ == "__main__":
    main()
