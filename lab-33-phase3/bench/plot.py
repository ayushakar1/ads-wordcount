"""Figures for the report from the CSV files of loadgen.py.

    python -m bench.plot latency results/phase2 --out results/figures/phase2
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=["latency"])
    parser.add_argument("inputs", nargs="+", help="result directories")
    parser.add_argument("--labels", nargs="+", help="one legend label per directory")
    parser.add_argument("--out", required=True, help="file name without extension")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    plot_latency(args.inputs, args.labels or args.inputs, args.out)


if __name__ == "__main__":
    main()
