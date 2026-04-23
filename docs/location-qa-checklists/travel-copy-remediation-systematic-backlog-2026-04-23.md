# Travel Copy Remediation Backlog — 2026-04-23

Audit source:
- `python3 scripts/audit_travel_copy.py`

Current backlog snapshot:
- `36` locations with generic `desc`
- `36` locations with generic `prac.wifi.note`
- `21` locations with generic `visa`
- `21` locations with flight-note wording flagged for manual review

Working rule for systematic enrichment:
1. Fix locations that appear in the most audit buckets first.
2. Group by geography where possible so route, visa and practical research can be reused.
3. Keep enrichment passes to `3` locations per task to match repo guidance in `AGENTS.md`.
4. In each pass, check `desc`, `todo`, `wifi`, `visa`, `fltNote`, airport metadata, `bestFor`, `alerts`, and `sweet`.

## Priority A
Locations with generic `desc`, generic `wifi`, generic `visa`, and flagged `fltNote`.

- `fethiye-turkey`
- `leon-nicaragua`
- `livno-bosnia-and-herzegovina`
- `neum-bosnia-and-herzegovina`
- `quellon-chile`
- `taroudant-morocco`
- `theth-albania`
- `trebizat-bosnia-and-herzegovina`
- `tyre-lebanon`
- `yerevan-armenia`

## Priority B
Locations with generic `desc`, generic `wifi`, and generic `visa`.

- `el-nido-philippines`
- `gaziantep-turkey`
- `granada-nicaragua`
- `kuta-lombok-indonesia`
- `muscat-oman`
- `phetchaburi-thailand`
- `sapporo-japan`
- `sidi-bou-said-tunisia`
- `taipei-taiwan`
- `valdivia-chile`
- `windhoek-namibia`

## Priority C
Locations with generic `desc`, generic `wifi`, and flagged `fltNote`.

- `hallstatt-austria`
- `rovinj-croatia`
- `terracina-italy`
- `zug-switzerland`

## Priority D
Locations with generic `desc` and generic `wifi` only.

- `gothenburg-sweden`
- `hadibu-yemen`
- `kuressaare-estonia`
- `larnaca-cyprus`
- `liepaja-latvia`
- `naxos-greece`
- `rauma-finland`
- `siena-italy`
- `timbuktu-mali`
- `tromso-norway`
- `villach-austria`

## Priority E
Locations with flight-note wording still flagged but no current generic copy signature.

- `alkmaar-netherlands`
- `beirut-lebanon`
- `bled`
- `minca-colombia`
- `torshavn-faroe-islands`
- `vinales-cuba`
- `zakopane`

## Suggested Batch Order
These batches aim to maximize overlap reduction while keeping research coherent.

### Batch 1
- `fethiye-turkey`
- `tyre-lebanon`
- `yerevan-armenia`

Focus:
- high-risk visa wording
- route truth from UK gateways
- destination-specific practical alerts

### Batch 2
- `livno-bosnia-and-herzegovina`
- `neum-bosnia-and-herzegovina`
- `trebizat-bosnia-and-herzegovina`

Focus:
- shared Bosnia entry/access research
- realistic airport-transfer logic
- removing repeated inland/Herzegovina boilerplate

### Batch 3
- `theth-albania`
- `hallstatt-austria`
- `zug-switzerland`

Focus:
- mountain/lake rail-transfer truth
- non-airport destination wording
- shoulder-season practicals

### Batch 4
- `leon-nicaragua`
- `granada-nicaragua`
- `el-nido-philippines`

Focus:
- long-haul transfer reality
- visa wording
- destination-specific wifi and town-vs-island practicals

### Batch 5
- `quellon-chile`
- `valdivia-chile`
- `taroudant-morocco`

Focus:
- remote-transfer logic
- bus/road practicality
- shoulder-season and weather-driven access notes

### Batch 6
- `muscat-oman`
- `windhoek-namibia`
- `taipei-taiwan`

Focus:
- major-hub airport truth
- current visa wording
- urban practicals and connectivity nuance

### Batch 7
- `kuta-lombok-indonesia`
- `phetchaburi-thailand`
- `sapporo-japan`

Focus:
- airport-plus-transfer routing
- seasonal flight pressure
- destination-specific sweet spots

### Batch 8
- `gaziantep-turkey`
- `sidi-bou-said-tunisia`
- `larnaca-cyprus`

Focus:
- eastern Med entry/access wording
- city-break vs resort practicals
- direct-flight truth at destination vs airport level

### Batch 9
- `rovinj-croatia`
- `terracina-italy`
- `naxos-greece`

Focus:
- ferry/airport split logic
- coastal seasonality
- car-light vs transfer-heavy positioning

### Batch 10
- `gothenburg-sweden`
- `kuressaare-estonia`
- `liepaja-latvia`

Focus:
- Baltic/Nordic connectivity
- shoulder-season daylight framing
- cleaner city/coast differentiation

### Batch 11
- `rauma-finland`
- `tromso-norway`
- `villach-austria`

Focus:
- northern rail and airport practicals
- winter vs shoulder-season specificity
- replacing generic climate-led copy

### Batch 12
- `hadibu-yemen`
- `timbuktu-mali`
- `beirut-lebanon`

Focus:
- safety-sensitive wording
- extra-careful visa/practical notes
- flight/access caveats

### Batch 13
- `alkmaar-netherlands`
- `bled`
- `zakopane`

Focus:
- flight-note cleanup only
- keep existing good copy
- verify airport-level direct flags

### Batch 14
- `minca-colombia`
- `torshavn-faroe-islands`
- `vinales-cuba`

Focus:
- flight-note cleanup only
- transfer reality and gateway wording

## Per-Location Enrichment Checklist
Use this every time before marking a destination done.

- [ ] `desc` is destination-specific and no longer matches audit signature wording
- [ ] `prac.wifi.note` is specific to likely stays and terrain/building realities
- [ ] `visa` reflects current country-specific entry rules
- [ ] `prac.fltNote` reflects actual airport or transfer reality
- [ ] destination-level `directFrom` remains distinct from airport-level `directFrom`
- [ ] `todo` includes at least `6` destination-specific entries where appropriate
- [ ] `bestFor` and `alerts` are destination-specific
- [ ] `sweet` reflects the destination rather than a generic climate phrase
- [ ] `python3 scripts/validate_locations.py`
- [ ] `python3 scripts/verify_climate_provenance.py`
- [ ] `python3 scripts/audit_locations.py --fail-on-high`
- [ ] `python3 scripts/audit_travel_copy.py`
