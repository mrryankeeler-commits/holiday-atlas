# Location QA Checklist — Generic Content Remediation 2026-04-17 (Batch 2)

- Batch doc: `docs/generic-content-remediation-2026-04-17.md`
- Batch ID: `generic-content-remediation-2026-04-17 / batch-2`
- Reviewed on (YYYY-MM-DD):
- Author:
- Reviewer:
- Audit command: `python3 scripts/audit_locations.py --fail-on-high`

## Destination: `rio-de-janeiro-brazil`

- [ ] ✅ / ❌ **desc/hls/todo specificity**
- [ ] ✅ / ❌ **bestFor specificity**
- [ ] ✅ / ❌ **entry/essentials specificity**
- [ ] ✅ / ❌ **direct-flight truthfulness vs gateway routing**
- [ ] ✅ / ❌ **climate provenance verified**

### Notes / remediation actions
-

## Destination: `asuncion-paraguay`

- [ ] ✅ / ❌ **desc/hls/todo specificity**
- [ ] ✅ / ❌ **bestFor specificity**
- [ ] ✅ / ❌ **entry/essentials specificity**
- [ ] ✅ / ❌ **direct-flight truthfulness vs gateway routing**
- [ ] ✅ / ❌ **climate provenance verified**

### Notes / remediation actions
-

## Destination: `tilcara-argentina`

- [ ] ✅ / ❌ **desc/hls/todo specificity**
- [ ] ✅ / ❌ **bestFor specificity**
- [ ] ✅ / ❌ **entry/essentials specificity**
- [ ] ✅ / ❌ **direct-flight truthfulness vs gateway routing**
- [ ] ✅ / ❌ **climate provenance verified**

### Notes / remediation actions
-

## Evidence
- Files reviewed:
  - `data/locations/<id>.json`
  - `data/locations/index.json`
- Commands run:
  - `python3 scripts/validate_locations.py`
  - `python3 scripts/verify_climate_provenance.py`
  - `python3 scripts/audit_locations.py --fail-on-high`
