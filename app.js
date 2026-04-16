let INDEX = [];
const LOC_CACHE = {};
let locRailScrollLeft = 0;
let lastSidebarLoc = null;
let locRailControlsBound = false;

let S = {
  view: "welcome",
  loc: null,
  tab: "climate",
  filter: null,
  chart: null,
  query: ""
};

const VIEW_HASH = {
  welcome: "#welcome",
  explorer: "#explorer"
};

const gl = () => LOC_CACHE[S.loc] || null;
const clbls = ["", "Budget", "Low", "Mid", "High", "Peak"];
const bclr = v => v <= 2 ? "#639922" : v <= 4 ? "#97C459" : v <= 6 ? "#C9973A" : v <= 8 ? "#EF9F27" : v <= 9 ? "#D85A30" : "#A32D2D";
const blbl = v => v <= 2 ? "Quiet" : v <= 4 ? "Low" : v <= 6 ? "Moderate" : v <= 8 ? "Busy" : v <= 9 ? "Very busy" : "Peak";
const cpc = v => `pill p${v}`;
const normalizeSearchText = value => String(value ?? "")
  .normalize("NFD")
  .replace(/\p{Diacritic}/gu, "")
  .trim()
  .replace(/\s+/g, " ")
  .toLowerCase();

function rSidebar() {
  const locListEl = document.getElementById("loc-list");
  const isMobile = window.matchMedia("(max-width: 900px)").matches;
  const selectedChanged = lastSidebarLoc !== S.loc;
  const priorRailScroll = isMobile && locListEl ? locListEl.scrollLeft : locRailScrollLeft;

  const query = normalizeSearchText(S.query);
  const filtered = INDEX.filter(l => {
    if (!query) return true;
    return [l.city, l.country, l.region]
      .filter(Boolean)
      .some(v => normalizeSearchText(v).includes(query));
  });
  const activeMissing = Boolean(S.loc) && !filtered.some(l => l.id === S.loc);
  const emptyState = query && filtered.length === 0
    ? `
    <div class="loc-filter-hint" role="status">
      No destinations match ‘${S.query}’.
    </div>
  `
    : "";

  locListEl.innerHTML = filtered.map(l => `
    <button class="loc-btn ${l.id === S.loc ? "active" : ""}" onclick="selLoc('${l.id}')">
      <span class="loc-city">${l.city}</span>
      <span class="loc-ctry">${l.country}</span>
    </button>
  `).join("") + emptyState + (activeMissing ? `
    <div class="loc-filter-hint" role="status">
      Selected destination is not in current filter.
    </div>
  ` : "");

  document.getElementById("dest-count").textContent = query
    ? `${filtered.length} of ${INDEX.length} destinations`
    : `${INDEX.length} destinations`;

  if (isMobile) {
    if (selectedChanged) {
      scrollActiveLocIntoView();
    } else {
      locListEl.scrollLeft = priorRailScroll;
      locRailScrollLeft = priorRailScroll;
    }
  }
  updateLocRailControls();

  lastSidebarLoc = S.loc;
}

function scrollActiveLocIntoView() {
  if (!window.matchMedia("(max-width: 900px)").matches) return;
  const rail = document.getElementById("loc-list");
  const activeBtn = document.querySelector("#loc-list .loc-btn.active");
  if (!activeBtn || !rail) return;
  activeBtn.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
  window.setTimeout(() => {
    locRailScrollLeft = rail.scrollLeft;
    updateLocRailControls();
  }, 250);
}

