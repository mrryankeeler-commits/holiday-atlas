let INDEX = [];
const LOC_CACHE = {};
let locRailScrollLeft = 0;
let lastSidebarLoc = null;
let locRailControlsBound = false;
let map = null;
let mapReady = false;
let mapInitAttempted = false;
const mapMarkers = new Map();
const visibleMapMarkerIds = new Set();
const hoveredMapMarkerIds = new Set();
const focusedMapMarkerIds = new Set();
let highlightedMarkerId = null;
let mapRolloutState = { enabled: false, reason: "" };

const FEATURE_FLAGS = {
  enableMap: true,
  requireMapCoordinateReadinessInProduction: true
};
const DEFAULT_MAP_CENTER = [20, 0];
const DEFAULT_MAP_ZOOM = 2;
const LOCATION_FOCUS_MIN_ZOOM = 5;
const MAP_ZOOM_LOW_MAX = 3;
const MAP_ZOOM_MID_MAX = 6;
const MARKER_FALLBACK_PALETTES = [
  { token: "palette-fallback-1", fill: "#1f7a5c", halo: "rgba(217,247,237,0.78)" },
  { token: "palette-fallback-2", fill: "#8c2f75", halo: "rgba(248,222,244,0.78)" },
  { token: "palette-fallback-3", fill: "#9a5300", halo: "rgba(255,231,200,0.78)" },
  { token: "palette-fallback-4", fill: "#205f9e", halo: "rgba(218,235,255,0.8)" },
  { token: "palette-fallback-5", fill: "#5f3f95", halo: "rgba(230,221,249,0.78)" }
];
const COUNTRY_FLAG_PALETTES = {
  "albania": { token: "flag-albania", fill: "radial-gradient(circle at 50% 50%, #111111 0 20%, transparent 21%), linear-gradient(90deg, #e41e26 0 100%)", halo: "rgba(255,224,224,0.82)" },
  "andorra": { token: "flag-andorra", fill: "linear-gradient(90deg, #1f4fb3 0 33.33%, #f6d34e 33.33% 66.66%, #c7362c 66.66% 100%)", halo: "rgba(232,238,255,0.85)" },
  "argentina": { token: "flag-argentina", fill: "linear-gradient(180deg, #74acdf 0 33.33%, #ffffff 33.33% 66.66%, #74acdf 66.66% 100%)", halo: "rgba(225,241,255,0.84)" },
  "australia": { token: "flag-australia", fill: "radial-gradient(circle at 34% 34%, #ffffff 0 7%, transparent 8%), radial-gradient(circle at 60% 54%, #ffffff 0 5%, transparent 6%), radial-gradient(circle at 72% 32%, #ffffff 0 4%, transparent 5%), #0a2f7a", halo: "rgba(222,232,255,0.82)" },
  "austria": { token: "flag-austria", fill: "linear-gradient(180deg, #d81e2c 0 33.33%, #ffffff 33.33% 66.66%, #d81e2c 66.66% 100%)", halo: "rgba(255,230,230,0.84)" },
  "belgium": { token: "flag-belgium", fill: "linear-gradient(90deg, #000000 0 33.33%, #ffde00 33.33% 66.66%, #ef3340 66.66% 100%)", halo: "rgba(255,242,214,0.84)" },
  "belize": { token: "flag-belize", fill: "linear-gradient(180deg, #ce1126 0 14%, #003f87 14% 86%, #ce1126 86% 100%)", halo: "rgba(224,236,255,0.84)" },
  "bolivia": { token: "flag-bolivia", fill: "linear-gradient(180deg, #d52b1e 0 33.33%, #f9e300 33.33% 66.66%, #007934 66.66% 100%)", halo: "rgba(255,246,214,0.84)" },
  "bosnia & herzegovina": { token: "flag-bosnia", fill: "linear-gradient(130deg, #1d3f8a 0 74%, #f2c94c 74% 100%)", halo: "rgba(224,233,255,0.84)" },
  "bosnia and herzegovina": { token: "flag-bosnia", fill: "linear-gradient(130deg, #1d3f8a 0 74%, #f2c94c 74% 100%)", halo: "rgba(224,233,255,0.84)" },
  "brazil": { token: "flag-brazil", fill: "linear-gradient(135deg, #009b3a 0 39%, #ffdf00 39% 61%, #002776 61% 100%)", halo: "rgba(227,255,235,0.84)" },
  "bulgaria": { token: "flag-bulgaria", fill: "linear-gradient(180deg, #ffffff 0 33.33%, #2f8d47 33.33% 66.66%, #d0342c 66.66% 100%)", halo: "rgba(232,255,238,0.84)" },
  "cambodia": { token: "flag-cambodia", fill: "linear-gradient(180deg, #032ea1 0 25%, #e00025 25% 75%, #032ea1 75% 100%)", halo: "rgba(224,235,255,0.84)" },
  "canada": { token: "flag-canada", fill: "radial-gradient(circle at 50% 50%, #d80621 0 14%, transparent 15%), linear-gradient(90deg, #d80621 0 25%, #ffffff 25% 75%, #d80621 75% 100%)", halo: "rgba(255,229,232,0.84)" },
  "chile": { token: "flag-chile", fill: "linear-gradient(135deg, #0039a6 0 33.33%, #ffffff 33.33% 66.66%, #d52b1e 66.66% 100%)", halo: "rgba(228,238,255,0.84)" },
  "china": { token: "flag-china", fill: "linear-gradient(90deg, #de2910 0 100%)", halo: "rgba(255,226,219,0.82)" },
  "colombia": { token: "flag-colombia", fill: "linear-gradient(180deg, #fcd116 0 50%, #003893 50% 75%, #ce1126 75% 100%)", halo: "rgba(255,246,214,0.84)" },
  "croatia": { token: "flag-croatia", fill: "linear-gradient(180deg, #d3202c 0 33.33%, #ffffff 33.33% 66.66%, #1f4ea3 66.66% 100%)", halo: "rgba(230,236,255,0.84)" },
  "cuba": { token: "flag-cuba", fill: "linear-gradient(180deg, #002a8f 0 20%, #ffffff 20% 40%, #002a8f 40% 60%, #ffffff 60% 80%, #002a8f 80% 100%)", halo: "rgba(225,235,255,0.84)" },
  "cyprus": { token: "flag-cyprus", fill: "radial-gradient(circle at 50% 44%, #d57800 0 16%, transparent 17%), radial-gradient(ellipse at 50% 66%, #3a8d3f 0 10%, transparent 11%), #ffffff", halo: "rgba(255,250,232,0.84)" },
  "czechia": { token: "flag-czechia", fill: "linear-gradient(180deg, #ffffff 0 50%, #d91d2a 50% 100%)", halo: "rgba(230,238,255,0.84)" },
  "denmark": { token: "flag-denmark", fill: "linear-gradient(90deg, transparent 0 30%, #ffffff 30% 44%, transparent 44%), linear-gradient(180deg, transparent 0 42%, #ffffff 42% 58%, transparent 58%), #c8102e", halo: "rgba(255,228,233,0.82)" },
  "dominican republic": { token: "flag-dominican-republic", fill: "conic-gradient(from 90deg, #002d62 0 25%, #ffffff 25% 50%, #ce1126 50% 75%, #ffffff 75% 100%)", halo: "rgba(226,236,255,0.84)" },
  "egypt": { token: "flag-egypt", fill: "linear-gradient(180deg, #ce1126 0 33.33%, #ffffff 33.33% 66.66%, #000000 66.66% 100%)", halo: "rgba(244,244,244,0.84)" },
  "england": { token: "flag-england", fill: "linear-gradient(90deg, transparent 0 38%, #ce1126 38% 62%, transparent 62%), linear-gradient(180deg, transparent 0 38%, #ce1126 38% 62%, transparent 62%), #ffffff", halo: "rgba(255,229,232,0.84)" },
  "ecuador": { token: "flag-ecuador", fill: "linear-gradient(180deg, #fcd116 0 50%, #003893 50% 75%, #ce1126 75% 100%)", halo: "rgba(255,245,212,0.84)" },
  "estonia": { token: "flag-estonia", fill: "linear-gradient(180deg, #4891d9 0 33.33%, #111111 33.33% 66.66%, #ffffff 66.66% 100%)", halo: "rgba(226,242,255,0.84)" },
  "faroe islands": { token: "flag-faroe-islands", fill: "linear-gradient(90deg, #ffffff 0 40%, #ef3340 40% 70%, #005eb8 70% 100%)", halo: "rgba(230,239,255,0.84)" },
  "france": { token: "flag-france", fill: "linear-gradient(90deg, #0055a4 0 33.33%, #ffffff 33.33% 66.66%, #ef4135 66.66% 100%)", halo: "rgba(229,238,255,0.84)" },
  "french polynesia": { token: "flag-french-polynesia", fill: "linear-gradient(180deg, #d21034 0 25%, #ffffff 25% 75%, #d21034 75% 100%)", halo: "rgba(255,231,235,0.84)" },
  "georgia": { token: "flag-georgia", fill: "linear-gradient(90deg, transparent 0 38%, #e41e26 38% 62%, transparent 62%), linear-gradient(180deg, transparent 0 38%, #e41e26 38% 62%, transparent 62%), #ffffff", halo: "rgba(255,228,228,0.84)" },
  "germany": { token: "flag-germany", fill: "linear-gradient(180deg, #000000 0 33.33%, #dd0000 33.33% 66.66%, #ffce00 66.66% 100%)", halo: "rgba(255,243,214,0.84)" },
  "ghana": { token: "flag-ghana", fill: "linear-gradient(180deg, #ce1126 0 33.33%, #fcd116 33.33% 66.66%, #006b3f 66.66% 100%)", halo: "rgba(255,245,212,0.84)" },
  "greece": { token: "flag-greece", fill: "linear-gradient(90deg, transparent 0 16%, #ffffff 16% 28%, transparent 28%), linear-gradient(180deg, transparent 0 16%, #ffffff 16% 28%, transparent 28%), linear-gradient(180deg, #0d5eaf 0 12.5%, #ffffff 12.5% 25%, #0d5eaf 25% 37.5%, #ffffff 37.5% 50%, #0d5eaf 50% 62.5%, #ffffff 62.5% 75%, #0d5eaf 75% 87.5%, #ffffff 87.5% 100%), #0d5eaf", halo: "rgba(228,240,255,0.84)" },
  "guatemala": { token: "flag-guatemala", fill: "linear-gradient(90deg, #6ec1e4 0 33.33%, #ffffff 33.33% 66.66%, #6ec1e4 66.66% 100%)", halo: "rgba(228,247,255,0.84)" },
  "hungary": { token: "flag-hungary", fill: "linear-gradient(180deg, #ce2939 0 33.33%, #ffffff 33.33% 66.66%, #477050 66.66% 100%)", halo: "rgba(231,255,238,0.84)" },
  "iceland": { token: "flag-iceland", fill: "linear-gradient(90deg, transparent 0 29%, #ffffff 29% 47%, #dc1e35 47% 57%, #ffffff 57% 71%, transparent 71%), linear-gradient(180deg, transparent 0 40%, #ffffff 40% 50%, #dc1e35 50% 58%, #ffffff 58% 68%, transparent 68%), #02529c", halo: "rgba(225,236,255,0.84)" },
  "india": { token: "flag-india", fill: "linear-gradient(180deg, #ff9933 0 33.33%, #ffffff 33.33% 66.66%, #138808 66.66% 100%)", halo: "rgba(255,238,220,0.84)" },
  "indonesia": { token: "flag-indonesia", fill: "linear-gradient(180deg, #ce1126 0 50%, #ffffff 50% 100%)", halo: "rgba(255,229,229,0.84)" },
  "italy": { token: "flag-italy", fill: "linear-gradient(90deg, #009246 0 33.33%, #ffffff 33.33% 66.66%, #ce2b37 66.66% 100%)", halo: "rgba(229,255,238,0.84)" },
  "japan": { token: "flag-japan", fill: "radial-gradient(circle at 50% 50%, #bc002d 0 37%, #ffffff 38% 100%)", halo: "rgba(255,230,236,0.84)" },
  "kazakhstan": { token: "flag-kazakhstan", fill: "radial-gradient(circle at 56% 50%, #f6c53d 0 13%, transparent 14%), linear-gradient(90deg, #f6c53d 0 10%, transparent 10%), #00afca", halo: "rgba(220,248,255,0.84)" },
  "kyrgyzstan": { token: "flag-kyrgyzstan", fill: "linear-gradient(90deg, #e8112d 0 100%)", halo: "rgba(255,225,230,0.83)" },
  "laos": { token: "flag-laos", fill: "linear-gradient(180deg, #ce1126 0 25%, #002868 25% 75%, #ce1126 75% 100%)", halo: "rgba(227,236,255,0.84)" },
  "latvia": { token: "flag-latvia", fill: "linear-gradient(180deg, #9e3039 0 42%, #ffffff 42% 58%, #9e3039 58% 100%)", halo: "rgba(255,232,235,0.84)" },
  "lithuania": { token: "flag-lithuania", fill: "linear-gradient(180deg, #fdb913 0 33.33%, #006a44 33.33% 66.66%, #c1272d 66.66% 100%)", halo: "rgba(255,245,213,0.84)" },
  "madagascar": { token: "flag-madagascar", fill: "linear-gradient(90deg, #ffffff 0 33.33%, #fc3d32 33.33% 66.66%, #007e3a 66.66% 100%)", halo: "rgba(232,255,238,0.84)" },
  "malawi": { token: "flag-malawi", fill: "linear-gradient(180deg, #000000 0 33.33%, #ce1126 33.33% 66.66%, #339e35 66.66% 100%)", halo: "rgba(244,244,244,0.84)" },
  "malaysia": { token: "flag-malaysia", fill: "linear-gradient(180deg, #cc0001 0 16.66%, #ffffff 16.66% 33.33%, #cc0001 33.33% 50%, #ffffff 50% 66.66%, #cc0001 66.66% 83.33%, #ffffff 83.33% 100%)", halo: "rgba(229,236,255,0.84)" },
  "malta": { token: "flag-malta", fill: "linear-gradient(90deg, #ffffff 0 50%, #cf142b 50% 100%)", halo: "rgba(255,231,235,0.84)" },
  "mauritius": { token: "flag-mauritius", fill: "linear-gradient(180deg, #ea2839 0 25%, #1a206d 25% 50%, #ffd500 50% 75%, #00a551 75% 100%)", halo: "rgba(227,238,255,0.84)" },
  "mexico": { token: "flag-mexico", fill: "linear-gradient(90deg, #006847 0 33.33%, #ffffff 33.33% 66.66%, #ce1126 66.66% 100%)", halo: "rgba(226,255,239,0.84)" },
  "mongolia": { token: "flag-mongolia", fill: "linear-gradient(90deg, #c4272f 0 33.33%, #015197 33.33% 66.66%, #c4272f 66.66% 100%)", halo: "rgba(226,238,255,0.84)" },
  "montenegro": { token: "flag-montenegro", fill: "linear-gradient(90deg, #c40308 0 100%)", halo: "rgba(255,225,225,0.82)" },
  "morocco": { token: "flag-morocco", fill: "radial-gradient(circle at 50% 50%, #006233 0 16%, transparent 17%), linear-gradient(90deg, #c1272d 0 100%)", halo: "rgba(255,227,227,0.82)" },
  "namibia": { token: "flag-namibia", fill: "linear-gradient(135deg, #003580 0 46%, #ffce00 46% 49%, #d21034 49% 52%, #009543 52% 100%)", halo: "rgba(226,238,255,0.84)" },
  "new zealand": { token: "flag-new-zealand", fill: "radial-gradient(circle at 42% 36%, #ffffff 0 7%, transparent 8%), radial-gradient(circle at 42% 36%, #cc142b 0 4%, transparent 5%), radial-gradient(circle at 64% 56%, #ffffff 0 6%, transparent 7%), radial-gradient(circle at 64% 56%, #cc142b 0 3.5%, transparent 4.5%), radial-gradient(circle at 74% 34%, #ffffff 0 5%, transparent 6%), radial-gradient(circle at 74% 34%, #cc142b 0 3%, transparent 4%), #00247d", halo: "rgba(224,233,255,0.82)" },
  "nicaragua": { token: "flag-nicaragua", fill: "linear-gradient(180deg, #0067c6 0 33.33%, #ffffff 33.33% 66.66%, #0067c6 66.66% 100%)", halo: "rgba(224,241,255,0.84)" },
  "northern ireland": { token: "flag-northern-ireland", fill: "radial-gradient(circle at 50% 50%, #c8102e 0 18%, transparent 19%), linear-gradient(90deg, transparent 0 38%, #c8102e 38% 62%, transparent 62%), linear-gradient(180deg, transparent 0 38%, #c8102e 38% 62%, transparent 62%), #ffffff", halo: "rgba(255,229,232,0.84)" },
  "norway": { token: "flag-norway", fill: "linear-gradient(90deg, transparent 0 31%, #ffffff 31% 41%, #00205b 41% 49%, #ffffff 49% 59%, transparent 59%), linear-gradient(180deg, transparent 0 42%, #ffffff 42% 50%, #00205b 50% 56%, #ffffff 56% 64%, transparent 64%), #ba0c2f", halo: "rgba(255,227,233,0.82)" },
  "north macedonia": { token: "flag-north-macedonia", fill: "radial-gradient(circle at 50% 50%, #f9d616 0 22%, #d20000 23% 100%)", halo: "rgba(255,234,214,0.84)" },
  "panama": { token: "flag-panama", fill: "linear-gradient(90deg, #ffffff 0 50%, #d21034 50% 100%)", halo: "rgba(232,240,255,0.84)" },
  "paraguay": { token: "flag-paraguay", fill: "linear-gradient(180deg, #d52b1e 0 33.33%, #ffffff 33.33% 66.66%, #0038a8 66.66% 100%)", halo: "rgba(228,238,255,0.84)" },
  "peru": { token: "flag-peru", fill: "linear-gradient(90deg, #d91023 0 33.33%, #ffffff 33.33% 66.66%, #d91023 66.66% 100%)", halo: "rgba(255,229,232,0.84)" },
  "philippines": { token: "flag-philippines", fill: "linear-gradient(180deg, #0038a8 0 50%, #ce1126 50% 100%)", halo: "rgba(230,238,255,0.84)" },
  "poland": { token: "flag-poland", fill: "linear-gradient(180deg, #ffffff 0 50%, #dc143c 50% 100%)", halo: "rgba(255,231,237,0.84)" },
  "portugal": { token: "flag-portugal", fill: "linear-gradient(90deg, #046a38 0 40%, #da291c 40% 100%)", halo: "rgba(225,255,236,0.84)" },
  "romania": { token: "flag-romania", fill: "linear-gradient(90deg, #002b7f 0 33.33%, #fcd116 33.33% 66.66%, #ce1126 66.66% 100%)", halo: "rgba(226,236,255,0.84)" },
  "saudi arabia": { token: "flag-saudi-arabia", fill: "linear-gradient(90deg, #006c35 0 100%)", halo: "rgba(223,255,236,0.84)" },
  "scotland": { token: "flag-scotland", fill: "linear-gradient(45deg, transparent 0 44%, #ffffff 44% 56%, transparent 56%), linear-gradient(-45deg, transparent 0 44%, #ffffff 44% 56%, transparent 56%), #0065bd", halo: "rgba(227,239,255,0.84)" },
  "senegal": { token: "flag-senegal", fill: "linear-gradient(90deg, #00853f 0 33.33%, #fdef42 33.33% 66.66%, #e31b23 66.66% 100%)", halo: "rgba(236,255,220,0.84)" },
  "slovakia": { token: "flag-slovakia", fill: "linear-gradient(180deg, #ffffff 0 33.33%, #0b4ea2 33.33% 66.66%, #ee1c25 66.66% 100%)", halo: "rgba(229,238,255,0.84)" },
  "slovenia": { token: "flag-slovenia", fill: "linear-gradient(180deg, #ffffff 0 33.33%, #0056a3 33.33% 66.66%, #d50032 66.66% 100%)", halo: "rgba(228,238,255,0.84)" },
  "south africa": { token: "flag-south-africa", fill: "linear-gradient(135deg, #007749 0 36%, #ffb81c 36% 40%, #000000 40% 46%, #ffffff 46% 52%, #de3831 52% 76%, #002395 76% 100%)", halo: "rgba(228,255,237,0.84)" },
  "south korea": { token: "flag-south-korea", fill: "radial-gradient(circle at 50% 50%, #cd2e3a 0 24%, #0047a0 24% 48%, #ffffff 49% 100%)", halo: "rgba(230,240,255,0.84)" },
  "spain": { token: "flag-spain", fill: "linear-gradient(180deg, #aa151b 0 25%, #f1bf00 25% 75%, #aa151b 75% 100%)", halo: "rgba(255,245,213,0.84)" },
  "sri lanka": { token: "flag-sri-lanka", fill: "linear-gradient(90deg, #ffb700 0 18%, #8d153a 18% 100%)", halo: "rgba(255,241,212,0.84)" },
  "switzerland": { token: "flag-switzerland", fill: "linear-gradient(90deg, transparent 0 36%, #ffffff 36% 64%, transparent 64%), linear-gradient(180deg, transparent 0 36%, #ffffff 36% 64%, transparent 64%), #d52b1e", halo: "rgba(255,226,223,0.82)" },
  "tanzania": { token: "flag-tanzania", fill: "linear-gradient(135deg, #1eb53a 0 46%, #fcd116 46% 49%, #000000 49% 51%, #00a3dd 51% 100%)", halo: "rgba(227,255,236,0.84)" },
  "turkey": { token: "flag-turkey", fill: "radial-gradient(circle at 42% 50%, #ffffff 0 14%, transparent 15%), radial-gradient(circle at 47% 50%, #e30a17 0 11%, transparent 12%), radial-gradient(circle at 62% 50%, #ffffff 0 6%, transparent 7%), #e30a17", halo: "rgba(255,224,227,0.82)" },
  "united arab emirates": { token: "flag-uae", fill: "linear-gradient(180deg, #00732f 0 33.33%, #ffffff 33.33% 66.66%, #000000 66.66% 100%)", halo: "rgba(232,255,239,0.84)" },
  "united states": { token: "flag-united-states", fill: "linear-gradient(180deg, #b22234 0 14%, #ffffff 14% 28%, #b22234 28% 42%, #ffffff 42% 56%, #b22234 56% 70%, #ffffff 70% 84%, #b22234 84% 100%)", halo: "rgba(228,236,255,0.84)" },
  "uruguay": { token: "flag-uruguay", fill: "linear-gradient(180deg, #ffffff 0 16.66%, #6ccff6 16.66% 33.33%, #ffffff 33.33% 50%, #6ccff6 50% 66.66%, #ffffff 66.66% 83.33%, #6ccff6 83.33% 100%)", halo: "rgba(227,247,255,0.84)" },
  "uzbekistan": { token: "flag-uzbekistan", fill: "linear-gradient(180deg, #1eb5e6 0 31%, #ffffff 31% 62%, #1aac4b 62% 100%)", halo: "rgba(225,247,255,0.84)" },
  "venezuela": { token: "flag-venezuela", fill: "linear-gradient(180deg, #f4d900 0 33.33%, #0033a0 33.33% 66.66%, #d52b1e 66.66% 100%)", halo: "rgba(255,247,212,0.84)" },
  "vietnam": { token: "flag-vietnam", fill: "linear-gradient(90deg, #da251d 0 100%)", halo: "rgba(255,227,224,0.82)" },
  "wales": { token: "flag-wales", fill: "radial-gradient(circle at 50% 52%, #d30731 0 28%, transparent 29%), linear-gradient(180deg, #ffffff 0 50%, #00a651 50% 100%)", halo: "rgba(228,255,236,0.84)" },
  "zambia": { token: "flag-zambia", fill: "linear-gradient(90deg, #198a00 0 100%)", halo: "rgba(226,255,231,0.84)" }
};
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
const DEPARTURE_AIRPORTS = [
  { code: "LGW", label: "Gatwick" },
  { code: "LCY", label: "London City" }
];
const DEPARTURE_AIRPORT_CODES = DEPARTURE_AIRPORTS.map(a => a.code);
const normalizeSearchText = value => String(value ?? "")
  .normalize("NFD")
  .replace(/\p{Diacritic}/gu, "")
  .trim()
  .replace(/\s+/g, " ")
  .toLowerCase();
