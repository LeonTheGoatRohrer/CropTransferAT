// Motion graphics of the Delta Green finale film. Every scene is a pure function of time, drawn in a 1920x1080 design space,
// and draws real data from data.js (export_data.py). Numbers: reports/finale_video/FAKTENCHECK.md.
// LEAD comes from timeline.js: seconds of a scene before its voice line starts, so v(i) is the start of sentence i on screen.
const C = { bg: '#0A0E0A', ink: '#EEF0E4', dim: '#969E8C', faint: '#232B22', line: '#3A4438', green: '#9DBB5C', sig: '#E4583E', amber: '#D69842', white: '#FFFFFF' };
const F = { d: 'Bricolage', s: 'Instrument', m: 'JetBrains' };
const RAMP = [[0, [228, 88, 62]], [.28, [214, 152, 66]], [.5, [196, 188, 92]], [.72, [112, 170, 88]], [1, [26, 118, 78]]];
const cv = document.getElementById('c'), g = cv.getContext('2d');
const SC = cv.width / 1920;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const ease = x => { x = clamp(x); return x * x * x * (x * (6 * x - 15) + 10); };
const seg = (t, a, b) => ease((t - a) / (b - a));
const inout = (t, a, b, c, d) => seg(t, a, b) * (1 - seg(t, c, d));
const de = (x, n = 2) => x.toFixed(n).replace('.', ',');
const lerp = (a, b, k) => a + (b - a) * k;
function rng(seed) { let s = seed; return () => (s = (s * 16807) % 2147483647) / 2147483647; }
function ramp(v) {
  for (let i = 1; i < RAMP.length; i++) if (v <= RAMP[i][0]) {
    const [a, ca] = RAMP[i - 1], [b, cb] = RAMP[i], k = (v - a) / (b - a);
    return [lerp(ca[0], cb[0], k), lerp(ca[1], cb[1], k), lerp(ca[2], cb[2], k)];
  }
  return RAMP[RAMP.length - 1][1];
}
const rgb = (c, a = 1) => `rgba(${c[0] | 0},${c[1] | 0},${c[2] | 0},${a})`;

function text(s, x, y, size, o = {}) {
  const a = o.a ?? 1; if (a <= 0.004) return;
  g.save(); g.globalAlpha = a; g.fillStyle = o.c || C.ink; g.textAlign = o.al || 'left'; g.textBaseline = o.bl || 'alphabetic';
  g.font = `${o.w || 500} ${size}px "${o.f || F.s}"`; if (o.sp) g.letterSpacing = o.sp + 'px';
  if (o.glow) { g.shadowColor = o.glowc || o.c || C.green; g.shadowBlur = o.glow * SC; }
  g.fillText(s, x, y); g.restore();
}
function line(x0, y0, x1, y1, c, w = 1, a = 1) { g.save(); g.globalAlpha = a; g.strokeStyle = c; g.lineWidth = w; g.beginPath(); g.moveTo(x0, y0); g.lineTo(x1, y1); g.stroke(); g.restore(); }
function rect(x, y, w, h, c, a = 1) { g.save(); g.globalAlpha = a; g.fillStyle = c; g.fillRect(x, y, w, h); g.restore(); }
function frame(x, y, w, h, c, lw = 1, a = 1) { g.save(); g.globalAlpha = a; g.strokeStyle = c; g.lineWidth = lw; g.strokeRect(x, y, w, h); g.restore(); }
function dot(x, y, r, c, a = 1, glow = 0) { g.save(); g.globalAlpha = a; g.fillStyle = c; if (glow) { g.shadowColor = c; g.shadowBlur = glow * SC; } g.beginPath(); g.arc(x, y, r, 0, 7); g.fill(); g.restore(); }
function ring(x, y, r, c, w = 1, a = 1) { g.save(); g.globalAlpha = a; g.strokeStyle = c; g.lineWidth = w; g.beginPath(); g.arc(x, y, r, 0, 7); g.stroke(); g.restore(); }
function bg() { g.fillStyle = C.bg; g.fillRect(0, 0, 1920, 1080); }
function vignette(s = .55) { const r = g.createRadialGradient(960, 540, 380, 960, 540, 1150); r.addColorStop(0, 'rgba(0,0,0,0)'); r.addColorStop(1, `rgba(0,0,0,${s})`); g.fillStyle = r; g.fillRect(0, 0, 1920, 1080); }
function blackbg() { g.fillStyle = '#000'; g.fillRect(0, 0, 1920, 1080); }
function fade(t, d, a = .3, b = .3) { const k = seg(t, 0, a) * (1 - seg(t, d - b, d)); if (k < 1) rect(0, 0, 1920, 1080, '#000', 1 - k); }

// Chapter mark: five ticks and the current chapter, always in the same place.
const CHAPTERS = ['DAS PROBLEM', 'DIE LÖSUNG', 'DIE DATEN', 'DER PROTOTYP', 'NACH DER ABGABE'];
function chapter(i, t, d, keep = false) {
  const a = keep ? seg(t, .1, .5) : inout(t, .1, .5, d - .4, d - .05);
  for (let k = 0; k < 5; k++) rect(84 + k * 34, 70, 26, 5, k === i ? C.green : C.line, a);
  text(CHAPTERS[i], 262, 81, 24, { f: F.m, c: C.dim, a, sp: 3 });
}
function foot(s, a = 1) { text(s, 84, 1034, 23, { c: '#858D7E', a, f: F.m }); }
function title(s, a, y = 190, x = 84) { text(s, x, y, 56, { f: F.d, w: 600, a }); }

// ---------- rasters: cached once per data set, then only drawn
const RC = new Map();
function raster(key, rows, col) {
  if (RC.has(key)) return RC.get(key);
  const h = rows.length, w = rows[0].length, c = document.createElement('canvas'); c.width = w; c.height = h;
  const x = c.getContext('2d');
  rows.forEach((r, j) => { for (let i = 0; i < w; i++) if (r[i] !== '.') { x.fillStyle = col(+r[i] / 9); x.fillRect(i, j, 1, 1); } });
  RC.set(key, c); return c;
}
function blit(c, x, y, w, h, a = 1) { g.save(); g.globalAlpha = a; g.imageSmoothingEnabled = false; g.drawImage(c, x, y, w, h); g.restore(); }

// The example field: every cell is a real 10 m cell with its measured yield and its NDVI.
const FLD = DATA.field;
function fieldFit(x, y, w, h) { const s = Math.min(w / FLD.w, h / FLD.h); return { s, ox: x + (w - s * FLD.w) / 2, oy: y + (h - s * FLD.h) / 2 }; }
function drawField(fit, colour, a = 1, gap = .06) {
  const { s, ox, oy } = fit;
  g.save(); g.globalAlpha = a;
  for (let i = 0; i < FLD.x.length; i++) { const c = colour(i); if (!c) continue; g.fillStyle = c; g.fillRect(ox + FLD.x[i] * s, oy + FLD.y[i] * s, s * (1 - gap), s * (1 - gap)); }
  g.restore();
}
const beat = (id) => DATA.beats[window.ANON && ANONLINES[id] ? ANONLINES[id] : id];
const ANONLINES = { f01: 'x01', f02: 'x02' };
const voiceAt = (scene, id) => { const b = beat(id), l = LEAD[scene] ?? 0; return (i) => l + b.s[Math.min(i, b.s.length - 1)]; };

// ---------- maps
function mapper(x, y, w, h) {
  const R = DATA.map.at; let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9;
  for (const [a, b] of R) { x0 = Math.min(x0, a); x1 = Math.max(x1, a); y0 = Math.min(y0, b); y1 = Math.max(y1, b); }
  const k = Math.cos(47.6 * Math.PI / 180), s = Math.min(w / ((x1 - x0) * k), h / (y1 - y0));
  const ox = x + (w - s * k * (x1 - x0)) / 2, oy = y + (h - s * (y1 - y0)) / 2;
  return (a, b) => [ox + s * k * (a - x0), oy + s * (y1 - b)];
}
function poly(m, R, fill, stroke, lw = 2, a = 1, frac = 1) {
  g.save(); g.globalAlpha = a; g.beginPath();
  const n = Math.floor(R.length * frac);
  for (let i = 0; i < n; i++) { const p = m(R[i][0], R[i][1]); i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1]); }
  if (frac >= 1) g.closePath();
  if (fill) { g.fillStyle = fill; g.fill(); }
  if (stroke) { g.strokeStyle = stroke; g.lineWidth = lw; g.lineJoin = 'round'; g.stroke(); }
  g.restore();
}

const S = {};

