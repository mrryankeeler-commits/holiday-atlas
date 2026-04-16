import { RECOMMENDATION_METRICS } from "./utils.js";

export function createStateStore(initialLoc = null) {
  const state = {
    view: "welcome",
    loc: initialLoc,
    tab: "climate",
    filter: null,
    chart: null,
    query: "",
    prefs: {
      weather: 4,
      budget: 3,
      crowds: 3,
      direct: 2
    }
  };

  return {
    state,
    setView(view) {
      state.view = view === "explorer" ? "explorer" : "welcome";
    },
    setLocation(id) {
      state.loc = id;
      state.filter = null;
      state.tab = "climate";
    },
    setTab(tab) {
      state.tab = tab;
      state.filter = null;
    },
    setFilter(filter) {
      state.filter = filter;
    },
    setQuery(query) {
      state.query = query;
    },
    setPref(key, value) {
      if (!RECOMMENDATION_METRICS.includes(key)) return;
      state.prefs[key] = Math.max(0, Math.min(5, Number(value) || 0));
    },
    setChart(chart) {
      state.chart = chart;
    }
  };
}
