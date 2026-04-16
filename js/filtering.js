import { normalizeSearchText } from "./utils.js";

export function matchesLocationSearch(location, normalizedQuery) {
  if (!normalizedQuery) return true;
  return [location?.city, location?.country, location?.region]
    .filter(Boolean)
    .some(value => normalizeSearchText(value).includes(normalizedQuery));
}

export function filterLocations(index = [], { query = "", region = "all" } = {}) {
  const normalizedQuery = normalizeSearchText(query);
  return index.filter(location => {
    const matchesRegion = region === "all" || location?.region === region;
    if (!matchesRegion) return false;
    return matchesLocationSearch(location, normalizedQuery);
  });
}