// ---- 1: the frozen film frame is scanned into the combine's real track and cuts seamlessly into the opener.
S.freezescan = (t, d) => {
  bg();
  const T = DATA.track, [sw, sh] = T.size, fit = Math.min(1720 / sw, 900 / sh);
  const e = x => x * x * (3 - 2 * x), push = fit * (1 + 0.035 * e(clamp(T.cut / 18.8)));
  const ox = 960 - sw * push / 2, oy = 540 - sh * push / 2 + 18;
  g.save(); g.lineCap = 'butt'; g.lineWidth = (T.swath * T.M + 3) * push;
  for (let i = 1; i < T.xy.length; i++) {
    const a = T.xy[i - 1], b = T.xy[i];
    if (Math.hypot(b[0] - a[0], b[1] - a[1]) > 22 * T.M) continue;
    g.strokeStyle = rgb(ramp(T.rank[i])); g.beginPath(); g.moveTo(ox + a[0] * push, oy + a[1] * push); g.lineTo(ox + b[0] * push, oy + b[1] * push); g.stroke();
  }
  g.restore();
  const hud = seg(t, .75, 1.3);
  text('HERBST · MÄHDRESCHER', 92, 76, 24, { f: F.m, sp: 3, a: hud });
  vignette(.45);
  const y = 1080 * seg(t, .12, 1.25) * 1.04;
  if (IMG.freeze1 && IMG.freeze1.naturalWidth) {
    g.save(); g.beginPath(); g.rect(0, y, 1920, 1080); g.clip(); g.drawImage(IMG.freeze1, 0, 0, 1920, 1080); rect(0, 0, 1920, 130, '#000'); rect(0, 950, 1920, 130, '#000');
    g.restore();
  }
  if (t > .1 && y < 1080) {
    const gr = g.createLinearGradient(0, y - 90, 0, y); gr.addColorStop(0, 'rgba(157,187,92,0)'); gr.addColorStop(1, 'rgba(157,187,92,.28)');
    g.fillStyle = gr; g.fillRect(0, y - 90, 1920, 90); line(0, y, 1920, y, '#D6EE9A', 3, 1);
  }
};

// ---- 2: the field falls apart into its yield spectrum, and all of it collapses into one number.
S.spread = (t, d) => {
  bg(); chapter(0, t, d);
  const v = voiceAt('spread', 'b01b');
  const appear = seg(t, .1, .7), fall = seg(t, v(2) + 1.2, v(2) + 3.2), one = seg(t, v(3) - .1, v(3) + 1.4);
  const fit = fieldFit(200, 110, 1520, 800);
  const lo = 0.3, hi = 1.5, bins = 60, base = 880, ax0 = 360, ax1 = 1560;
  const hist = new Array(bins).fill(0); const height = 5.6;
  const X = i => (FLD.rel[i] - lo) / (hi - lo);
  const r = rng(7);
  for (let i = 0; i < FLD.x.length; i++) {
    const delay = r() * .5, k = ease((fall * 1.5) - delay), b = Math.floor(clamp(X(i)) * (bins - 1)), n = hist[b]++;
    const fx = fit.ox + FLD.x[i] * fit.s, fy = fit.oy + FLD.y[i] * fit.s, sz = lerp(fit.s * .94, 18, k);
    const tx = ax0 + (ax1 - ax0) * (b / bins), ty = base - (n + 1) * height;
    const collapseX = ax0 + (ax1 - ax0) * ((1 - lo) / (hi - lo)), px = lerp(lerp(fx, tx, k), collapseX, one), py = lerp(lerp(fy, ty, k), base - 240 * (i / FLD.x.length) - 6, one);
    const c = ramp(FLD.relr[i]), mid = ramp(.5), col = [lerp(c[0], mid[0], one), lerp(c[1], mid[1], one), lerp(c[2], mid[2], one)];
    rect(px, py, sz, lerp(k > .5 ? height * .8 : sz, 4, one), rgb(col), appear * (1 - one * .4));
  }
  const axA = fall * (1 - one);
  line(ax0, base + 6, ax1, base + 6, C.line, 2, axA);
  [[.4, '40 %'], [1, '100 %'], [1.39, 'fast 140 %']].forEach(([val, lab]) => {
    const x = ax0 + (ax1 - ax0) * ((val - lo) / (hi - lo));
    line(x, base + 6, x, base + 22, C.dim, 2, axA);
    text(lab, x, base + 58, 34, { f: F.m, al: 'center', a: axA, c: val === 1 ? C.ink : (val < 1 ? C.sig : C.green) });
  });
  text('Ertrag je 10-m-Zelle, relativ zum Mittel dieses Feldes', 960, base + 112, 28, { c: C.dim, a: axA, al: 'center' });
  const oneA = seg(t, v(3) + .5, v(3) + 1.5);
  text('100 %', 960, 400, 170, { f: F.d, w: 600, al: 'center', a: oneA });
  text('Der Durchschnitt. Eine Zahl.', 960, 480, 42, { al: 'center', c: C.dim, a: oneA });
  foot('Echte Daten · USDA BARC, Feld 5-12, 2021 · 1.338 Zellen', appear * (1 - fall));
  vignette(); fade(t, d);
};

// ---- 2b: only a yield map shows where; most fields have none; Austria publishes none.
S.nomap = (t, d) => {
  bg(); chapter(0, t, d);
  const v = voiceAt('nomap', 'b02');
  const fit = fieldFit(340, 200, 1240, 560), gone = seg(t, v(1) - .1, v(1) + .9), toAt = seg(t, v(2) - .3, v(2) + .6);
  const a = (1 - toAt) * seg(t, .1, .7);
  drawField(fit, i => rgb(ramp(FLD.relr[i])), a * (1 - gone));
  g.save(); g.globalAlpha = a * gone; g.fillStyle = C.faint;
  for (let i = 0; i < FLD.x.length; i++) g.fillRect(fit.ox + FLD.x[i] * fit.s, fit.oy + FLD.y[i] * fit.s, fit.s * .94, fit.s * .94);
  g.restore();
  text('ERTRAGSKARTE', 960, 870, 40, { f: F.m, al: 'center', sp: 8, a: a * (1 - seg(gone, 0, .45)) });
  text('MEIST KEINE KARTE', 960, 870, 40, { f: F.m, al: 'center', sp: 8, a: a * seg(gone, .55, 1), c: C.sig });
  const m = mapper(330, 170, 1260, 500), ata = seg(t, v(2) - .1, v(2) + .9);
  poly(m, DATA.map.at, '#111811', C.dim, 2.5, ata, seg(t, v(2) - .1, v(2) + 1.1) < 1 ? seg(t, v(2) - .1, v(2) + 1.1) : 1);
  text('0', 960, 480, 210, { f: F.d, w: 600, al: 'center', a: seg(t, v(2) + .5, v(2) + 1.1), c: C.sig });
  text('öffentliche Erträge einzelner Felder', 960, 800, 52, { f: F.d, w: 500, al: 'center', a: seg(t, v(2) + .6, v(2) + 1.3) });
  text('Österreich', 960, 740, 30, { f: F.m, c: C.dim, sp: 4, al: 'center', a: ata });
  vignette(); fade(t, d);
};

// ---- 3: signature transition: the film frame freezes and is scanned into real 10 m pixels.
S.zoom = (t, d) => {
  bg(); chapter(1, t, d, true);
  const v = voiceAt('zoom', 'c01');
  const fit = fieldFit(170, 170, 1580, 620);
  const scan = seg(t, .05, 1.2), yScan = scan * 1090;
  const weak = seg(t, v(2) + 1.3, v(2) + 2.1);
  g.save(); g.beginPath(); g.rect(0, 0, 1920, yScan); g.clip();
  drawField(fit, i => {
    const low = FLD.ndvi[i] < .25, c = ramp(FLD.ndvi[i]);
    return low ? rgb([lerp(c[0], 228, weak), lerp(c[1], 88, weak), lerp(c[2], 62, weak)]) : rgb(c, 1 - weak * .72);
  });
  g.restore();
  if (scan < 1 && IMG.freeze2 && IMG.freeze2.naturalWidth) {
    g.save(); g.beginPath(); g.rect(0, yScan, 1920, 1080); g.clip(); g.drawImage(IMG.freeze2, 0, 0, 1920, 1080); g.restore();
    const gr = g.createLinearGradient(0, yScan - 90, 0, yScan); gr.addColorStop(0, 'rgba(157,187,92,0)'); gr.addColorStop(1, 'rgba(157,187,92,.28)');
    g.fillStyle = gr; g.fillRect(0, yScan - 90, 1920, 90); line(0, yScan, 1920, yScan, '#D6EE9A', 3, 1);
  }
  const a = seg(t, 1.2, 1.7);
  text('10 m PRO PIXEL', 960, 876, 30, { f: F.m, al: 'center', c: C.dim, sp: 5, a: a * (1 - weak) });
  text('Hier zuerst hinschauen', 960, 880, 62, { f: F.d, w: 600, al: 'center', a: weak, c: C.ink });
  text('Ohne Sensor. Ohne Kosten für den Betrieb.', 960, 948, 38, { al: 'center', c: C.dim, a: seg(t, v(3), v(3) + .5) });
  foot('Echte Daten · Sentinel-2, 16.7.–15.8.2021 · USDA BARC · rot: schwächstes Viertel der Pixel', a);
  vignette(.4); fade(t, d, 0, .3);
};

