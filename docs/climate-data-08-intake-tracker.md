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

## Active queue

| # | staging batch | id | CSV location | rows | state | next action |
|---:|---:|---|---|---:|---|---|
| 1 | 1 | `gordes-france` | Gordes, France | 12 | staged | promote to live schema, then enrich in max-3 batch |
| 2 | 1 | `gjirokaster-albania` | Gjirokaster, Albania | 12 | staged | promote to live schema, then enrich in max-3 batch |
| 3 | 1 | `gallipoli-italy` | Gallipoli, Italy | 12 | staged | promote to live schema, then enrich in max-3 batch |
| 4 | 1 | `moab-usa` | Moab, USA | 12 | staged | promote to live schema, then enrich in max-3 batch |
| 5 | 1 | `aspen-usa` | Aspen, USA | 12 | staged | promote to live schema, then enrich in max-3 batch |
| 6 | 2 | `burlington-usa` | Burlington, USA | 12 | staged | promote to live schema, then enrich in max-3 batch |
| 7 | 2 | `huangzhou-china` | Huangzhou, China | 12 | staged | name review likely Hangzhou/Huangzhou; promote to live schema, then enrich in max-3 batch |
| 8 | 2 | `lyon-france` | Lyon, France | 12 | staged | promote to live schema, then enrich in max-3 batch |
| 9 | 2 | `rotterdam-netherlands` | Rotterdam, Netherlands | 12 | staged | promote to live schema, then enrich in max-3 batch |
| 10 | 2 | `amsterdam-netherlands` | Amsterdam, Netherlands | 12 | staged | promote to live schema, then enrich in max-3 batch |
| 11 | 3 | `bruges-belgium` | Bruges, Belgium | 12 | staged | promote to live schema, then enrich in max-3 batch |
| 12 | 3 | `busan-south-korea` | Busan, South Korea | 12 | staged | promote to live schema, then enrich in max-3 batch |
| 13 | 3 | `doha-qatar` | Doha, Qatar | 12 | staged | promote to live schema, then enrich in max-3 batch |
| 14 | 3 | `suchitoto-el-salvador` | Suchitoto, El Salvador | 12 | staged | promote to live schema, then enrich in max-3 batch |
| 15 | 3 | `angra-dos-reis-brazil` | Angra dos Reis, Brazil | 12 | staged | promote to live schema, then enrich in max-3 batch |
| 16 | 4 | `charkestown-st-kitts-nevis` | Charkestown, St. kitts & Nevis | 12 | staged | name/country capitalization review; promote to live schema, then enrich in max-3 batch |
| 17 | 4 | `skardu-pakistan` | Skardu, Pakistan | 12 | staged | diacritic/id review; promote to live schema, then enrich in max-3 batch |
| 18 | 4 | `osh-kyrgyzstan` | Osh, Kyrgyzstan | 12 | staged | promote to live schema, then enrich in max-3 batch |
| 19 | 4 | `lucerne-switzerland` | Lucerne, Switzerland | 12 | staged | promote to live schema, then enrich in max-3 batch |
| 20 | 4 | `bolzano-italy` | Bolzano, Italy | 12 | staged | promote to live schema, then enrich in max-3 batch |
| 21 | 5 | `miskolc-hungary` | Miskolc, Hungary | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 22 | 5 | `anchorage-alaska` | Anchorage, Alaska | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 23 | 5 | `motovan-croatia` | Motovan, Croatia | 12 | not staged | stage pending JSON in a max-5 staging batch; name review likely Motovun |
| 24 | 5 | `capri-italy` | Capri, Italy | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 25 | 5 | `natal-brazil` | Natal, Brazil | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 26 | 6 | `ushuaia-argentina` | Ushuaia, Argentina | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 27 | 6 | `petra-jordan` | Petra, Jordan | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 28 | 6 | `meissen-germany` | Meissen, Germany | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 29 | 6 | `postiano-italy` | Postiano, Italy | 12 | not staged | stage pending JSON in a max-5 staging batch; name review likely Positano |
| 30 | 6 | `mardin-turkey` | Mardin, Turkey | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 31 | 7 | `hopa-turkey` | Hopa, Turkey | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 32 | 7 | `almaty-kazakhstan` | Almaty, Kazakhstan | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 33 | 7 | `karakol-kyrgyzstan` | Karakol, Kyrgyzstan | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 34 | 7 | `bishkek-kyrgyzstan` | Bishkek, Kyrgyzstan | 12 | live exists | existing live file; decide whether CSV refresh is intended |
| 35 | 7 | `khiwa-uzbekistan` | Khiwa, Uzbekistan | 12 | not staged | stage pending JSON in a max-5 staging batch; name review likely Khiva |
| 36 | 8 | `aktau-kazakhstan` | Aktau, Kazakhstan | 12 | blocked | routing decision: preflight fuzzy-matches `astana`; do not bulk import |
| 37 | 8 | `panjakent-tajikistan` | Panjakent, Tajikistan | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 38 | 8 | `tataouine-tunisia` | Tataouine, Tunisia | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 39 | 8 | `bagan-myanmar` | Bagan, Myanmar | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 40 | 8 | `jajce-bosnia-and-herzegovina` | Jajce, Bosnia and Herzegovina | 12 | blocked | routing decision: preflight fuzzy-matches `sarajevo-bosnia-and-herzegovina` |
| 41 | 9 | `blagaj-bosnia-and-herzegovina` | Blagaj, Bosnia and Herzegovina | 12 | blocked | routing decision: preflight fuzzy-matches `sarajevo-bosnia-and-herzegovina` |
| 42 | 9 | `mestia-georgia` | Mestia, Georgia | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 43 | 9 | `stepantsminda-georgia` | Stepantsminda, Georgia | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 44 | 9 | `piran-slovenia` | Piran, Slovenia | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 45 | 9 | `sibenik-croatia` | Sibenik, Croatia | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 46 | 10 | `matera-italy` | Matera, Italy | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 47 | 10 | `orvieto-italy` | Orvieto, Italy | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 48 | 10 | `cadaques-spain` | Cadaques, Spain | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 49 | 10 | `cuenca-spain` | Cuenca, Spain | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 50 | 10 | `tavira-portugal` | Tavira, Portugal | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 51 | 11 | `paraty-brazil` | Paraty, Brazil | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 52 | 11 | `lijiang-china` | Lijiang, China | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 53 | 11 | `chefchaouene-morocco` | Chefchaouene, Morocco | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 54 | 11 | `siwa-oasis-egypt` | Siwa Oasis, Egypt | 12 | not staged | stage pending JSON in a max-5 staging batch |
| 55 | 11 | `lamu-kenya` | Lamu, Kenya | 12 | not staged | stage pending JSON in a max-5 staging batch |
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
