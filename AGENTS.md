# AGENTS.md

## Scope
These instructions apply to the entire repository.

## Project overview
Holiday Atlas is a static front-end app (`index.html`, `app.js`, `styles.css`) that renders destinations and monthly travel data.

## Data layout (source of truth)
- Destination manifest: `data/locations/index.json`
- One file per location: `data/locations/<id>.json`
- `id` must be lowercase kebab-case and match filename exactly.

## Task routing guidance
- “Add/edit a destination”:
  1) Update `data/locations/index.json`
  2) Update/create `data/locations/<id>.json`
- “Change rendering/UX”:
  - Edit `app.js` and/or `styles.css`
- “Change copy/static markup”:
  - Edit `index.html` (and `app.js` where strings are generated)

## Data contract
### index.json required fields
- `id`, `city`, `country`, `region`

### <id>.json required fields
- `id`, `city`, `country`, `region`, `desc`, `hls`, `todo`, `prac`, `sweet`, `months`

## Quality checks (before commit)
- JSON files parse
- Every `index.json` id has a corresponding `data/locations/<id>.json`
- Every location file id matches filename
- No duplicate ids
- Climate provenance check passes:
  - `python3 scripts/verify_climate_provenance.py`
  - A location may only be marked `source.climateVerified: true` when linked CSV source rows exist and the CSV climate values match the JSON month values shown in-app.

### Month object climate schema
- Required month keys (exact): `m`, `avg`, `hi`, `lo`, `daylight`, `cld`, `rain`, `busy`, `ac`, `fl`
- `daylight` is the only daylight-hours key (do not use `sun`)
- Do not generate `rise` or `set`

## Guardrails
- Do not reintroduce a single monolithic destinations file.
- Do not silently change schema; update this AGENTS.md when schema changes.

## Migration workflow (pending -> live)
When moving staged records from `data/pending-locations/` to `data/locations/`:
1) Convert to full live schema required by this file (`desc`, `hls`, `todo`, `prac`, `sweet`, `months`).
2) Add/confirm entry in `data/locations/index.json`.
3) Ensure climate fields in `months` match uploaded CSV source values.
4) Set `source` metadata:
   - Verified only if CSV-backed month values match JSON.
   - Otherwise mark unverified with a concrete `climateVerificationNote`.
5) Remove the pending file once live file and index entry are in place.
6) Run all quality checks listed above.

## Enrichment batching policy
- Climate-source/provenance updates may be done in larger batches.
- Full destination enrichment (copy + practicals + costs/flights + todo research) should be done in small batches of up to **3 locations per task** to keep research quality high.
- For enriched entries, include practical and pricing depth (busyness, accommodation, flights from UK/Ireland, direct-flight notes where available) and keep claims evidence-backed.
