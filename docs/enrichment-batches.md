# Enrichment country-patch tracker

Use this tracker for enrichment planning by **country patch** rather than fixed location IDs. Keep each patch to **up to 3 locations** to match AGENTS policy and stay flexible as new locations are added.

## Depth target

Use **Dubrovnik** as the baseline depth/quality reference for “done enough for now”.

## Two-pass flow

- **Pass 1 = research + update**: enrich up to 3 locations in the chosen country patch.
- **Pass 2 = independent consistency recheck**: re-validate against rubric and neighboring-month consistency before sign-off.

## Country patch queue (live coverage snapshot)

Create/assign patches in this format: `Country - Patch N (up to 3 locations)`

| Country | Live locations now | Patch status |
|---|---:|---|
| Italy | 6 | [ ] Planned |
| Poland | 4 | [ ] Planned |
| China | 3 | [ ] Planned |
| India | 3 | [ ] Planned |
| Montenegro | 3 | [ ] Planned |
| Spain | 3 | [ ] Planned |
| Sri Lanka | 3 | [ ] Planned |
| Egypt | 2 | [ ] Planned |
| Greece | 2 | [ ] Planned |
| Portugal | 2 | [ ] Planned |
| Turkey | 2 | [ ] Planned |
| Albania | 1 | [ ] Planned |
| Andorra | 1 | [ ] Planned |
| Austria | 1 | [ ] Planned |
| Bosnia & Herzegovina | 1 | [ ] Planned |
| Bulgaria | 1 | [ ] Planned |
| Croatia | 1 | [ ] Planned |
| Cyprus | 1 | [ ] Planned |
| Czechia | 1 | [ ] Planned |
| Denmark | 1 | [ ] Planned |
| Estonia | 1 | [ ] Planned |
| Georgia | 1 | [ ] Planned |
| Germany | 1 | [ ] Planned |
| Guatemala | 1 | [ ] Planned |
| Hungary | 1 | [ ] Planned |
| Japan | 1 | [ ] Planned |
| Kazakhstan | 1 | [ ] Planned |
| Latvia | 1 | [ ] Planned |
| Malta | 1 | [ ] Planned |
| Morocco | 1 | [ ] Planned |
| Norway | 1 | [ ] Planned |
| Slovakia | 1 | [ ] Planned |
| Slovenia | 1 | [ ] Planned |
| Switzerland | 1 | [ ] Planned |
| Tanzania | 1 | [ ] Planned |
| Uzbekistan | 1 | [ ] Planned |
| Vietnam | 1 | [ ] Planned |

## Patch template (copy per patch)

### `<Country> - Patch <N>` (up to 3 locations)

- Locations in this patch: `<id-1>`, `<id-2>`, `<id-3>`

#### Core enrichment completeness
- [ ] description reviewed (`desc`) — clear positioning + seasonality context
- [ ] highlights reviewed (`hls`) — concise, concrete, non-generic
- [ ] things-to-do reviewed (`todo`) — practical and distinct, not repetition
- [ ] practicals reviewed (`prac`) — visa/lang/currency/tz/bestFor/alerts present and sensible
- [ ] Wi-Fi notes reviewed (`prac.wifi`)
- [ ] UK flight notes reviewed (`prac.fltNote`, `prac.directGW`)
- [ ] nearest airports reviewed (`prac.airports`) — include multiple nearest options where relevant
- [ ] sweet spot reviewed (`sweet`)

#### Pricing + access signals
- [ ] monthly `busy/ac/fl` reviewed across all months
- [ ] flight price guidance included in notes (`prac.fltNote`) as a rough band/trend (not exact fare guarantees)
- [ ] direct-flight reality check for Gatwick/UK notes completed (`prac.directGW`, `prac.fltNote`)

#### Scoring provenance alignment (`source.scoring`)
- [ ] `source.scoring.reviewedOn` updated (ISO date)
- [ ] `source.scoring.profile` confirmed as `seasonality-inference-v1` (or override documented)
- [ ] any `source.scoring.overrides` clearly justified and limited to real exceptions
- [ ] normalization/rubric sanity check completed (`busy` 1–10, `ac` 1–5, `fl` 1–5; destination-relative month ranking)

#### Pass 2 QA (independent check)
- [ ] neighboring-month consistency recheck completed (no abrupt unexplained jumps)
- [ ] rubric consistency recheck completed against Dubrovnik-level baseline
- [ ] second-pass QA completed
