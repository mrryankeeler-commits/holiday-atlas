# Missing Set v1 (Frozen, normalized)
- Finalized on: 2026-04-17 (updated 2026-04-17)
- Live visibility source: `data/locations/index.json`
- Intake source: all CSV uploads in `data/climate/uploads/`
- Normalization method: `scripts/import_climate_csv.py` resolution (`exact`/`alias`/`fuzzy`) with `fuzzy_cutoff=0.84` and `data/climate/aliases.json`.
- Intake raw candidate IDs: 133
- Canonical LIVE IDs covered by intake: 130 / 130
- MISSING after normalization: 0

## Intake candidate checklist (raw → normalized)

| Raw candidate id | Normalized id | Status | Resolution | Intake source file(s) |
|---|---|---|---|---|
| `a-lat-vietnam` | `a-lat-vietnam` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `andorra-la-vella-andorra` | `andorra-la-vella` | ✅ LIVE | `exact` | `climate_data_03 - Climate Data.csv` |
| `antalya-turkey` | `antalya-turkey` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `antigua-guatemala` | `antigua-guatemala` | ✅ LIVE | `exact` | `monthly_climate_02 - Climate Data.csv` |
| `arequipa-peru` | `arequipa-peru` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `arhus-denmark` | `arhus-denmark` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `astana-kazakhstan` | `astana` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `asuncion-paraguay` | `asuncion-paraguay` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `athens-greece` | `athens` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `auckland-new-zealand` | `auckland-new-zealand` | ✅ LIVE | `exact` | `monthly_climate_02 - Climate Data.csv` |
| `bacalar-mexico` | `bacalar-mexico` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `barranquilla-colombia` | `barranquilla-colombia` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `belize-city-belize` | `belize-city-belize` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `berat-albania` | `berat-albania` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `bergen-norway` | `bergen` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `bishkek-kyrgyzstan` | `bishkek-kyrgyzstan` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `bled-slovenia` | `bled` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `bodrum-turkey` | `bodrum-turkey` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `bolivar-venezuela` | `bolivar-venezuela` | ✅ LIVE | `exact` | `monthly_climate_02 - Climate Data.csv` |
| `braga-portugal` | `braga` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `brasov-romania` | `brasov-romania` | ✅ LIVE | `exact` | `monthly_climate_02 - Climate Data.csv` |
| `bratislava-slovakia` | `bratislava` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `brno-czechia` | `brno-czechia` | ✅ LIVE | `exact` | `monthly_climate_02 - Climate Data.csv` |
| `budapest-hungary` | `budapest` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `budva-montenegro` | `budva` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `cairo-egypt` | `cairo` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `cartagena-colombia` | `cartagena-colombia` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `catania-italy` | `catania` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `chengdu-china` | `chengdu` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `colombo-sri-lanka` | `colombo` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `copenhagen-denmark` | `copenhagen` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `dahab-egypt` | `dahab-egypt` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `darjeeling-india` | `darjeeling` | ✅ LIVE | `exact` | `climate_data_03 - Climate Data.csv` |
| `dubai-uae` | `dubai-uae` | ✅ LIVE | `exact` | `monthly_climate_02 - Climate Data.csv` |
| `dubrovnik-croatia` | `dubrovnik` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `el-cotillo-fuerteventura-spain` | `el-cotillo-fuerteventura-spain` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `faro-portugal` | `faro` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `florence-italy` | `florence` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `gdansk-poland` | `gdansk` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `ghent-belgium` | `ghent-belgium` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `goa-india` | `goa` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `goreme-turkey` | `goreme` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `granada-spain` | `granada` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `graz-austria` | `graz-austria` | ✅ LIVE | `exact` | `monthly_climate_02 - Climate Data.csv` |
| `guilin-china` | `guilin` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `ha-giang-vietnam` | `ha-giang` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `havana-cuba` | `havana-cuba` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `hegra-saudi-arabia` | `hegra-saudi-arabia` | ✅ LIVE | `exact` | `climate_data_03 - Climate Data.csv` |
| `hoa-lu-ninh-binh-vietnam` | `hoa-lu-ninh-binh-vietnam` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `hoi-an-vietnam` | `hoi-an-vietnam` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `hurghada-egypt` | `hurghada` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `ilha-de-sao-miguel-azores-portugal` | `ilha-de-sao-miguel-azores-portugal` | ✅ LIVE | `exact` | `monthly_climate_02 - Climate Data.csv` |
| `istanbul-turkey` | `istanbul` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `jaipur-india` | `jaipur-india` | ✅ LIVE | `exact` | `monthly_climate_02 - Climate Data.csv` |
| `kampot-cambodia` | `kampot-cambodia` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `kandy-sri-lanka` | `kandy` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `katowice-poland` | `katowice` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `kaunas-lithuania` | `kaunas-lithuania` | ✅ LIVE | `exact` | `monthly_climate_02 - Climate Data.csv` |
| `kotor-montenegro` | `kotor` | ✅ LIVE | `exact` | `climate_data_03 - Climate Data.csv` |
| `krakow-poland` | `krakow` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `kutaisi-georgia` | `kutaisi-georgia` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `leh-kashmir-india` | `leh-kashmir-india` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `leipzig-germany` | `leipzig` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `lima-peru` | `lima-peru` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `ljubljana-slovenia` | `ljubljana-slovenia` | ✅ LIVE | `exact` | `monthly_climate_02 - Climate Data.csv` |
| `luang-prabang-laos` | `luang-prabang-laos` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `madeira-portugal` | `madeira-portugal` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `makassar-indonesia` | `makassar-indonesia` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `makunduchi-tanzania` | `makunduchi` | ✅ LIVE | `exact` | `climate_data_03 - Climate Data.csv` |
| `malay-philippines` | `malay-philippines` | ✅ LIVE | `exact` | `climate_data_03 - Climate Data.csv` |
| `manado-indonesia` | `manado-indonesia` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `marrakesh-morocco` | `marrakech` | ✅ LIVE | `fuzzy` | `monthly_climate_01.csv` |
| `medellin-colombia` | `medellin-colombia` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `merida-yucatan-mexico` | `merida-yucatan-mexico` | ✅ LIVE | `exact` | `monthly_climate_02 - Climate Data.csv` |
| `meteora-greece` | `meteora` | ✅ LIVE | `exact` | `climate_data_03 - Climate Data.csv` |
| `minca-colombia` | `minca-colombia` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `mostar-bosnia-and-herzegovina` | `mostar` | ✅ LIVE | `fuzzy` | `monthly_climate_01.csv` |
| `munnar-india` | `munnar` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `munnar-kerala-india` | `munnar-kerala-india` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `oia-greece` | `oia-greece` | ✅ LIVE | `exact` | `monthly_climate_02 - Climate Data.csv` |
| `ometepe-nicaragua` | `ometepe-nicaragua` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `osaka-japan` | `osaka` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `palermo-italy` | `palermo` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `panama-city-panama` | `panama-city-panama` | ✅ LIVE | `exact` | `monthly_climate_02 - Climate Data.csv` |
| `paphos-cyprus` | `paphos` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `phoenix-arizona-united-states` | `phoenix-arizona-united-states` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `placencia-belize` | `placencia-belize` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `plovdiv-bulgaria` | `plovdiv-bulgaria` | ✅ LIVE | `exact` | `monthly_climate_02 - Climate Data.csv` |
| `pottuvil-sri-lanka` | `pottuvil` | ✅ LIVE | `exact` | `climate_data_03 - Climate Data.csv` |
| `prague-czechia` | `prague` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `puerto-ayora-ecuador` | `puerto-ayora-ecuador` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `puno-peru` | `puno-peru` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `punta-cana-dominican-republic` | `punta-cana-dominican-republic` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `queenstown-new-zealand` | `queenstown-new-zealand` | ✅ LIVE | `exact` | `monthly_climate_02 - Climate Data.csv` |
| `quetzaltenango-guatemala` | `quetzaltenango-guatemala` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `quito-ecuador` | `quito-ecuador` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `reckong-peo-india` | `reckong-peo-india` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `reine-norway` | `reine-norway` | ✅ LIVE | `exact` | `monthly_climate_02 - Climate Data.csv` |
| `riga-latvia` | `riga` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `rio-de-janeiro-brazil` | `rio-de-janeiro-brazil` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `rome-italy` | `rome` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `ronda-spain` | `ronda-spain` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `samarkand-uzbekistan` | `samarkand` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `san-pedro-la-laguna-guatemala` | `san-pedro-la-laguna-guatemala` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `santa-marta-colombia` | `santa-marta-colombia` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `sanya-china` | `sanya` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `sarajevo-bosnia-and-herzegovina` | `sarajevo-bosnia-and-herzegovina` | ✅ LIVE | `exact` | `monthly_climate_02 - Climate Data.csv` |
| `seoul-south-korea` | `seoul-south-korea` | ✅ LIVE | `exact` | `monthly_climate_02 - Climate Data.csv` |
| `seville-spain` | `seville` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `sharjah-uae` | `sharjah-uae` | ✅ LIVE | `exact` | `monthly_climate_02 - Climate Data.csv` |
| `sydney-australia` | `sydney-australia` | ✅ LIVE | `exact` | `monthly_climate_02 - Climate Data.csv` |
| `tallinn-estonia` | `tallinn` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `tangalla-sri-lanka` | `tangalla-sri-lanka` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `tbilisi-georgia` | `tbilisi` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `tekapo-new-zealand` | `tekapo-new-zealand` | ✅ LIVE | `exact` | `climate_data_03 - Climate Data.csv` |
| `tilcara-argentina` | `tilcara-argentina` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `tirana-albania` | `tirana` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `tokyo-japan` | `tokyo-japan` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `toledo-spain` | `toledo` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `trieste-italy` | `trieste` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `turin-italy` | `turin` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `ulaanbaatar-mongolia` | `ulaanbaatar-mongolia` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `ulcinj-montenegro` | `ulcinj` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `valletta-malta` | `valletta` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `varna-bulgaria` | `varna` | ✅ LIVE | `exact` | `monthly_climate_01.csv, monthly_climate_02 - Climate Data.csv` |
| `vienna-austria` | `vienna` | ✅ LIVE | `exact` | `monthly_climate_01.csv` |
| `vinales-cuba` | `vinales-cuba` | ✅ LIVE | `exact` | `climate_data_04 - Climate_Data.csv` |
| `waigeo-indonesia` | `waigeo-indonesia` | ✅ LIVE | `exact` | `climate_data_03 - Climate Data.csv` |
| `zakopane-poland` | `zakopane` | ✅ LIVE | `exact` | `climate_data_03 - Climate Data.csv` |
| `zakynthos-greece` | `zakynthos-greece` | ✅ LIVE | `exact` | `monthly_climate_02 - Climate Data.csv` |
| `zermatt-switzerland` | `zermatt` | ✅ LIVE | `exact` | `climate_data_03 - Climate Data.csv` |
| `zhangjiajie-hunan-china` | `zhangjiajie-hunan-china` | ✅ LIVE | `exact` | `monthly_climate_02 - Climate Data.csv` |
| `zhangye-china` | `zhangye-china` | ✅ LIVE | `exact` | `monthly_climate_02 - Climate Data.csv` |

