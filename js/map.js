export const FEATURE_FLAGS = {
  enableMap: true,
  requireMapCoordinateReadinessInProduction: true,
  mapClustering: true,
  mapRegionFilters: true,
  mapResponsiveSplitTuning: true
};

const DEFAULT_MAP_CENTER = [20, 0];
const DEFAULT_MAP_ZOOM = 2;
const LOCATION_FOCUS_MIN_ZOOM = 5;


export const isValidCoordinatePair = loc => Number.isFinite(loc?.lat)
  && Number.isFinite(loc?.lng)
  && loc.lat >= -90
  && loc.lat <= 90
  && loc.lng >= -180
  && loc.lng <= 180;

export const isProductionRuntime = ({ protocol, hostname }) => protocol !== "file:"
  && !["localhost", "127.0.0.1"].includes(hostname);

export const getMapRolloutState = ({ featureFlags, protocol, hostname, index }) => {
  if (!featureFlags.enableMap) {
    return { enabled: false, reason: "Map rollout is currently disabled via feature flag. Browse destinations from the list." };
  }

  if (
    featureFlags.requireMapCoordinateReadinessInProduction
    && isProductionRuntime({ protocol, hostname })
    && !index.every(isValidCoordinatePair)
  ) {
    return { enabled: false, reason: "Map is temporarily disabled until all destination coordinates pass the production readiness gate." };
  }

  return { enabled: true, reason: "" };
};

export function createMapController({ getState, getIndex, onMarkerSelect }) {
  let map = null;
  let mapReady = false;
  let mapInitAttempted = false;
  const mapMarkers = new Map();
  const clusterMarkers = [];
  const visibleMapMarkerIds = new Set();
  let highlightedMarkerId = null;
  let clusterLayer = null;

  const getEnhancementFlags = () => ({
    mapClustering: FEATURE_FLAGS.mapClustering,
    mapRegionFilters: FEATURE_FLAGS.mapRegionFilters,
    mapResponsiveSplitTuning: FEATURE_FLAGS.mapResponsiveSplitTuning
  });

  const mapIcon = ({ isActive = false } = {}) => L.divIcon({
    className: "",
    html: `<span class="dest-marker variant-country ${isActive ? "active" : ""}" aria-hidden="true"></span>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9]
  });
  const clusterIcon = (count) => L.divIcon({
    className: "",
    html: `<span class="cluster-marker" aria-hidden="true">${count}</span>`,
    iconSize: [34, 34],
    iconAnchor: [17, 17]
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


  const getMapRolloutStateForRuntime = () => getMapRolloutState({
    featureFlags: FEATURE_FLAGS,
    protocol: window.location.protocol,
    hostname: window.location.hostname,
    index: getIndex()
  });

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

  const clearClusterMarkers = () => {
    clusterMarkers.forEach(marker => marker.remove());
    clusterMarkers.length = 0;
  };

  const setMarkerVisibility = (marker, visible) => {
    marker.setOpacity(visible ? 1 : 0);
    const markerEl = marker.getElement();
    if (markerEl) {
      markerEl.style.pointerEvents = visible ? "auto" : "none";
      markerEl.style.visibility = visible ? "visible" : "hidden";
    }
  };

  const getClusterCellSize = (zoom) => {
    if (zoom <= 2) return 16;
    if (zoom <= 4) return 10;
    if (zoom <= 6) return 6;
    return 0;
  };

  const applyClusterVisibility = () => {
    if (!mapReady || !FEATURE_FLAGS.mapClustering) return;
    clearClusterMarkers();
    const cellSize = getClusterCellSize(map.getZoom());
    if (!cellSize) {
      visibleMapMarkerIds.forEach(id => {
        if (mapMarkers.has(id)) setMarkerVisibility(mapMarkers.get(id), true);
      });
      highlightMapMarker(visibleMapMarkerIds.has(getState().loc) ? getState().loc : null);
      return;
    }

    const clusters = new Map();
    visibleMapMarkerIds.forEach(id => {
      const marker = mapMarkers.get(id);
      if (!marker) return;
      const p = map.project(marker.getLatLng(), map.getZoom());
      const key = `${Math.floor(p.x / cellSize)}:${Math.floor(p.y / cellSize)}`;
      if (!clusters.has(key)) clusters.set(key, []);
      clusters.get(key).push({ id, marker });
    });

    clusters.forEach(entries => {
      if (entries.length === 1) {
        setMarkerVisibility(entries[0].marker, true);
        return;
      }
      entries.forEach(entry => setMarkerVisibility(entry.marker, false));
      const center = entries
        .map(entry => entry.marker.getLatLng())
        .reduce((acc, curr) => L.latLng(acc.lat + curr.lat, acc.lng + curr.lng), L.latLng(0, 0));
      const clusterCenter = L.latLng(center.lat / entries.length, center.lng / entries.length);
      const marker = L.marker(clusterCenter, {
        icon: clusterIcon(entries.length),
        keyboard: true,
        title: `Cluster with ${entries.length} destinations`
      }).addTo(clusterLayer);
      marker.on("click", () => {
        map.flyTo(clusterCenter, Math.min(map.getZoom() + 2, 9), { duration: 0.45 });
      });
      clusterMarkers.push(marker);
    });

    if (getState().loc && mapMarkers.has(getState().loc) && visibleMapMarkerIds.has(getState().loc)) {
      const selectedMarker = mapMarkers.get(getState().loc);
      setMarkerVisibility(selectedMarker, true);
      selectedMarker.bringToFront();
    }
    highlightMapMarker(visibleMapMarkerIds.has(getState().loc) ? getState().loc : null);
  };

  return {
    initMap() {
      const rolloutState = getMapRolloutStateForRuntime();
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
        if (FEATURE_FLAGS.mapClustering) clusterLayer = L.layerGroup().addTo(map);
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
        map.on("zoomend moveend", () => {
          applyClusterVisibility();
        });
      } catch (err) {
        console.error(err);
        showMapFallback("Map failed to initialize. You can still browse destinations from the list.");
      }
    },

    applyFilter(filteredLocations, query) {
      if (!mapReady) return;
      const filteredIds = new Set(filteredLocations.map(loc => loc.id));

      visibleMapMarkerIds.clear();
      mapMarkers.forEach((marker, id) => {
        const visible = filteredIds.has(id);
        setMarkerVisibility(marker, visible);
        if (visible) visibleMapMarkerIds.add(id);
      });

      if (FEATURE_FLAGS.mapClustering) applyClusterVisibility();
      else highlightMapMarker(visibleMapMarkerIds.has(getState().loc) ? getState().loc : null);
    },

    focusLocation(id, options = {}) {
      if (!mapReady || !id || !mapMarkers.has(id) || !visibleMapMarkerIds.has(id)) return;
      const marker = mapMarkers.get(id);
      if (options.pan !== false) {
        map.flyTo(marker.getLatLng(), Math.max(map.getZoom(), LOCATION_FOCUS_MIN_ZOOM), { duration: 0.55 });
      }
      setMarkerVisibility(marker, true);
      marker.bringToFront();
      clearClusterMarkers();
      if (FEATURE_FLAGS.mapClustering) applyClusterVisibility();
      highlightMapMarker(id);
    },

    resetHomeViewport() {
      if (!mapReady) return;
      map.flyTo(DEFAULT_MAP_CENTER, DEFAULT_MAP_ZOOM, { duration: 0.55 });
      highlightMapMarker(null);
    },

    invalidateSize() {
      map?.invalidateSize();
    },
    getEnhancementFlags
  };
}
