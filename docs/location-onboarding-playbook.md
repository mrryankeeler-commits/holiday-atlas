# Holiday Atlas – New Location CSV + Enrichment Playbook

Use this checklist every time you add new destinations.

## 0) Golden rules (must always hold)

- `data/locations/index.json` is the manifest.
- Each location lives in `data/locations/<id>.json`.
- `id` must be lowercase kebab-case and match filename.
- Month keys must be exactly:
  - `m`, `avg`, `hi`, `lo`, `daylight`, `cld`, `rain`, `busy`, `ac`, `fl`
- Do not use `sun`, `rise`, or `set` month keys.
- Keep enrichment batches small: **max 3 locations per task**.

---

## 1) Preferred local mixed-CSV intake flow

Use this as the default local workflow for a new mixed climate CSV.

1. Put the CSV in `data/climate/uploads/`.
2. Update `data/climate/aliases.json` first if you already know about spelling variants or alternate IDs.
3. Run preflight before importing:
   - `python3 scripts/plan_climate_import.py --input-file 'data/climate/uploads/batch.csv' --mode stage`
4. Run the local intake wrapper:
   - `python3 scripts/run_location_intake.py --input-file 'data/climate/uploads/batch.csv' --write-reports`
5. Review what still needs real work:
   - `python3 scripts/plan_enrichment_batch.py`
6. Review queue/checklist drift separately:
   - `python3 scripts/reconcile_enrichment_queue.py`

### Script roles

- `scripts/plan_climate_import.py`
  - Preflight preview only. Use it to catch fuzzy matches, unknown locations, and incomplete month coverage before writing files.
- `scripts/run_location_intake.py`
  - Preferred local wrapper for mixed CSV intake. It runs preflight first, imports only if the plan passes, then runs validation, provenance verification, audit, and enrichment planning.
- `scripts/plan_enrichment_batch.py`
  - Shows locations that still have real enrichment reasons. Queue membership by itself is not treated as enrichment-needed.
- `scripts/reconcile_enrichment_queue.py`
  - Dry-run helper for queue/checklist drift. Use it after review work to identify queue-only pending locations that are safe manual cleanup candidates.

---

## 2) Upload CSV (GitHub Web)

1. Upload CSV to `data/climate/uploads/`.
2. If needed, update `data/climate/aliases.json` for misspellings/variants.
3. Commit upload to your working branch.

---

## 3) Run importer workflow

1. Open **Actions**.
2. Run **Import climate CSV (GitHub Web friendly)**.
3. Inputs:
   - `csv_path`: e.g. `data/climate/uploads/batch-2026-04.csv`
   - `mode`:
     - `stage` (recommended first): unknown locations go to pending only
     - `create`: directly creates live location files
   - `fuzzy_cutoff`: start at `0.84` (lower if spelling is noisy)

---

## 4) Promote staged locations to live (recommended path)

For each location promoted from pending:

1. Create/update `data/locations/<id>.json`.
2. Add/update entry in `data/locations/index.json`.
3. Ensure full live schema exists:
   - Manifest entry (`data/locations/index.json`): `id`, `city`, `country`, `region`, `lat`, `lng`
   - Top-level location file (`data/locations/<id>.json`): `id`, `city`, `country`, `region`, `desc`, `hls`, `todo`, `prac`, `sweet`, `months`
4. Ensure `prac` is complete:
   - `directGW` (boolean)
   - `visa`, `currency`, `lang`, `tz`, `fltNote`
   - `alerts` (array)
   - `airports` (array with nearest airport objects)
   - `bestFor` (array)
   - `wifi` object with expected keys
5. Remove pending file after live version is correct.

---

## 5) Enrich in small batches (max 3 locations)

For each location in batch:

1. Fill `desc` and `hls` with useful traveler-facing content.
2. Add structured `todo` items (not plain strings if your UI expects objects).
3. Add practical info depth:
   - nearest airports + transfer notes
   - visa and currency
   - language/timezone/power
   - connectivity and safety notes
4. Add “best for” tags (e.g. beaches, hiking, budget city break).
5. Add/confirm `source.scoring`:
   - `reviewedOn` (ISO date)
   - `profile`: `seasonality-inference-v1`

### Proven review rhythm

Use this process rhythm while the editorial bar is still being applied by review judgment rather than a final frozen checklist:

1. Review 5 live `data/locations/<id>.json` files against the actual payloads, not just the queue markdown.
2. Fix the weak ones immediately.
3. Mark only the safe ones complete in the tracking files.
4. Re-run:
   - `python3 scripts/plan_enrichment_batch.py`
   - `python3 scripts/reconcile_enrichment_queue.py`
5. Move to the next 5.

---

## 6) Climate verification (required target state: all verified)

For each location file:

1. Verify climate source linkage exists in `source.climate`.
2. Run provenance check:
   - `python3 scripts/verify_climate_provenance.py`
3. Only set `source.climateVerified: true` if values match linked CSV rows.
4. If not matched:
   - keep `climateVerified: false`
   - add concrete `climateVerificationNote`.

---

## 7) Contract checks before merge

Run:

- `python3 scripts/validate_locations.py`
- `python3 scripts/verify_climate_provenance.py`

Also manually confirm:

- no duplicate ids
- every `index.json` id has a matching file
- every file id matches filename
- new locations open in app without payload errors

### Essentials-field remediation checklist (good vs bad examples)

Use this when validation flags `prac.visa`, `prac.currency`, `prac.lang`, or `prac.tz` as generic.

- `prac.tz`
  - ✅ Good: `Europe/Lisbon (UTC+0 winter, UTC+1 summer)`
  - ❌ Bad: `see destination local timezone`
  - Rule: include a real timezone identifier and/or a concrete UTC/GMT offset clue.

- `prac.lang`
  - ✅ Good: `Portuguese; English common in tourist areas`
  - ❌ Bad: `local language plus variable English`
  - Rule: name real language(s), then add English-usage nuance.

- `prac.visa`
  - ✅ Good: `UK and Irish passport holders can enter visa-free for up to 90 days; always verify latest rules.`
  - ❌ Bad: `Always verify entry rules before travel.`
  - Rule: include country/passport policy context (who, what permission type, and often duration), not only a generic warning.

- `prac.currency`
  - ✅ Good: `Euro (EUR); cards widely accepted, cash useful in small towns`
  - ❌ Bad: `standard`
  - Rule: name the local currency explicitly and optionally add practical payment context.

---

## 8) App smoke check

1. Open app.
2. Click each newly added location.
3. Confirm no “Could not load destination details”.
4. Confirm tabs load, climate table shows 12 months, and practical info renders.

---

## 9) Release discipline

- Merge climate-only imports first if needed.
- Then do enrichment PRs in small, reviewable batches.
- Never mix huge climate + deep copy + schema refactors in one PR.
