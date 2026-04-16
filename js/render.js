import {
  DEPARTURE_AIRPORTS,
  getDirectAirportCodes,
  normalizeSearchText,
  computeRecommendationScores,
  bclr,
  blbl,
  cpc,
  clbls
} from "./utils.js";

export function createRenderer({ getState, getIndex, getLocation, actions, mapController }) {
  let lastSidebarLoc = null;

  const getFilteredLocations = (normalizedQuery = normalizeSearchText(getState().query)) => getIndex().filter(l => {
    if (!normalizedQuery) return true;
    return [l.city, l.country, l.region].filter(Boolean).some(v => normalizeSearchText(v).includes(normalizedQuery));
  });

  const resetMainHorizontalOffsets = () => {
    const mainEl = document.getElementById("main");
    if (mainEl) {
      mainEl.scrollLeft = 0;
      mainEl.style.transform = "none";
    }
    document.querySelectorAll("#main .tscroll, #main .chart-scroll, #main .tab-nav").forEach(el => {
      el.scrollLeft = 0;
    });
  };

  const rWelcome = () => `
    <section class="welcome-panel" aria-labelledby="welcome-heading">
      <h1 id="welcome-heading" class="welcome-title" tabindex="-1">Plan your next trip with confidence.</h1>
      <p class="welcome-copy">Holiday Atlas helps you compare climate, costs, flights, and practical details month by month.</p>
      <button id="welcome-cta" class="welcome-cta" type="button" data-action="go-explorer">Explore map</button>
    </section>
  `;

  const rTodo = L => `<div class="todo-grid">${L.todo.map(t => `<div class="tc"><div class="tc-cat">${t.cat}</div><div class="tc-name">${t.name}</div><div class="tc-desc">${t.desc}</div></div>`).join("")}</div>`;

  const rCosts = L => `
    <p style="font-size:13px;color:var(--color-text-secondary);margin-bottom:14px;max-width:600px;line-height:1.6">Cost ratings reflect relative pricing within the year.</p>
    <div class="tscroll"><table class="dt" style="min-width:auto"><thead><tr><th>Month</th><th>Accommodation</th><th>Flights from UK</th><th>Overall</th><th>Busyness</th></tr></thead>
      <tbody>${L.months.map(d => {
        const ov = Math.round((d.ac + d.fl) / 2);
        const bc = bclr(d.busy);
        return `<tr><td data-label="Month" style="font-weight:500">${d.m}</td><td><span class="${cpc(d.ac)}">${clbls[d.ac]}</span></td><td><span class="${cpc(d.fl)}">${clbls[d.fl]}</span></td><td><span class="${cpc(ov)}">${clbls[ov]}</span></td><td><div style="display:flex;align-items:center;gap:5px"><div style="display:flex;gap:1px">${Array.from({ length: 10 }).map((_, i) => `<div style="width:5px;height:10px;border-radius:1px;background:${i < d.busy ? bc : "var(--color-border-tertiary)"}"></div>`).join("")}</div><span style="font-size:11px;color:var(--color-text-secondary)">${blbl(d.busy)}</span></div></td></tr>`;
      }).join("")}</tbody></table></div>
    <div class="hl-tip"><span style="font-weight:500;color:var(--color-text-primary)">Sweet spot:</span> ${L.sweet}</div>
  `;

  const rPrac = L => {
    const p = L.prac;
    const routeDirectCodes = getDirectAirportCodes(p.directFrom);
    const routeDirectLabel = DEPARTURE_AIRPORTS.map(a => a.label).join(" / ");
    return `${p.alerts.map(a => `<div class="alert-box">⚠ ${a}</div>`).join("")}
    <div class="pgrid"><div class="pc"><div class="pt">Flights from ${routeDirectLabel}</div><div class="pv">${routeDirectCodes.length ? routeDirectCodes.map(code => `<span class="dbadge">Direct ${code}</span>`).join(" ") : "✗ No direct flights from configured London airports"}</div><div class="pn" style="margin-top:5px">${p.fltNote}</div></div></div>`;
  };

  const rClimate = L => {
    const filters = [
      { id: "warm", lbl: "Warmest" },
      { id: "sunny", lbl: "Longest daylight" },
      { id: "dry", lbl: "Driest" },
      { id: "cheap", lbl: "Cheapest" },
      { id: "quiet", lbl: "Quietest" }
    ];
    const recommendations = computeRecommendationScores(L, getState().prefs).slice(0, 4);

    return `
      <section class="best-months-panel" aria-label="Best months for you">
        <div class="pref-grid" role="group" aria-label="Recommendation preferences">
          ${["weather", "budget", "crowds", "direct"].map(key => `
            <label class="pref-item">${key}
              <input type="range" min="0" max="5" step="1" value="${getState().prefs[key]}" data-pref-key="${key}" />
              <span class="pref-val">${getState().prefs[key]}</span>
            </label>
          `).join("")}
        </div>
        <div class="rec-chip-row">${recommendations.map((rec, idx) => `<article class="rec-chip"><div class="rec-top"><span class="rec-rank">#${idx + 1}</span><span class="rec-month">${rec.month}</span><span class="rec-score">${rec.score}</span></div><p class="rec-why">${rec.rationale}</p></article>`).join("")}</div>
      </section>
      <div class="filter-row"><span class="fl-lbl">Highlight months:</span>
        ${filters.map(f => `<button class="fb ${getState().filter === f.id ? "act" : ""}" data-action="set-filter" data-filter="${f.id}">${f.lbl}</button>`).join("")}
        ${getState().filter ? `<button class="fb act" data-action="set-filter" data-filter="">✕ Clear</button>` : ""}
      </div>
      <div class="chart-scroll"><div class="chart-wrap"><div class="chart-inner"><canvas id="tc"></canvas></div></div></div>`;
  };

  const rTab = L => {
    if (!L) return "";
    if (getState().tab === "climate") return rClimate(L);
    if (getState().tab === "costs") return rCosts(L);
    if (getState().tab === "todo") return rTodo(L);
    return rPrac(L);
  };

  const initChart = () => {
    const L = getLocation();
    const c = document.getElementById("tc");
    if (!c || !L) return;
    if (getState().chart) getState().chart.destroy();
    const labels = L.months.map(m => m.m);
    actions.setChart(new Chart(c, {
      type: "line",
      data: { labels, datasets: [{ label: "High", data: L.months.map(m => m.hi), borderColor: "#D85A30" }, { label: "Avg", data: L.months.map(m => m.avg), borderColor: "#C9973A" }, { label: "Low", data: L.months.map(m => m.lo), borderColor: "#378ADD" }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
    }));
  };

  const renderMain = () => {
    if (getState().view === "welcome") {
      document.getElementById("main").innerHTML = rWelcome();
      resetMainHorizontalOffsets();
      return;
    }
    const L = getLocation();
    if (!L) return;
    document.getElementById("main").innerHTML = `
      <div class="hero"><div class="loc-name">${L.city}</div><div class="loc-meta">${L.country} &middot; ${L.region}</div></div>
      <div class="tab-nav">${[["climate", "Climate"], ["costs", "Costs & flights"], ["todo", "Things to do"], ["prac", "Practical info"]].map(([id, lbl]) => `<button class="tab-btn ${id === getState().tab ? "active" : ""}" data-action="switch-tab" data-tab="${id}">${lbl}</button>`).join("")}</div>
      <div class="tab-body" id="tab-body">${rTab(L)}</div>`;
    if (getState().tab === "climate") initChart();
    resetMainHorizontalOffsets();
  };

  const renderSidebar = () => {
    const locListEl = document.getElementById("loc-list");
    const query = normalizeSearchText(getState().query);
    const filtered = getFilteredLocations(query);
    locListEl.innerHTML = filtered.map(l => `<button class="loc-btn ${l.id === getState().loc ? "active" : ""}" data-action="select-loc" data-id="${l.id}"><span class="loc-city">${l.city}</span><span class="loc-ctry">${l.country}</span></button>`).join("");
    document.getElementById("dest-count").textContent = query ? `${filtered.length} of ${getIndex().length} destinations` : `${getIndex().length} destinations`;
    mapController.applyFilter(filtered, query);
    lastSidebarLoc = getState().loc;
  };

  const syncHeaderNavState = () => {
    const homeBtn = document.getElementById("home-btn");
    const exploreBtn = document.getElementById("explore-btn");
    if (!homeBtn || !exploreBtn) return;
    const onWelcome = getState().view === "welcome";
    homeBtn.classList.toggle("active", onWelcome);
    exploreBtn.classList.toggle("active", !onWelcome);
  };

  const bindEvents = () => {
    document.addEventListener("click", (event) => {
      const target = event.target.closest("[data-action]");
      if (!target) return;
      const action = target.dataset.action;
      if (action === "go-home") actions.goHome();
      if (action === "go-explorer") actions.goExplorer();
      if (action === "open-add") actions.addLoc();
      if (action === "select-loc") actions.selectLocation(target.dataset.id);
      if (action === "switch-tab") actions.switchTab(target.dataset.tab);
      if (action === "set-filter") actions.setFilter(target.dataset.filter || null);
    });

    document.addEventListener("input", (event) => {
      const prefInput = event.target.closest("[data-pref-key]");
      if (prefInput) actions.setPref(prefInput.dataset.prefKey, prefInput.value);
    });

    document.getElementById("loc-search")?.addEventListener("input", (e) => actions.setQuery(e.target.value));
  };

  return {
    bindEvents,
    getFilteredLocations,
    renderSidebar,
    renderMain,
    syncHeaderNavState,
    initChart,
    resetMainHorizontalOffsets
  };
}
