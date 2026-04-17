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

## 1) Upload CSV (GitHub Web)

1. Upload CSV to `data/climate/uploads/`.
2. If needed, update `data/climate/aliases.json` for misspellings/variants.
3. Commit upload to your working branch.

---

## 2) Run importer workflow

1. Open **Actions**.
2. Run **Import climate CSV (GitHub Web friendly)**.
3. Inputs:
   - `csv_path`: e.g. `data/climate/uploads/batch-2026-04.csv`
   - `mode`:
     - `stage` (recommended first): unknown locations go to pending only
     - `create`: directly creates live location files
   - `fuzzy_cutoff`: start at `0.84` (lower if spelling is noisy)

---

## 3) Promote staged locations to live (recommended path)

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

## 4) Enrich in small batches (max 3 locations)

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

---

## 5) Climate verification (required target state: all verified)

For each location file:

1. Verify climate source linkage exists in `source.climate`.
2. Run provenance check:
   - `python3 scripts/verify_climate_provenance.py`
3. Only set `source.climateVerified: true` if values match linked CSV rows.
4. If not matched:
   - keep `climateVerified: false`
   - add concrete `climateVerificationNote`.

---

## 6) Contract checks before merge

Run:

- `python3 scripts/validate_locations.py`
- `python3 scripts/verify_climate_provenance.py`

Also manually confirm:

- no duplicate ids
- every `index.json` id has a matching file
- every file id matches filename
- new locations open in app without payload errors

---

## 6a) Essentials field specificity checklist (`prac` remediation)

Use this before submitting any new or edited destination.

- `prac.visa`
  - ✅ Good: “UK/IE passport holders can enter Japan visa-free for short stays (up to 90 days); always verify latest Ministry guidance before travel.”
  - ❌ Bad: “Always verify entry rules before travel.”
- `prac.currency`
  - ✅ Good: “Japanese yen (JPY); cards widely accepted in cities, but carry cash for smaller inns/temples.”
  - ❌ Bad: “Local currency.”
- `prac.lang`
  - ✅ Good: “Japanese is the main language; English signage is common in major transport hubs.”
  - ❌ Bad: “Local language plus variable English.”
- `prac.tz`
  - ✅ Good: “Asia/Tokyo (UTC+9), no daylight saving.”
  - ❌ Bad: “See destination local timezone.”

When in doubt, include at least one concrete anchor in each field:
- visa policy type + nationality context,
- currency name and/or ISO code,
- named language(s),
- IANA timezone and/or UTC offset.

---

## 7) App smoke check

1. Open app.
2. Click each newly added location.
3. Confirm no “Could not load destination details”.
4. Confirm tabs load, climate table shows 12 months, and practical info renders.

---

## 8) Release discipline

- Merge climate-only imports first if needed.
- Then do enrichment PRs in small, reviewable batches.
- Never mix huge climate + deep copy + schema refactors in one PR.
