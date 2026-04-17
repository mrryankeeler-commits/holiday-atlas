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
- `id`, `city`, `country`, `region`, `lat`, `lng`

### <id>.json required fields
- `id`, `city`, `country`, `region`, `desc`, `hls`, `todo`, `prac`, `sweet`, `months`

## Quality checks (before commit)
- JSON files parse
- Every `index.json` id has a corresponding `data/locations/<id>.json`
- Every location file id matches filename
- No duplicate ids
- Generic-content check passes in `scripts/validate_locations.py`:
  - Top-level `desc` and `sweet` must be destination-specific (no known boilerplate templates).
  - `prac.bestFor[]` entries must be destination-specific (no generic audience tags/templates).
  - `hls[]` and `todo[].desc` are checked against known template signatures and fail when matched.
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

## Required author/reviewer checklist (new destinations + enrichment edits)
This checklist is mandatory for **both**:
- new destination additions, and
- enrichment edits to existing destinations.

Before approval/merge, confirm all of the following:
- `prac.airports` contains at least one realistic airport and includes distance information.
- `region` is specific to the destination context (not a country-generic placeholder).
- `prac.alerts` is destination-specific and not copied boilerplate.
- `prac.fltNote` references route seasonality and/or transfer reality for that destination.
- Metadata in `data/locations/index.json` matches the corresponding location file (`id`, `city`, `country`, `region`, `lat`, `lng`).

## Direct-flight semantics (destination vs gateway)
- `prac.directFrom` is the destination-level nonstop truth map used by the renderer for route badges.
  - Keep keys aligned with UI departure codes (`LGW`, `LCY`) and store booleans.
  - Set `true` only when there is a realistic nonstop from that origin to the destination itself.
- `prac.airports[*].directFrom` is airport-level metadata for each listed gateway airport.
  - Do not use airport-level `directFrom` to imply destination-level nonstop availability.
- `prac.directGW` is legacy and should mirror `prac.directFrom.LGW` only when the destination itself has LGW nonstop service.
- If `prac.fltNote` says the destination has no airport or no practical direct/nonstop routing, destination-level direct flags must be `false`.

## Seasonality scoring provenance + rubric
When a location file includes month-level `busy`, `ac`, and `fl` values, keep a consistent provenance object at `source.scoring`.

### `source.scoring` required structure
- `reviewedOn`: ISO date (`YYYY-MM-DD`) for the most recent rubric/source review.
- `profile`: shared scoring profile identifier (current: `seasonality-inference-v1`).
- Optional `overrides`: only include when this location does **not** follow the default profile.
  - May override `signals` sources and/or scoring notes for `busy`, `ac`, `fl`.

### Default scoring profile (`seasonality-inference-v1`)
Use this as the default for all destinations unless there is a clear exception.

#### Source inputs by metric
- `busy`: inferred from destination seasonality baseline + climate comfort window (`hi/lo`, `rain`, `cld`, `daylight`) + known event/holiday peaks when evidence exists.
- `ac`: inferred from `busy` pattern, destination accommodation market seasonality, and shoulder/off-season compression.
- `fl`: inferred from UK flight seasonality pattern (school holidays + summer peaks) and destination route seasonality context.

#### Scoring rubric (keep criteria consistent)
- `busy` (1–10): relative in-destination monthly tourism pressure (crowding/queue intensity).  
  `1` = very quiet off-season, `10` = peak crowding month.
- `ac` (1–5): relative in-destination monthly accommodation price pressure.  
  `1` = lowest seasonal pricing pressure, `5` = highest.
- `fl` (1–5): relative monthly UK-origin flight seasonality pressure for the destination.  
  `1` = lowest UK flight price/competition pressure, `5` = highest.

#### Normalization rule
- Use destination-relative monthly normalization (within the same destination, not globally across all destinations):
  1) rank the 12 monthly raw signals for each metric,  
  2) bucket into ordinal bands,  
  3) map to integer output scale (`busy`: 1–10, `ac`: 1–5, `fl`: 1–5),  
  4) clamp outliers to scale bounds,  
  5) keep ties in the same band.

Store these definitions here in `AGENTS.md` (single source of truth). Location files should reference the shared profile and only add `overrides` when needed.
