#!/usr/bin/env python3
"""Plot one or more training-curve CSVs (from run_experiment.py) on one chart -
for report evidence such as Q-learning vs SARSA, or intrinsic vs no-intrinsic.

Example:
  python plot_curves.py logs/level1_qlearning.csv:Q-learning logs/level1_sarsa.csv:SARSA \
      --title "Level 1: Q-learning vs SARSA" --out report_assets/level1_comparison.png
"""
import argparse
import csv

import matplotlib.pyplot as plt


def load_csv(path):
    episodes, returns = [], []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            episodes.append(int(row["episode"]))
            returns.append(float(row["env_return"]))
    return episodes, returns


def moving_average(values, window):
    if window <= 1:
        return values
    out = []
    for i in range(len(values)):
        lo = max(0, i - window + 1)
        out.append(sum(values[lo:i + 1]) / (i - lo + 1))
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("series", nargs="+", help="one or more path.csv:Label entries")
    parser.add_argument("--title", default="Training curve")
    parser.add_argument("--smooth", type=int, default=20, help="moving-average window (episodes)")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    plt.figure(figsize=(8, 5))
    for spec in args.series:
        path, _, label = spec.partition(":")
        label = label or path
        episodes, returns = load_csv(path)
        plt.plot(episodes, moving_average(returns, args.smooth), label=label)

    plt.xlabel("Episode")
    plt.ylabel(f"Return (smoothed, window={args.smooth})")
    plt.title(args.title)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(args.out, dpi=150)
    print(f"Saved plot to {args.out}")


if __name__ == "__main__":
    main()