const escapeHtml = value => String(value ?? "")
  .replace(/&/g, "&amp;")
  .replace(/</g, "&lt;")
  .replace(/>/g, "&gt;")
  .replace(/"/g, "&quot;")
  .replace(/'/g, "&#39;");

const markerVariantCache = new Map();

function mapIcon({ isActive = false, markerPalette } = {}) {
  const palette = markerPalette || { token: "variant-default", fill: "#2f74d0", halo: "rgba(255,255,255,0.72)" };
  const markerStyle = `--marker-fill:${palette.fill}; --marker-halo:${palette.halo};`;
  return L.divIcon({
    className: "",
    html: `<span class="dest-marker variant-country ${palette.token} ${isActive ? "active" : ""}" style="${markerStyle}" aria-hidden="true"></span>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9]
  });
}

function getMapZoomBand(zoomLevel) {
  if (!Number.isFinite(zoomLevel)) return "zoom-low";
  if (zoomLevel <= MAP_ZOOM_LOW_MAX) return "zoom-low";
  if (zoomLevel <= MAP_ZOOM_MID_MAX) return "zoom-mid";
  return "zoom-high";
}

function applyMapZoomClass() {
  if (!map) return;
  const mapEl = document.getElementById("map");
  if (!mapEl) return;
  const zoomBand = getMapZoomBand(map.getZoom());
  mapEl.classList.remove("zoom-low", "zoom-mid", "zoom-high");
  mapEl.classList.add(zoomBand);
}

function getMarkerVariantForLocation(loc) {
  const id = loc?.id;
  if (!id) return { token: "variant-default", fill: "#2f74d0", halo: "rgba(255,255,255,0.72)" };
  if (markerVariantCache.has(id)) return markerVariantCache.get(id);

  const normalizedCountry = normalizeSearchText(loc?.country);
  if (COUNTRY_FLAG_PALETTES[normalizedCountry]) {
    const palette = COUNTRY_FLAG_PALETTES[normalizedCountry];
    markerVariantCache.set(id, palette);
    return palette;
  }

  let hash = 0;
  for (let i = 0; i < normalizedCountry.length; i += 1) {
    hash = (hash * 31 + normalizedCountry.charCodeAt(i)) % 2147483647;
  }
  const fallbackPalette = MARKER_FALLBACK_PALETTES[hash % MARKER_FALLBACK_PALETTES.length];
  markerVariantCache.set(id, fallbackPalette);
  return fallbackPalette;
}

function getMarkerVariantById(id) {
  if (!id) return { token: "variant-default", fill: "#2f74d0", halo: "rgba(255,255,255,0.72)" };
  if (markerVariantCache.has(id)) return markerVariantCache.get(id);
  const loc = INDEX.find(item => item.id === id);
  return getMarkerVariantForLocation(loc);
}

function formatMarkerAccessibleLabel(loc) {
  const city = String(loc?.city || "").trim();
  const country = String(loc?.country || "").trim();
  return `${city}, ${country}`;
}

function formatMarkerTooltipLabel(loc) {
  return String(loc?.city || "").trim();
}

function normalizeDirectFrom(rawMap) {
  const normalized = {};
  const source = rawMap && typeof rawMap === "object" ? rawMap : {};

  DEPARTURE_AIRPORT_CODES.forEach(code => {
    normalized[code] = Boolean(source[code]);
  });

  return normalized;
}

function getDirectAirportCodes(directFromMap) {
  return DEPARTURE_AIRPORT_CODES.filter(code => Boolean(directFromMap?.[code]));
}

function showMapFallback(message) {
  const fallback = document.getElementById("map-fallback");
  if (!fallback) return;
  fallback.textContent = message;
  fallback.hidden = false;
}

function hideMapFallback() {
  const fallback = document.getElementById("map-fallback");
  if (!fallback) return;
  fallback.hidden = true;
}

function isValidCoordinatePair(loc) {
  return Number.isFinite(loc?.lat)
    && Number.isFinite(loc?.lng)
    && loc.lat >= -90
    && loc.lat <= 90
    && loc.lng >= -180
    && loc.lng <= 180;
}

function allIndexLocationsHaveValidCoordinates() {
  return INDEX.every(isValidCoordinatePair);
}

function isProductionRuntime() {
  const protocol = window.location.protocol;
  const host = window.location.hostname;
  return protocol !== "file:" && !["localhost", "127.0.0.1"].includes(host);
}

function getMapRolloutState() {
  if (!FEATURE_FLAGS.enableMap) {
    return {
      enabled: false,
      reason: "Map rollout is currently disabled via feature flag. Browse destinations from the list."
    };
  }

  if (
    FEATURE_FLAGS.requireMapCoordinateReadinessInProduction
    && isProductionRuntime()
    && !allIndexLocationsHaveValidCoordinates()
  ) {
    return {
      enabled: false,
      reason: "Map is temporarily disabled until all destination coordinates pass the production readiness gate."
    };
  }

  return { enabled: true, reason: "" };
}

function applyMapRolloutState(state) {
  const mapEl = document.getElementById("map");
  if (!mapEl) return;

  mapEl.hidden = !state.enabled;

  if (state.enabled) {
    hideMapFallback();
    return;
  }

  showMapFallback(state.reason);
}

function initMap() {
  if (!mapRolloutState.enabled) return;
  if (mapInitAttempted) return;
  mapInitAttempted = true;

  const mapEl = document.getElementById("map");
  if (!mapEl) return;

  if (!window.L) {
    showMapFallback("Map library failed to load. You can still browse destinations from the list.");
    return;
  }

  try {
    map = L.map(mapEl, {
      zoomControl: true,
      scrollWheelZoom: true
    }).setView(DEFAULT_MAP_CENTER, DEFAULT_MAP_ZOOM);
    applyMapZoomClass();
    map.on("zoomend", applyMapZoomClass);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    const points = INDEX.filter(isValidCoordinatePair);

    points.forEach(loc => {
      const markerVariant = getMarkerVariantForLocation(loc);
      const marker = L.marker([loc.lat, loc.lng], {
        icon: mapIcon({ isActive: loc.id === S.loc, markerPalette: markerVariant }),
        keyboard: true,
        title: formatMarkerAccessibleLabel(loc)
      }).addTo(map);
      marker.bindTooltip(formatMarkerTooltipLabel(loc), {
        direction: "top",
        offset: [0, -8]
      });

      marker.on("mouseover", () => {
        hoveredMapMarkerIds.add(loc.id);
        syncMarkerInteractiveState(loc.id);
        marker.openTooltip();
      });

      marker.on("mouseout", () => {
        hoveredMapMarkerIds.delete(loc.id);
        syncMarkerInteractiveState(loc.id);
        if (!focusedMapMarkerIds.has(loc.id)) marker.closeTooltip();
      });

      marker.on("focus", () => {
        focusedMapMarkerIds.add(loc.id);
        syncMarkerInteractiveState(loc.id);
        marker.openTooltip();
      });

      marker.on("blur", () => {
        focusedMapMarkerIds.delete(loc.id);
        syncMarkerInteractiveState(loc.id);
        if (!hoveredMapMarkerIds.has(loc.id)) marker.closeTooltip();
      });

      marker.on("click", () => {
        selLoc(loc.id);
      });

      mapMarkers.set(loc.id, marker);
      visibleMapMarkerIds.add(loc.id);
    });

    if (points.length > 1) {
      map.fitBounds(points.map(loc => [loc.lat, loc.lng]), { padding: [26, 26] });
    } else if (points.length === 1) {
      map.setView([points[0].lat, points[0].lng], 7);
    }

    mapReady = true;
    applyMapFilter(getFilteredLocations(), normalizeSearchText(S.query));
    focusMapOnLocation(S.loc, { pan: false });
    window.setTimeout(() => map?.invalidateSize(), 60);
  } catch (err) {
    console.error(err);
    showMapFallback("Map failed to initialize. You can still browse destinations from the list.");
    mapReady = false;
  }
}

function syncMarkerInteractiveState(id) {
  if (!mapMarkers.has(id)) return;
  const marker = mapMarkers.get(id);
  const markerEl = marker.getElement();
  if (!markerEl) return;
  const isHovered = hoveredMapMarkerIds.has(id);
  const isFocused = focusedMapMarkerIds.has(id);
  markerEl.classList.toggle("is-hovered", isHovered);
  markerEl.classList.toggle("is-focused", isFocused);
  const markerDot = markerEl.querySelector(".dest-marker");
  if (markerDot) {
    markerDot.classList.toggle("is-hovered", isHovered);
    markerDot.classList.toggle("is-focused", isFocused);
  }
}

function applyMarkerContrastState() {
  mapMarkers.forEach((marker, id) => {
    const markerEl = marker.getElement();
    if (!markerEl) return;
    markerEl.classList.remove("is-dimmed");
    const markerDot = markerEl.querySelector(".dest-marker");
    if (markerDot) markerDot.classList.remove("is-dimmed");
  });
}

function updateMarkerSelectionState(id, isActive) {
  if (!mapMarkers.has(id)) return;
  mapMarkers.get(id).setIcon(mapIcon({
    isActive,
    markerPalette: getMarkerVariantById(id)
  }));
  syncMarkerInteractiveState(id);
}

function highlightMapMarker(id) {
  if (!mapReady) return;
  if (highlightedMarkerId && mapMarkers.has(highlightedMarkerId)) {
    updateMarkerSelectionState(highlightedMarkerId, false);
  }
  if (id && visibleMapMarkerIds.has(id) && mapMarkers.has(id)) {
    updateMarkerSelectionState(id, true);
    highlightedMarkerId = id;
    applyMarkerContrastState();
    return;
  }
  highlightedMarkerId = null;
  applyMarkerContrastState();
}

function focusMapOnLocation(id, options = {}) {
  if (!mapReady || !id || !mapMarkers.has(id) || !visibleMapMarkerIds.has(id)) return;
  const marker = mapMarkers.get(id);
  const { pan = true } = options;
  if (pan) {
    map.flyTo(marker.getLatLng(), Math.max(map.getZoom(), LOCATION_FOCUS_MIN_ZOOM), { duration: 0.55 });
  }
  highlightMapMarker(id);
}

function resetMapToHomeViewport() {
  if (!mapReady) return;
  map.flyTo(DEFAULT_MAP_CENTER, DEFAULT_MAP_ZOOM, { duration: 0.55 });
  highlightMapMarker(null);
}

function applySelectionRenderHooks(options = {}) {
  const { panMap = true } = options;
  rSidebar();
  focusMapOnLocation(S.loc, { pan: panMap });
}

function rSidebar() {
  const locListEl = document.getElementById("loc-list");
  const isMobile = window.matchMedia("(max-width: 900px)").matches;
  const selectedChanged = lastSidebarLoc !== S.loc;
  const priorRailScroll = isMobile && locListEl ? locListEl.scrollLeft : locRailScrollLeft;

  const query = normalizeSearchText(S.query);
  const filtered = getFilteredLocations(query);
  const activeMissing = Boolean(S.loc) && !filtered.some(l => l.id === S.loc);
  const emptyState = query && filtered.length === 0
    ? `
    <div class="loc-filter-hint" role="status">
      No destinations match ‘${escapeHtml(S.query)}’.
    </div>
  `
    : "";

  locListEl.innerHTML = filtered.map(l => `
    <button class="loc-btn ${l.id === S.loc ? "active" : ""}" type="button" data-loc-id="${escapeHtml(l.id)}">
      <span class="loc-city">${escapeHtml(l.city)}</span>
      <span class="loc-ctry">${escapeHtml(l.country)}</span>
    </button>
  `).join("") + emptyState + (activeMissing ? `
    <div class="loc-filter-hint" role="status">
      Selected destination is not in current filter.
    </div>
  ` : "");

  document.getElementById("dest-count").textContent = query
    ? `${filtered.length} of ${INDEX.length} destinations`
    : `${INDEX.length} destinations`;
  applyMapFilter(filtered, query);

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

function getFilteredLocations(normalizedQuery = normalizeSearchText(S.query)) {
  return INDEX.filter(l => {
    if (!normalizedQuery) return true;
    return [l.city, l.country, l.region]
      .filter(Boolean)
      .some(v => normalizeSearchText(v).includes(normalizedQuery));
  });
}

function applyMapFilter(filteredLocations, normalizedQuery) {
  if (!mapReady) return;
  const activeQuery = normalizedQuery ?? normalizeSearchText(S.query);
  const hasQuery = Boolean(activeQuery);
  const filteredIds = new Set(filteredLocations.map(loc => loc.id));
  const visiblePoints = [];

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
    if (visible) visiblePoints.push(marker.getLatLng());
  });

  if (!visibleMapMarkerIds.has(S.loc)) {
    highlightMapMarker(null);
  } else {
    highlightMapMarker(S.loc);
  }

  if (!hasQuery || visiblePoints.length === 0) return;

  if (visiblePoints.length === 1) {
    map.setView(visiblePoints[0], Math.max(map.getZoom(), 4));
    return;
  }
  map.fitBounds(visiblePoints, { padding: [26, 26] });
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
  syncHeaderNavState();
  if (S.view === "welcome") {
    resetMapToHomeViewport();
  }

  if (!changed && options.preserveFocus) return;

  if (S.view === "welcome") {
    const welcomeHeading = document.getElementById("welcome-heading");
    const welcomeCta = document.getElementById("welcome-cta");
    (welcomeHeading || welcomeCta)?.focus();
    return;
  }

  document.getElementById("loc-search")?.focus();
}

function syncHeaderNavState() {
  const homeBtn = document.getElementById("home-btn");
  const exploreBtn = document.getElementById("explore-btn");
  if (!homeBtn || !exploreBtn) return;

  const onWelcome = S.view === "welcome";
  homeBtn.classList.toggle("active", onWelcome);
  exploreBtn.classList.toggle("active", !onWelcome);
  homeBtn.setAttribute("aria-current", onWelcome ? "page" : "false");
  exploreBtn.setAttribute("aria-current", !onWelcome ? "page" : "false");
}

function rWelcome() {
  return `
    <section class="welcome-panel" aria-labelledby="welcome-heading">
      <h1 id="welcome-heading" class="welcome-title" tabindex="-1">Plan your next trip with confidence.</h1>
      <p class="welcome-copy">
        Holiday Atlas helps you compare climate, costs, flights, and practical details month by month.
      </p>
      <button id="welcome-cta" class="welcome-cta" type="button">
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
  const directCodes = getDirectAirportCodes(L.prac.directFrom);

  document.getElementById("main").innerHTML = `
    <div class="hero">
      <div class="loc-name">${escapeHtml(L.city)}</div>
      <div class="loc-meta">${escapeHtml(L.country)} &middot; ${escapeHtml(L.region)}</div>
      <div class="tags">
        ${directCodes.length
          ? directCodes.map(code => `<span class="tag g">✓ Direct ${escapeHtml(code)}</span>`).join("")
          : '<span class="tag w">✗ No direct flights from configured London airports</span>'}
        ${L.source?.climateVerified
          ? '<span class="tag g">✓ Climate verified</span>'
          : (L.source?.climate?.length || L.source?.climateVerificationNote)
            ? '<span class="tag w">⚠ Climate unverified</span>'
            : ""}
        <span class="tag">${escapeHtml(L.prac.visa)}</span>
        <span class="tag">${escapeHtml(L.prac.currency)}</span>
      </div>
      <div class="desc">${escapeHtml(L.desc)}</div>
      <div class="hls">${L.hls.map(h => `<span class="hl">◆ ${escapeHtml(h)}</span>`).join("")}</div>
    </div>
    <div class="tab-nav">
      ${[
        ["climate", "Climate"],
        ["costs", "Costs & flights"],
        ["todo", "Things to do"],
        ["prac", "Practical info"]
      ].map(([id, lbl]) => `
        <button class="tab-btn ${id === S.tab ? "active" : ""}" type="button" data-tab="${escapeHtml(id)}" aria-selected="${id === S.tab}">${escapeHtml(lbl)}</button>
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
  const sourceNames = climateSources.map(s => escapeHtml(s.name)).filter(Boolean);
  const verifiedLabel = sourceNames.length ? sourceNames.join(", ") : "source";
  const verifiedOn = L.source?.climateVerifiedOn ? ` (${escapeHtml(L.source.climateVerifiedOn)})` : "";
  const verificationNote = L.source?.climateVerified
    ? `<div style="margin:8px 0 0;font-size:12px;color:var(--color-text-secondary)">✓ Climate data verified via ${verifiedLabel}${verifiedOn}</div>`
    : (climateSources.length || L.source?.climateVerificationNote)
      ? `<div style="margin:8px 0 0;font-size:12px;color:var(--color-text-secondary)">⚠ Climate data not yet verified${L.source?.climateVerificationNote ? ` — ${escapeHtml(L.source.climateVerificationNote)}` : ""}</div>`
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
          <canvas id="tc" role="img" aria-label="Monthly temperature chart for ${escapeHtml(L.city)}.">
            ${escapeHtml(L.city)} monthly temperatures.
          </canvas>
        </div>
      </div>
    </div>

    <div class="filter-row">
      <span class="fl-lbl">Highlight months:</span>
      ${filters.map(f => `<button class="fb ${S.filter === f.id ? "act" : ""}" type="button" data-filter-id="${escapeHtml(f.id)}">${escapeHtml(f.lbl)}</button>`).join("")}
      ${S.filter ? `<button class="fb act" type="button" data-filter-clear="true">✕ Clear</button>` : ""}
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
            const avg = Number(d.avg);
            const hi = Number(d.hi);
            const lo = Number(d.lo);
            const daylight = Number(d.daylight);
            const cld = Number(d.cld);
            const rain = Number(d.rain);
            const busy = Number(d.busy);
            const bc = bclr(busy);
            const daylightLabel = Number.isFinite(daylight) ? daylight.toFixed(1) : "0.0";

            return `
              <tr class="${h}">
                <td data-label="Month" style="font-weight:500">${escapeHtml(d.m)}</td>
                <td data-label="Avg">${avg}°</td>
                <td data-label="High" style="color:#D85A30;font-weight:500">${hi}°</td>
                <td data-label="Low" style="color:#378ADD">${lo}°</td>
                <td data-label="Daylight">${daylightLabel}</td>
                <td data-label="Cloud">
                  <div style="display:flex;align-items:center;gap:6px">
                    <div style="width:44px;height:5px;border-radius:3px;background:var(--color-border-tertiary);overflow:hidden">
                      <div style="width:${cld}%;height:100%;background:#B4B2A9;border-radius:3px"></div>
                    </div>
                    <span>${cld}%</span>
                  </div>
                </td>
                <td data-label="Rain">${rain}</td>
                <td data-label="Busy">
                  <div style="display:flex;align-items:center;gap:6px">
                    <div style="display:flex;gap:1px">
                      ${Array.from({ length: 10 }).map((_, i) => `
                        <div style="width:5px;height:10px;border-radius:1px;background:${i < busy ? bc : "var(--color-border-tertiary)"}"></div>
                      `).join("")}
                    </div>
                    <span style="font-size:11px;color:var(--color-text-secondary)">${escapeHtml(blbl(busy))}</span>
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
            const ac = Number(d.ac);
            const fl = Number(d.fl);
            const busy = Number(d.busy);
            const ov = Math.round((ac + fl) / 2);
            const bc = bclr(busy);

            return `
              <tr>
                <td data-label="Month" style="font-weight:500">${escapeHtml(d.m)}</td>
                <td><span class="${cpc(ac)}">${escapeHtml(clbls[ac] || "")}</span></td>
                <td><span class="${cpc(fl)}">${escapeHtml(clbls[fl] || "")}</span></td>
                <td><span class="${cpc(ov)}">${clbls[ov]}</span></td>
                <td>
                  <div style="display:flex;align-items:center;gap:5px">
                    <div style="display:flex;gap:1px">
                      ${Array.from({ length: 10 }).map((_, i) => `
                        <div style="width:5px;height:10px;border-radius:1px;background:${i < busy ? bc : "var(--color-border-tertiary)"}"></div>
                      `).join("")}
                    </div>
                    <span style="font-size:11px;color:var(--color-text-secondary)">${escapeHtml(blbl(busy))}</span>
                  </div>
                </td>
              </tr>
            `;
          }).join("")}
        </tbody>
      </table>
    </div>

    <div class="hl-tip"><span style="font-weight:500;color:var(--color-text-primary)">Sweet spot:</span> ${escapeHtml(L.sweet)}</div>
  `;
}

function rTodo(L) {
  return `
    <div class="todo-grid">
      ${L.todo.map(t => `
        <div class="tc">
          <div class="tc-cat">${escapeHtml(t.cat)}</div>
          <div class="tc-name">${escapeHtml(t.name)}</div>
          <div class="tc-desc">${escapeHtml(t.desc)}</div>
        </div>
      `).join("")}
    </div>
  `;
}

function rPrac(L) {
  const p = L.prac;
  const wifiRating = Number(p.wifi.r);
  const routeDirectCodes = getDirectAirportCodes(p.directFrom);
  const routeDirectLabel = DEPARTURE_AIRPORTS.map(a => a.label).join(" / ");

  return `
    ${p.alerts.map(a => `<div class="alert-box">⚠ ${escapeHtml(a)}</div>`).join("")}
    <div class="pgrid">
      <div class="pc">
        <div class="pt">WiFi &amp; remote work</div>
        <div style="display:flex;gap:3px;margin-bottom:6px">
          ${Array.from({ length: 5 }).map((_, i) => `
            <div style="width:11px;height:11px;border-radius:50%;background:${i < wifiRating ? "#639922" : "var(--color-border-tertiary)"}"></div>
          `).join("")}
        </div>
        <div class="pv">${escapeHtml(p.wifi.spd)}</div>
        <div class="pn">${escapeHtml(p.wifi.note)}</div>
      </div>

      <div class="pc">
        <div class="pt">Flights from ${routeDirectLabel}</div>
        <div class="pv" style="color:${routeDirectCodes.length ? "var(--color-text-success)" : "var(--color-text-warning)"}">
          ${routeDirectCodes.length
            ? routeDirectCodes.map(code => `<span class="dbadge">Direct ${escapeHtml(code)}</span>`).join(" ")
            : "✗ No direct flights from configured London airports"}
        </div>
        <div class="pn" style="margin-top:5px">${escapeHtml(p.fltNote)}</div>
      </div>

      <div class="pc">
        <div class="pt">Nearest airports</div>
        ${p.airports.map(a => `
          <div class="ar">
            <div>
              <span style="font-weight:500">${escapeHtml(a.name)}</span>
              <span style="font-size:11px;color:var(--color-text-secondary)">(${escapeHtml(a.code)}) · ${Number(a.km)} km</span>
            </div>
            ${(() => {
              const directCodes = getDirectAirportCodes(a.directFrom);
              return directCodes.map(code => `<span class="dbadge">Direct ${escapeHtml(code)}</span>`).join("");
            })()}
          </div>
        `).join("")}
      </div>

      <div class="pc">
        <div class="pt">Entry &amp; essentials</div>
        <div class="ir"><span class="il">Visa</span><span style="text-align:right;max-width:60%">${escapeHtml(p.visa)}</span></div>
        <div class="ir"><span class="il">Currency</span><span style="text-align:right;max-width:60%">${escapeHtml(p.currency)}</span></div>
        <div class="ir"><span class="il">Language</span><span>${escapeHtml(p.lang)}</span></div>
        <div class="ir"><span class="il">Timezone</span><span>${escapeHtml(p.tz)}</span></div>
      </div>

      <div class="pc">
        <div class="pt">Best suited for</div>
        <div style="display:flex;flex-wrap:wrap;gap:5px;margin-top:4px">
          ${p.bestFor.map(b => `<span class="tag">${escapeHtml(b)}</span>`).join("")}
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
  const ChartCtor = window.Chart;

  if (typeof ChartCtor !== "function") {
    const chartWrap = c.closest(".chart-inner");
    if (chartWrap) {
      chartWrap.insertAdjacentHTML(
        "beforeend",
        `<p style="margin:8px 0 0;font-size:12px;color:var(--color-text-secondary)">
          Climate chart unavailable right now. Monthly climate table is still available below.
        </p>`
      );
    }
    return;
  }

  S.chart = new ChartCtor(c, {
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

async function setSelectedLocation(id, options = {}) {
  const { panMap = true, switchToExplorer = true } = options;
  if (!id || !INDEX.some(loc => loc.id === id)) return;

  S.loc = id;
  S.filter = null;
  S.tab = "climate";
  if (switchToExplorer && S.view !== "explorer") {
    setView("explorer", { preserveFocus: true });
  }
  applySelectionRenderHooks({ panMap });

  try {
    await loadLocation(id);
    if (S.view === "explorer") rMain();
    resetMainHorizontalOffsets();
  } catch (err) {
    rLocError(id, err);
    console.error(err);
  }
}

async function selLoc(id) {
  return setSelectedLocation(id, { panMap: true });
}

async function selLocFromDeepLink(id) {
  return setSelectedLocation(id, { panMap: false, switchToExplorer: false });
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

function goHome() {
  setView("welcome");
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
        directFrom: normalizeDirectFrom(a.directFrom)
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
      directFrom: normalizeDirectFrom(loc.prac?.directFrom),
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
      ${escapeHtml(id)}: ${escapeHtml(err?.message)}
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
    INDEX = INDEX.map(loc => ({
      ...loc,
      lat: Number(loc.lat),
      lng: Number(loc.lng)
    }));
    mapRolloutState = getMapRolloutState();
    applyMapRolloutState(mapRolloutState);

    const searchInput = document.getElementById("loc-search");
    const homeBtn = document.getElementById("home-btn");
    const exploreBtn = document.getElementById("explore-btn");
    const addDestinationBtn = document.getElementById("add-destination-btn");
    const mainEl = document.getElementById("main");
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
    homeBtn?.addEventListener("click", goHome);
    exploreBtn?.addEventListener("click", goExplorer);
    addDestinationBtn?.addEventListener("click", addLoc);
    mainEl?.addEventListener("click", e => {
      const target = e.target instanceof Element ? e.target : null;
      if (!target) return;

      const welcomeCtaBtn = target.closest("#welcome-cta");
      if (welcomeCtaBtn) {
        goExplorer();
        return;
      }

      const tabBtn = target.closest(".tab-btn[data-tab]");
      if (tabBtn) {
        swTab(tabBtn.dataset.tab);
        return;
      }

      const clearFilterBtn = target.closest(".fb[data-filter-clear='true']");
      if (clearFilterBtn) {
        setF(null);
        return;
      }

      const filterBtn = target.closest(".fb[data-filter-id]");
      if (filterBtn) {
        setF(filterBtn.dataset.filterId);
      }
    });

    S.loc = INDEX[0].id;
    S.view = normalizeViewMode(viewFromHash() || "welcome");
    const locListEl = document.getElementById("loc-list");
    if (locListEl) {
      locListEl.addEventListener("click", e => {
        const target = e.target instanceof Element ? e.target : null;
        const button = target?.closest(".loc-btn[data-loc-id]");
        if (!button) return;
        selLoc(button.dataset.locId);
      });
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
        map?.invalidateSize();
      });
      locRailControlsBound = true;
    }
    applySelectionRenderHooks({ panMap: false });
    if (mapRolloutState.enabled) initMap();

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
        ${escapeHtml(err?.message)}
      </div>
    `;
    console.error(err);
  }
}

init();

window.selLocFromDeepLink = selLocFromDeepLink;
