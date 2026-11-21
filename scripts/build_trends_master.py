#!/usr/bin/env python3
"""Build the Trends Master from the legacy map data.

One row per geography x indicator x year for every indicator in
data/indicators/indicator_master.csv whose source_id is legacy_community_data.
ZIP values come from community_data.json, Service Center values from
files/service_centers.json. Stdlib only.

Writes:
  data/trends/trends_master.csv  readable table (names, units, both scores)
  data/trends/trend_value.csv    load-ready for the trend_value table in
                                 data/sql/IAC_SQL_draft_schema.sql

Rules:
  - percentages on 0-100; population change (stored as a fraction) x 100
  - missing values are left out, never written as 0
  - score_1_10  = the existing legacy score (10 = best)
  - score_1_100 = linear between score_worst (1) and score_best (100) from the
                  Indicator Master, clipped (blank where there is no rule)
  - every row is status legacy_unverified
  - pop_dominant_landform is a category: in trends_master.csv only
"""
import csv, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)


def score_100(x, worst, best):
    v = 1 + 99 * (x - worst) / (best - worst)
    return round(max(1, min(100, v)), 1)


def main():
    im = {r["indicator_id"]: r for r in csv.DictReader(open(P("data/indicators/indicator_master.csv"), encoding="utf-8"))}
    comp = {r["component_id"]: r["component_name"] for r in csv.DictReader(open(P("data/indicators/components.csv"), encoding="utf-8"))}
    cd = json.load(open(P("community_data.json"), encoding="utf-8"))
    sc = json.load(open(P("files/service_centers.json"), encoding="utf-8"))

    rows = []

    def add(i, level, gid, name, x, score10, year, period_start=None):
        is_change = i["indicator_id"] == "pop_population_change"
        val = round(x * 100, 4) if is_change else x
        s100 = ""
        if i["scoring_method"] == "linear_bands" and i["value_type"] != "category":
            s100 = score_100(float(x), float(i["score_worst"]), float(i["score_best"]))
        rows.append(dict(
            geo_id=gid, geo_level=level, geo_name=name, indicator_id=i["indicator_id"],
            indicator_name=i["indicator_name"], component=comp.get(i["component_id"], i["component_id"]),
            year=year, period=f"{period_start}-{year}" if period_start else "", period_start=period_start or "",
            raw_value=val, unit="percent" if is_change else i["unit"], moe="",
            score_1_10="" if score10 in (None, "") else score10, score_1_100=s100,
            source_id=i["source_id"], status="legacy_unverified"))

    for i in im.values():
        if i["source_id"] != "legacy_community_data":
            continue
        raw, scf = i["legacy_raw_field"], i["legacy_score_field"]
        change = i["indicator_id"] == "pop_population_change"
        if i["geo_level"] == "zip":
            for z, v in cd.items():
                x = v.get(raw)
                if x in (None, ""):
                    continue
                add(i, "zip", z.zfill(5), v.get("town"), x, v.get(scf) if scf else None,
                    2020 if change else 2024, 2010 if change else None)
        else:
            for gid, v in sc.items():
                x = v.get(raw)
                if x in (None, ""):
                    continue
                add(i, "service_center", gid, v.get("name"), x, v.get(scf) if scf else None, 2020)
    # population change also exists at Service Center level
    i = im["pop_population_change"]
    for gid, v in sc.items():
        if v.get("pct_change_2010_2020") is not None:
            add(i, "service_center", gid, v["name"], v["pct_change_2010_2020"], v.get("pop_change_score"), 2020, 2010)

    rows.sort(key=lambda r: (r["geo_level"] != "zip", r["geo_id"], r["indicator_id"]))
    os.makedirs(P("data/trends"), exist_ok=True)
    readable = ["geo_id", "geo_level", "geo_name", "indicator_id", "indicator_name", "component", "year", "period",
                "raw_value", "unit", "moe", "score_1_10", "score_1_100", "source_id", "status"]
    sql = ["indicator_id", "geo_level", "geo_id", "year", "period_start", "raw_value", "moe", "score_1_10",
           "source_id", "status"]
    with open(P("data/trends/trends_master.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, readable, extrasaction="ignore", lineterminator="\n"); w.writeheader(); w.writerows(rows)
    with open(P("data/trends/trend_value.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, sql, extrasaction="ignore", lineterminator="\n"); w.writeheader()
        w.writerows(r for r in rows if im[r["indicator_id"]]["value_type"] != "category")
    print(f"{len(rows)} rows -> data/trends/trends_master.csv, trend_value.csv")


if __name__ == "__main__":
    main()
