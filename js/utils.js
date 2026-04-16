export const VIEW_HASH = {
  welcome: "#welcome",
  explorer: "#explorer"
};

export const DEPARTURE_AIRPORTS = [
  { code: "LGW", label: "Gatwick" },
  { code: "LCY", label: "London City" }
];

export const DEPARTURE_AIRPORT_CODES = DEPARTURE_AIRPORTS.map(a => a.code);

export const RECOMMENDATION_METRICS = ["weather", "budget", "crowds", "direct"];

export const clbls = ["", "Budget", "Low", "Mid", "High", "Peak"];
export const bclr = v => v <= 2 ? "#639922" : v <= 4 ? "#97C459" : v <= 6 ? "#C9973A" : v <= 8 ? "#EF9F27" : v <= 9 ? "#D85A30" : "#A32D2D";
export const blbl = v => v <= 2 ? "Quiet" : v <= 4 ? "Low" : v <= 6 ? "Moderate" : v <= 8 ? "Busy" : v <= 9 ? "Very busy" : "Peak";
export const cpc = v => `pill p${v}`;

export const normalizeSearchText = value => String(value ?? "")
  .normalize("NFD")
  .replace(/\p{Diacritic}/gu, "")
  .trim()
  .replace(/\s+/g, " ")
  .toLowerCase();

export const clamp01 = n => Math.min(1, Math.max(0, n));
export const isFiniteNumber = n => Number.isFinite(Number(n));
export const escapeHtml = value => String(value ?? "")
  .replace(/&/g, "&amp;")
  .replace(/</g, "&lt;")
  .replace(/>/g, "&gt;")
  .replace(/"/g, "&quot;")
  .replace(/'/g, "&#39;");

export function normalizeValue(value, min, max, { invert = false } = {}) {
  if (!isFiniteNumber(value) || !isFiniteNumber(min) || !isFiniteNumber(max) || max === min) return 0.5;
  const raw = (value - min) / (max - min);
  const normalized = clamp01(raw);
  return invert ? 1 - normalized : normalized;
}

export function getFieldRange(months, key) {
  const values = months.map(m => Number(m?.[key])).filter(Number.isFinite);
  if (!values.length) return { min: 0, max: 1 };
  return { min: Math.min(...values), max: Math.max(...values) };
}

export function computeWeatherComfort(month, ranges) {
  if (!isFiniteNumber(month?.avg) || !isFiniteNumber(month?.rain) || !isFiniteNumber(month?.cld) || !isFiniteNumber(month?.daylight)) {
    return { value: null, reason: "missing climate fields" };
  }

  const avgTemp = Number(month.avg);
  const rain = Number(month.rain);
  const cloud = Number(month.cld);
  const daylight = Number(month.daylight);

  const tempComfort = clamp01(1 - (Math.abs(avgTemp - 22) / 16));
  const rainComfort = normalizeValue(rain, ranges.rain.min, ranges.rain.max, { invert: true });
  const cloudComfort = clamp01(1 - (cloud / 100));
  const daylightComfort = clamp01(1 - (Math.abs(daylight - 11) / 6));
  const weather = (tempComfort * 0.4) + (rainComfort * 0.25) + (cloudComfort * 0.2) + (daylightComfort * 0.15);

  return { value: weather, reason: "" };
}

export function computeRecommendationScores(location, prefs = {}) {
  const months = Array.isArray(location?.months) ? location.months : [];
  const ranges = {
    ac: getFieldRange(months, "ac"),
    fl: getFieldRange(months, "fl"),
    busy: getFieldRange(months, "busy"),
    rain: getFieldRange(months, "rain")
  };
  const hasDirectFlight = getDirectAirportCodes(location?.prac?.directFrom).length > 0;
  const metricWeights = {
    weather: Number(prefs.weather) || 0,
    budget: Number(prefs.budget) || 0,
    crowds: Number(prefs.crowds) || 0,
    direct: Number(prefs.direct) || 0
  };

  return months.map(month => {
    const weather = computeWeatherComfort(month, ranges);
    const budgetValue = (isFiniteNumber(month?.ac) && isFiniteNumber(month?.fl))
      ? ((normalizeValue(month.ac, ranges.ac.min, ranges.ac.max, { invert: true }) * 0.55)
        + (normalizeValue(month.fl, ranges.fl.min, ranges.fl.max, { invert: true }) * 0.45))
      : null;
    const crowdsValue = isFiniteNumber(month?.busy)
      ? normalizeValue(month.busy, ranges.busy.min, ranges.busy.max, { invert: true })
      : null;
    const directValue = hasDirectFlight ? 1 : 0.3;

    const metrics = { weather: weather.value, budget: budgetValue, crowds: crowdsValue, direct: directValue };

    const weightedParts = RECOMMENDATION_METRICS
      .filter(metric => metricWeights[metric] > 0 && metrics[metric] !== null);
    const numerator = weightedParts.reduce((sum, metric) => sum + (metrics[metric] * metricWeights[metric]), 0);
    const denominator = weightedParts.reduce((sum, metric) => sum + metricWeights[metric], 0);
    const score = denominator > 0 ? Math.round((numerator / denominator) * 100) : 0;

    const availableCount = RECOMMENDATION_METRICS.filter(metric => metrics[metric] !== null).length;
    const coverage = availableCount / RECOMMENDATION_METRICS.length;
    const confidence = coverage >= 1 ? "High" : coverage >= 0.75 ? "Medium" : "Low";
    const rationale = [
      metrics.weather !== null && metrics.weather >= 0.66 ? "comfortable weather" : "",
      metrics.budget !== null && metrics.budget >= 0.66 ? "moderate costs" : "",
      metrics.crowds !== null && metrics.crowds >= 0.66 ? "low crowds" : "",
      hasDirectFlight && metricWeights.direct > 0 ? "direct-flight friendly" : ""
    ].filter(Boolean);

    return {
      month: month.m,
      score,
      metrics,
      coverage,
      confidence,
      rationale: rationale.length ? rationale.slice(0, 3).join(" + ") : "mixed trade-offs"
    };
  }).sort((a, b) => b.score - a.score);
}

export function normalizeDirectFrom(rawMap, legacyLGWValue = false) {
  const normalized = {};
  const source = rawMap && typeof rawMap === "object" ? rawMap : {};

  DEPARTURE_AIRPORT_CODES.forEach(code => {
    normalized[code] = Boolean(source[code]);
  });

  if (legacyLGWValue) normalized.LGW = true;

  return normalized;
}

export function getDirectAirportCodes(directFromMap) {
  return DEPARTURE_AIRPORT_CODES.filter(code => Boolean(directFromMap?.[code]));
}

export function viewFromHash(hash = window.location.hash) {
  if (hash === VIEW_HASH.explorer) return "explorer";
  if (hash === VIEW_HASH.welcome) return "welcome";
  return null;
}