function updateLocRailControls() {
  const controls = document.getElementById("loc-rail-controls");
  const rail = document.getElementById("loc-list");
  const prev = document.getElementById("loc-rail-prev");
  const next = document.getElementById("loc-rail-next");
  const isRailMode = window.matchMedia("(max-width: 900px)").matches;

  if (!controls || !rail || !prev || !next) return;

  if (!isRailMode) {
    controls.hidden = true;
    return;
  }

  const maxLeft = Math.max(0, rail.scrollWidth - rail.clientWidth);
  const hasOverflow = maxLeft > 2;
  controls.hidden = !hasOverflow;
  controls.setAttribute("aria-hidden", String(!hasOverflow));

  if (!hasOverflow) return;
  prev.disabled = rail.scrollLeft <= 1;
  next.disabled = rail.scrollLeft >= maxLeft - 1;
}

function scrollLocRailByPage(direction) {
  const rail = document.getElementById("loc-list");
  if (!rail) return;
  const amount = Math.max(160, Math.floor(rail.clientWidth * 0.8));
  rail.scrollBy({ left: direction * amount, behavior: "smooth" });
  window.setTimeout(updateLocRailControls, 260);
}

function resetMainHorizontalOffsets() {
  const mainEl = document.getElementById("main");
  if (mainEl) {
    mainEl.scrollLeft = 0;
    mainEl.style.transform = "none";
  }
  document.querySelectorAll("#main .tscroll, #main .chart-scroll, #main .tab-nav").forEach(el => {
    el.scrollLeft = 0;
  });
}

function normalizeViewMode(view) {
  return view === "explorer" ? "explorer" : "welcome";
}

function viewFromHash(hash = window.location.hash) {
  if (hash === VIEW_HASH.explorer) return "explorer";
  if (hash === VIEW_HASH.welcome) return "welcome";
  return null;
}

function syncViewHash() {
  const desired = VIEW_HASH[S.view];
  if (window.location.hash !== desired) {
    history.replaceState(null, "", desired);
  }
}

function setView(view, options = {}) {
  const next = normalizeViewMode(view);
  const changed = S.view !== next;
  S.view = next;

  if (!options.skipHashSync) syncViewHash();
  rMain();

  if (!changed && options.preserveFocus) return;

  if (S.view === "welcome") {
    const welcomeHeading = document.getElementById("welcome-heading");
    const welcomeCta = document.getElementById("welcome-cta");
    (welcomeHeading || welcomeCta)?.focus();
    return;
  }

  document.getElementById("loc-search")?.focus();
}

function rWelcome() {
  return `
    <section class="welcome-panel" aria-labelledby="welcome-heading">
      <h1 id="welcome-heading" class="welcome-title" tabindex="-1">Plan your next trip with confidence.</h1>
      <p class="welcome-copy">
        Holiday Atlas helps you compare climate, costs, flights, and practical details month by month.
      </p>
      <button id="welcome-cta" class="welcome-cta" type="button" onclick="goExplorer()">
        Explore map
      </button>
    </section>
  `;
}

function rMain() {
  if (S.view === "welcome") {
    document.getElementById("main").innerHTML = rWelcome();
    resetMainHorizontalOffsets();
    return;
  }

  const L = gl();
  if (!L) return;

  document.getElementById("main").innerHTML = `
    <div class="hero">
      <div class="loc-name">${L.city}</div>
      <div class="loc-meta">${L.country} &middot; ${L.region}</div>
      <div class="tags">
        ${L.prac.directGW ? '<span class="tag g">✓ Direct from Gatwick</span>' : '<span class="tag w">✗ No direct Gatwick flight</span>'}
        ${L.source?.climateVerified
          ? '<span class="tag g">✓ Climate verified</span>'
          : (L.source?.climate?.length || L.source?.climateVerificationNote)
            ? '<span class="tag w">⚠ Climate unverified</span>'
            : ""}
        <span class="tag">${L.prac.visa}</span>
        <span class="tag">${L.prac.currency}</span>
      </div>
      <div class="desc">${L.desc}</div>
      <div class="hls">${L.hls.map(h => `<span class="hl">◆ ${h}</span>`).join("")}</div>
    </div>
    <div class="tab-nav">
      ${[
        ["climate", "Climate"],
        ["costs", "Costs & flights"],
        ["todo", "Things to do"],
        ["prac", "Practical info"]
      ].map(([id, lbl]) => `
        <button class="tab-btn ${id === S.tab ? "active" : ""}" data-tab="${id}" aria-selected="${id === S.tab}" onclick="swTab('${id}')">${lbl}</button>
      `).join("")}
    </div>
    <div class="tab-body" id="tab-body">${rTab()}</div>
  `;

  if (S.tab === "climate") initChart();
  resetMainHorizontalOffsets();
}