// ---- 3b: wall of the 41 real field-years, then the number.
S.wall = (t, d) => {
  bg(); chapter(1, t, d);
  const v = voiceAt('wall', 'c02');
  const W = DATA.wall, cols = 7, rows = 6, tw = 244, th = 118, gx = 14, gy = 14, x0 = (1920 - cols * tw - (cols - 1) * gx) / 2, y0 = 130;
  const dim = seg(t, v(1) - .3, v(1) + .6);
  const yc = (u) => { const q = ramp(u); return rgb(q); };
  W.forEach((f, i) => {
    const col = i % cols, row = Math.floor(i / cols), x = x0 + col * (tw + gx), y = y0 + row * (th + gy);
    const on = seg(t, .2 + i * .1, .5 + i * .1); if (on <= 0) return;
    const A = raster('y' + i, f.yield, yc), B = raster('n' + i, f.ndvi, yc);
    const slot = (tw - 12) / 2, sc = Math.min(slot / A.width, (th - 30) / A.height), w = A.width * sc, h = A.height * sc;
    rect(x, y, tw, th, '#121812', on * (1 - dim * .6));
    blit(A, x + 4 + (slot - w) / 2, y + 4 + (th - 30 - h) / 2, w, h, on * (1 - dim * .78));
    blit(B, x + 8 + slot + (slot - w) / 2, y + 4 + (th - 30 - h) / 2, w, h, on * (1 - dim * .78));
    text(`${f.year}  ρ ${de(f.rho)}`, x + 6, y + th - 8, 17, { f: F.m, c: C.dim, a: on * (1 - dim * .8) });
    const chk = seg(t, .42 + i * .1, .62 + i * .1);
    if (chk > 0) text('✓', x + tw - 28, y + th - 8, 22, { c: C.green, a: chk * (1 - dim * .8), w: 700 });
  });
  const hd = inout(t, .3, .9, v(1) - .3, v(1) + .3);
  text('links Mähdrescher, rechts Satellit', 84, 112, 22, { c: C.dim, a: hd, f: F.m });
  const a = seg(t, v(1), v(1) + .7), sa = seg(t, v(2) - .1, v(2) + .6), px0 = 360, px1 = 1560, py = 820;
  if (a > 0) {
    rect(0, 0, 1920, 1080, C.bg, a * .55);
    const n = .68 * seg(t, v(1) + .9, v(1) + 2.6);
    text(de(n), 960, 560, 300, { f: F.d, w: 600, al: 'center', a, glow: 30 });
    text('Rangkorrelation Satellit und Mähdrescher, im selben Feld', 960, 634, 34, { al: 'center', c: C.dim, a });
    line(px0, py, px1, py, C.line, 3, sa);
    [[0, '0  Zufall'], [1, '1  perfekt']].forEach(([u, lab]) => { const x = lerp(px0, px1, u); line(x, py - 12, x, py + 12, C.dim, 3, sa); text(lab, x, py + 56, 30, { f: F.m, al: 'center', a: sa }); });
    const all = seg(t, v(3) - .1, v(3) + 1.4);
    W.forEach((f, i) => { const k = clamp(all * 41 - i * .7); if (k > 0) dot(lerp(px0, px1, f.rho), py - 26 - (i % 5) * 13, 6, C.green, k * .9); });
    const mx = lerp(px0, px1, .68 * sa); dot(mx, py, 13, C.ink, sa, 18);
    text('41 von 41 positiv', 960, 968, 58, { f: F.d, w: 600, al: 'center', c: C.green, a: seg(t, v(3) + .4, v(3) + 1.2) });
  }
  foot('Median-ρ 0,68 [0,54; 0,71] · 41 Feld-Jahre, 27 Felder · USDA BARC, Maryland', seg(t, .4, 1));
  vignette(.45); fade(t, d);
};

// ---- 3c: weakest quarter of pixels, 58 % against 27 %.
S.quart = (t, d) => {
  bg(); chapter(1, t, d);
  const v = voiceAt('quart', 'c03');
  const fit = fieldFit(84, 170, 900, 560), mark = seg(t, .3, 1.2);
  drawField(fit, i => FLD.ndvi[i] < .25 ? rgb([lerp(ramp(FLD.ndvi[i])[0], 228, mark), lerp(ramp(FLD.ndvi[i])[1], 88, mark), lerp(ramp(FLD.ndvi[i])[2], 62, mark)]) : rgb(ramp(FLD.ndvi[i]), 1 - mark * .78), seg(t, 0, .5));
  text('Schwächstes Viertel der Pixel', 84, 150, 34, { f: F.d, w: 600, a: seg(t, .3, 1), c: C.sig });
  const bars = seg(t, v(0) + 3.0, v(0) + 4.4), rnd = seg(t, v(1), v(1) + 1.2);
  const bx = 1090, bw = 720;
  text('Wirklich in einer Problemzone', bx, 250, 34, { c: C.ink, a: seg(t, v(0) + 2.6, v(0) + 3.2) });
  rect(bx, 280, bw, 120, C.faint, seg(t, v(0) + 2.6, v(0) + 3.2)); rect(bx, 280, bw * .58 * bars, 120, C.sig);
  text(`${Math.round(58 * bars)} %`, bx + 24, 366, 80, { f: F.d, w: 600, a: bars, c: C.white });
  text('Bei zufälliger Auswahl', bx, 490, 34, { c: C.dim, a: rnd });
  rect(bx, 520, bw, 120, C.faint, rnd); rect(bx, 520, bw * .27 * rnd, 120, C.dim);
  text(`${Math.round(27 * rnd)} %`, bx + 24, 606, 80, { f: F.d, w: 600, a: rnd, c: C.white });
  const lim = seg(t, v(2), v(2) + .7);
  rect(84, 820, 1752, 104, '#141A13', lim); rect(84, 820, 8, 104, C.amber, lim);
  text('Belastbar bisher nur an diesem einen Standort', 120, 888, 46, { f: F.d, w: 600, a: lim });
  foot('Median über 41 Feld-Jahre · Problemzone: Ertrag unter 85 % des Feldmittels · Karte: Feld 5-12, 2021', seg(t, .5, 1.1));
  vignette(.4); fade(t, d);
};

// ---- 3d: 782 tiles, one per trained variant, grouped by the real blocks; they go out block by block until three results are left.
S.tiles = (t, d) => {
  bg(); chapter(1, t, d);
  const v = voiceAt('tiles', 'c04');
  const cols = 46, rows = 17, ts = 34, gap = 5, W = cols * (ts + gap) - gap, x0 = (1920 - W) / 2, y0 = 170;
  const blocks = DATA.blocks; let idx = 0;
  const start = v(1), lit = seg(t, start - .2, start + 2.4);
  const outStart = v(2) - .5, outEnd = v(3) - .2;
  const r = rng(41), shades = ['#7FA34F', '#5E8F55', '#9DBB5C', '#4C7F58', '#B5C065', '#6B9C5B', '#3F7458', '#8BAE58', '#A7B85F', '#5A8A50', '#74A052'];
  const ends = seg(t, v(3) - .3, v(3) + .6);
  blocks.forEach(([name, n], b) => {
    const a0 = lerp(outStart, outEnd, b / blocks.length), a1 = a0 + (outEnd - outStart) / blocks.length * 1.4;
    for (let k = 0; k < n; k++, idx++) {
      const col = idx % cols, row = Math.floor(idx / cols), x = x0 + col * (ts + gap), y = y0 + row * (ts + gap);
      const on = clamp(lit * 782 / 40 - idx / 40);
      const off = seg(t, a0 + r() * .25, a1);
      const alpha = on * (1 - off * .94);
      if (alpha > .005) rect(x, y, ts, ts, shades[b], alpha * (1 - ends * .7));
    }
  });
  const num = Math.round(782 * lit);
  text(`${num}`, 84, 1000 - 40, 96, { f: F.d, w: 600, a: seg(t, start - .2, start + .3) * (1 - ends) });
  text('Modellvarianten trainiert und bewertet', 300, 950, 36, { c: C.dim, a: seg(t, start, start + .6) * (1 - ends) });
  if (t < v(1) - .2) { text('Kann KI das besser?', 960, 520, 96, { f: F.d, w: 600, al: 'center', a: inout(t, .2, .8, v(1) - .6, v(1) - .2) }); }
  const sTxt = inout(t, v(2), v(2) + .6, v(3) - .4, v(3) - .1);
  rect(0, 440, 1920, 170, C.bg, sTxt * .82);
  text('Die einfachen Methoden haben sich durchgesetzt', 960, 548, 70, { f: F.d, w: 600, al: 'center', a: sTxt });
  const cards = [['Karte im Feld', 'kein Training', C.green], ['Stress-Score', 'kein Training', C.green], ['EU-Regionalmodell', 'gelernt', C.dim]];
  cards.forEach(([a, b, c], i) => {
    const k = seg(t, v(3) + .1 + i * .25, v(3) + .7 + i * .25), x = 150 + i * 560, y = 360 + (1 - k) * 24;
    rect(x, y, 500, 300, '#141A13', k); rect(x, y, 500, 6, c, k);
    text(a, x + 30, y + 130, 46, { f: F.d, w: 600, a: k });
    text(b, x + 30, y + 200, 36, { f: F.m, c, a: k });
  });
  foot('782 Varianten in 11 Experimentblöcken · gezählt aus results/, siehe Projektdoku', seg(t, start, start + .6));
  vignette(.4); fade(t, d);
};

