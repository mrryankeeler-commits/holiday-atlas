import { createStateStore } from "./js/state.js";
import { createDataStore } from "./js/data.js";
import { createMapController } from "./js/map.js";
import { createRenderer } from "./js/render.js";
import { viewFromHash, VIEW_HASH } from "./js/utils.js";

const dataStore = createDataStore();
const stateStore = createStateStore();
let mapEnhancementFlags = {
  mapClustering: false,
  mapRegionFilters: false,
  mapResponsiveSplitTuning: false
};

const syncViewHash = () => {
  const desired = VIEW_HASH[stateStore.state.view];
  if (window.location.hash !== desired) history.replaceState(null, "", desired);
};

let renderer;

const renderErrorState = (message, detail = "") => {
  const main = document.getElementById("main");
  if (!main) return;

  const container = document.createElement("div");
  container.style.padding = "20px";
  container.style.color = "#8b2e2e";

  const title = document.createElement("strong");
  title.textContent = message;
  container.append(title);

  if (detail) {
    container.append(document.createElement("br"), document.createElement("br"));
    container.append(document.createTextNode(detail));
  }

  main.replaceChildren(container);
};

const setView = (view, { skipHashSync = false } = {}) => {
  stateStore.setView(view);
  if (!skipHashSync) syncViewHash();
  renderer.renderMain();
  renderer.syncHeaderNavState();
  if (stateStore.state.view === "welcome") mapController.resetHomeViewport();
};

const getLocation = () => dataStore.getLocationFromCache(stateStore.state.loc);
const getFilteredLocations = () => renderer.getFilteredLocations();

const refreshExplorerSync = ({ shouldFocusMap = false } = {}) => {
  renderer.renderSidebar();
  if (stateStore.state.view === "explorer") renderer.renderMain();
  if (shouldFocusMap) mapController.focusLocation(stateStore.state.loc, { pan: false });
};

const selectLocation = async (id, options = {}) => {
  if (!id || !dataStore.getIndex().some(loc => loc.id === id)) return;
  stateStore.setLocation(id);
  if (options.switchToExplorer !== false && stateStore.state.view !== "explorer") setView("explorer");
  renderer.renderSidebar();
  mapController.focusLocation(stateStore.state.loc, { pan: options.panMap !== false });
  try {
    await dataStore.loadLocation(id);
    if (stateStore.state.view === "explorer") renderer.renderMain();
  } catch (err) {
    const detail = `${id}: ${err?.message ?? "Unknown error"}`;
    renderErrorState("Could not load destination details.", detail);
  }
};

const mapController = createMapController({
  getState: () => stateStore.state,
  getIndex: () => dataStore.getIndex(),
  onMarkerSelect: (id) => selectLocation(id, { panMap: true })
});

renderer = createRenderer({
  getState: () => stateStore.state,
  getIndex: () => dataStore.getIndex(),
  getLocation,
  mapController,
  actions: {
    setChart: chart => stateStore.setChart(chart),
    goHome: () => setView("welcome"),
    goExplorer: () => setView("explorer"),
    addLoc: () => alert("Add a new file in data/locations/<id>.json and add summary entry to data/locations/index.json."),
    selectLocation: id => selectLocation(id),
    switchTab: tab => {
      stateStore.setTab(tab);
      renderer.renderMain();
    },
    setFilter: filter => {
      stateStore.setFilter(filter);
      renderer.renderMain();
    },
    setPref: (key, value) => {
      stateStore.setPref(key, value);
      if (stateStore.state.tab === "climate") renderer.renderMain();
    },
    setQuery: query => {
      stateStore.setQuery(query);
      renderer.renderSidebar();
    },
    setRegionFilter: region => {
      if (!mapEnhancementFlags.mapRegionFilters) return;
      stateStore.setRegion(region);
      const filtered = getFilteredLocations();
      if (!filtered.some(loc => loc.id === stateStore.state.loc)) {
        const nextLocation = filtered[0]?.id || dataStore.getIndex()[0]?.id || null;
        if (nextLocation) stateStore.setLocation(nextLocation);
      }
      refreshExplorerSync({ shouldFocusMap: true });
    }
  }
});

async function init() {
  try {
    await dataStore.loadIndex();
    stateStore.setLocation(dataStore.getIndex()[0].id);
    stateStore.setView(viewFromHash() || "welcome");

    renderer.bindEvents();
    document.getElementById("home-btn")?.setAttribute("data-action", "go-home");
    document.getElementById("explore-btn")?.setAttribute("data-action", "go-explorer");
    document.querySelector(".add-btn-sb")?.setAttribute("data-action", "open-add");
    mapEnhancementFlags = mapController.getEnhancementFlags();
    document.body.classList.toggle("ff-responsive-split-tuning", Boolean(mapEnhancementFlags.mapResponsiveSplitTuning));

    renderer.renderSidebar();
    mapController.initMap();

    await dataStore.loadLocation(stateStore.state.loc);
    setView(stateStore.state.view);

    window.addEventListener("hashchange", () => {
      const hashView = viewFromHash();
      if (!hashView) return;
      setView(hashView, { skipHashSync: true });
    });

    window.addEventListener("resize", () => {
      mapController.invalidateSize();
      stateStore.state.chart?.resize();
    });
  } catch (err) {
    renderErrorState("Could not load destination data.", err?.message ?? "Unknown error");
  }
}

init();

window.selLocFromDeepLink = id => selectLocation(id, { panMap: false, switchToExplorer: false });