## Canonical LIVE checklist (`index.json`)

| Canonical live id | Status | Seen in intake CSVs |
|---|---|---|
| `a-lat-vietnam` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `andorra-la-vella` | ✅ LIVE | `climate_data_03 - Climate Data.csv` |
| `antigua-guatemala` | ✅ LIVE | `monthly_climate_02 - Climate Data.csv` |
| `arequipa-peru` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `astana` | ✅ LIVE | `monthly_climate_01.csv` |
| `asuncion-paraguay` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `athens` | ✅ LIVE | `monthly_climate_01.csv` |
| `auckland-new-zealand` | ✅ LIVE | `monthly_climate_02 - Climate Data.csv` |
| `bacalar-mexico` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `barranquilla-colombia` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `belize-city-belize` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `bergen` | ✅ LIVE | `monthly_climate_01.csv` |
| `bishkek-kyrgyzstan` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `bled` | ✅ LIVE | `monthly_climate_01.csv` |
| `bolivar-venezuela` | ✅ LIVE | `monthly_climate_02 - Climate Data.csv` |
| `braga` | ✅ LIVE | `monthly_climate_01.csv` |
| `brasov-romania` | ✅ LIVE | `monthly_climate_02 - Climate Data.csv` |
| `bratislava` | ✅ LIVE | `monthly_climate_01.csv` |
| `brno-czechia` | ✅ LIVE | `monthly_climate_02 - Climate Data.csv` |
| `budapest` | ✅ LIVE | `monthly_climate_01.csv` |
| `budva` | ✅ LIVE | `monthly_climate_01.csv` |
| `cairo` | ✅ LIVE | `monthly_climate_01.csv` |
| `cartagena-colombia` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `catania` | ✅ LIVE | `monthly_climate_01.csv` |
| `chengdu` | ✅ LIVE | `monthly_climate_01.csv` |
| `colombo` | ✅ LIVE | `monthly_climate_01.csv` |
| `copenhagen` | ✅ LIVE | `monthly_climate_01.csv` |
| `darjeeling` | ✅ LIVE | `climate_data_03 - Climate Data.csv` |
| `dubai-uae` | ✅ LIVE | `monthly_climate_02 - Climate Data.csv` |
| `dubrovnik` | ✅ LIVE | `monthly_climate_01.csv` |
| `el-cotillo-fuerteventura-spain` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `faro` | ✅ LIVE | `monthly_climate_01.csv` |
| `florence` | ✅ LIVE | `monthly_climate_01.csv` |
| `gdansk` | ✅ LIVE | `monthly_climate_01.csv` |
| `goa` | ✅ LIVE | `monthly_climate_01.csv` |
| `goreme` | ✅ LIVE | `monthly_climate_01.csv` |
| `granada` | ✅ LIVE | `monthly_climate_01.csv` |
| `graz-austria` | ✅ LIVE | `monthly_climate_02 - Climate Data.csv` |
| `guilin` | ✅ LIVE | `monthly_climate_01.csv` |
| `ha-giang` | ✅ LIVE | `monthly_climate_01.csv` |
| `havana-cuba` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `hegra-saudi-arabia` | ✅ LIVE | `climate_data_03 - Climate Data.csv` |
| `hoa-lu-ninh-binh-vietnam` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `hoi-an-vietnam` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `hurghada` | ✅ LIVE | `monthly_climate_01.csv` |
| `ilha-de-sao-miguel-azores-portugal` | ✅ LIVE | `monthly_climate_02 - Climate Data.csv` |
| `istanbul` | ✅ LIVE | `monthly_climate_01.csv` |
| `jaipur-india` | ✅ LIVE | `monthly_climate_02 - Climate Data.csv` |
| `kampot-cambodia` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `kandy` | ✅ LIVE | `monthly_climate_01.csv` |
| `katowice` | ✅ LIVE | `monthly_climate_01.csv` |
| `kaunas-lithuania` | ✅ LIVE | `monthly_climate_02 - Climate Data.csv` |
| `kotor` | ✅ LIVE | `climate_data_03 - Climate Data.csv` |
| `krakow` | ✅ LIVE | `monthly_climate_01.csv` |
| `kutaisi-georgia` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `leh-kashmir-india` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `leipzig` | ✅ LIVE | `monthly_climate_01.csv` |
| `lima-peru` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `ljubljana-slovenia` | ✅ LIVE | `monthly_climate_02 - Climate Data.csv` |
| `luang-prabang-laos` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `madeira-portugal` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `makassar-indonesia` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `makunduchi` | ✅ LIVE | `climate_data_03 - Climate Data.csv` |
| `malay-philippines` | ✅ LIVE | `climate_data_03 - Climate Data.csv` |
| `manado-indonesia` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `marrakech` | ✅ LIVE | `monthly_climate_01.csv` |
| `medellin-colombia` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `merida-yucatan-mexico` | ✅ LIVE | `monthly_climate_02 - Climate Data.csv` |
| `meteora` | ✅ LIVE | `climate_data_03 - Climate Data.csv` |
| `minca-colombia` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `mostar` | ✅ LIVE | `monthly_climate_01.csv` |
| `munnar` | ✅ LIVE | `monthly_climate_01.csv` |
| `munnar-kerala-india` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `oia-greece` | ✅ LIVE | `monthly_climate_02 - Climate Data.csv` |
| `ometepe-nicaragua` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `osaka` | ✅ LIVE | `monthly_climate_01.csv` |
| `palermo` | ✅ LIVE | `monthly_climate_01.csv` |
| `panama-city-panama` | ✅ LIVE | `monthly_climate_02 - Climate Data.csv` |
| `paphos` | ✅ LIVE | `monthly_climate_01.csv` |
| `phoenix-arizona-united-states` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `placencia-belize` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `plovdiv-bulgaria` | ✅ LIVE | `monthly_climate_02 - Climate Data.csv` |
| `pottuvil` | ✅ LIVE | `climate_data_03 - Climate Data.csv` |
| `prague` | ✅ LIVE | `monthly_climate_01.csv` |
| `puerto-ayora-ecuador` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `puno-peru` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `punta-cana-dominican-republic` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `queenstown-new-zealand` | ✅ LIVE | `monthly_climate_02 - Climate Data.csv` |
| `quetzaltenango-guatemala` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `quito-ecuador` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `reckong-peo-india` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `reine-norway` | ✅ LIVE | `monthly_climate_02 - Climate Data.csv` |
| `riga` | ✅ LIVE | `monthly_climate_01.csv` |
| `rio-de-janeiro-brazil` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `rome` | ✅ LIVE | `monthly_climate_01.csv` |
| `ronda-spain` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `samarkand` | ✅ LIVE | `monthly_climate_01.csv` |
| `san-pedro-la-laguna-guatemala` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `santa-marta-colombia` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `sanya` | ✅ LIVE | `monthly_climate_01.csv` |
| `sarajevo-bosnia-and-herzegovina` | ✅ LIVE | `monthly_climate_02 - Climate Data.csv` |
| `seoul-south-korea` | ✅ LIVE | `monthly_climate_02 - Climate Data.csv` |
| `seville` | ✅ LIVE | `monthly_climate_01.csv` |
| `sharjah-uae` | ✅ LIVE | `monthly_climate_02 - Climate Data.csv` |
| `sydney-australia` | ✅ LIVE | `monthly_climate_02 - Climate Data.csv` |
| `tallinn` | ✅ LIVE | `monthly_climate_01.csv` |
| `tangalla-sri-lanka` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `tbilisi` | ✅ LIVE | `monthly_climate_01.csv` |
| `tekapo-new-zealand` | ✅ LIVE | `climate_data_03 - Climate Data.csv` |
| `tilcara-argentina` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `tirana` | ✅ LIVE | `monthly_climate_01.csv` |
| `tokyo-japan` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `toledo` | ✅ LIVE | `monthly_climate_01.csv` |
| `trieste` | ✅ LIVE | `monthly_climate_01.csv` |
| `turin` | ✅ LIVE | `monthly_climate_01.csv` |
| `ulaanbaatar-mongolia` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `ulcinj` | ✅ LIVE | `monthly_climate_01.csv` |
| `valletta` | ✅ LIVE | `monthly_climate_01.csv` |
| `varna` | ✅ LIVE | `monthly_climate_01.csv, monthly_climate_02 - Climate Data.csv` |
| `vienna` | ✅ LIVE | `monthly_climate_01.csv` |
| `vinales-cuba` | ✅ LIVE | `climate_data_04 - Climate_Data.csv` |
| `waigeo-indonesia` | ✅ LIVE | `climate_data_03 - Climate Data.csv` |
| `zakopane` | ✅ LIVE | `climate_data_03 - Climate Data.csv` |
| `zakynthos-greece` | ✅ LIVE | `monthly_climate_02 - Climate Data.csv` |
| `zermatt` | ✅ LIVE | `climate_data_03 - Climate Data.csv` |
| `zhangjiajie-hunan-china` | ✅ LIVE | `monthly_climate_02 - Climate Data.csv` |
| `zhangye-china` | ✅ LIVE | `monthly_climate_02 - Climate Data.csv` |

## Missing Set v1