// ---- 3e: what failed.
S.failed = (t, d) => {
  bg(); chapter(1, t, d);
  const v = voiceAt('failed', 'c05');
  title('Was gescheitert ist', seg(t, .1, .7));
  const rowsF = ['Radar', 'Wärmebild', 'Jahresvorhersage, Runde 1', 'Jahresvorhersage, Runde 2', 'Jahresvorhersage, Runde 3'];
  rowsF.forEach((s, i) => {
    const a = seg(t, v(0) + 3.0 + i * .55, v(0) + 3.4 + i * .55), y = 330 + i * 118, st = seg(t, v(0) + 3.4 + i * .55, v(0) + 3.9 + i * .55);
    text(s, 150, y, 64, { f: F.d, w: 500, a, c: st > .5 ? C.dim : C.ink });
    g.save(); g.font = `500 64px "${F.d}"`; const w = g.measureText(s).width; g.restore();
    line(140, y - 22, 140 + (w + 20) * st, y - 22, C.sig, 6, a);
    text('nicht gereicht', 1760, y, 38, { f: F.m, c: C.sig, al: 'right', a: st });
  });
  foot('Vorab festgelegte Kriterien · Auch das steht im Bericht', seg(t, .5, 1));
  vignette(.4); fade(t, d);
};

// ---- 4: where the training data came from, and the open requests.
S.sources = (t, d) => {
  bg(); chapter(2, t, d);
  const v = voiceAt('sources', 'd01');
  // Lines run from the public data sets into training. Nothing connects Austria to training: that is the rule.
  const m = mapper(690, 590, 540, 250), ca = seg(t, .1, .8);
  poly(m, DATA.map.at, '#141A13', C.line, 2, ca);
  text('Keine öffentlichen Feld-Erträge', 960, 890, 30, { f: F.m, al: 'center', c: C.sig, a: ca });
  const left = [['USA', 'Ertragskarten, Versuchsfelder'], ['Italien', 'Ertragskarte'], ['16 EU-Länder', 'Regionalerträge'], ['Afrika', 'Betriebsdaten']];
  const lA = seg(t, v(1) - .2, v(1) + .4);
  text('ÖFFENTLICHE DATENSÄTZE', 84, 230, 24, { f: F.m, c: C.green, sp: 3, a: lA });
  const tk = seg(t, v(1) + .9, v(1) + 1.6);
  rect(740, 310, 440, 150, '#1B2717', tk); frame(740, 310, 440, 150, C.green, 3, tk);
  text('Training', 960, 408, 64, { f: F.d, w: 600, al: 'center', a: tk });
  left.forEach(([a, b], i) => {
    const k = seg(t, v(1) + i * .3, v(1) + .5 + i * .3), y = 290 + i * 142;
    rect(84, y, 500, 120, '#141A13', k); rect(84, y, 6, 120, C.green, k);
    text(a, 112, y + 54, 40, { f: F.d, w: 600, a: k }); text(b, 112, y + 96, 26, { c: C.dim, a: k });
    const p = seg(t, v(1) + .4 + i * .3, v(1) + 1.5 + i * .3); line(584, y + 60, lerp(584, 740, p), lerp(y + 60, 385, p), C.green, 2.5, k * .8);
  });
  const reqStart = v(1) + 3.3, rA = seg(t, reqStart, reqStart + .4);
  text('ANFRAGEN', 1320, 230, 24, { f: F.m, c: C.amber, sp: 3, a: rA });
  ['Fachleute', 'Versuchsstationen', 'Hochschulen'].forEach((s, i) => {
    const k = seg(t, reqStart + i * .3, reqStart + .5 + i * .3), y = 290 + i * 142;
    rect(1320, y, 516, 120, '#141A13', k); rect(1320, y, 6, 120, C.amber, k);
    text(s, 1348, y + 74, 42, { f: F.d, w: 600, a: k });
  });
  const op = seg(t, v(2), v(2) + .5);
  text('Viele davon offen', 1320, 790, 52, { f: F.d, w: 600, c: C.amber, a: op });
  foot('Quellen und Lizenzen: DATA_SOURCES.md, SUPPORT.md', ca);
  vignette(.4); fade(t, d);
};

// ---- 4b: zero.
S.zero = (t, d) => {
  bg(); chapter(2, t, d);
  const v = voiceAt('zero', 'd02');
  const k = seg(t, v(1) - .1, v(1) + .5);
  text('Österreich bleibt reine Prüfung', 960, 300, 56, { f: F.d, w: 600, al: 'center', a: seg(t, .2, .8), c: C.dim });
  text('0', 960, 720, 420, { f: F.d, w: 600, al: 'center', a: k, c: C.green, glow: 40 });
  text('österreichische Werte im Training', 960, 830, 56, { f: F.d, w: 500, al: 'center', a: seg(t, v(1) + .2, v(1) + .8) });
  vignette(.5); fade(t, d);
};

// A stamp that slams in: used wherever a rule is frozen.
function stamp(cx, cy, s1, s2, t, at, col = C.green, alpha = 1) {
  const k = clamp((t - at) / .16) * alpha; if (k <= 0) return;
  const sc = lerp(1.7, 1, ease(clamp((t - at) / .16)));
  g.save(); g.translate(cx, cy); g.rotate(-.045); g.scale(sc, sc); g.globalAlpha = k;
  g.strokeStyle = col; g.lineWidth = 7; g.strokeRect(-350, -80, 700, 160); g.restore();
  g.save(); g.translate(cx, cy); g.rotate(-.045); g.scale(sc, sc);
  text(s1, 0, -4, 62, { f: F.d, w: 700, al: 'center', c: col, a: k });
  text(s2, 0, 46, 26, { f: F.m, al: 'center', c: col, a: k });
  g.restore();
}

// ---- 4c: frozen rule, then Upper Austria.
S.freezeoo = (t, d) => {
  bg(); chapter(2, t, d);
  const v = voiceAt('freezeoo', 'd03');
  stamp(960, 500, 'EINGEFROREN', 'Regel vor dem Test · freeze-at-1', t, .55, C.green, 1 - seg(t, v(1) - .4, v(1) - .1));
  const a = seg(t, v(1) - .2, v(1) + .5), m = mapper(70, 170, 860, 480);
  poly(m, DATA.map.at, '#111811', C.line, 2, a);
  poly(m, DATA.map.oo, '#26331F', C.green, 3, a);
  Object.entries(DATA.map.sites_oo).forEach(([n, p], i) => {
    const k = seg(t, v(1) + .4 + i * .3, v(1) + .8 + i * .3), q = m(p[0], p[1]);
    if (k > 0) { dot(q[0], q[1], 8, C.green, k, 14); ring(q[0], q[1], 8 + 24 * k, C.green, 2, (1 - k) * .8 + .08); }
  });
  text('Oberösterreich · 34 Standort-Jahre', 84, 720, 34, { f: F.m, a, c: C.dim });
  const nA = seg(t, v(1) + 5.2, v(1) + 5.8), n = .5 * seg(t, v(1) + 5.2, v(1) + 6.6);
  text(de(n), 1040, 400, 230, { f: F.d, w: 600, a: nA, glow: 20 });
  text('[0,19; 0,68]', 1050, 470, 36, { f: F.m, c: C.dim, a: nA });
  const r1 = seg(t, v(1) + 3.2, v(1) + 3.8), r2 = seg(t, v(2), v(2) + .5), r3 = seg(t, v(2) + 3.1, v(2) + 3.6);
  [['Gute und schlechte Jahre', 'ja', C.green, r1], ['Standorte im selben Jahr', 'nein', C.sig, r2], ['Einfacher Grünwert', 'ebenso 0,50', C.amber, r3]].forEach(([a1, b1, c1, k], i) => {
    const y = 590 + i * 112; rect(1040, y - 58, 796, 92, '#141A13', k);
    text(a1, 1066, y, 36, { a: k }); text(b1, 1812, y, 38, { f: F.m, c: c1, al: 'right', a: k });
  });
  foot('Rangkorrelation Stress-Score und Ertrag am 1.9. · 7 Jahre · US-Regel, nie auf Österreich angepasst', a);
  vignette(.4); fade(t, d);
};

