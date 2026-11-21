# Trends Master

One row per geography × indicator × year. Built by `scripts/build_trends_master.py`
from the legacy map data (`community_data.json`, `files/service_centers.json`) for the
indicators in `data/indicators/indicator_master.csv` with `source_id = legacy_community_data`.

| File | Use |
|---|---|
| `trends_master.csv` | Readable table: names, component, unit, `score_1_10` (legacy) and `score_1_100` |
| `trend_value.csv` | Load-ready for the `trend_value` table in `data/sql/IAC_SQL_draft_schema.sql` (PostgreSQL) |

- All values are legacy and **not verified**: `status = legacy_unverified`.
- Percentages on 0–100; population change converted from a fraction (0.0405 → 4.05).
- `score_1_100` (100 = best) is the agreed scale from 21 Nov 2026: linear between
  `score_worst` and `score_best` in the Indicator Master, clipped. Those parameters were
  inferred from the legacy scores and still need confirmation.
- Missing values are left out, never 0. Labor force participation has no year in the
  legacy data; 2024 is assumed.
- `pop_dominant_landform` is a category, so it is only in `trends_master.csv`.

Rebuild: `python3 scripts/build_trends_master.py`
