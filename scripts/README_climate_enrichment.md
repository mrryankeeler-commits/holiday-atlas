# Climate enrichment PoC (Open-Meteo)

This document defines the climate-enrichment behavior for the current proof of concept.

## Scope

- **Index scan scope:** process only the first **50** records from `data/locations/index.json`.
- **Write scope (PoC):** only these 3 IDs are write-enabled:
  - `andorra-la-vella`
  - `accra-ghana`
  - `beppu-japan`
- Other records in the first 50 may be fetched/processed for validation, but are not written in this phase.

## Provider rule: Open-Meteo primary + explicit fallback logging

- Open-Meteo is the primary provider in this phase.
- Open-Meteo geocoding is the primary source for `elevation`, `timezone`, `population`, `admin1`, and `admin2`.
- Open-Meteo historical archive is the primary source for monthly climatology.
- Do **not** call secondary weather providers by default.
- If Open-Meteo data is unavailable/incomplete for a field, persist `null` for that field (see missing-data policy).
- If any non-Open-Meteo fallback is ever used, record the fallback endpoint/source and the reason in:
  1) the script code comment near provider constants/call site, and
  2) this README fallback section.

### Explicit fallback policy (still Open-Meteo-only)

1. **Geocoding:** use Open-Meteo geocoding endpoint.
2. **Result selection fallback (within Open-Meteo response):**
   - first preference: exact city+country match
   - second preference: same-country result
   - third preference: first result returned
3. **Elevation fallback:**
   - use geocoding `elevation` when present
   - otherwise call Open-Meteo elevation endpoint
4. **Primary climatology source:** use Open-Meteo historical archive for monthly climatology calculations.
5. **No provider fallback by default:** if Open-Meteo cannot provide a metric, keep `null` and log the failure.
6. **All-upstream-failed guardrail:** if geocoding + elevation fallback + archive all fail for a destination,
   do **not** overwrite existing destination data; log and continue batch processing.
7. **Future non-Open-Meteo fallback rule:** if a fallback provider/endpoint is ever introduced, document
   endpoint/source + reason in both script comments and this README before/with rollout.

## Exact endpoints

- Geocoding: `https://geocoding-api.open-meteo.com/v1/search`
- Elevation: `https://api.open-meteo.com/v1/elevation`
- Historical archive: `https://archive-api.open-meteo.com/v1/archive`

## Variables requested from Open-Meteo archive

### Daily variables (canonical list)

- `temperature_2m_mean`
- `temperature_2m_max`
- `temperature_2m_min`
- `apparent_temperature_mean`
- `apparent_temperature_max`
- `apparent_temperature_min`
- `relative_humidity_2m_mean`
- `dew_point_2m_mean`
- `precipitation_sum`
- `rain_sum`
- `snowfall_sum`
- `precipitation_hours`
- `cloud_cover_mean`
- `sunshine_duration`
- `daylight_duration`
- `wind_speed_10m_mean`
- `wind_gusts_10m_max`
- `sunrise`
- `sunset`

## Time window and timezone

- Historical baseline window:
  - `start_date=1991-01-01`
  - `end_date=2020-12-31`
- `timezone=auto` (local-time aligned daily values).

## Aggregation formulas

All monthly values are destination-relative monthly climatologies from daily records.

### General mean aggregation

For month `m` and variable `x`:

- collect all daily values in month `m` across all years in scope
- drop `null` days
- monthly value = arithmetic mean of remaining values
- round to 2 decimals

If no non-null values exist, result is `null`.

### Rainfall/rain monthly-total averaging (important)

For `precipitation_sum` (`rainfall_mm`) and `rain_sum` (`rain_mm`):

1. For each year `y`, sum all non-null daily values in month `m`:
   - `month_total(y,m) = Σ daily_value(y,m,day)`
2. Keep yearly totals only for years with at least one non-null value.
3. Monthly climatology = arithmetic mean of yearly month totals:
   - `monthly_mm(m) = mean_y(month_total(y,m))`
4. Round to 2 decimals.

This is **not** the same as mean daily rain × days; it is the average of yearly monthly totals.

### Duration conversions

- `sunshine_duration` and `daylight_duration` are seconds/day from API.
- Convert to hours with `hours = seconds / 3600`, round to 2 decimals.

### Sunrise/sunset monthly representative value

- Parse all non-null daily local timestamps in month.
- Convert each to seconds after midnight.
- Use median seconds-of-day.
- Format as `HH:MM` local time.

## Snowfall unit handling

- Open-Meteo daily `snowfall_sum` source unit is **centimeters**.
- Persist monthly snowfall as `snowfall_cm` (same physical unit family as source).
- If internal normalization temporarily uses meters for calculations, convert with:
  - `snowfall_cm = snowfall_m * 100`
- Do not infer snowfall from precipitation/rain deltas.

## Missing-data policy (strict)

- Missing or invalid source data must map to `null`.
- No guessed values.
- No interpolation.
- No borrowing from nearby months.
- No backfilling from other providers.

## Failure logging behavior

- Log failures per destination and continue batch processing.
- Recommended log format:
  - success: `[OK] <id>: <message>`
  - failure: `[FAIL] <id>: <error>`
- Batch summary must include success/failure counts.
- Process exit code should be non-zero if any destination fails.

## Helper text strings

These are canonical helper labels/descriptions for enriched climate fields.

- **Feels like:** `Perceived temperature (apparent temperature) including humidity and wind effects.`
- **Humidity:** `Average relative humidity for the month.`
- **Mugginess:** `Comfort label inferred from monthly mean dew point.`
- **Rainy hours:** `Average daily hours with measurable rain, aggregated to monthly climatology.`
- **Cloud cover:** `Average fraction of sky covered by cloud during the month.`
- **Wind:** `Average 10 m wind speed for the month.`
- **Gusts:** `Average daily maximum 10 m wind gust in the month.`

## Backward compatibility

- Existing frontend behavior is unchanged.
- The UI continues to consume legacy `months` data as-is.
- Enrichment adds parallel climate metadata/blocks only.

## Frontend wiring status for this phase

- **No frontend wiring is included in this phase.**
- No UI components are added, modified, or switched to enriched climate blocks in this PoC.
