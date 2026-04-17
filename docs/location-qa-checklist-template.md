# Location QA Checklist Template

Use this checklist for each destination touched in a remediation/enrichment batch. Duplicate this file into `docs/location-qa-checklists/` and fill one section per destination.

## Batch metadata
- Batch doc: <!-- link to source batch plan -->
- Batch ID: <!-- e.g. generic-content-remediation-2026-04-17 / batch-1 -->
- Reviewed on (YYYY-MM-DD): <!-- date -->
- Author: <!-- handle/name -->
- Reviewer: <!-- handle/name -->
- Audit command: `python3 scripts/audit_locations.py --fail-on-high`

---

## Destination: `<id>`

- [ ] ✅ / ❌ **desc/hls/todo specificity**
  - `desc` is destination-specific (no generic boilerplate).
  - `hls[]` is destination-specific and materially true.
  - `todo[].desc` is destination-specific and actionable.

- [ ] ✅ / ❌ **bestFor specificity**
  - `prac.bestFor[]` avoids generic audience labels and reflects this destination.

- [ ] ✅ / ❌ **entry/essentials specificity**
  - `prac.entry` and `prac.essentials` are destination-specific and current enough for planning.

- [ ] ✅ / ❌ **direct-flight truthfulness vs gateway routing**
  - `prac.directFrom` only marks realistic destination-level nonstops as `true`.
  - `prac.airports[*].directFrom` is treated as gateway-level metadata only.
  - `prac.fltNote` matches nonstop/transfer reality and does not imply nonexistent nonstops.

- [ ] ✅ / ❌ **climate provenance verified**
  - `source.climateVerified` is `true` only when CSV-linked month values match JSON.
  - Climate verification note is present when not verified.

## Notes / remediation actions
- <!-- add concrete follow-up items -->

## Evidence
- Files reviewed:
  - `data/locations/<id>.json`
  - `data/locations/index.json` (metadata parity)
- Commands run:
  - `python3 scripts/validate_locations.py`
  - `python3 scripts/verify_climate_provenance.py`
  - `python3 scripts/audit_locations.py --fail-on-high`