// ---- 4d: Styria, too few site-years: the state at the deadline.
function slots(x, y, n, filled, t, at, size = 88, gap = 12, cols = 15) {
  for (let i = 0; i < n; i++) {
    const k = seg(t, at + i * .1, at + .25 + i * .1), px = x + (i % cols) * (size + gap), py = y + Math.floor(i / cols) * (size + gap);
    if (i < filled) rect(px, py, size, size, C.green, k * .9); else frame(px + 2, py + 2, size - 4, size - 4, C.sig, 4, k);
  }
}
S.stmk = (t, d) => {
  bg(); chapter(2, t, d);
  const v = voiceAt('stmk', 'd04');
  const m = mapper(560, 130, 800, 400), a = seg(t, .1, .8);
  poly(m, DATA.map.at, '#111811', C.line, 2, a); poly(m, DATA.map.st, '#33291A', C.amber, 3, a);
  text('Steiermark', 960, 590, 34, { f: F.m, al: 'center', c: C.amber, a });
  slots(210, 630, 15, 12, t, .9);
  text('12 statt 15 Standort-Jahre', 960, 830, 72, { f: F.d, w: 600, al: 'center', a: seg(t, 2.2, 2.8) });
  text('Nicht auswertbar', 960, 900, 44, { f: F.m, al: 'center', c: C.sig, a: seg(t, 2.8, 3.3) });
  const st = seg(t, v(1), v(1) + .4);
  text('Stand bei der Abgabe · 18.10.2026', 960, 985, 34, { f: F.m, al: 'center', c: C.dim, a: st });
  vignette(.4); fade(t, d);
};

// ---- 6: the climax. Four steps at the top, always readable: before, what came, what I did, after.
function steps(i, t) {
  const names = ['VORHER', 'WAS DAZUKAM', 'VORGEHEN', 'NACHHER'], a = seg(t, 0, .4);
  names.forEach((n, k) => {
    const x = 84 + k * 330, on = k === i;
    rect(x, 112, 300, 4, on ? C.green : C.line, a);
    text(n, x, 152, 25, { f: F.m, sp: 2, c: on ? C.ink : '#5B6456', a });
  });
}
const anon = () => !!window.ANON;
function typed(s, t, at, cps = 34) { const n = Math.floor(clamp((t - at) * cps, 0, s.length)); return s.slice(0, n); }

S.mail = (t, d) => {
  bg(); chapter(4, t, d, true);
  const v = voiceAt('mail', 'f01');
  steps(t < v(2) - .2 ? 0 : 1, t);
  const X = 84, Y = 300, lh = 158;
  text('So 18.10.2026', X, Y, 34, { f: F.m, c: C.dim, a: seg(t, .2, .6) });
  text(typed('Abgabe. Steiermark nicht testbar, 12 statt 15.', t, .4), X + 340, Y, 54, { f: F.d, w: 600 });
  const w = seg(t, v(1) - .1, v(1) + .3);
  text('Wochenende', X, Y + lh, 34, { f: F.m, c: C.dim, a: w });
  text(typed('Keine Antwort.', t, v(1)), X + 340, Y + lh, 54, { f: F.d, w: 500, c: C.dim });
  const e = seg(t, v(2) - .1, v(2) + .3);
  text(anon() ? 'Danach' : 'Mo 19.10., 09:44', X, Y + lh * 2, 34, { f: F.m, c: C.dim, a: e });
  text(typed(anon() ? 'Eine Hochschule, Schweiz' : 'ETH Zürich', t, v(2)), X + 340, Y + lh * 2, 54, { f: F.d, w: 600 });
  text('Kein Österreich', 1836, Y + lh * 2, 34, { f: F.m, c: C.amber, al: 'right', a: seg(t, v(4) - .2, v(4) + .4) });
  const z = seg(t, v(3) - .1, v(3) + .3);
  text('Danach', X, Y + lh * 3, 34, { f: F.m, c: C.dim, a: z });
  text(typed(anon() ? 'Ertragskarte, Deutschland, 27.811 Punkte' : 'ZALF, Brandenburg: Ertragskarte, 27.811 Punkte', t, v(3), 42), X + 340, Y + lh * 3, 54, { f: F.d, w: 600 });
  text('Kein Österreich', 1836, Y + lh * 3 + 60, 34, { f: F.m, c: C.amber, al: 'right', a: seg(t, v(4) - .2, v(4) + .4) });
  foot('Angekommen. Für diesen Film nicht ausgewertet.', seg(t, v(4), v(4) + .6));
  vignette(.4); fade(t, d);
};

S.hatz = (t, d) => {
  bg(); chapter(4, t, d, true); steps(1, t);
  const v = voiceAt('hatz', 'f02');
  text('28.10.2026', 960, 370, 170, { f: F.d, w: 600, al: 'center', a: seg(t, .2, .7), glow: 16 });
  text('Zehn Tage nach der Abgabe', 960, 440, 46, { al: 'center', c: C.dim, a: seg(t, .9, 1.5) });
  const size = 56, gap = 9, x0 = 400, base = 590, at = v(0) + 3.6;
  text(anon() ? 'Versuchsreihen aus der Steiermark' : 'Excel-Reihen der Versuchsstation Hatzendorf', 960, 530, 36, { al: 'center', a: seg(t, at - .4, at), f: F.m, c: C.green });
  const rowsH = anon() ? [['Standort A', 2007, []], ['Standort B', 2009, [2017, 2019, 2023, 2025]]] : [['Wagna', 2007, []], ['Kalsdorf', 2009, [2017, 2019, 2023, 2025]]];
  rowsH.forEach(([n, y0, miss], r) => {
    const y = base + r * 150;
    text(n, 370, y + 42, 38, { f: F.d, w: 600, al: 'right', a: seg(t, at, at + .4) });
    for (let yr = 2007; yr <= 2026; yr++) {
      const i = yr - 2007, k = seg(t, at + i * .07 + r * .5, at + .2 + i * .07 + r * .5), x = x0 + i * (size + gap);
      if (yr < y0) continue;
      if (miss.includes(yr)) frame(x + 2, y + 2, size - 4, size - 4, C.line, 3, k); else rect(x, y, size, size, yr === 2026 ? C.sig : C.green, k * (yr === 2026 ? 1 : .8));
    }
    if (!anon()) text(`${y0}–2026`, 1836, y + 92, 28, { f: F.m, al: 'right', c: C.dim, a: seg(t, at + 1.2, at + 1.6) });
  });
  text('rot: 2026, das blinde Jahr  ·  leer: kein Ertragswert in diesem Jahr', 400, 880, 26, { f: F.m, c: '#7C8476', a: seg(t, at + 1.5, at + 2) });
  vignette(.4); fade(t, d);
};

S.stamp = (t, d) => {
  bg(); chapter(4, t, d, true); steps(2, t);
  const v = voiceAt('stamp', 'f03');
  text('Der Test, der vorher an den Daten gescheitert war', 960, 310, 54, { f: F.d, w: 500, al: 'center', a: seg(t, .2, .8), c: C.dim });
  const at = v(1) + .4;
  ['Stichtag', 'Ertragsgröße', 'Kriterium', 'Standorte, Jahre'].forEach((s, i) => {
    const k = seg(t, v(1) + i * .16, v(1) + .3 + i * .16), y = 450 + i * 66;
    text(s, 150, y, 32, { f: F.m, c: C.dim, a: k * .85 }); rect(490, y - 18, 300, 12, C.line, k);
  });
  stamp(1330, 540, 'FESTGESCHRIEBEN', `${DATA.freeze.tag} · ${DATA.freeze.commit} · 28.10.2026`, t, at + .5);
  text('Dann einmal ausgewertet.', 960, 850, 72, { f: F.d, w: 600, al: 'center', a: seg(t, at + 1.5, at + 2.1) });
  vignette(.4); fade(t, d);
};