function rTab() {
  const L = gl();
  if (!L) return "";
  if (S.tab === "climate") return rClimate(L);
  if (S.tab === "costs") return rCosts(L);
  if (S.tab === "todo") return rTodo(L);
  if (S.tab === "prac") return rPrac(L);
  return "";
}

function rClimate(L) {
  const filters = [
    { id: "warm", lbl: "Warmest", fn: d => d.avg >= 20 },
    { id: "sunny", lbl: "Longest daylight", fn: d => d.daylight >= 12 },
    { id: "dry", lbl: "Driest", fn: d => d.rain < 35 },
    { id: "cheap", lbl: "Cheapest", fn: d => d.ac <= 2 && d.fl <= 2 },
    { id: "quiet", lbl: "Quietest", fn: d => d.busy <= 3 }
  ];

  const af = filters.find(f => f.id === S.filter);
  const climateSources = Array.isArray(L.source?.climate) ? L.source.climate : [];
  const sourceNames = climateSources.map(s => s.name).filter(Boolean);
  const verifiedLabel = sourceNames.length ? sourceNames.join(", ") : "source";
  const verifiedOn = L.source?.climateVerifiedOn ? ` (${L.source.climateVerifiedOn})` : "";
  const verificationNote = L.source?.climateVerified
    ? `<div style="margin:8px 0 0;font-size:12px;color:var(--color-text-secondary)">✓ Climate data verified via ${verifiedLabel}${verifiedOn}</div>`
    : (climateSources.length || L.source?.climateVerificationNote)
      ? `<div style="margin:8px 0 0;font-size:12px;color:var(--color-text-secondary)">⚠ Climate data not yet verified${L.source?.climateVerificationNote ? ` — ${L.source.climateVerificationNote}` : ""}</div>`
    : "";

  return `
    <div class="legend">
      <span class="lg-item"><span class="lg-dot" style="background:#D85A30"></span>High</span>
      <span class="lg-item"><span class="lg-dot" style="background:#C9973A"></span>Average</span>
      <span class="lg-item"><span class="lg-dot" style="background:#378ADD"></span>Low</span>
    </div>

    <div class="chart-scroll">
      <div class="chart-wrap">
        <div class="chart-inner">
          <canvas id="tc" role="img" aria-label="Monthly temperature chart for ${L.city}.">
            ${L.city} monthly temperatures.
          </canvas>
        </div>
      </div>
    </div>

    <div class="filter-row">
      <span class="fl-lbl">Highlight months:</span>
      ${filters.map(f => `<button class="fb ${S.filter === f.id ? "act" : ""}" onclick="setF('${f.id}')">${f.lbl}</button>`).join("")}
      ${S.filter ? `<button class="fb act" onclick="setF(null)">✕ Clear</button>` : ""}
    </div>
    ${verificationNote}

    <div class="tscroll climate-table-scroll">
      <table class="dt dt-climate">
        <thead>
          <tr>
            <th>Month</th><th>Avg</th><th>High</th><th>Low</th>
            <th>Daylight</th><th>Cloud</th><th>Rain</th>
            <th>Busy</th>
          </tr>
        </thead>
        <tbody>
          ${L.months.map(d => {
            const h = af && af.fn(d) ? "hi-row" : "";
            const bc = bclr(d.busy);

            return `
              <tr class="${h}">
                <td data-label="Month" style="font-weight:500">${d.m}</td>
                <td data-label="Avg">${d.avg}°</td>
                <td data-label="High" style="color:#D85A30;font-weight:500">${d.hi}°</td>
                <td data-label="Low" style="color:#378ADD">${d.lo}°</td>
                <td data-label="Daylight">${d.daylight.toFixed(1)}</td>
                <td data-label="Cloud">
                  <div style="display:flex;align-items:center;gap:6px">
                    <div style="width:44px;height:5px;border-radius:3px;background:var(--color-border-tertiary);overflow:hidden">
                      <div style="width:${d.cld}%;height:100%;background:#B4B2A9;border-radius:3px"></div>
                    </div>
                    <span>${d.cld}%</span>
                  </div>
                </td>
                <td data-label="Rain">${d.rain}</td>
                <td data-label="Busy">
                  <div style="display:flex;align-items:center;gap:6px">
                    <div style="display:flex;gap:1px">
                      ${Array.from({ length: 10 }).map((_, i) => `
                        <div style="width:5px;height:10px;border-radius:1px;background:${i < d.busy ? bc : "var(--color-border-tertiary)"}"></div>
                      `).join("")}
                    </div>
                    <span style="font-size:11px;color:var(--color-text-secondary)">${blbl(d.busy)}</span>
                  </div>
                </td>
              </tr>
            `;
          }).join("")}
        </tbody>
      </table>
    </div>
  `;
}

