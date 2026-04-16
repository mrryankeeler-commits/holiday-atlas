import { normalizeDirectFrom } from "./utils.js";

export function createDataStore() {
  let index = [];
  const locCache = {};

  const isValidLocation = (loc, id) => Boolean(
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

  const sanitizeLocation = (loc) => {
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
      ? loc.todo.map(t => ({ cat: t.cat, name: t.name, desc: t.desc }))
      : [];

    const airports = Array.isArray(loc.prac?.airports)
      ? loc.prac.airports.map(a => ({
          name: a.name,
          code: a.code,
          km: a.km,
          directFrom: normalizeDirectFrom(a.directFrom, a.dgw)
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
          ? loc.source.climate.map(s => ({ name: s?.name ?? "", url: s?.url ?? "" }))
          : []
      },
      months,
      todo,
      prac: {
        directFrom: normalizeDirectFrom(loc.prac?.directFrom, loc.prac?.directGW),
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
  };

  return {
    getIndex: () => index,
    getLocationFromCache: (id) => locCache[id] || null,
    async loadIndex() {
      const res = await fetch("./data/locations/index.json");
      if (!res.ok) throw new Error(`Failed to load index.json (${res.status})`);
      const payload = await res.json();
      if (!Array.isArray(payload) || payload.length === 0) throw new Error("Location index data is empty or invalid.");
      index = payload.map(loc => ({ ...loc, lat: Number(loc.lat), lng: Number(loc.lng) }));
      return index;
    },
    async loadLocation(id) {
      if (locCache[id]) return locCache[id];
      const res = await fetch(`./data/locations/${id}.json`);
      if (!res.ok) throw new Error(`Failed to load ${id}.json (${res.status})`);
      const loc = await res.json();
      if (!isValidLocation(loc, id)) throw new Error(`Invalid location payload for ${id}.`);
      locCache[id] = sanitizeLocation(loc);
      return locCache[id];
    }
  };
}
