-- IAC GeoBase: draft SQL schema for the Indicator Master, Source and Trends tables
-- Draft for discussion, 18 Nov 2026 (Sofiia Hordiienko). Target engine: PostgreSQL (proposed, not final).
-- Mirrors the current CSV masters in the repository (data/indicators/*.csv).
-- ZIP / Community / Service Center / Anchor come from the base map (Melissa's IAC Community Report);
-- they are referenced here, not duplicated.

-- 1. Components (Economy, Education, ...)
CREATE TABLE component (
    component_id        TEXT PRIMARY KEY,               -- e.g. 'economy'
    component_name      TEXT NOT NULL,
    display_order       SMALLINT NOT NULL,
    in_top10_structure  BOOLEAN NOT NULL DEFAULT TRUE,  -- FALSE for Demographics / Environment (temporary)
    weight              NUMERIC(6,4),                   -- blank until the weighting is decided
    notes               TEXT
);

-- 2. Source table: one row per data source
CREATE TABLE source (
    source_id           TEXT PRIMARY KEY,               -- e.g. 'acs5_b15003'
    source_name         TEXT NOT NULL,
    publisher           TEXT,
    dataset_or_table    TEXT,
    url                 TEXT,
    native_geo_levels   TEXT,                           -- e.g. 'zcta;county;state'
    release_cycle       TEXT,                           -- e.g. 'Annual (December)'
    years_available     TEXT,
    reliability_1to5    SMALLINT CHECK (reliability_1to5 BETWEEN 1 AND 5),
    zip_availability    TEXT,                           -- High / Moderate / Low
    notes               TEXT
);

-- 3. Indicator Master: one row per indicator (or sub-measure)
CREATE TABLE indicator (
    indicator_id         TEXT PRIMARY KEY,              -- permanent, e.g. 'eco_poverty_rate'
    level                TEXT NOT NULL CHECK (level IN ('indicator', 'measure')),
    parent_indicator_id  TEXT REFERENCES indicator (indicator_id),
    component_id         TEXT NOT NULL REFERENCES component (component_id),
    priority_rank        SMALLINT,
    indicator_name       TEXT NOT NULL,
    short_label          TEXT,
    status               TEXT NOT NULL CHECK (status IN ('planned', 'defined', 'published')),
    definition           TEXT,
    unit                 TEXT,                          -- USD, percent (0-100), persons, ...
    value_type           TEXT,
    direction            TEXT CHECK (direction IN ('higher_is_better', 'lower_is_better', 'neutral')),
    geo_level            TEXT,                          -- level the indicator is scored at: zip / service_center
    native_geo_level     TEXT,                          -- level the source publishes at
    source_id            TEXT REFERENCES source (source_id),
    source_variables     TEXT,
    derivation           TEXT,                          -- how a composite is built from its measures
    methodology          TEXT,
    release_cycle        TEXT,
    years_planned        TEXT,
    scoring_method       TEXT,                          -- e.g. 'linear_bands'
    score_worst          NUMERIC,                       -- raw value that scores 1
    score_best           NUMERIC,                       -- raw value that scores 10
    scoring_status       TEXT,
    legend_1             TEXT,
    legend_2             TEXT,
    legend_4             TEXT,
    legend_5             TEXT,
    weight               NUMERIC(6,4),
    notes                TEXT
    -- The CSV also has front-end / migration columns (binding, legacy_* fields, research_indicator,
    -- match_type, match_rationale, existing_materials_match, revision_needed). They can stay in the
    -- CSV or move to a separate mapping table; they are not needed for the data model itself.
);

-- 4. Trends (fact table): one row per geography x indicator x year.
--    Only indicator_id is stored; name, component and unit come from the indicator table.
CREATE TABLE trend_value (
    indicator_id   TEXT NOT NULL REFERENCES indicator (indicator_id),
    geo_level      TEXT NOT NULL CHECK (geo_level IN ('zip', 'service_center', 'school_district', 'county')),
    geo_id         TEXT NOT NULL,                      -- 5-digit ZIP as text (keeps leading zeros), or SC / district / county id
    year           SMALLINT NOT NULL CHECK (year BETWEEN 1990 AND 2100),  -- ACS 5-year: end year
    period_start   SMALLINT,                           -- for change indicators, e.g. 2010 (period 2010-2020)
    raw_value      NUMERIC NOT NULL,                   -- as published; percentages on a 0-100 scale
    moe            NUMERIC,                            -- margin of error, if published
    score_1_10     SMALLINT CHECK (score_1_10 BETWEEN 1 AND 10),  -- calculated from raw_value at load time
    source_id      TEXT NOT NULL REFERENCES source (source_id),
    status         TEXT NOT NULL DEFAULT 'legacy_unverified'
                   CHECK (status IN ('legacy_unverified', 'submitted', 'validated')),
    allocated      BOOLEAN NOT NULL DEFAULT FALSE,     -- TRUE if allocated from district / county to ZIP
    loaded_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (indicator_id, geo_level, geo_id, year)
);

CREATE INDEX trend_value_geo_idx ON trend_value (geo_level, geo_id);
CREATE INDEX trend_value_year_idx ON trend_value (indicator_id, year);

-- 5. Readable view: what the Excel Trends Master showed, rebuilt by joins
CREATE VIEW trend_value_readable AS
SELECT t.geo_id AS zip,
       t.geo_level,
       t.indicator_id,
       i.indicator_name,
       c.component_name AS component,
       t.year,
       CASE WHEN t.period_start IS NOT NULL THEN t.period_start || '-' || t.year END AS period,
       t.raw_value,
       i.unit,
       t.moe,
       t.score_1_10,
       t.source_id,
       t.status
FROM trend_value t
JOIN indicator i ON i.indicator_id = t.indicator_id
JOIN component c ON c.component_id = i.component_id;

-- Open points (to agree):
-- * Engine: PostgreSQL proposed (free, standard SQL, PostGIS available later for ZIP shapes). To confirm with John.
-- * Base map tables (zip -> community -> service_center -> anchor) and the Jurisdiction design:
--   to be modelled with Melissa; trend_value.geo_id joins to the ZIP there.
-- * ZCTA vs ZIP: PO-box ZIPs have no ACS data; 2000/2010 values need a ZCTA vintage crosswalk.