function rCosts(L) {
  return `
    <p style="font-size:13px;color:var(--color-text-secondary);margin-bottom:14px;max-width:600px;line-height:1.6">
      Cost ratings reflect relative pricing within the year.
      <span style="font-weight:500;color:var(--color-text-primary)">Budget</span> = cheapest months;
      <span style="font-weight:500;color:var(--color-text-primary)">Peak</span> = most expensive.
    </p>

    <div class="tscroll">
      <table class="dt" style="min-width:auto">
        <thead>
          <tr><th>Month</th><th>Accommodation</th><th>Flights from UK</th><th>Overall</th><th>Busyness</th></tr>
        </thead>
        <tbody>
          ${L.months.map(d => {
            const ov = Math.round((d.ac + d.fl) / 2);
            const bc = bclr(d.busy);

            return `
              <tr>
                <td data-label="Month" style="font-weight:500">${d.m}</td>
                <td><span class="${cpc(d.ac)}">${clbls[d.ac]}</span></td>
                <td><span class="${cpc(d.fl)}">${clbls[d.fl]}</span></td>
                <td><span class="${cpc(ov)}">${clbls[ov]}</span></td>
                <td>
                  <div style="display:flex;align-items:center;gap:5px">
                    <div style="display:flex;gap:1px">
                      ${Array.from({ length: 10 }).map((_, i) => `
                        <div style="width:5px;height:10px;border-radius:1px;background:${i < d.busy ? bc : "var(--color-border-tertiary)"}"></div>
                      `).join("")}
                    </div>
                    <span style="font-size:11px;color:var(--color-text-secondary)">${blbl(d.busy)}</span>
                  </div>
                </td>
              </tr>
            `;
          }).join("")}
        </tbody>
      </table>
    </div>

    <div class="hl-tip"><span style="font-weight:500;color:var(--color-text-primary)">Sweet spot:</span> ${L.sweet}</div>
  `;
}

function rTodo(L) {
  return `
    <div class="todo-grid">
      ${L.todo.map(t => `
        <div class="tc">
          <div class="tc-cat">${t.cat}</div>
          <div class="tc-name">${t.name}</div>
          <div class="tc-desc">${t.desc}</div>
        </div>
      `).join("")}
    </div>
  `;
}

