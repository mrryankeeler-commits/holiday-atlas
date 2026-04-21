# Holiday Atlas

## Front-end dependency pinning policy

Holiday Atlas is a static app, so third-party front-end dependencies are loaded either from pinned CDN URLs or from versioned files committed in-repo. To keep releases reproducible and secure:

- Always pin an explicit version in the asset URL (never use floating tags like `latest`).
- For externally hosted scripts/styles, always include Subresource Integrity (`integrity`) and `crossorigin` attributes.
- When upgrading a dependency version, update **both**:
  - the version in the URL/path, and
  - the corresponding SRI hash value in `index.html`.
- Treat SRI updates as part of the same change as the version bump; do not merge a version upgrade without a matching integrity refresh.
- If a dependency cannot be loaded with SRI from the network environment, vendor the exact versioned artifact in-repo and reference it locally instead.

## Contributor note: adding a new location

This repository is transitioning from a single `data/destinations.json` file to per-location files.
When adding a location, use this structure:

- Summary manifest: `data/locations/index.json`
- Full record file: `data/locations/<id>.json`

### Naming convention

- `id` **must** be URL-safe lowercase and use dashes only (example: `lisbon-portugal`).
- `id` in data **must exactly match** the filename (`<id>.json`) and the manifest entry `id`.

### Required fields

#### `data/locations/index.json` (manifest entry)
Each entry should include at minimum:

- `id`
- `city`
- `country`
- `region`
- `lat` (number, -90..90)
- `lng` (number, -180..180)

#### `data/locations/<id>.json` (full record)
Each full location file should include at minimum:

- `id`
- `city`
- `country`
- `region`
- `desc`
- `hls` (array)
- `sweet`
- `months` (array)
- `todo` (array)
- `prac` (object)

Within `prac`, include:

- `directGW`
- `visa`
- `currency`
- `alerts` (array)
- `wifi` (object with `r` and `notes`)
- `sim`
- `safety`
- `lang`
- `power`

### Quick reviewer consistency checklist

- [ ] An index entry exists in `data/locations/index.json`.
- [ ] A matching file exists at `data/locations/<id>.json`.
- [ ] The `id` matches between manifest entry and filename.
- [ ] Required keys are present in both manifest and full record.
- [ ] Climate provenance passes strict verification:
  - `python3 scripts/verify_climate_provenance.py`
  - Verified means linked CSV source data exists *and* matches JSON climate values shown in the app.

## Refreshing monthly climate data (CSV workflow)

Monthly climate data is maintained from local CSV sources only (no external weather API/provider scripts).

### Preferred local mixed-CSV workflow

For a new mixed climate CSV, use the local flow below as the default:

1. Preview the batch before writing anything:
   - `python3 scripts/plan_climate_import.py --input-file 'data/climate/uploads/batch.csv' --mode stage`
2. Run the local intake wrapper:
   - `python3 scripts/run_location_intake.py --input-file 'data/climate/uploads/batch.csv' --write-reports`
3. Review real enrichment work only:
   - `python3 scripts/plan_enrichment_batch.py`
4. Review queue/checklist drift separately:
   - `python3 scripts/reconcile_enrichment_queue.py`

Script roles:

- `scripts/plan_climate_import.py`
  - Preflight preview for mixed CSVs. Use it to catch fuzzy matches, unknown IDs, and invalid month coverage before import.
- `scripts/run_location_intake.py`
  - Preferred local wrapper for mixed CSV intake. It runs preflight first, imports only if the plan passes, then runs validation, provenance verification, audit, and enrichment planning.
- `scripts/plan_enrichment_batch.py`
  - Lists locations with real enrichment reasons. Queue membership alone is no longer treated as enrichment-needed.
- `scripts/reconcile_enrichment_queue.py`
  - Dry-run helper for queue/checklist drift. Use it after review work to find queue-only pending entries that are safe manual cleanup candidates.

### Low-level import commands

- Bulk import all CSV files in a directory:
  - `python scripts/import_climate_csv.py --input-dir data/climate`
- Import one location by id from a directory:
  - `python scripts/import_climate_csv.py --input-dir data/climate --id athens`
- Import one explicit file:
  - `python scripts/import_climate_csv.py --input-file data/climate/athens.csv --id athens`
- Import a single mixed CSV containing many locations:
  - `python scripts/import_climate_csv.py --input-file data/climate/batch.csv --location-col "Location" --month-col "Month" --avg-col "Avg Temp (°C)" --hi-col "Avg High (°C)" --lo-col "Avg Low (°C)" --daylight-col "Daylight (h/day)" --cloud-col "Cloud Cover (%)" --rain-col "Rainfall (mm)"`
- Allow creation of new location files from the mixed CSV:
  - `python scripts/import_climate_csv.py --input-file data/climate/batch.csv --create-missing --default-region Europe`
- Stage unknown/future locations without showing them in the app yet:
  - `python scripts/import_climate_csv.py --input-file data/climate/batch.csv --stage-unknown-dir data/pending-locations`
