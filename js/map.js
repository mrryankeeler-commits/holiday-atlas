import { normalizeSearchText } from "./utils.js";

const FEATURE_FLAGS = {
  enableMap: true,
  requireMapCoordinateReadinessInProduction: true
};

const DEFAULT_MAP_CENTER = [20, 0];
const DEFAULT_MAP_ZOOM = 2;
const LOCATION_FOCUS_MIN_ZOOM = 5;

export function createMapController({ getState, getIndex, onMarkerSelect }) {
  let map = null;
  let mapReady = false;
  let mapInitAttempted = false;
  const mapMarkers = new Map();
  const visibleMapMarkerIds = new Set();
  let highlightedMarkerId = null;

  const mapIcon = ({ isActive = false } = {}) => L.divIcon({
    className: "",
    html: `<span class="dest-marker variant-country ${isActive ? "active" : ""}" aria-hidden="true"></span>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9]
  });

  const showMapFallback = (message) => {
    const fallback = document.getElementById("map-fallback");
    if (!fallback) return;
    fallback.textContent = message;
    fallback.hidden = false;
  };

  const hideMapFallback = () => {
    const fallback = document.getElementById("map-fallback");
    if (!fallback) return;
    fallback.hidden = true;
  };

  const isValidCoordinatePair = loc => Number.isFinite(loc?.lat)
    && Number.isFinite(loc?.lng)
    && loc.lat >= -90
    && loc.lat <= 90
    && loc.lng >= -180
    && loc.lng <= 180;

  const isProductionRuntime = () => {
    const protocol = window.location.protocol;
    const host = window.location.hostname;
    return protocol !== "file:" && !["localhost", "127.0.0.1"].includes(host);
  };

  const getMapRolloutState = () => {
    if (!FEATURE_FLAGS.enableMap) {
      return { enabled: false, reason: "Map rollout is currently disabled via feature flag. Browse destinations from the list." };
    }
    if (FEATURE_FLAGS.requireMapCoordinateReadinessInProduction && isProductionRuntime() && !getIndex().every(isValidCoordinatePair)) {
      return { enabled: false, reason: "Map is temporarily disabled until all destination coordinates pass the production readiness gate." };
    }
    return { enabled: true, reason: "" };
  };

  const applyMapRolloutState = (rolloutState) => {
    const mapEl = document.getElementById("map");
    if (!mapEl) return;
    mapEl.hidden = !rolloutState.enabled;
    if (rolloutState.enabled) {
      hideMapFallback();
      return;
    }
    showMapFallback(rolloutState.reason);
  };

  const highlightMapMarker = id => {
    if (!mapReady) return;
    if (highlightedMarkerId && mapMarkers.has(highlightedMarkerId)) {
      mapMarkers.get(highlightedMarkerId).setIcon(mapIcon({ isActive: false }));
    }
    if (id && visibleMapMarkerIds.has(id) && mapMarkers.has(id)) {
      mapMarkers.get(id).setIcon(mapIcon({ isActive: true }));
      highlightedMarkerId = id;
      return;
    }
    highlightedMarkerId = null;
  };

  return {
    initMap() {
      const rolloutState = getMapRolloutState();
      applyMapRolloutState(rolloutState);
      if (!rolloutState.enabled || mapInitAttempted) return;
      mapInitAttempted = true;

      const mapEl = document.getElementById("map");
      if (!mapEl) return;
      if (!window.L) {
        showMapFallback("Map library failed to load. You can still browse destinations from the list.");
        return;
      }

      try {
        map = L.map(mapEl, { zoomControl: true, scrollWheelZoom: true }).setView(DEFAULT_MAP_CENTER, DEFAULT_MAP_ZOOM);
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          maxZoom: 19,
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        const points = getIndex().filter(isValidCoordinatePair);
        points.forEach(loc => {
          const marker = L.marker([loc.lat, loc.lng], {
            icon: mapIcon({ isActive: loc.id === getState().loc }),
            keyboard: true,
            title: `${loc.city}, ${loc.country}`
          }).addTo(map);
          marker.bindTooltip(loc.city, { direction: "top", offset: [0, -8] });
          marker.on("click", () => onMarkerSelect(loc.id));
          mapMarkers.set(loc.id, marker);
          visibleMapMarkerIds.add(loc.id);
        });

        if (points.length > 1) map.fitBounds(points.map(loc => [loc.lat, loc.lng]), { padding: [26, 26] });
        else if (points.length === 1) map.setView([points[0].lat, points[0].lng], 7);

        mapReady = true;
      } catch (err) {
        console.error(err);
        showMapFallback("Map failed to initialize. You can still browse destinations from the list.");
      }
    },

    applyFilter(filteredLocations, query) {
      if (!mapReady) return;
      const activeQuery = query ?? normalizeSearchText(getState().query);
      const hasQuery = Boolean(activeQuery);
      const filteredIds = new Set(filteredLocations.map(loc => loc.id));

      visibleMapMarkerIds.clear();
      mapMarkers.forEach((marker, id) => {
        const visible = !hasQuery || filteredIds.has(id);
        marker.setOpacity(visible ? 1 : 0);
        if (visible) visibleMapMarkerIds.add(id);
        const markerEl = marker.getElement();
        if (markerEl) {
          markerEl.style.pointerEvents = visible ? "auto" : "none";
          markerEl.style.visibility = visible ? "visible" : "hidden";
        }
      });

      highlightMapMarker(visibleMapMarkerIds.has(getState().loc) ? getState().loc : null);
    },

    focusLocation(id, options = {}) {
      if (!mapReady || !id || !mapMarkers.has(id) || !visibleMapMarkerIds.has(id)) return;
      const marker = mapMarkers.get(id);
      if (options.pan !== false) {
        map.flyTo(marker.getLatLng(), Math.max(map.getZoom(), LOCATION_FOCUS_MIN_ZOOM), { duration: 0.55 });
      }
      highlightMapMarker(id);
    },

    resetHomeViewport() {
      if (!mapReady) return;
      map.flyTo(DEFAULT_MAP_CENTER, DEFAULT_MAP_ZOOM, { duration: 0.55 });
      highlightMapMarker(null);
    },

    invalidateSize() {
      map?.invalidateSize();
    }
  };
}
