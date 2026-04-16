import test from "node:test";
import assert from "node:assert/strict";

import { normalizeSearchText } from "../../js/utils.js";
import { filterLocations } from "../../js/filtering.js";
import { createStateStore } from "../../js/state.js";
import { FEATURE_FLAGS, getMapRolloutState } from "../../js/map.js";

test("normalizeSearchText normalizes whitespace, case, and diacritics", () => {
  assert.equal(normalizeSearchText("  São   PAULO "), "sao paulo");
});

test("normalizeSearchText handles nullish values", () => {
  assert.equal(normalizeSearchText(null), "");
  assert.equal(normalizeSearchText(undefined), "");
});

test("filterLocations filters by normalized query", () => {
  const index = [
    { id: "lisbon", city: "Lisbon", country: "Portugal", region: "Europe" },
    { id: "sao-paulo", city: "São Paulo", country: "Brazil", region: "South America" },
    { id: "kyoto", city: "Kyoto", country: "Japan", region: "Asia" }
  ];

  const filtered = filterLocations(index, { query: "sao" });
  assert.deepEqual(filtered.map(loc => loc.id), ["sao-paulo"]);
});

test("filterLocations applies query and region together", () => {
  const index = [
    { id: "lisbon", city: "Lisbon", country: "Portugal", region: "Europe" },
    { id: "porto", city: "Porto", country: "Portugal", region: "Europe" },
    { id: "kyoto", city: "Kyoto", country: "Japan", region: "Asia" }
  ];

  const filtered = filterLocations(index, { region: "Europe", query: "porto" });
  assert.deepEqual(filtered.map(loc => loc.id), ["porto"]);
});

test("selection invariant: setLocation resets filter and tab", () => {
  const store = createStateStore("lisbon");
  store.setTab("todo");
  store.setFilter("warm");

  store.setLocation("kyoto");

  assert.equal(store.state.loc, "kyoto");
  assert.equal(store.state.tab, "climate");
  assert.equal(store.state.filter, null);
});

test("selection invariant: setTab resets filter", () => {
  const store = createStateStore("lisbon");
  store.setFilter("dry");

  store.setTab("costs");

  assert.equal(store.state.tab, "costs");
  assert.equal(store.state.filter, null);
});

test("map rollout gate disables map when feature flag is off", () => {
  const state = getMapRolloutState({
    featureFlags: { ...FEATURE_FLAGS, enableMap: false },
    protocol: "https:",
    hostname: "holiday-atlas.example",
    index: [{ id: "ok", lat: 41.1, lng: -8.6 }]
  });

  assert.equal(state.enabled, false);
  assert.match(state.reason, /disabled via feature flag/);
});

test("map rollout gate disables map in production when any coordinate is invalid", () => {
  const state = getMapRolloutState({
    featureFlags: { ...FEATURE_FLAGS },
    protocol: "https:",
    hostname: "holiday-atlas.example",
    index: [{ id: "bad", lat: 300, lng: 1000 }]
  });

  assert.equal(state.enabled, false);
  assert.match(state.reason, /production readiness gate/);
});

test("map rollout gate allows local runtime with invalid coordinates", () => {
  const state = getMapRolloutState({
    featureFlags: { ...FEATURE_FLAGS },
    protocol: "http:",
    hostname: "localhost",
    index: [{ id: "bad", lat: 300, lng: 1000 }]
  });

  assert.deepEqual(state, { enabled: true, reason: "" });
});