- Resolve known spelling variants/misspellings via alias map:
  - `python scripts/import_climate_csv.py --input-file data/climate/batch.csv --aliases-file data/climate/aliases.json`

If you use GitHub Web and do not want terminal commands, use the Actions workflow guide:

- `docs/github-web-csv-import.md`

Useful flags:

- `--month-col`, `--avg-col`, `--hi-col`, `--lo-col`, `--daylight-col`, `--cloud-col`, `--rain-col`
- `--location-col`, `--id-col`, `--city-col`, `--country-col`, `--region-col` (for combined CSV imports)
- `--aliases-file`, `--fuzzy-cutoff`, `--disable-fuzzy-match` (for typo handling and inferred matching; lower cutoff is more forgiving)
- `--create-missing`, `--default-region`
- `--stage-unknown-dir` (keeps unknown/future locations out of active `data/locations/`)
- `--allow-score-overrides` (only then read busy/ac/fl columns)

### Source files

- Store CSV inputs under `data/climate/` (one file per location).
- Use the location id as the filename where possible (example: `data/climate/athens.csv`).

### Expected CSV columns

Each CSV row should represent one month and include:

- `month` (month number or month name)
- `avg` (average temperature, required)
- `hi` (average high)
- `lo` (average low)
- `daylight` (daylight hours)
- `cld` (cloud cover)
- `rain` (rainfall)

### Transformation output

- Transformed climate metrics are written to each location's `months` array in `data/locations/<id>.json`.
- Existing non-climate month scoring fields (`busy`, `ac`, `fl`) are preserved unless `--allow-score-overrides` is provided.
- When `--create-missing` is used for a new location, the importer estimates initial `busy`, `ac`, and `fl` values from climate seasonality and conditions.
- Unknown locations can be staged under a pending folder (`--stage-unknown-dir`) so they are stored but not displayed in-app.
- Staged payloads may include a `source` field for import provenance; treat it as internal metadata and never surface it in destination UI.
- The importer does not generate `rise` or `set`.

### Automatic provenance verification

After importing/updating climate data, run:

- `python3 scripts/validate_locations.py`
- `python3 scripts/verify_climate_provenance.py`
- `python3 scripts/audit_locations.py --fail-on-high` (runs schema/data contract, climate provenance, generic-content, and direct-flight consistency checks with consolidated JSON report output)
- `make audit-locations` (alias for the consolidated audit command)

For local pre-commit enforcement, install and run the repository hooks:

- `python3 -m pip install pre-commit`
- `pre-commit install`
- `pre-commit run --all-files`

`scripts/validate_locations.py` is a **mandatory pre-merge contract check** and is enforced in CI via `.github/workflows/location-data-validation.yml` on pull requests that touch location data.

The validator now also blocks:

- empty `prac.airports` unless `prac.airportsExceptionNote` is present and non-empty,
- known placeholder `prac.alerts` arrays,
- generic `region` values such as `"<country> region"`,
- empty/generic practical text in `prac.visa`, `prac.currency`, `prac.lang`, `prac.tz`,
- draft scaffolds emitted by `scripts/import_climate_csv.py` when `source.draftOnly: true` remains set.

### Remediating generic-content validator failures

If `python3 scripts/validate_locations.py` flags boilerplate text:

- Rewrite `desc` and `sweet` with concrete destination details (named neighborhoods, seasonal realities, trip style fit).
- Replace `prac.bestFor[]` generic audience tags with destination-specific traveler profiles.
- For optional checks in `hls[]` and `todo[].desc`, replace template language with place-specific highlights and activity context.
- Re-run `python3 scripts/validate_locations.py` until all flagged field/index entries are cleared.

If you need CI-style strictness that fails whenever any destination is still unverified:

- `python3 scripts/verify_climate_provenance.py --fail-on-unverified`

`verify_climate_provenance.py` enforces:

- `source.climateVerified: true` is allowed only when linked CSV rows are present and climate fields (`avg`, `hi`, `lo`, `daylight`, `cld`, `rain`) match JSON.
- Otherwise the location must be marked unverified with a note.

## Batch policy for richer destination updates

- Climate/provenance-only updates can be bulked.
- In-depth destination enrichment (research-heavy practicals, costs/flights, activities, alerts) should be done in batches of up to **3 locations** for quality control.

### Proven review rhythm

For queue-only pending locations, use this lightweight review loop:

1. Review 5 real `data/locations/<id>.json` files.
2. Fix the weak ones immediately.
3. Mark only the safe ones complete in the tracking files.
4. Re-run:
   - `python3 scripts/plan_enrichment_batch.py`
   - `python3 scripts/reconcile_enrichment_queue.py`
5. Move to the next 5.

### Month schema (documented fields)

Validator contract: month objects must use exactly these keys (including scoring), `daylight` replaces any legacy `sun` key, and `rise`/`set` are not allowed.


```json
{
  "m": "Jan",
  "avg": 13,
  "hi": 16,
  "lo": 9,
  "daylight": 9.8,
  "cld": 42,
  "rain": 52,
  "busy": 3,
  "ac": 3,
  "fl": 3
}
```
