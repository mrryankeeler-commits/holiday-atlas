# Travel Copy Remediation Backlog — 2026-04-23

This document is the active single source of truth for the repo-wide travel-copy remediation track.

Audit source:
- `python3 scripts/audit_travel_copy.py`

Last reviewed:
- `2026-04-24`

## Current Status

Current audit snapshot:
- `0` locations with generic `desc`
- `0` locations with generic `prac.wifi.note`
- `0` locations with generic `visa`
- `1` location with flight-note wording still flagged for manual review

Remaining audit target:
- `vinales-cuba`

## Completion Summary

Completed remediation batches:
- Batch 1: `fethiye-turkey`, `tyre-lebanon`, `yerevan-armenia`
- Batch 2: `livno-bosnia-and-herzegovina`, `neum-bosnia-and-herzegovina`, `trebizat-bosnia-and-herzegovina`
- Batch 3: `theth-albania`, `hallstatt-austria`, `zug-switzerland`
- Batch 4: `leon-nicaragua`, `granada-nicaragua`, `el-nido-philippines`
- Batch 5: `quellon-chile`, `valdivia-chile`, `taroudant-morocco`
- Batch 6: `muscat-oman`, `windhoek-namibia`, `taipei-taiwan`
- Batch 7: `kuta-lombok-indonesia`, `phetchaburi-thailand`, `sapporo-japan`
- Batch 8: `gaziantep-turkey`, `sidi-bou-said-tunisia`, `larnaca-cyprus`
- Batch 9: `rovinj-croatia`, `terracina-italy`, `naxos-greece`
- Batch 10: `gothenburg-sweden`, `kuressaare-estonia`, `liepaja-latvia`
- Batch 11: `rauma-finland`, `tromso-norway`, `villach-austria`
- Batch 12: `hadibu-yemen`, `timbuktu-mali`, `beirut-lebanon`
- Batch 13: `alkmaar-netherlands`, `bled`, `zakopane`

Batch 14 status:
- Done: `minca-colombia`, `torshavn-faroe-islands`
- Remaining: `vinales-cuba`

## Active Queue

### Next Batch
- `vinales-cuba`

Focus:
- flight-note cleanup only
- keep gateway-vs-destination nonstop semantics explicit
- preserve the stronger existing wifi/cash/transfer detail

## Workflow Rules

Working rule for systematic enrichment:
1. Keep enrichment passes to `3` locations per task to match repo guidance in `AGENTS.md`.
2. When a destination is flagged for flight-note review only, avoid unnecessary copy churn elsewhere.
3. In each pass, check `desc`, `todo`, `wifi`, `visa`, `fltNote`, airport metadata, `bestFor`, `alerts`, and `sweet`.
4. Keep destination-level `directFrom` distinct from airport-level `directFrom`.

## Validation Checklist

Use this before marking the remaining item done.

- [ ] `prac.fltNote` reflects actual airport or transfer reality
- [ ] destination-level `directFrom` remains distinct from airport-level `directFrom`
- [ ] airport-level `directFrom` flags match realistic gateway truth
- [ ] `python3 scripts/validate_locations.py`
- [ ] `python3 scripts/verify_climate_provenance.py`
- [ ] `python3 scripts/audit_locations.py --fail-on-high`
- [ ] `python3 scripts/audit_travel_copy.py`

## Notes

- The older April 17 generic-content remediation docs were historical planning artifacts for an earlier phase and have been superseded by this file.
- Keep any future remediation progress updates here rather than reviving separate batch-planning docs for the completed April 17 workstream.