// ---- 6b: real scatter of the 15 site-years; 13 known ones in grey, in silence; then the two blind points fall in.
function scatterAxes() {
  const x0 = 180, x1 = 1320, y0 = 930, y1 = 230, sx = v => lerp(x0, x1, (v + .058) / .06), sy = v => lerp(y0, y1, (v - .2) / 1.15);
  return { x0, x1, y0, y1, sx, sy };
}
S.scatter = (t, d) => {
  bg(); chapter(4, t, d, true); steps(3, t);
  const v = voiceAt('scatter', 'f04'), v0 = v(0), P = DATA.scatter;
  const known = P.filter(p => p.year !== 2026).sort((a, b) => a.year - b.year), blind = P.filter(p => p.year === 2026);
  if (anon()) {                                                                             // aggregated variant: scores only, no yields, no places
    const sorted = P.slice().sort((a, b) => a.score - b.score), xa = 180, xb = 1740, yy = 560, sx = u => lerp(xa, xb, (u + .058) / .06);
    line(xa, yy, xb, yy, C.line, 3, seg(t, 0, .5));
    text('Stress-Score am 1.9.: niedrig bedeutet früher braun', xa, yy + 110, 34, { f: F.m, c: C.dim, a: seg(t, .1, .6) });
    sorted.filter(p => p.year !== 2026).forEach((p, i) => { const k = seg(t, .3 + i * .13, .5 + i * .13); dot(sx(p.score), yy, 13, C.dim, k); });
    sorted.filter(p => p.year === 2026).forEach((p, i) => { const at = v0 + .5 + i * .35, k = clamp((t - at) / .3), yp = lerp(170, yy, ease(k)); if (k > 0) dot(sx(p.score), yp, 22, C.sig, 1, 34); });
    text('Die zwei blinden Punkte', 540, 330, 56, { f: F.d, w: 600, c: C.sig, a: seg(t, v0 + 1.2, v0 + 1.9) });
    text('Die niedrigsten Scores aller 15', 540, 400, 40, { a: seg(t, v0 + 2, v0 + 2.6) });
    text('Die Versuche lagen weit unter dem Üblichen', 180, 800, 50, { f: F.d, w: 600, a: seg(t, v(1), v(1) + .6) });
    vignette(.35); fade(t, d, .3, .1); return;
  }
  const A = scatterAxes(), ax = seg(t, 0, .6);
  line(A.x0, A.y0, A.x1, A.y0, C.line, 3, ax); line(A.x0, A.y0, A.x0, A.y1, C.line, 3, ax);
  text('Stress-Score am 1.9.', (A.x0 + A.x1) / 2, A.y0 + 66, 28, { f: F.m, al: 'center', c: C.dim, a: ax });
  g.save(); g.translate(A.x0 - 104, (A.y0 + A.y1) / 2); g.rotate(-Math.PI / 2); text('Ertrag relativ zum Üblichen', 0, 0, 28, { f: F.m, al: 'center', c: C.dim, a: ax }); g.restore();
  [.4, .6, .8, 1.0, 1.2].forEach(u => { text(de(u, 1), A.x0 - 24, A.sy(u) + 8, 24, { f: F.m, al: 'right', c: C.dim, a: ax }); line(A.x0 - 12, A.sy(u), A.x0, A.sy(u), C.line, 2, ax); });
  [-.05, -.03, -.01].forEach(u => { text(de(u, 2), A.sx(u), A.y0 + 32, 22, { f: F.m, al: 'center', c: C.dim, a: ax }); });
  const mark = (p, k, col, big = 0) => {
    const x = A.sx(p.score), y = A.sy(p.yas), r = 12 + big;
    if (p.site === 'wagna') dot(x, y, r, col, k, big ? 30 : 0); else rect(x - r, y - r, r * 2, r * 2, col, k);
    text(String(p.year).slice(2), x + r + 5, y - r - 2, 22, { f: F.m, c: col, a: k });
  };
  const span = Math.max(v0 - .4, 1);
  known.forEach((p, i) => mark(p, seg(t, .35 + i * span / known.length, .55 + i * span / known.length), '#9AA292'));
  blind.forEach((p, i) => {
    const at = v0 + .9 + i * .4, k = clamp((t - at) / .32); if (k <= 0) return;
    const f = ease(k), x = A.sx(p.score), y = lerp(40, A.sy(p.yas), f * f), r = 18;
    if (p.site === 'wagna') dot(x, y, r, C.sig, 1, 34); else { g.save(); g.shadowColor = C.sig; g.shadowBlur = 34 * SC; rect(x - r, y - r, r * 2, r * 2, C.sig); g.restore(); }
    if (k >= 1) { text(p.site === 'wagna' ? 'Wagna 2026' : 'Kalsdorf 2026', x + 30, y + 10, 30, { f: F.m, c: C.sig }); ring(x, y, 18 + 90 * clamp((t - at - .32) / .7), C.sig, 3, 1 - clamp((t - at - .32) / .7)); }
  });
  const bx = 1400;
  text('● Wagna   ■ Kalsdorf', bx, 300, 28, { f: F.m, c: C.dim, a: ax });
  text('13 bekannte Punkte', bx, 372, 32, { c: '#9AA292', a: seg(t, .4, 1) });
  const b1 = seg(t, v0 + 1.6, v0 + 2.2), b2 = seg(t, v(1), v(1) + .6);
  text('2 blinde Punkte', bx, 480, 52, { f: F.d, w: 600, c: C.sig, a: b1 });
  text('Die niedrigsten', bx, 548, 40, { a: b1 }); text('Scores aller 15', bx, 596, 40, { a: b1 });
  text('Ertrag weit unter', bx, 700, 40, { a: b2 }); text('dem Üblichen', bx, 748, 40, { a: b2 });
  text('0,62 und 0,48', bx, 806, 34, { f: F.m, c: C.sig, a: b2 });
  vignette(.35); fade(t, d, .3, .1);
};

S.big = (t, d) => {
  bg(); chapter(4, t, d, true); steps(3, t);
  const k = seg(t, .05, .9), n = .77 * k;
  text(de(n), 960, 610, 400, { f: F.d, w: 600, al: 'center', glow: 46, a: seg(t, 0, .3) });
  text('[0,30; 0,97]  ·  15 Standort-Jahre', 960, 720, 48, { f: F.m, al: 'center', c: C.dim, a: seg(t, .7, 1.2) });
  stamp(960, 880, 'BESTANDEN', 'Kriterium vorab festgelegt', t, voiceAt('big', 'f05')(1) + .4);
  foot('Rangkorrelation Stress-Score und Ertrag · geprüft: nur die Unterscheidung der Jahre', seg(t, .9, 1.4));
  vignette(.4);
};

S.lines = (t, d) => {
  bg(); chapter(4, t, d, true); steps(3, t);
  const v = voiceAt('lines', 'f06');
  const a = seg(t, 0, .5);
  text('0,77', 84, 270, 84, { f: F.d, w: 600, a }); text('[0,30; 0,97] · n = 15', 310, 268, 34, { f: F.m, c: C.dim, a });
  [['13 von 15', 'Punkten waren vorher bekannt', v(0)], ['1', 'einziges blindes Jahr', v(1)], ['0,72', 'einfaches Grün (NDVI)', v(2)]].forEach(([big, s, at], i) => {
    const k = seg(t, at - .05, at + .4), y = 430 + i * 164;
    rect(84, y - 92, 1752, 138, '#141A13', k); rect(84, y - 92, 8, 138, C.amber, k);
    text(big, 130, y + 2, 84, { f: F.d, w: 600, a: k, c: C.amber }); text(s, 660, y - 4, 58, { f: F.d, w: 500, a: k });
  });
  text('Hagelversicherung: Daten angefragt', 84, 950, 40, { f: F.m, c: C.dim, a: seg(t, v(3), v(3) + .5) });
  vignette(.4); fade(t, d, .2, .4);
};