function rPrac(L) {
  const p = L.prac;

  return `
    ${p.alerts.map(a => `<div class="alert-box">⚠ ${a}</div>`).join("")}
    <div class="pgrid">
      <div class="pc">
        <div class="pt">WiFi &amp; remote work</div>
        <div style="display:flex;gap:3px;margin-bottom:6px">
          ${Array.from({ length: 5 }).map((_, i) => `
            <div style="width:11px;height:11px;border-radius:50%;background:${i < p.wifi.r ? "#639922" : "var(--color-border-tertiary)"}"></div>
          `).join("")}
        </div>
        <div class="pv">${p.wifi.spd}</div>
        <div class="pn">${p.wifi.note}</div>
      </div>

      <div class="pc">
        <div class="pt">Flights from Gatwick</div>
        <div class="pv" style="color:${p.directGW ? "var(--color-text-success)" : "var(--color-text-warning)"}">
          ${p.directGW ? "✓ Direct flights available" : "✗ No direct flights"}
        </div>
        <div class="pn" style="margin-top:5px">${p.fltNote}</div>
      </div>

      <div class="pc">
        <div class="pt">Nearest airports</div>
        ${p.airports.map(a => `
          <div class="ar">
            <div>
              <span style="font-weight:500">${a.name}</span>
              <span style="font-size:11px;color:var(--color-text-secondary)">(${a.code}) · ${a.km} km</span>
            </div>
            ${a.dgw ? '<span class="dbadge">Direct LGW</span>' : ""}
          </div>
        `).join("")}
      </div>

      <div class="pc">
        <div class="pt">Entry &amp; essentials</div>
        <div class="ir"><span class="il">Visa</span><span style="text-align:right;max-width:60%">${p.visa}</span></div>
        <div class="ir"><span class="il">Currency</span><span style="text-align:right;max-width:60%">${p.currency}</span></div>
        <div class="ir"><span class="il">Language</span><span>${p.lang}</span></div>
        <div class="ir"><span class="il">Timezone</span><span>${p.tz}</span></div>
      </div>

      <div class="pc">
        <div class="pt">Best suited for</div>
        <div style="display:flex;flex-wrap:wrap;gap:5px;margin-top:4px">
          ${p.bestFor.map(b => `<span class="tag">${b}</span>`).join("")}
        </div>
      </div>
    </div>
  `;
}

function initChart() {
  const L = gl();
  const c = document.getElementById("tc");
  if (!c || !L) return;

  if (S.chart) {
    S.chart.destroy();
    S.chart = null;
  }

  const isMobile = window.matchMedia("(max-width: 900px)").matches;
  const gc = "rgba(0,0,0,.06)";
  const tc = "#888780";
  const labels = L.months.map(m => m.m);

  S.chart = new Chart(c, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "High",
          data: L.months.map(m => m.hi),
          borderColor: "#D85A30",
          backgroundColor: "rgba(216,90,48,0.08)",
          fill: true,
          tension: 0.4,
          borderWidth: isMobile ? 1.8 : 2,
          pointRadius: isMobile ? 2 : 3,
          pointHoverRadius: isMobile ? 3 : 5
        },
        {
          label: "Avg",
          data: L.months.map(m => m.avg),
          borderColor: "#C9973A",
          backgroundColor: "transparent",
          tension: 0.4,
          borderWidth: isMobile ? 1.8 : 2,
          pointRadius: isMobile ? 2 : 3,
          borderDash: [5, 3]
        },
        {
          label: "Low",
          data: L.months.map(m => m.lo),
          borderColor: "#378ADD",
          backgroundColor: "rgba(55,138,221,0.07)",
          fill: true,
          tension: 0.4,
          borderWidth: isMobile ? 1.8 : 2,
          pointRadius: isMobile ? 2 : 3,
          pointHoverRadius: isMobile ? 3 : 5
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          mode: "index",
          intersect: false,
          callbacks: {
            label: ctx => ` ${ctx.dataset.label}: ${ctx.raw}°C`
          }
        }
      },
      scales: {
        x: {
          grid: { color: gc },
          ticks: {
            color: tc,
            font: { size: isMobile ? 10 : 11 },
            maxRotation: 0,
            autoSkip: true,
            maxTicksLimit: isMobile ? 6 : 12,
            callback: (value, index) => isMobile ? labels[index].slice(0, 3) : labels[index]
          },
          border: { color: gc }
        },
        y: {
          grid: { color: gc },
          ticks: {
            color: tc,
            font: { size: isMobile ? 10 : 11 },
            callback: v => v + "°"
          },
          border: { color: gc },
          title: {
            display: !isMobile,
            text: "Temperature (°C)",
            color: tc,
            font: { size: 11 }
          }
        }
      }
    }
  });

}

