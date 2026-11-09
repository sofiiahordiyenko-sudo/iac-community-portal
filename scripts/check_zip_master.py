#!/usr/bin/env python3
"""Compare the ZIP master (data/masters/zip_master.csv) with the data the Lens
map currently draws from (community_data.json + files/service_centers.json).

The ZIP master is Melissa's IAC Community Report (ZIP -> Community -> Service
Center -> Anchor). It replaces the original handover data in
community_data.json as the source of truth for ZIP assignments, but the live
map has not been switched over yet. Run this whenever a new version of the
report is dropped into data/masters/, to see what switching would change.

Stdlib only, offline, run from anywhere:
    python3 scripts/check_zip_master.py              # summary
    python3 scripts/check_zip_master.py --csv DIR    # also write detail CSVs
"""
import argparse
import csv
import json
import os
import re
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
MASTER_PATH = os.path.join(REPO_ROOT, "data", "masters", "zip_master.csv")
CUT_PATH = os.path.join(REPO_ROOT, "data", "masters", "zip_master_dakota_cut.csv")
EXCL_PATH = os.path.join(REPO_ROOT, "data", "masters", "zip_master_excluded_e_wisconsin.csv")
COMMUNITY_DATA_PATH = os.path.join(REPO_ROOT, "community_data.json")
SERVICE_CENTERS_PATH = os.path.join(REPO_ROOT, "files", "service_centers.json")
SC_CLASSIFICATION_PATH = os.path.join(REPO_ROOT, "files", "sc_classification.json")


def norm(name):
    """'Mankato, MN' / 'Mankato Service Center' -> 'mankato'."""
    s = (name or "").lower().replace("service center", "").replace("–", "-").strip()
    s = re.sub(r",\s*(mn|ia|nd|sd|wi|ne|il|mo)$", "", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fields):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", metavar="DIR", help="write detail CSVs to DIR")
    args = ap.parse_args()

    master = {r["zip"].zfill(5): r for r in read_csv(MASTER_PATH)}
    cut = {r["zip_code"].zfill(5) for r in read_csv(CUT_PATH) if r.get("decision") == "Cut"}
    excluded = {r["zip_code"].zfill(5) for r in read_csv(EXCL_PATH)}
    with open(COMMUNITY_DATA_PATH, encoding="utf-8") as f:
        cd = json.load(f)
    with open(SERVICE_CENTERS_PATH, encoding="utf-8") as f:
        sc = json.load(f)
    with open(SC_CLASSIFICATION_PATH, encoding="utf-8") as f:
        cls = json.load(f)

    def repo_sc(z):
        scid = cd[z].get("scid")
        return sc[str(scid)]["name"] if scid not in (None, "") and str(scid) in sc else ""

    communities = {norm(r["community"]) for r in master.values()}
    service_centers = {norm(r["service_center"]) for r in master.values()}

    print(f"ZIP master: {len(master)} ZIPs, {len({r['community'] for r in master.values()})} Communities, "
          f"{len({r['service_center'] for r in master.values()})} Service Centers, "
          f"{len({r['anchor'] for r in master.values()})} Anchors")
    print(f"Map data:   {len(cd)} ZIPs in community_data.json, {len(sc)} SCs in service_centers.json")

    # 1. ZIPs with no SC in the map data
    unassigned = [z for z in cd if cd[z].get("scid") in (None, "")]
    in_master = [z for z in unassigned if z in master]
    print(f"\n1. ZIPs with no SC in the map data: {len(unassigned)}; assigned in the master: {len(in_master)}")
    for (comm, scn), n in Counter((master[z]["community"], master[z]["service_center"]) for z in in_master).most_common():
        print(f"   {n:4d}  Community {comm}  /  SC {scn}")

    # 2. Coverage
    only_map = sorted(set(cd) - set(master))
    only_master = sorted(set(master) - set(cd))
    why = Counter("Dakota cut" if z in cut else "E. Wisconsin excluded" if z in excluded else "no reason recorded"
                  for z in only_map)
    print(f"\n2. In map data but not in the master: {len(only_map)} ({dict(why)})")
    print(f"   In the master but not in map data: {len(only_master)} "
          f"(by state: {dict(Counter(master[z]['state'] for z in only_master))})")

    # 3. Different assignment
    moved = [z for z in cd if z in master and repo_sc(z) and norm(repo_sc(z)) != norm(master[z]["community"])]
    print(f"\n3. ZIPs whose map SC differs from their master Community: {len(moved)}")
    for (a, b), n in Counter((repo_sc(z), master[z]["community"]) for z in moved).most_common(10):
        print(f"   {n:4d}  {a}  ->  {b}")

    # 4. SCs only in sc_classification.json
    extra = [k for k in cls if k not in sc]
    print(f"\n4. SCs in sc_classification.json with no ZIP list: {len(extra)}")
    rows = []
    for k in extra:
        n = norm(cls[k]["name"])
        status = ("SC and Community in master" if n in service_centers and n in communities else
                  "SC in master" if n in service_centers else
                  "Community (not SC) in master" if n in communities else "not in master")
        rows.append({"scid": k, "name": cls[k]["name"], "center_type": cls[k]["center_type"], "master_status": status})
    for status, n in Counter(r["master_status"] for r in rows).most_common():
        print(f"   {n:4d}  {status}: " + ", ".join(r["name"] for r in rows if r["master_status"] == status))

    if args.csv:
        os.makedirs(args.csv, exist_ok=True)
        f = ["zip", "town", "state", "map_sc", "community", "service_center", "anchor", "floater"]
        write_csv(os.path.join(args.csv, "unassigned_in_map.csv"),
                  [{**master[z], "map_sc": ""} for z in in_master], f)
        write_csv(os.path.join(args.csv, "moved.csv"), [{**master[z], "map_sc": repo_sc(z)} for z in moved], f)
        write_csv(os.path.join(args.csv, "map_only.csv"),
                  [{"zip": z, "town": cd[z]["town"], "state": cd[z]["state"], "map_sc": repo_sc(z),
                    "reason": "Dakota cut" if z in cut else "E. Wisconsin excluded" if z in excluded else ""}
                   for z in only_map], ["zip", "town", "state", "map_sc", "reason"])
        write_csv(os.path.join(args.csv, "master_only.csv"), [master[z] for z in only_master],
                  ["zip", "town", "state", "county", "community", "service_center"])
        write_csv(os.path.join(args.csv, "sc_without_zips.csv"), rows, ["scid", "name", "center_type", "master_status"])
        print(f"\nDetail CSVs written to {args.csv}")


if __name__ == "__main__":
    main()