// ---- 7: the logo (real Pixel-Delta from the website), and who did what.
const LOGO = [[[32, 8.31], [24, 22.18], [40, 22.18], '#23704a'], [[22, 25.64], [14, 39.51], [30, 39.51], '#55a05a'], [[24, 24.49], [40, 24.49], [32, 38.36], '#9dbb5c'], [[42, 25.64], [34, 39.51], [50, 39.51], '#e4694a'], [[12, 42.98], [4, 56.84], [20, 56.84], '#9dbb5c'], [[14, 41.82], [30, 41.82], [22, 55.69], '#55a05a'], [[32, 42.98], [24, 56.84], [40, 56.84], '#c4a44b'], [[34, 41.82], [50, 41.82], [42, 55.69], '#55a05a'], [[52, 42.98], [44, 56.84], [60, 56.84], '#8a6a36']];
const TAGLINE = 'Schon im Sommer sehen, wo im Feld Ertrag fehlt.';
function drawLogo(cx, cy, size, t, start, step, span) {
  LOGO.forEach(([a, b, c, col], i) => {
    const e = seg(t, start + i * step, start + span + i * step); if (e <= 0) return;
    const pts = [a, b, c].map(p => [p[0] - 32, p[1] - 32]), m = [(pts[0][0] + pts[1][0] + pts[2][0]) / 3, (pts[0][1] + pts[1][1] + pts[2][1]) / 3];
    g.save(); g.globalAlpha = e; g.fillStyle = col; g.beginPath();
    pts.forEach((p, k) => { const x = cx + ((p[0] - m[0]) * (.5 + .5 * e) + m[0] * (1 + (1 - e) * 1.6)) * size, y = cy + ((p[1] - m[1]) * (.5 + .5 * e) + m[1] * (1 + (1 - e) * 1.6)) * size; k ? g.lineTo(x, y) : g.moveTo(x, y); });
    g.closePath(); g.fill(); g.restore();
  });
}
function drawName(size, y, a) {
  g.save(); g.globalAlpha = a; g.font = `650 ${size}px "${F.d}"`; g.textBaseline = 'alphabetic';
  const w1 = g.measureText('Delta ').width, w2 = g.measureText('Green').width, x = 960 - (w1 + w2) / 2;
  g.fillStyle = C.ink; g.fillText('Delta ', x, y); g.fillStyle = C.green; g.fillText('Green', x + w1, y); g.restore();
}
S.end = (t, d) => {
  bg();
  drawLogo(960, 340, 4.6, t, .15, .07, .55);
  const e = seg(t, .9, 1.5);
  drawName(148, 660 + (1 - e) * 16, e);
  text(TAGLINE, 960, 736, 40, { al: 'center', c: '#BEC4B2', w: 400, a: seg(t, 1.4, 1.9) });
  const c = seg(t, 2.2, 2.8);
  text('Stimme: KI (ElevenLabs)  ·  Stimmungsbilder und Musik: KI-generiert (Higgsfield)  ·  Alles, was wie ein Messwert aussieht: echte Daten', 960, 960, 22, { f: F.m, al: 'center', c: '#7C8476', a: c });
  text('Hilfe und Datenquellen: SUPPORT.md', 960, 996, 22, { f: F.m, al: 'center', c: '#7C8476', a: c });
  vignette(.4); fade(t, d, .2, .7);
};

// ---- opening: the title lands on the biggest hit of the music, over the real field.
S.titlecard = (t, d) => {
  bg();
  const fit = fieldFit(120, 60, 1680, 960), s = 1 + .03 * t / d;
  g.save(); g.translate(960, 540); g.scale(s, s); g.translate(-960, -540);
  drawField(fit, i => rgb(ramp(FLD.relr[i])), .1 * seg(t, 0, .6));
  drawLogo(960, 330, 5.2, t, 0, .025, .3);
  const e = seg(t, .1, .45);
  drawName(176, 680 + (1 - e) * 22, e);
  text(TAGLINE, 960, 772, 50, { f: F.d, w: 500, al: 'center', c: '#D5DAC9', a: seg(t, .55, 1.1) });
  g.restore();
  vignette(.55);
  rect(0, 0, 1920, 1080, '#F3F8E0', .85 * (1 - seg(t, 0, .32)));
  fade(t, d, 0, .5);
};

