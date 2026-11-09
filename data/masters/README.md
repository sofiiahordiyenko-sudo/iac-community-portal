# ZIP master

`zip_master.csv` is the source of truth for **ZIP → Community → Service Center → Anchor**.
It is the main sheet of Melissa Nare's *IAC Community Report*, currently **v7**:
2,749 ZIPs, 132 Communities, 61 Service Centers, 5 Anchors.

It replaces `community_data.json` (the original handover data) as the ZIP
master. **The Lens map has not been switched to it yet**: the map still draws
from `community_data.json` and `files/service_centers.json`.

v7 is the current version but not final. The floater decisions and the metro
clean-up will change it. The latest version always lives in Melissa's shared
Drive folder (`Latest`; older versions go to `Archive`).

## Files

| File | From v7 sheet | Content |
|---|---|---|
| `zip_master.csv` | ZIP-Community-SC-Anchor | One row per ZIP: town, state, county, population, lat/lng, community, service_center, sc_subtype, anchor, orientation (Oriented / Dedicated / Shared), floater |
| `zip_master_changelog.csv` | Changes | What changed in v4–v7 and why |
| `zip_master_dakota_cut.csv` | Dakota Cut | v7: western Dakotas removed (Williston, Dickinson, Minot, Bismarck, Pierre); 27 ZIPs kept and moved east |
| `zip_master_nebraska_adds.csv` | Nebraska Adds | v7: 31 NE Nebraska ZIPs added |
| `zip_master_windom_area_moves.csv` | Windom Area Moves | v5: 23 ZIPs moved, new Communities St. James, Springfield MN, Slayton, Estherville |
| `zip_master_excluded_e_wisconsin.csv` | Excluded ZIPs (E. Wisconsin) | v4: 385 ZIPs excluded as closer to Milwaukee, Madison, Green Bay, etc. |

## Updating to a new version

1. Download the file from `Latest` in Melissa's folder.
2. Export the sheets above to these CSVs (ZIP codes as 5-digit text).
3. Run `python3 scripts/check_zip_master.py` to see what changed against the map data
   (`--csv DIR` writes the detail lists).

## How v7 compares with the map data (9 Nov 2026)

`python3 scripts/check_zip_master.py`:

- **121 ZIPs with no SC in `community_data.json`**: all are assigned in v7
  (Fort Dodge SC: Fort Dodge 33, Storm Lake 32, Harlan 18, Carroll 13; Hallock 19;
  Winona 3; La Crosse 2; Austin 1). Austin (55912) is its own Community and SC.
- **Coverage**: 2,155 ZIPs are in both. 130 are only in the map data (70 Dakota
  cut; 60 with no reason recorded, mostly 45 around Sioux City, IA). 594 are only
  in v7 (IA 293, WI 198, NE 31, IL 27, …).
- **Assignments**: 594 ZIPs in both have a different Community in v7 than their
  map SC, mainly because v7 splits the large SCs (e.g. Des Moines → Ottumwa,
  Atlantic, Ames; Minneapolis–St Paul → Ridgedale, Riverdale, Southdale, …).
- **30 SCs in `sc_classification.json` with no ZIP list**: 12 are Service
  Centers in v7 (Arbor Lakes, Buffalo, Burnsville, Eden Prairie, MOA, Ridgedale,
  Riverdale, Rosedale, Southdale, Stillwater, Waconia, Woodbury); 4 are
  Communities but not SCs (Marshfield, Tomah, Valley City, Wahpeton); 3 were
  removed in the Dakota cut (Bismarck, Minot, Pierre); 11 are not in v7 under
  those names (Fairmont, Duluth-Superior, Elk River, Northfield and 7 metro nodes).
  Build / merge / drop for these is John's decision; the metro ones are held for
  the next release.

Switching the map to the master means rebuilding `service_centers.json`
(132 Communities instead of 71 SCs) and the ZIP→SC fields in
`community_data.json`. That is deliberately not done yet, until the floater
and metro decisions are in.
