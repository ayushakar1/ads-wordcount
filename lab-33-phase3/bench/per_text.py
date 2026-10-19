"""Latency of cache misses and hits per text for one run, and which texts are in the slowest 1%.

    python -m bench.per_text results/phase2/rate50_1.csv

The requests are made again with the same seed, so row i of the CSV file is request i.
"""

import argparse
import collections
import csv

import numpy as np

from bench.loadgen import data_DIR, make_requests
from wordcount.server import load_texts, tokenize


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    with open(args.csv, newline="") as f:
        rows = list(csv.DictReader(f))
    requests = make_requests(len(rows), args.seed)
    words = {name: len(tokenize(text)) for name, text in load_texts(data_DIR).items()}

    latency = collections.defaultdict(list)
    for (text, _), row in zip(requests, rows):
        if not row["error"]:
            latency[text, row["cache_hit"] == "True"].append(float(row["latency_ms"]))

    print(f"{'text':22}{'words':>8}{'miss (ms)':>11}{'hit (ms)':>10}   (medians)")
    for text in sorted(words):
        miss, hit = (f"{np.median(latency[text, h]):.1f}" if latency[text, h] else "-" for h in (False, True))
        print(f"{text:22}{words[text]:8}{miss:>11}{hit:>10}")

    ok = [(text, float(row["latency_ms"])) for (text, _), row in zip(requests, rows) if not row["error"]]
    p99 = np.percentile([ms for _, ms in ok], 99)
    slowest = collections.Counter(text for text, ms in ok if ms >= p99)
    print(f"requests at or above the 99th percentile ({p99:.1f} ms):", dict(slowest.most_common()))


if __name__ == "__main__":
    main()