// ---- opening: what the product is meant to do. A phone with the real orthophoto and the real maize parcel of the pitch intro (basemap.at 2024, INVEKOS 2024).
// The notification does not exist on the website yet, so the scene says so in the picture; the phone map is an example, not a measurement.
const PARCEL = [[189.8, 534.9], [252.5, 509.4], [248.5, 314.7], [202.5, 318.4], [178.2, 324.3], [111.0, 348.2]];
const PHONE = { x: 870, y: 86, w: 470, h: 908, sx: 886, sy: 102, sw: 438, sh: 876 };
function phoneScreen(t, v) {
  const P = PHONE, k = P.sh / 746, up = seg(t, 2.8, 3.2), ox = P.sx - (394 * k - P.sw) / 2, oy = P.sy - 190 * up, pt = p => [ox + p[0] * k, oy + p[1] * k];   // the map moves up with the sheet, so the parcel stays in view
  const lock = seg(t, v(1) - .1, v(1) + .2);
  // map, parcel outline, threshold sheet
  if (lock < 1) {
    if (IMG.map && IMG.map.naturalWidth) { g.filter = 'brightness(1.12) saturate(1.15) contrast(1.05)'; g.drawImage(IMG.map, ox, oy, 394 * k, 746 * k); g.filter = 'none'; }
    const t0 = 1.25, step = .24, n = PARCEL.length, done = clamp((t - t0) / (step * n));
    const shown = Math.floor(done * n), frac = done * n - shown;
    if (done >= 1) { g.beginPath(); PARCEL.forEach((p, i) => { const q = pt(p); i ? g.lineTo(q[0], q[1]) : g.moveTo(q[0], q[1]); }); g.closePath(); g.fillStyle = `rgba(157,187,92,${.34 * seg(t, t0 + step * n, t0 + step * n + .25)})`; g.fill(); }
    g.save(); g.strokeStyle = '#E8F5B0'; g.lineWidth = 5; g.lineJoin = 'round'; g.beginPath();
    for (let i = 0; i <= Math.min(shown, n); i++) { const q = pt(PARCEL[i % n]); i ? g.lineTo(q[0], q[1]) : g.moveTo(q[0], q[1]); }
    let tip = null;
    if (t > t0 && shown < n) { const a = pt(PARCEL[shown]), b = pt(PARCEL[(shown + 1) % n]); tip = [lerp(a[0], b[0], frac), lerp(a[1], b[1], frac)]; g.lineTo(tip[0], tip[1]); }
    g.stroke(); g.restore();
    PARCEL.forEach((p, i) => { const on = t - (t0 + i * step); if (on < 0) return; const q = pt(p); dot(q[0], q[1], 9, '#F6FBDC'); if (on < .4) ring(q[0], q[1], 9 + 60 * on, '#F6FBDC', 3, 1 - on / .4); });
    if (tip) dot(tip[0], tip[1], 20, '#FFFFFF', .35);
    if (done >= 1) { const q = pt([200, 425]); text('2,9 ha', q[0], q[1], 30, { f: F.m, al: 'center', w: 700, a: seg(t, t0 + step * n, t0 + step * n + .2) }); }
    rect(P.sx, P.sy, P.sw, 108, 'rgba(10,14,10,.86)');            // header below the notch
    text('Delta Green', P.sx + 26, P.sy + 90, 28, { f: F.d, w: 600 });
    text(t < 2.85 ? 'Eigenes Feld' : 'Warnschwelle', P.sx + P.sw - 26, P.sy + 89, 22, { f: F.m, al: 'right', c: C.green });
    if (up > 0) {
      const H = 348, y = P.sy + P.sh - H * up;
      g.save(); g.fillStyle = '#10160F'; g.beginPath(); g.roundRect(P.sx, y, P.sw, H + 30, [30, 30, 0, 0]); g.fill(); g.restore();
      text('Warnen ab', P.sx + 34, y + 66, 32, { c: C.dim });
      const val = 10 * seg(t, 3.1, 4.0);
      text(`${Math.round(val)} %`, P.sx + 34, y + 176, 104, { f: F.d, w: 600, c: C.green });
      text('auffälliger Feldfläche', P.sx + 34, y + 224, 30, { c: C.ink });
      const tx = P.sx + 34, tw = P.sw - 68, ty = y + 282, kx = tx + tw * (val / 50);
      rect(tx, ty - 4, tw, 8, C.line); rect(tx, ty - 4, kx - tx, 8, C.green); dot(kx, ty, 17, '#FFFFFF');
    }
  }
  // lock screen: the message
  if (lock > 0) {
    const gr = g.createLinearGradient(0, P.sy, 0, P.sy + P.sh); gr.addColorStop(0, '#0D1A12'); gr.addColorStop(1, '#040705');
    g.save(); g.globalAlpha = lock; g.fillStyle = gr; g.fillRect(P.sx, P.sy, P.sw, P.sh); g.restore();
    const cx = P.sx + P.sw / 2;
    text('9:41', cx, P.sy + 170, 110, { f: F.d, w: 500, al: 'center', a: lock });
    const n0 = v(1) + 1.15, nk = clamp((t - n0) / .28);
    if (nk > 0) {
      const over = 1 + .05 * Math.sin(nk * Math.PI), y = P.sy + 210 + (1 - ease(nk)) * -150;
      g.save(); g.translate(cx, y + 74); g.scale(over, over); g.translate(-cx, -(y + 74)); g.globalAlpha = nk;
      g.fillStyle = 'rgba(236,240,226,.97)'; g.beginPath(); g.roundRect(P.sx + 14, y, P.sw - 28, 150, 28); g.fill();
      g.restore();
      text('DELTA GREEN', P.sx + 38, y + 40, 21, { f: F.m, c: '#47513F', a: nk, w: 700, sp: 1 });
      text('jetzt', P.sx + P.sw - 38, y + 40, 21, { f: F.m, al: 'right', c: '#6B7564', a: nk });
      text('Schwache Zone im Feld', P.sx + 38, y + 86, 31, { f: F.d, w: 700, c: '#10160F', a: nk });
      text('Schwelle 10 % überschritten', P.sx + 38, y + 124, 26, { c: '#2E352A', a: nk });
      const m = seg(t, n0 + .25, n0 + .7);
      if (m > 0) {
        const fit = fieldFit(P.sx + 22, P.sy + 396, P.sw - 44, 340);
        drawField(fit, i => FLD.ndvi[i] < .25 ? rgb([228, 88, 62]) : rgb(ramp(FLD.ndvi[i]), .38), m, .08);
        text('Hier zuerst hinschauen', cx, P.sy + 796, 36, { f: F.d, w: 600, al: 'center', a: m });
      }
    }
  }
}
S.phone = (t, d) => {
  bg();
  const v = voiceAt('phone', 'o8'), P = PHONE, n0 = v(1) + 1.15;
  // satellite and Earth behind everything: the real film clip, black becomes the dark background
  if (IMG.sat && IMG.sat.naturalWidth) {
    const dx = 680, dy = -130, drift = t * 5;
    g.save(); g.globalCompositeOperation = 'lighten'; g.globalAlpha = seg(t, 0, .5); g.drawImage(IMG.sat, dx - drift, dy, 1920, 1080); g.restore();
    const gb = g.createLinearGradient(0, 640, 0, 950); gb.addColorStop(0, 'rgba(10,14,10,0)'); gb.addColorStop(1, C.bg); g.fillStyle = gb; g.fillRect(0, 640, 1920, 440);
  }
  // the signal leaves the satellite and reaches the phone
  const bA = inout(t, v(1) + .1, v(1) + .4, n0 + .55, n0 + .95), sx = 1590, sy = 400, ex = P.x + P.w - 26, ey = P.y + 190;
  if (bA > 0) {
    line(sx, sy, ex, ey, C.green, 2.5, bA * .55);
    for (let i = 0; i < 6; i++) {
      const k = ((t * 1.5 + i / 6) % 1), x = lerp(sx, ex, k), y = lerp(sy, ey, k);
      dot(x, y, 8, '#D6EE9A', bA * Math.sin(k * Math.PI), 16); ring(x, y, 10 + 20 * k, C.green, 2, bA * (1 - k) * .7);
    }
    dot(sx, sy, 10, '#E8F5B0', bA, 26);
  }
  // left: three plain steps
  const steps = [['Eigenes Feld einstellen', .7, 2.85], ['Schwelle einstellen', 2.85, v(1) - .1], ['Nachricht aufs Handy', v(1) - .1, 99]];
  text('DAS ZIEL', 110, 268, 28, { f: F.m, c: C.green, sp: 5, a: seg(t, .1, .5) });
  steps.forEach(([s, a, b], i) => {
    const y = 390 + i * 150, on = t >= a && t < b, past = t >= b, k = seg(t, Math.max(a - .05, .15), Math.max(a, .15) + .3);
    if (k <= 0) return;
    ring(150, y - 18, 34, on ? C.green : C.line, 4, k); if (on) dot(150, y - 18, 34, C.green, k * .2);
    text(past ? '✓' : String(i + 1), 150, y - 3, 40, { f: F.d, w: 700, al: 'center', c: on || past ? C.green : C.dim, a: k });
    text(s, 212, y, 50, { f: F.d, w: on ? 650 : 500, c: on ? C.ink : '#778071', a: k });
  });
  text('Zielbild: Die Benachrichtigung', 110, 880, 34, { c: C.amber, a: seg(t, .5, 1) });
  text('ist noch nicht umgesetzt.', 110, 926, 34, { c: C.amber, a: seg(t, .5, 1) });
  text('Beispiel. Luftbild: basemap.at', 110, 972, 22, { f: F.m, c: '#7C8476', a: seg(t, .5, 1) });
  // phone: rises in, buzzes when the message arrives
  const up = 1 - ease(t / .55), buzz = t > n0 && t < n0 + .55 ? Math.sin((t - n0) * 90) * 6 * (1 - (t - n0) / .55) : 0;
  g.save(); g.translate(buzz, up * 220);
  g.fillStyle = '#050705'; g.strokeStyle = '#3B453A'; g.lineWidth = 3; g.beginPath(); g.roundRect(P.x, P.y, P.w, P.h, 62); g.fill(); g.stroke();
  g.save(); g.beginPath(); g.roundRect(P.sx, P.sy, P.sw, P.sh, 48); g.clip();
  phoneScreen(t, v);
  g.restore();
  rect(P.x + P.w / 2 - 62, P.sy + 12, 124, 30, '#050705');
  g.restore();
  if (t > n0 && t < n0 + .8) { const k = (t - n0) / .8; g.save(); g.strokeStyle = '#D6EE9A'; g.globalAlpha = 1 - k; g.lineWidth = 5; g.beginPath(); g.roundRect(P.x - k * 40, P.y - k * 40, P.w + k * 80, P.h + k * 80, 62 + k * 30); g.stroke(); g.restore(); }
  vignette(.35);
};

// ---- opening: the three words, screen-blended over film
function bigWord(s, t, d) { blackbg(); const a = seg(t, 0, .12) * (1 - seg(t, d - .08, d)); g.save(); g.translate(960, 540); const z = 1 + .05 * t / d; g.scale(z, z); text(s, 0, 56, 176, { f: F.d, w: 700, al: 'center', sp: 10, a, glow: 26, glowc: 'rgba(255,255,255,.35)' }); g.restore(); }
// ---- opening: what the real combine track on screen means
S.p_tracks = (t, d) => {
  blackbg();
  const a = inout(t, .2, .7, d - .3, d), x = 1490;           // right of the field's spike, nothing touches the track
  text('Echte Spur.', x, 150, 46, { f: F.d, w: 650, a });
  text('Echte Messwerte.', x, 206, 46, { f: F.d, w: 650, a });
  for (let i = 0; i < 38; i++) rect(x + i * 10, 234, 10.5, 18, rgb(ramp(i / 37)), a);
  text('wenig Ertrag', x, 286, 26, { c: C.sig, a });
  text('viel', x + 380, 286, 26, { al: 'right', c: C.green, a });
};
S.p_duerre = (t, d) => bigWord('DÜRRE', t, d);
S.p_befall = (t, d) => bigWord('BEFALL', t, d);
S.p_unwetter = (t, d) => bigWord('UNWETTER', t, d);

// ---- plates, screen-blended over film (black = transparent)
S.p_ch0 = (t, d) => { blackbg(); chapter(0, t, d); };
S.p_sat = (t, d) => {
  blackbg(); chapter(1, t, d, true);
  const v = voiceAt('p_sat', 'c01');
  text('SENTINEL-2', 960, 900, 84, { f: F.d, w: 600, al: 'center', a: inout(t, v(0) + 3.6, v(0) + 4.2, d - .3, d) });
};
S.p_desc = (t, d) => {
  blackbg(); chapter(1, t, d, true);
  text('Zehn Meter pro Pixel. Frei für alle.', 960, 900, 62, { f: F.d, w: 600, al: 'center', a: seg(t, .15, .55) });
};
S.p_ch4 = (t, d) => { blackbg(); chapter(4, t, d, true); };
S.p_rise = (t, d) => { blackbg(); };

window.drawScene = (name, t, d) => {
  g.setTransform(SC, 0, 0, SC, 0, 0);
  S[name](t, d);
};