async function selLoc(id) {
  S.loc = id;
  S.filter = null;
  S.tab = "climate";
  rSidebar();

  try {
    await loadLocation(id);
    rMain();
    resetMainHorizontalOffsets();
  } catch (err) {
    rLocError(id, err);
    console.error(err);
  }
}

function swTab(t) {
  S.tab = t;
  S.filter = null;
  syncTabNavState();
  document.getElementById("tab-body").innerHTML = rTab();
  if (S.tab === "climate") initChart();
  resetMainHorizontalOffsets();
}

function goExplorer() {
  setView("explorer");
}

function setF(f) {
  S.filter = f;
  const L = gl();
  if (!L) return;
  document.getElementById("tab-body").innerHTML = rClimate(L);
  initChart();
  resetMainHorizontalOffsets();
}

function syncTabNavState() {
  document.querySelectorAll(".tab-nav .tab-btn").forEach(btn => {
    const isActive = btn.dataset.tab === S.tab;

    btn.classList.toggle("active", isActive);
    btn.setAttribute("aria-selected", String(isActive));
  });
}

function addLoc() {
  alert("Add a new file in data/locations/<id>.json and add summary entry to data/locations/index.json.");
}

function isValidLocation(loc, id) {
  return Boolean(
    loc &&
    typeof loc === "object" &&
    loc.id === id &&
    Array.isArray(loc.months) &&
    Array.isArray(loc.hls) &&
    Array.isArray(loc.todo) &&
    loc.prac &&
    Array.isArray(loc.prac.alerts) &&
    Array.isArray(loc.prac.airports) &&
    Array.isArray(loc.prac.bestFor)
  );
}

function sanitizeLocation(loc) {
  const months = Array.isArray(loc.months)
    ? loc.months.map(m => ({
        m: m.m,
        avg: m.avg,
        hi: m.hi,
        lo: m.lo,
        daylight: m.daylight,
        cld: m.cld,
        rain: m.rain,
        busy: m.busy,
        ac: m.ac,
        fl: m.fl
      }))
    : [];

  const todo = Array.isArray(loc.todo)
    ? loc.todo.map(t => ({
        cat: t.cat,
        name: t.name,
        desc: t.desc
      }))
    : [];

  const airports = Array.isArray(loc.prac?.airports)
    ? loc.prac.airports.map(a => ({
        name: a.name,
        code: a.code,
        km: a.km,
        dgw: Boolean(a.dgw)
      }))
    : [];

  return {
    id: loc.id,
    city: loc.city,
    country: loc.country,
    region: loc.region,
    desc: loc.desc,
    hls: Array.isArray(loc.hls) ? loc.hls : [],
    sweet: loc.sweet ?? "",
    source: {
      climateVerified: Boolean(loc.source?.climateVerified),
      climateVerifiedOn: loc.source?.climateVerifiedOn ?? "",
      climateVerificationNote: loc.source?.climateVerificationNote ?? "",
      climate: Array.isArray(loc.source?.climate)
        ? loc.source.climate.map(s => ({
            name: s?.name ?? "",
            url: s?.url ?? ""
          }))
        : []
    },
    months,
    todo,
    prac: {
      directGW: Boolean(loc.prac?.directGW),
      visa: loc.prac?.visa ?? "",
      currency: loc.prac?.currency ?? "",
      alerts: Array.isArray(loc.prac?.alerts) ? loc.prac.alerts : [],
      wifi: {
        r: Number(loc.prac?.wifi?.r) || 0,
        spd: loc.prac?.wifi?.spd ?? "",
        note: loc.prac?.wifi?.note ?? loc.prac?.wifi?.notes ?? ""
      },
      fltNote: loc.prac?.fltNote ?? "",
      airports,
      lang: loc.prac?.lang ?? "",
      tz: loc.prac?.tz ?? "",
      bestFor: Array.isArray(loc.prac?.bestFor) ? loc.prac.bestFor : []
    }
  };
}

