#!/usr/bin/env python3
"""Re-score the legacy map fields with the IAC scoring rule.

John, 22 Nov 2026: scales are set by the data; 1 is always the best, 10 the
worst, 2 decimals. The old *_score fields in community_data.json and
files/service_centers.json were whole numbers with 10 = best. This script
recomputes them from the raw fields next to them, with the same function the
Indicator Master build uses (scripts/build_indicators.py: minmax_score and
SCORE_BOUNDS_PCT), so every score on the map means the same thing.

Descriptive scores without a "better" end (pop_balance_score,
pop_size_score) are left as they are; the map shows them in a neutral colour.

Usage:  python3 scripts/rescore_legacy.py          (rewrites both files)
        python3 scripts/rescore_legacy.py --check  (only prints the summary)
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from build_indicators import minmax_score, score_bounds  # noqa: E402

# score field -> (raw field, direction)
ZIP_FIELDS = {
    "median_household_income_score": ("median_household_income_2024", "higher_is_better"),
    "poverty_rate_score": ("poverty_rate_2024", "lower_is_better"),
    "unemployment_rate_score": ("unemployment_rate_2024", "lower_is_better"),
    "labor_force_participation_score": ("labor_force_participation_pct", "higher_is_better"),
    "pop_change_score": ("pct_change_2010_2020", "higher_is_better"),
}
SC_FIELDS = {
    "pop_change_score": ("pct_change_2010_2020", "higher_is_better"),
}


def rescore(records, fields, label):
    for score_f, (raw_f, direction) in fields.items():
        raws = [r[raw_f] for r in records if isinstance(r.get(raw_f), (int, float))]
        lo, hi = score_bounds(raws)
        n = 0
        for r in records:
            x = r.get(raw_f)
            if isinstance(x, (int, float)):
                r[score_f] = minmax_score(x, lo, hi, direction)
                n += 1
            elif score_f in r:
                r[score_f] = None
        print(f"{label:22s} {score_f:34s} {n:5d} scored  bounds {lo:g} .. {hi:g} ({direction})")


def main():
    check = "--check" in sys.argv
    zpath = os.path.join(ROOT, "community_data.json")
    spath = os.path.join(ROOT, "files", "service_centers.json")
    zips = json.load(open(zpath, encoding="utf-8"))
    scs = json.load(open(spath, encoding="utf-8"))
    rescore(list(zips.values()), ZIP_FIELDS, "community_data.json")
    rescore(list(scs.values()), SC_FIELDS, "service_centers.json")
    if check:
        return
    for path, data in ((zpath, zips), (spath, scs)):
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, indent=2))   # same layout as the existing files
    print("Wrote community_data.json and files/service_centers.json")


if __name__ == "__main__":
    main()
