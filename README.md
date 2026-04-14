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
