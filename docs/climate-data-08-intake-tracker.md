# Climate Data 08 intake tracker

Source CSV: `data/climate/uploads/Climate_Date_08 - Climate Data.csv`

Created: 2026-04-24

## Rules for this intake

- Stage at most 5 locations per action/prompt.
- Promote staged records to live files only after climate rows are confirmed against the source CSV.
- Enrich live destinations in batches of at most 3 locations.
- When a location is fully promoted, enriched, validated, and provenance-checked, remove it from the active queue table and append it to the completed log.
- Do not bulk import this CSV: preflight found fuzzy matches that could overwrite unrelated live files.

## State meanings

- `not staged`: no pending JSON exists yet.
- `staged`: pending JSON exists in `data/pending-locations/`.
- `live exists`: the CSV location matched an existing live location; decide whether this is a climate refresh or duplicate before touching it.
- `blocked`: needs a routing/name decision before staging or importing.
- `complete`: live file exists, index entry matches, enrichment checklist passed, JSON validation passed, and climate provenance passed.

## Preflight summary

Command used:

```bash
python3 scripts/plan_climate_import.py --input-file 'data/climate/uploads/Climate_Date_08 - Climate Data.csv' --mode stage
```

Summary:

- Total CSV locations: 64
- Month rows per location: 12
- Exact live matches: 2 (`bishkek-kyrgyzstan`, `salento-colombia`)
- Fuzzy matches requiring manual routing: 3 (`aktau-kazakhstan`, `jajce-bosnia-and-herzegovina`, `blagaj-bosnia-and-herzegovina`)
- Unknown/new stage candidates: 59
- **Batch 11 complete (5 locations promoted and enriched): `paraty-brazil`, `lijiang-china`, `chefchaouene-morocco`, `siwa-oasis-egypt`, `lamu-kenya`**

## Active queue

| # | staging batch | id | CSV location | rows | state | next action |
|---:|---:|---|---|---:|---|---|
| 34 | 7 | `bishkek-kyrgyzstan` | Bishkek, Kyrgyzstan | 12 | live exists | existing live file; decide whether CSV refresh is intended |
| 36 | 8 | `aktau-kazakhstan` | Aktau, Kazakhstan | 12 | blocked | routing decision: preflight fuzzy-matches `astana`; do not bulk import |
| 39 | 8 | `bagan-myanmar` | Bagan, Myanmar | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 40 | 8 | `jajce-bosnia-and-herzegovina` | Jajce, Bosnia and Herzegovina | 12 | blocked | routing decision: preflight fuzzy-matches `sarajevo-bosnia-and-herzegovina` |
| 41 | 9 | `blagaj-bosnia-and-herzegovina` | Blagaj, Bosnia and Herzegovina | 12 | blocked | routing decision: preflight fuzzy-matches `sarajevo-bosnia-and-herzegovina` |
| 45 | 9 | `sibenik-croatia` | Sibenik, Croatia | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 46 | 10 | `matera-italy` | Matera, Italy | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 47 | 10 | `orvieto-italy` | Orvieto, Italy | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 48 | 10 | `cadaques-spain` | Cadaques, Spain | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 49 | 10 | `cuenca-spain` | Cuenca, Spain | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 50 | 10 | `tavira-portugal` | Tavira, Portugal | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 56 | 12 | `villa-de-leiva-colombia` | Villa de Leiva, Colombia | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 57 | 12 | `jardin-colombia` | Jardin, Colombia | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 58 | 12 | `san-carlos-de-bariloche-argentina` | San Carlos de Bariloche, Argentina | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 59 | 12 | `puerto-varas-chile` | Puerto, Varas, Chile | 12 | not staged | stage pending JSON in a max-5 staging batch; CSV comma split/name review: Puerto Varas |
| 60 | 12 | `salento-colombia` | Salento, Colombia | 12 | live exists | existing live file; decide whether CSV refresh is intended |
| 61 | 13 | `sucre-bolivia` | Sucre, Bolivia | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 62 | 13 | `murren-switzerland` | Murren, Switzerland | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 63 | 13 | `lauterbrunnen-switzerland` | Lauterbrunnen, Switzerland | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 64 | 13 | `ushguli-georgia` | Ushguli, Georgia | 12 | not staged | stage pending JSON in a max-5 staging batch |

## Completion log

Move rows here only after full live promotion, enrichment, validation, and climate provenance verification.

