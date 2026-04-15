# Holiday Atlas

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
- `desc`

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

## Refreshing monthly climate data (CSV workflow)

Monthly climate data is maintained from local CSV sources only (no external weather API/provider scripts).

### Import command

- Bulk import all CSV files in a directory:
  - `python scripts/import_climate_csv.py --input-dir data/climate`
- Import one location by id from a directory:
  - `python scripts/import_climate_csv.py --input-dir data/climate --id athens`
- Import one explicit file:
  - `python scripts/import_climate_csv.py --input-file data/climate/athens.csv --id athens`

Useful flags:

- `--month-col`, `--avg-col`, `--hi-col`, `--lo-col`, `--daylight-col`, `--cloud-col`, `--rain-col`
- `--allow-score-overrides` (only then read busy/ac/fl columns)

### Source files

- Store CSV inputs under `data/climate/` (one file per location).
- Use the location id as the filename where possible (example: `data/climate/athens.csv`).

### Expected CSV columns

Each CSV row should represent one month and include:

- `month` (month number or month name)
- `avg` (average temperature)
- `hi` (average high)
- `lo` (average low)
- `daylight` (daylight hours)
- `cld` (cloud cover)
- `rain` (rainfall)

### Transformation output

- Transformed climate metrics are written to each location's `months` array in `data/locations/<id>.json`.
- Existing non-climate month scoring fields (`busy`, `ac`, `fl`) are preserved unless `--allow-score-overrides` is provided.
- The importer does not generate `rise` or `set`.

### Month schema (documented fields)

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