function rLocError(id, err) {
  document.getElementById("main").innerHTML = `
    <div style="padding:20px;font-family:system-ui,sans-serif;color:#8b2e2e;">
      <strong>Could not load destination details.</strong><br><br>
      ${id}: ${err.message}
    </div>
  `;
}

async function loadLocation(id) {
  if (LOC_CACHE[id]) return LOC_CACHE[id];

  const res = await fetch(`./data/locations/${id}.json`);
  if (!res.ok) throw new Error(`Failed to load ${id}.json (${res.status})`);

  const loc = await res.json();
  if (!isValidLocation(loc, id)) {
    throw new Error(`Invalid location payload for ${id}.`);
  }

  LOC_CACHE[id] = sanitizeLocation(loc);
  return LOC_CACHE[id];
}

async function init() {
  try {
    const res = await fetch("./data/locations/index.json");
    if (!res.ok) throw new Error(`Failed to load index.json (${res.status})`);

    INDEX = await res.json();

    if (!Array.isArray(INDEX) || INDEX.length === 0) {
      throw new Error("Location index data is empty or invalid.");
    }

    const searchInput = document.getElementById("loc-search");
    if (searchInput) {
      let isComposing = false;
      const onSearchInput = e => {
        if (isComposing) return;
        S.query = e.target.value;
        rSidebar();
      };

      searchInput.addEventListener("compositionstart", () => {
        isComposing = true;
      });
      searchInput.addEventListener("compositionend", e => {
        isComposing = false;
        S.query = e.target.value;
        rSidebar();
      });
      searchInput.addEventListener("input", onSearchInput);
      searchInput.addEventListener("search", onSearchInput);
    }

    S.loc = INDEX[0].id;
    S.view = normalizeViewMode(viewFromHash() || "welcome");
    const locListEl = document.getElementById("loc-list");
    if (locListEl) {
      locListEl.addEventListener("scroll", () => {
        locRailScrollLeft = locListEl.scrollLeft;
        updateLocRailControls();
      }, { passive: true });
    }
    if (!locRailControlsBound) {
      document.getElementById("loc-rail-prev")?.addEventListener("click", () => {
        scrollLocRailByPage(-1);
      });
      document.getElementById("loc-rail-next")?.addEventListener("click", () => {
        scrollLocRailByPage(1);
      });
      window.addEventListener("resize", () => {
        updateLocRailControls();
        resetMainHorizontalOffsets();
        S.chart?.resize();
      });
      locRailControlsBound = true;
    }
    rSidebar();

    try {
      await loadLocation(S.loc);
      if (!window.__holidayAtlasHashBound) {
        window.addEventListener("hashchange", () => {
          const hashView = viewFromHash();
          if (!hashView) return;
          setView(hashView, { skipHashSync: true, preserveFocus: true });
        });
        window.__holidayAtlasHashBound = true;
      }
      setView(S.view);
    } catch (err) {
      rLocError(S.loc, err);
      console.error(err);
    }
  } catch (err) {
    document.getElementById("main").innerHTML = `
      <div style="padding:20px;font-family:system-ui,sans-serif;color:#8b2e2e;">
        <strong>Could not load destination data.</strong><br><br>
        ${err.message}
      </div>
    `;
    console.error(err);
  }
}

init();
