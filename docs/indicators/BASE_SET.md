# Base indicator set

Agreed in the run-through of 18 Nov 2026: build the **base set** first, not all 70 indicators.
Base set = the **top 3 indicators (priority rank 1–3) of each of the 7 components** = 21 indicators.
Defined 21 Nov 2026 in `data/indicators/indicator_master.csv` (rows marked "Base set" in `notes`).

Status: `published` = on the map today (legacy data); `defined` = definition, source, variables and
provisional scoring are set, **data still to be loaded** (the Lens lists them as "data pending").

| Component | # | Indicator | Status | Source | Native level | Direction |
|---|---|---|---|---|---|---|
| Economy | 1 | Median Household Income | published | Existing community_data.json / service_centers.json fields | zip | higher_is_better |
| Economy | 2 | Per Capita Income | defined | ACS 5-Year Estimates, Per Capita Income | zip | higher_is_better |
| Economy | 3 | Poverty Rate | published | Existing community_data.json / service_centers.json fields | zip | lower_is_better |
| Infrastructure & Housing | 1 | Housing Cost Burden | defined | ACS 5-Year Estimates, Tenure by Housing Costs as a Percentage of Household Income | zip | lower_is_better |
| Infrastructure & Housing | 2 | Median Home Value | defined | ACS 5-Year Estimates, Median Value (Owner-Occupied Housing Units) | zip | higher_is_better |
| Infrastructure & Housing | 3 | Median Gross Rent | defined | ACS 5-Year Estimates, Median Gross Rent | zip | neutral |
| Education | 1 | High School Graduation Rate | defined | 4-Year Adjusted Cohort Graduation Rate | school_district | higher_is_better |
| Education | 2 | Postsecondary Educational Attainment | defined | ACS 5-Year Estimates, Educational Attainment for the Population 25 Years and Over | zip | higher_is_better |
| Education | 3 | Bachelor's Degree or Higher | defined | ACS 5-Year Estimates, Educational Attainment for the Population 25 Years and Over | zip | higher_is_better |
| Health & Human Services | 1 | Life Expectancy | defined | County Health Rankings & Roadmaps: Life Expectancy | county | higher_is_better |
| Health & Human Services | 2 | Chronic Disease Prevalence | defined | CDC PLACES: Local Data for Better Health (ZCTA release) | zip | lower_is_better |
| Health & Human Services | 3 | Mental Health | defined | CDC PLACES: Local Data for Better Health (ZCTA release) | zip | lower_is_better |
| Safety & Governance | 1 | Violent Crime Rate | defined | FBI Crime Data Explorer (UCR / NIBRS) | county | lower_is_better |
| Safety & Governance | 2 | Property Crime Rate | defined | FBI Crime Data Explorer (UCR / NIBRS) | county | lower_is_better |
| Safety & Governance | 3 | Homicide Rate | defined | CDC WONDER Underlying Cause of Death (homicide, ICD-10 X85-Y09, U01-U02) | county | lower_is_better |
| Connectivity & Access | 1 | Broadband Adoption | defined | ACS 5-Year Estimates, Presence and Types of Internet Subscriptions in Household | zip | higher_is_better |
| Connectivity & Access | 2 | High-Speed Internet Availability | defined | FCC National Broadband Map (Broadband Data Collection) | zip | higher_is_better |
| Connectivity & Access | 3 | Average Commute Time | defined | ACS 5-Year Estimates, Aggregate and Count of Travel Time to Work | zip | lower_is_better |
| Community, Culture & Quality of Life | 1 | Social Connectedness | defined | Social Capital Atlas (Chetty et al. 2022) | zip | higher_is_better |
| Community, Culture & Quality of Life | 2 | Volunteerism | defined | Social Capital Atlas (Chetty et al. 2022) | county | higher_is_better |
| Community, Culture & Quality of Life | 3 | Civic / Community Organization Participation | defined | Social Capital Atlas (Chetty et al. 2022) | county | higher_is_better |

Also on the map already (Economy 4–5, Population & Land): Unemployment Rate, Labor Force Participation,
Population Change, Population Balance, Population Size, Dominant Landform.

## Open points

1. **Scoring bands are placeholders** (`scoring_status = provisional`). Recalibrate `score_worst` / `score_best`
   to the 5th–95th percentile after the first data load. Scale for display: 1–100, 100 = best (agreed 21 Nov 2026).
2. **County-level sources** (life expectancy, crime, homicide, volunteerism, civic organizations) need
   `data/indicators/crosswalks/county_to_zip.csv` (e.g. HUD USPS ZIP crosswalk, residential ratio). Until it
   exists the build warns and does not publish those values.
3. **Direction to confirm with John:** Median Home Value (set higher = better) and Median Gross Rent (neutral).
4. **Next step:** load the values. 10 of the 16 new indicators come straight at ZIP/ZCTA level
   (ACS, CDC PLACES, FCC, Social Capital Atlas). Put them in `data/indicators/research/` with the
   researcher template, then run `python3 scripts/build_indicators.py`.