| completed on | id | live file | notes |
|---|---|---|---|
| 2026-04-25 | `mestia-georgia` | `data/locations/mestia-georgia.json` | Promoted from batch 9, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-25 | `stepantsminda-georgia` | `data/locations/stepantsminda-georgia.json` | Promoted from batch 9, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-25 | `piran-slovenia` | `data/locations/piran-slovenia.json` | Promoted from batch 9, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-25 | `khiva-uzbekistan` | `data/locations/khiva-uzbekistan.json` | Promoted from staged `khiwa-uzbekistan`, corrected to canonical Khiva spelling, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-25 | `panjakent-tajikistan` | `data/locations/panjakent-tajikistan.json` | Promoted from batch 8, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-25 | `tataouine-tunisia` | `data/locations/tataouine-tunisia.json` | Promoted from batch 8, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-25 | `paraty-brazil` | `data/locations/paraty-brazil.json` | Promoted from batch 11, enriched with Brazil-specific content, index-added, pending file removed, climate provenance verified. |
| 2026-04-25 | `lijiang-china` | `data/locations/lijiang-china.json` | Promoted from batch 11, enriched with Yunnan heritage and trekking focus, index-added, pending file removed, climate provenance verified. |
| 2026-04-25 | `chefchaouene-morocco` | `data/locations/chefchaouene-morocco.json` | Promoted from batch 11, enriched with Rif mountain context, index-added, pending file removed, climate provenance verified. |
| 2026-04-25 | `siwa-oasis-egypt` | `data/locations/siwa-oasis-egypt.json` | Promoted from batch 11, enriched with desert isolation and Siwan culture emphasis, index-added, pending file removed, climate provenance verified. |
| 2026-04-25 | `lamu-kenya` | `data/locations/lamu-kenya.json` | Promoted from batch 11, enriched with Swahili heritage and dhow sailing emphasis, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `capri-italy` | `data/locations/capri-italy.json` | Promoted from batch 5, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `miskolc-hungary` | `data/locations/miskolc-hungary.json` | Promoted from batch 5, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `natal-brazil` | `data/locations/natal-brazil.json` | Promoted from batch 5, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `anchorage-alaska-united-states` | `data/locations/anchorage-alaska-united-states.json` | Promoted from staged `anchorage-alaska`, normalized to repo U.S. naming, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `motovun-croatia` | `data/locations/motovun-croatia.json` | Promoted from staged `motovan-croatia`, corrected to canonical Motovun spelling, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `ushuaia-argentina` | `data/locations/ushuaia-argentina.json` | Promoted from batch 6, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `gordes-france` | `data/locations/gordes-france.json` | Promoted from batch 1, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `gjirokaster-albania` | `data/locations/gjirokaster-albania.json` | Promoted from batch 1, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `gallipoli-italy` | `data/locations/gallipoli-italy.json` | Promoted from batch 1, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `moab-utah-united-states` | `data/locations/moab-utah-united-states.json` | Promoted from staged `moab-usa`, normalized to repo U.S. naming, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `aspen-colorado-united-states` | `data/locations/aspen-colorado-united-states.json` | Promoted from staged `aspen-usa`, normalized to repo U.S. naming, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `burlington-vermont-united-states` | `data/locations/burlington-vermont-united-states.json` | Promoted from staged `burlington-usa`, normalized to repo U.S. naming, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `hangzhou-china` | `data/locations/hangzhou-china.json` | Promoted from staged `huangzhou-china`, corrected to canonical Hangzhou spelling, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `lyon-france` | `data/locations/lyon-france.json` | Promoted from batch 2, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `rotterdam-netherlands` | `data/locations/rotterdam-netherlands.json` | Promoted from batch 2, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `amsterdam-netherlands` | `data/locations/amsterdam-netherlands.json` | Promoted from batch 2, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `bruges-belgium` | `data/locations/bruges-belgium.json` | Promoted from batch 3, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `busan-south-korea` | `data/locations/busan-south-korea.json` | Promoted from batch 3, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `doha-qatar` | `data/locations/doha-qatar.json` | Promoted from batch 3, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `suchitoto-el-salvador` | `data/locations/suchitoto-el-salvador.json` | Promoted from batch 3, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `angra-dos-reis-brazil` | `data/locations/angra-dos-reis-brazil.json` | Promoted from batch 3, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `charlestown-saint-kitts-and-nevis` | `data/locations/charlestown-saint-kitts-and-nevis.json` | Promoted from staged `charkestown-st-kitts-nevis`, corrected to Charlestown and normalized country naming, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `skardu-pakistan` | `data/locations/skardu-pakistan.json` | Promoted from batch 4, normalized staged `Skārdu` city spelling to ASCII `Skardu`, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `osh-kyrgyzstan` | `data/locations/osh-kyrgyzstan.json` | Promoted from batch 4, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `lucerne-switzerland` | `data/locations/lucerne-switzerland.json` | Promoted from batch 4, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `bolzano-italy` | `data/locations/bolzano-italy.json` | Promoted from batch 4, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `petra-jordan` | `data/locations/petra-jordan.json` | Promoted from batch 6, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `meissen-germany` | `data/locations/meissen-germany.json` | Promoted from batch 6, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `praiano-italy` | `data/locations/praiano-italy.json` | Promoted from staged `postiano-italy`, corrected to Praiano after source review, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `mardin-turkey` | `data/locations/mardin-turkey.json` | Promoted from batch 6, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `hopa-turkey` | `data/locations/hopa-turkey.json` | Promoted from batch 7, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `almaty-kazakhstan` | `data/locations/almaty-kazakhstan.json` | Promoted from batch 7, enriched, index-added, pending file removed, climate provenance verified. |
| 2026-04-24 | `karakol-kyrgyzstan` | `data/locations/karakol-kyrgyzstan.json` | Promoted from batch 7, enriched, index-added, pending file removed, climate provenance verified. |
