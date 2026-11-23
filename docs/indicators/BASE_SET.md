# Base indicator set

Agreed in the run-through of 18 Nov 2026: build the **base set** first, not all 70 indicators.
Base set = the **top 3 indicators (priority rank 1–3) of each of the 7 components** = 21 indicators.
Defined 21 Nov 2026 in `data/indicators/indicator_master.csv` (rows marked "Base set" in `notes`).

Status: `published` = on the map today (legacy data); `defined` = definition, source and variables
are set, **data still to be loaded** (the Lens lists them as "data pending").

## Scoring rule (John, 22 Nov 2026)

The scales are set by the data, not by hand. For each indicator and year we take the smallest and the
largest actual value across all ZIPs and interpolate between them:

- **1 is always the best, 10 the worst**, with 2 decimal places.
- `higher_is_better`: score = 1 + 9 × (max − value) / (max − min)
- `lower_is_better`: score = 1 + 9 × (value − min) / (max − min)
- Even a narrow spread (e.g. volunteerism from 3% to 5%) uses the full 1–10 scale.
- **The ends are the 5th and 95th percentile**, not the single smallest and largest value; values beyond
  them get 1.00 or 10.00. Tested on the map data (23 Nov): with pure min/max one tiny ZIP with 100%
  unemployment puts 99% of all ZIPs in the best band, and 93% for poverty; with the 5th–95th percentile
  they spread over all five bands. One setting switches back to pure min/max:
  `SCORE_BOUNDS_PCT = (0, 100)` in `scripts/build_indicators.py`.

In `indicator_master.csv` this is `scoring_method = minmax_interpolation` with `scoring_status = data_driven`;
`score_worst` / `score_best` stay empty because the build script (`scripts/build_indicators.py`) takes
min and max from the loaded values. The hand-set placeholder ranges of 21 Nov are removed.

The same rule now applies to everything on the map: `scripts/rescore_legacy.py` re-scores the existing
fields in `community_data.json` (income, poverty, unemployment, labor force participation, population
change) and `files/service_centers.json`, and the map colours run from dark green (1.00–2.80, best) to dark
red (8.21–10.00, worst). Population Balance and Population Size describe a place rather than rate it, so
they keep their old 1–10 and are shown in neutral blues.

"Better when" below is the only thing we set by hand: it decides which end of the data gets the 1.

| Component | # | Indicator | Status | Source | Native level | Better when |
|---|---|---|---|---|---|---|
| Economy | 1 | Median Household Income | published | Existing community_data.json / service_centers.json fields | zip | higher |
| Economy | 2 | Per Capita Income | defined | ACS 5-Year Estimates, Per Capita Income | zip | higher |
| Economy | 3 | Poverty Rate | published | Existing community_data.json / service_centers.json fields | zip | lower |
| Infrastructure & Housing | 1 | Housing Cost Burden | defined | ACS 5-Year Estimates, Tenure by Housing Costs as a Percentage of Household Income | zip | lower |
| Infrastructure & Housing | 2 | Median Home Value | defined | ACS 5-Year Estimates, Median Value (Owner-Occupied Housing Units) | zip | higher |
| Infrastructure & Housing | 3 | Median Gross Rent | defined | ACS 5-Year Estimates, Median Gross Rent | zip | **open** (see below) |
| Education | 1 | High School Graduation Rate | defined | 4-Year Adjusted Cohort Graduation Rate | school_district | higher |
| Education | 2 | Postsecondary Educational Attainment | defined | ACS 5-Year Estimates, Educational Attainment for the Population 25 Years and Over | zip | higher |
| Education | 3 | Bachelor's Degree or Higher | defined | ACS 5-Year Estimates, Educational Attainment for the Population 25 Years and Over | zip | higher |
| Health & Human Services | 1 | Life Expectancy | defined | County Health Rankings & Roadmaps: Life Expectancy | county | higher |
| Health & Human Services | 2 | Chronic Disease Prevalence | defined | CDC PLACES: Local Data for Better Health (ZCTA release) | zip | lower |
| Health & Human Services | 3 | Mental Health | defined | CDC PLACES: Local Data for Better Health (ZCTA release) | zip | lower |
| Safety & Governance | 1 | Violent Crime Rate | defined | FBI Crime Data Explorer (UCR / NIBRS) | county | lower |
| Safety & Governance | 2 | Property Crime Rate | defined | FBI Crime Data Explorer (UCR / NIBRS) | county | lower |
| Safety & Governance | 3 | Homicide Rate | defined | CDC WONDER Underlying Cause of Death (homicide, ICD-10 X85-Y09, U01-U02) | county | lower |
| Connectivity & Access | 1 | Broadband Adoption | defined | ACS 5-Year Estimates, Presence and Types of Internet Subscriptions in Household | zip | higher |
| Connectivity & Access | 2 | High-Speed Internet Availability | defined | FCC National Broadband Map (Broadband Data Collection) | zip | higher |
| Connectivity & Access | 3 | Average Commute Time | defined | ACS 5-Year Estimates, Aggregate and Count of Travel Time to Work | zip | lower |
| Community, Culture & Quality of Life | 1 | Social Connectedness | defined | Social Capital Atlas (Chetty et al. 2022) | zip | higher |
| Community, Culture & Quality of Life | 2 | Volunteerism | defined | Social Capital Atlas (Chetty et al. 2022) | county | higher |
| Community, Culture & Quality of Life | 3 | Civic / Community Organization Participation | defined | Social Capital Atlas (Chetty et al. 2022) | county | higher |

Also on the map already (Economy 4–5, Population & Land): Unemployment Rate, Labor Force Participation,
Population Change, Population Balance, Population Size, Dominant Landform.

## Open points

1. **Percentiles:** the map uses the 5th–95th percentile (see the scoring rule). To confirm with John.
2. **Median Gross Rent has no direction.** It was `neutral`, but the 1 = best rule needs a direction, so it
   gets no score until we decide (lower = more affordable, or leave it as a plain value without a score).
   Median Home Value stays higher = better for now; affordability is covered by Housing Cost Burden.
3. **Done 23 Nov:** the map no longer uses 10 = best. Old scores re-scored, colours flipped, decimals handled.
4. **County-level sources** (life expectancy, crime, homicide, volunteerism, civic organizations) need
   `data/indicators/crosswalks/county_to_zip.csv` (e.g. HUD USPS ZIP crosswalk, residential ratio). Until it
   exists the build warns and does not publish those values.
5. **IDs:** once Emem's master index list is ready, map the 21 base-set indicators to her IDs.
6. **Next step:** load the values. The researchers are collecting them. 10 of the 16 new indicators come
   straight at ZIP/ZCTA level (ACS, CDC PLACES, FCC, Social Capital Atlas). Put them in
   `data/indicators/research/` with the researcher template, then run `python3 scripts/build_indicators.py`.
7. **Later ("when we have time"):** a third level for complex components such as services.
