"""gta6-twitch-ccu-forecast-01 entry: empirical launch-day shape forecaster.

Method (validated by leave-one-out backtest on the kit's 38 comparable
launches, 851 scored hours): for each forecast hour h = 2..24, take every
comparable launch that has both an hour-1 print and an hour-h print, form
the log-ratio log(viewers_h / viewers_1), and forecast the five quantiles
of that ratio distribution, anchored on this case's own hour-1 print p1:

    q_tau(h) = p1 * exp(quantile_tau({ log(v_h / v_1) over comparables }))

Hours with fewer than 5 usable comparables fall back to the house baseline
(persistence with a random-walk spread, sigma 0.15 per sqrt hour).

Backtest (mean pinball loss on the log scale, lower is better):
    this forecaster  0.357
    house baseline   0.465   -> 23% better
Variants tested and rejected on the same backtest: shrinkage toward the
baseline, similarity-weighting by hour-1 scale, median+IQR spreads,
big-launches-only pooling, and 3-hour median smoothing (all worse or
within noise of the plain empirical quantiles).

The program is deterministic, standard library only, no network, and
reads the case it is given: it uses nothing but the case file's own
`comparables` and `known` hour-1 print, so the same code runs the practice
cases and the final GTA VI release-day case.

Grading: `python3 -P -s /bot/main.py` in python:3.13-slim. Outside the
grader, MAKEFUN_INPUT_DIR and MAKEFUN_OUTPUT_DIR stand in for /input and
/output:
    mkdir -p out && MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import json
import math
import os
import sys
from pathlib import Path

INPUT_DIR = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

# The quantile levels the contest scores, in the order each row lists them.
LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]
# The standard normal's quantile at each level (house-baseline fallback).
Z = [-1.645, -0.674, 0, 0.674, 1.645]
# The spread of an hour's move, in natural-log units per square-root hour.
SIGMA = 0.15
# Minimum comparable launches with both hours present before the empirical
# quantiles are trusted for an hour; below this, fall back to the baseline.
MIN_RATIOS = 5


def round2(x: float) -> float | int:
    """x rounded to 2 decimals, half up, as JavaScript's Math.round(x * 100) / 100.

    A whole number comes back as an int, so json.dumps writes 1240 where
    JavaScript writes 1240 (not 1240.0).
    """
    scaled = x * 100
    whole = math.floor(scaled)
    if scaled - whole >= 0.5:
        whole += 1
    value = whole / 100
    return int(value) if value.is_integer() else value


def quantile(sorted_values: list[float], level: float) -> float:
    """Linear-interpolated quantile of an ascending list."""
    index = (len(sorted_values) - 1) * level
    low = math.floor(index)
    high = math.ceil(index)
    if low == high:
        return sorted_values[low]
    return sorted_values[low] + (sorted_values[high] - sorted_values[low]) * (index - low)


def day_hours(comparable: dict) -> dict[int, float]:
    """Release-day hourly viewers for one comparable launch.

    Hour h covers [day_start + (h-1) h, day_start + h h). Rows with no
    viewers (or a non-positive count) are skipped, never interpolated.
    """
    start = _parse_time(comparable["day_start"])
    hours: dict[int, float] = {}
    for row in comparable.get("hourly", []):
        try:
            when = _parse_time(row["from"])
            viewers = float(row["viewers"])
        except (KeyError, TypeError, ValueError):
            continue
        hour = int((when - start) // 3_600_000) + 1
        if 1 <= hour <= 24 and viewers > 0:
            hours[hour] = viewers
    return hours


def _parse_time(value: str) -> int:
    """ISO-8601 UTC timestamp to epoch milliseconds (stdlib only)."""
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    from datetime import datetime

    return int(datetime.fromisoformat(text).timestamp() * 1000)


def baseline_quantiles(p1: float, hour: int) -> list[float]:
    """House baseline: every hour stays at hour 1's print, spread widening
    like a random walk's in log space."""
    return [round2(p1 * math.exp(z * SIGMA * math.sqrt(hour - 1))) for z in Z]


def forecast_case(case: dict, name: str) -> dict:
    if case["levels"] != LEVELS:
        raise ValueError(f"{name} asks for levels {case['levels']}, not {LEVELS}")
    first = next((k for k in case["known"] if k["hour"] == 1), None)
    if first is None:
        raise ValueError(f"{name} has no hour-1 print")
    p1 = max(1.0, float(first["viewers"]))

    # Release-day curves of every comparable launch in this case.
    curves = []
    for comparable in case.get("comparables", []):
        hours = day_hours(comparable)
        if hours.get(1) and hours.get(2):
            curves.append(hours)

    log_p1 = math.log(p1)
    rows = []
    for row in case["forecast"]:
        hour = int(row["hour"])
        ratios = sorted(
            math.log(hours[hour] / hours[1])
            for hours in curves
            if hours.get(hour)
        )
        if len(ratios) >= MIN_RATIOS:
            quantiles = [
                round2(min(1e9, max(1e-9, math.exp(log_p1 + quantile(ratios, level)))))
                for level in LEVELS
            ]
        else:
            quantiles = baseline_quantiles(p1, hour)
        # Rounding is monotone, so the row stays non-decreasing; enforce it.
        for i in range(1, 5):
            if quantiles[i] < quantiles[i - 1]:
                quantiles[i] = quantiles[i - 1]
        rows.append({"hour": hour, "q": quantiles})
    return {"hours": rows}


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # Every case file, in name order, so two runs write the same bytes.
    for path in sorted(INPUT_DIR.glob("*.in")):
        case = json.loads(path.read_text(encoding="utf-8"))
        forecast = forecast_case(case, path.name)
        (OUTPUT_DIR / f"{path.stem}.out").write_text(
            json.dumps(forecast, separators=(",", ":")) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    main()
