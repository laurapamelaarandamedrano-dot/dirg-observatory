/* DIRG Observatory renderer.
   Data-agnostic: every number, label and sentence comes from data/observatory.json, which the
   Python pipeline generates. This file only draws. It computes nothing scientific. */
(function () {
  'use strict';

  // ------------------------------------------------------------------ state
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const S = { mode: 'srti', sub: 'pillar', variant: 'srti', year: 2025, sel: null, hover: null,
              lang: 'en', motion: !reduceMotion, focused: false, playing: false, expanded: false };
  let D, T, features, mexicoFC, land;
  const $ = (q, el) => (el || document).querySelector(q);
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  const MODES = [
    { k: 'srti', c: '#a9dcff' }, { k: 'W', c: '#5ec2ef' }, { k: 'E', c: '#f0b452' }, { k: 'D', c: '#a796ff' },
    { k: 'V', c: '#6fd0a0' }, { k: 'cov', c: '#cfe9ff' }, { k: 'G', c: '#e6dfcb' }];
  const RAMPS = {
    srti: ['#16233d', '#2c5a7a', '#5c978c', '#b4c27b', '#f4d06f'],
    W: ['#0d2433', '#1d6a91', '#5ec2ef', '#cdf0ff'], E: ['#2a1c0c', '#8a5a1d', '#f0b452', '#ffe9b8'],
    D: ['#191431', '#4c3f9a', '#a796ff', '#e6e0ff'], V: ['#0c2219', '#246a4b', '#6fd0a0', '#d6f6e5'],
    cov: ['#1a2433', '#3c5672', '#7fa8cc', '#d4ecff'], G: ['#24211b', '#6e6656', '#bdb49c', '#f3eddc'] };
  const interp = {};
  Object.keys(RAMPS).forEach((k) => { interp[k] = d3.interpolateRgbBasis(RAMPS[k]); });
  const LEDGER_COLORS = { known: '#a9dcff', derived: '#c8d3e3', estimated: '#f2c46d', modelled: '#c9b8ff', unknown: '#3a4558' };
  const LEDGER_OF = { observed: 'known', administrative: 'known', documentary: 'known', geospatial: 'known',
                      derived: 'derived', estimated: 'estimated', modelled: 'modelled', hypothesized: 'unknown', unknown: 'unknown' };
  const t = (key) => key.split('.').reduce((o, k) => (o == null ? o : o[k]), T[S.lang]);
  const vars = () => D.variables;
  const lbl = (k) => vars()[k].label[S.lang];
  const nf = (v, d) => (v == null || Number.isNaN(v)) ? '—' :
    new Intl.NumberFormat(S.lang === 'es' ? 'es-MX' : 'en-US', { maximumFractionDigits: d, minimumFractionDigits: d }).format(v);
  const fmt = (v) => v == null ? '—' : (Number.isInteger(v) || Math.abs(v) >= 100 ? nf(v, 0) : Math.abs(v) >= 10 ? nf(v, 1) : nf(v, 2));

  // ------------------------------------------------------------------ value model
  const varScale = {};
  function buildScales() {
    Object.keys(vars()).forEach((k) => {
      let lo = Infinity, hi = -Infinity;
      D.territories.forEach((tr) => D.meta.years.forEach((y) => {
        const v = D.data[tr.id][y].ind[k][0];
        if (v != null) { lo = Math.min(lo, v); hi = Math.max(hi, v); }
      }));
      const log = vars()[k].transform === 'log1p';
      const f = log ? (x) => Math.log1p(Math.max(0, x)) : (x) => x;
      const a = f(lo), b = f(hi);
      varScale[k] = { lo, hi, log, t: (x) => (x == null ? null : (b > a ? (f(x) - a) / (b - a) : 0.5)) };
    });
  }
  function subsFor(mode) {
    if (mode === 'srti' || mode === 'cov') return [];
    if (mode === 'G') return Object.keys(vars()).filter((k) => vars()[k].pillar === 'G');
    const inIdx = Object.keys(vars()).filter((k) => vars()[k].pillar === mode);
    const ctx = { W: [], E: ['e_selfsupply_new_mw_3y'], D: ['d_cloud_regions_announced'], V: ['c_population', 'c_pop_growth_5y'] }[mode] || [];
    return ['pillar'].concat(inIdx, ctx);
  }
  function rampKey() { return S.mode === 'srti' ? 'srti' : S.mode; }
  function texFromIndicator(st, flags) {
    if (st === 'unknown') return 'none';
    if (/CARRIED_FORWARD|PARTIAL_YEAR|UNDATED_VINTAGE/.test(flags || '')) return 'hatch';
    if (st === 'estimated' || st === 'modelled') return 'stipple';
    return 'solid';
  }
  const TIER_TEX = { high: 'solid', moderate: 'stipple', limited: 'hatch', insufficient: 'none' };
  function valueOf(ce, y) {
    const rec = D.data[ce][y];
    if (S.mode === 'srti') {
      const v = S.variant === 'rbi' ? rec.rbi : rec.srti;
      return { v, t: v == null ? null : v / 100, tex: v == null ? 'none' : TIER_TEX[rec.tier], unit: '/100', label: S.variant === 'rbi' ? t('rbi_label') : 'SRTI' };
    }
    if (S.mode === 'cov') return { v: rec.cov, t: rec.cov, tex: TIER_TEX[rec.tier], unit: '', label: t('coverage_label') };
    const k = S.mode === 'G' ? (S.sub === 'pillar' ? 'g_veda_area' : S.sub) : S.sub;
    if (k === 'pillar') {
      const v = rec.P[S.mode];
      return { v, t: v == null ? null : v / 100, tex: v == null ? 'none' : TIER_TEX[rec.tier], unit: '/100', label: t('pillar_score') };
    }
    const ind = rec.ind[k];
    let tt = varScale[k].t(ind[0]);
    if (tt != null && vars()[k].direction < 0) tt = 1 - tt;
    return { v: ind[0], t: tt, tex: ind[0] == null ? 'none' : texFromIndicator(ind[2], ind[3]), unit: vars()[k].unit, label: lbl(k), status: ind[2] };
  }

  // ------------------------------------------------------------------ globe
  const canvas = $('#globe');
  const ctx = canvas.getContext('2d');
  const proj = d3.geoOrthographic().clipAngle(90).precision(0.35);
  const path = d3.geoPath(proj, ctx);
  const grat10 = d3.geoGraticule10();
  const grat30 = d3.geoGraticule().step([30, 30])();
  const FOCUS_ROT = [102, -23.5, 0];
  let W = 0, H = 0, dpr = 1;
  const view = { rot: [118, -18, 0], scale: 300, tx: 0, ty: 0 };
  let orbitTarget = { scale: 300, tx: 0, ty: 0 }, focusTarget = { scale: 900, tx: 0, ty: 0 };
  let flight = null, userZoom = 1, lastInteract = -1e9, dragging = null, focusBase = FOCUS_ROT.slice();
  const colors = {}; let colorTween = null; let scan = null; let pulseStart = 0;
  const patterns = {};

  function mkPattern(kind) {
    const c = document.createElement('canvas'); const s = 6 * dpr; c.width = s; c.height = s;
    const g = c.getContext('2d');
    g.fillStyle = 'rgba(5,8,14,0.58)'; g.strokeStyle = 'rgba(5,8,14,0.62)'; g.lineWidth = 1.2 * dpr;
    if (kind === 'stipple') { g.beginPath(); g.arc(s * 0.25, s * 0.25, 0.75 * dpr, 0, 6.3); g.arc(s * 0.75, s * 0.75, 0.75 * dpr, 0, 6.3); g.fill(); }
    if (kind === 'hatch') { g.beginPath(); g.moveTo(0, s); g.lineTo(s, 0); g.moveTo(-s / 2, s / 2); g.lineTo(s / 2, -s / 2); g.moveTo(s / 2, s * 1.5); g.lineTo(s * 1.5, s / 2); g.stroke(); }
    return ctx.createPattern(c, 'repeat');
  }
  function swatchCanvas(color, kind) {
    const c = document.createElement('canvas'); c.width = 36; c.height = 24; const g = c.getContext('2d');
    if (kind === 'none') { g.setLineDash([3, 2]); g.strokeStyle = 'rgba(148,176,214,.6)'; g.strokeRect(1, 1, 34, 22); return c; }
    g.fillStyle = color; g.fillRect(0, 0, 36, 24);
    if (kind === 'stipple') { g.fillStyle = 'rgba(5,8,14,.6)'; for (let x = 2; x < 36; x += 6) for (let y = 2; y < 24; y += 6) { g.beginPath(); g.arc(x, y, 1.2, 0, 6.3); g.fill(); } }
    if (kind === 'hatch') { g.strokeStyle = 'rgba(5,8,14,.65)'; g.lineWidth = 2; for (let i = -24; i < 36; i += 7) { g.beginPath(); g.moveTo(i, 24); g.lineTo(i + 24, 0); g.stroke(); } }
    return c;
  }

  const isMobile = () => window.innerWidth <= 760;
  function resize() {
    const r = canvas.getBoundingClientRect();
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = r.width; H = r.height;
    canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
    patterns.stipple = mkPattern('stipple'); patterns.hatch = mkPattern('hatch');
    const panelW = isMobile() ? 0 : (parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--panel-w')) || 380) + 32;
    orbitTarget = { scale: Math.min(W, H) * (isMobile() ? 0.42 : 0.37), tx: isMobile() ? W / 2 : W * 0.6, ty: H * 0.52 };
    const pad = isMobile() ? 18 : 40;
    const x0 = isMobile() ? pad : Math.min(W * 0.3, 460), x1 = W - panelW - pad;
    const y0 = isMobile() ? pad : 120, y1 = H - (isMobile() ? pad : 150);
    const p2 = d3.geoOrthographic().clipAngle(90).rotate(FOCUS_ROT).fitExtent([[x0, y0], [Math.max(x0 + 200, x1), Math.max(y0 + 200, y1)]], mexicoFC);
    focusTarget = { scale: p2.scale(), tx: p2.translate()[0], ty: p2.translate()[1] };
    const tgt = S.focused ? focusTarget : orbitTarget;
    if (!flight) { view.scale = tgt.scale * (S.focused ? userZoom : 1); view.tx = tgt.tx; view.ty = tgt.ty; }
    requestDraw();
  }

  function applyView() { proj.rotate(view.rot).scale(view.scale).translate([view.tx, view.ty]); }

  function draw(now) {
    applyView();
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);
    const R = view.scale, cx = view.tx, cy = view.ty;
    // atmosphere limb
    const atm = ctx.createRadialGradient(cx, cy, R * 0.96, cx, cy, R * 1.16);
    atm.addColorStop(0, 'rgba(169,220,255,0.0)'); atm.addColorStop(0.18, 'rgba(169,220,255,0.16)'); atm.addColorStop(1, 'rgba(169,220,255,0)');
    ctx.fillStyle = atm; ctx.beginPath(); ctx.arc(cx, cy, R * 1.16, 0, Math.PI * 2); ctx.fill();
    // sphere
    const sph = ctx.createRadialGradient(cx - R * 0.35, cy - R * 0.4, R * 0.1, cx, cy, R);
    sph.addColorStop(0, '#0f1d31'); sph.addColorStop(1, '#060b14');
    ctx.beginPath(); path({ type: 'Sphere' }); ctx.fillStyle = sph; ctx.fill();
    ctx.lineWidth = 0.5; ctx.strokeStyle = 'rgba(148,176,214,0.06)'; ctx.beginPath(); path(grat10); ctx.stroke();
    ctx.strokeStyle = 'rgba(148,176,214,0.13)'; ctx.beginPath(); path(grat30); ctx.stroke();
    // land
    ctx.beginPath(); path(land); ctx.fillStyle = 'rgba(128,156,196,0.09)'; ctx.fill();
    ctx.lineWidth = 0.5; ctx.strokeStyle = 'rgba(148,176,214,0.22)'; ctx.stroke();
    // territories
    features.forEach((f) => {
      const c = colors[f.id]; if (!c) return;
      ctx.beginPath(); path(f);
      if (c.tex === 'none') {
        ctx.save(); ctx.setLineDash([3, 3]); ctx.lineWidth = 0.9; ctx.strokeStyle = 'rgba(148,176,214,0.55)'; ctx.stroke(); ctx.restore();
        return;
      }
      ctx.fillStyle = c.cur; ctx.fill();
      if (c.tex === 'stipple' || c.tex === 'hatch') { ctx.fillStyle = patterns[c.tex]; ctx.fill(); }
      ctx.lineWidth = 0.8; ctx.strokeStyle = 'rgba(5,8,14,0.95)'; ctx.stroke();
    });
    ctx.beginPath(); path(mexicoFC); ctx.lineWidth = 1; ctx.strokeStyle = 'rgba(169,220,255,0.35)'; ctx.stroke();
    if (S.hover && S.hover !== S.sel) { ctx.beginPath(); path(byId[S.hover]); ctx.lineWidth = 1.6; ctx.strokeStyle = '#a9dcff'; ctx.stroke(); }
    if (S.sel) {
      ctx.save(); ctx.shadowColor = 'rgba(169,220,255,0.9)'; ctx.shadowBlur = 10;
      ctx.beginPath(); path(byId[S.sel]); ctx.lineWidth = 2; ctx.strokeStyle = '#ffffff'; ctx.stroke(); ctx.restore();
    }
    drawNodes(now);
    if (scan) drawScan(now);
  }

  function drawNodes(now) {
    if (!(S.mode === 'srti' || S.mode === 'D')) return;
    const center = [-view.rot[0], -view.rot[1]];
    D.territories.forEach((tr) => {
      const n = D.data[tr.id][S.year].ind.d_cloud_regions[0];
      if (!n) return;
      if (d3.geoDistance(tr.anchor, center) > Math.PI / 2 - 0.08) return;
      const [x, y] = proj(tr.anchor);
      const r = 2.6 + 2.4 * Math.sqrt(n);
      const prev = S.year > D.meta.years[0] ? D.data[tr.id][S.year - 1].ind.d_cloud_regions[0] : null;
      if (S.motion && prev != null && n > prev) {
        const ph = ((now - pulseStart) % 2400) / 2400;
        ctx.beginPath(); ctx.arc(x, y, r + ph * 22, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(167,150,255,${0.75 * (1 - ph)})`; ctx.lineWidth = 1.2; ctx.stroke();
      }
      ctx.beginPath(); ctx.arc(x, y, r + 3, 0, Math.PI * 2); ctx.strokeStyle = 'rgba(167,150,255,0.85)'; ctx.lineWidth = 1; ctx.stroke();
      ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fillStyle = 'rgba(240,236,255,0.95)'; ctx.fill();
      ctx.font = `500 10px "IBM Plex Mono", monospace`; ctx.fillStyle = '#e6e0ff'; ctx.fillText(String(n), x + r + 6, y + 3.5);
    });
  }
  function drawScan(now) {
    const p = Math.min(1, (now - scan.t0) / 750);
    const b = path.bounds(mexicoFC); const y = b[0][1] + p * (b[1][1] - b[0][1]);
    const g = ctx.createLinearGradient(0, y - 18, 0, y + 1);
    g.addColorStop(0, 'rgba(169,220,255,0)'); g.addColorStop(1, 'rgba(169,220,255,0.22)');
    ctx.fillStyle = g; ctx.fillRect(b[0][0] - 10, y - 18, b[1][0] - b[0][0] + 20, 19);
    ctx.fillStyle = 'rgba(169,220,255,0.7)'; ctx.fillRect(b[0][0] - 10, y, b[1][0] - b[0][0] + 20, 1);
    if (p >= 1) scan = null;
  }

  // animation loop: runs only while something moves
  let rafId = null, lastFrame = 0, visible = true;
  function requestDraw() { if (!rafId) rafId = requestAnimationFrame(frame); }
  function idleMotion() { return S.motion && visible && !dragging && !flight; }
  function frame(now) {
    rafId = null;
    let moving = false;
    if (flight) {
      const k = Math.min(1, (now - flight.t0) / flight.dur), e = d3.easeCubicInOut(k);
      view.rot = flight.rot(e); view.scale = flight.scale(e); view.tx = flight.tx(e); view.ty = flight.ty(e);
      if (k >= 1) { flight = null; lastInteract = now; }
      moving = true;
    } else if (idleMotion() && now - lastInteract > 6000) {
      if (S.focused) {
        const tt = now / 1000;
        view.rot = [focusBase[0] + 4 * Math.sin(tt * 2 * Math.PI / 24), focusBase[1] + 1.4 * Math.sin(tt * 2 * Math.PI / 31), 0];
      } else {
        view.rot = [view.rot[0] + 0.045, view.rot[1] + (-18 - view.rot[1]) * 0.01, 0];
      }
      moving = true;
    }
    if (colorTween) {
      const k = Math.min(1, (now - colorTween.t0) / colorTween.dur);
      Object.keys(colors).forEach((id) => { const c = colors[id]; c.cur = c.interp(d3.easeCubicOut(k)); });
      if (k >= 1) colorTween = null;
      moving = true;
    }
    if (scan || (S.motion && pulsesActive())) moving = true;
    const idleOnly = moving && !flight && !colorTween && !scan;
    if (!idleOnly || now - lastFrame > 30) { draw(now); lastFrame = now; }
    if (moving && visible) requestDraw();
  }
  function pulsesActive() {
    if (!(S.mode === 'srti' || S.mode === 'D') || S.year === D.meta.years[0]) return false;
    return D.territories.some((tr) => { const a = D.data[tr.id][S.year].ind.d_cloud_regions[0], b = D.data[tr.id][S.year - 1].ind.d_cloud_regions[0]; return a != null && b != null && a > b; });
  }
  function flyTo(target, rot, dur) {
    const r0 = view.rot.slice();
    flight = { t0: performance.now(), dur: reduceMotion ? 1 : dur,
               rot: d3.interpolate(r0, rot), scale: d3.interpolate(view.scale, target.scale),
               tx: d3.interpolate(view.tx, target.tx), ty: d3.interpolate(view.ty, target.ty) };
    requestDraw();
  }

  function recolor(animate) {
    const dur = animate && S.motion ? 650 : 1;
    D.territories.forEach((tr) => {
      const v = valueOf(tr.id, S.year);
      const tgt = v.t == null ? 'rgba(0,0,0,0)' : interp[rampKey()](Math.max(0, Math.min(1, v.t)));
      const prev = colors[tr.id] ? colors[tr.id].cur : tgt;
      colors[tr.id] = { cur: prev, tgt, tex: v.tex, interp: d3.interpolateRgb(prev, tgt) };
    });
    colorTween = { t0: performance.now(), dur };
    requestDraw();
  }

  // pointer interaction
  function pick(x, y) {
    const dx = x - view.tx, dy = y - view.ty;
    if (dx * dx + dy * dy > view.scale * view.scale) return null;
    const ll = proj.invert([x, y]); if (!ll) return null;
    const f = features.find((ft) => d3.geoContains(ft, ll));
    return f ? f.id : null;
  }
  const pointers = new Map(); let pinch0 = null;
  canvas.addEventListener('pointerdown', (e) => {
    canvas.setPointerCapture(e.pointerId); pointers.set(e.pointerId, [e.offsetX, e.offsetY]);
    if (pointers.size === 2) { const [a, b] = [...pointers.values()]; pinch0 = { d: Math.hypot(a[0] - b[0], a[1] - b[1]), s: view.scale }; }
    dragging = { x: e.offsetX, y: e.offsetY, rot: view.rot.slice(), moved: false };
    flight = null; lastInteract = performance.now();
  });
  canvas.addEventListener('pointermove', (e) => {
    if (pointers.has(e.pointerId)) pointers.set(e.pointerId, [e.offsetX, e.offsetY]);
    if (pinch0 && pointers.size === 2) {
      const [a, b] = [...pointers.values()]; const d = Math.hypot(a[0] - b[0], a[1] - b[1]);
      setScale(pinch0.s * d / pinch0.d); return;
    }
    if (dragging) {
      const dx = e.offsetX - dragging.x, dy = e.offsetY - dragging.y;
      if (Math.abs(dx) + Math.abs(dy) > 3) { dragging.moved = true; canvas.classList.add('dragging'); }
      const k = 70 / view.scale;
      view.rot = [dragging.rot[0] + dx * k, Math.max(-80, Math.min(80, dragging.rot[1] - dy * k)), 0];
      if (S.focused) focusBase = view.rot.slice();
      lastInteract = performance.now(); hideTip(); requestDraw(); return;
    }
    const id = pick(e.offsetX, e.offsetY);
    if (id !== S.hover) { S.hover = id; requestDraw(); }
    if (id) showTip(id, e.offsetX, e.offsetY); else hideTip();
  });
  function endPointer(e) {
    pointers.delete(e.pointerId); if (pointers.size < 2) pinch0 = null;
    if (dragging && !dragging.moved && e.type === 'pointerup') {
      const id = pick(e.offsetX, e.offsetY);
      if (id) { if (!S.focused) focus(); select(id); }
    }
    dragging = null; canvas.classList.remove('dragging'); lastInteract = performance.now(); requestDraw();
  }
  canvas.addEventListener('pointerup', endPointer);
  canvas.addEventListener('pointercancel', endPointer);
  canvas.addEventListener('pointerleave', () => { if (S.hover) { S.hover = null; requestDraw(); } hideTip(); });
  canvas.addEventListener('wheel', (e) => { e.preventDefault(); setScale(view.scale * Math.exp(-e.deltaY * 0.0015)); }, { passive: false });
  function setScale(s) {
    const base = S.focused ? focusTarget.scale : orbitTarget.scale;
    view.scale = Math.max(base * 0.5, Math.min(base * 4, s)); userZoom = view.scale / base;
    lastInteract = performance.now(); requestDraw();
  }
  const tip = $('#tooltip');
  function showTip(id, x, y) {
    const v = valueOf(id, S.year), rec = D.data[id][S.year];
    tip.innerHTML = `<b>${esc(nameOf(id))}</b><span class="tv">${esc(v.label)}: ${fmt(v.v)}${v.unit === '/100' ? '' : ' <small>' + esc(v.unit) + '</small>'}</span><br><small>${esc(t('tiers.' + rec.tier))}</small>`;
    tip.hidden = false;
    const tw = tip.offsetWidth, th = tip.offsetHeight;
    tip.style.left = Math.min(W - tw - 8, x + 14) + 'px'; tip.style.top = Math.max(8, y - th - 10) + 'px';
  }
  function hideTip() { tip.hidden = true; }

  // ------------------------------------------------------------------ UI
  const byId = {};
  const nameOf = (id) => D.territories.find((x) => x.id === id).name;
  function focus() {
    if (S.focused) return;
    S.focused = true; $('#observatory').classList.add('focused');
    focusBase = FOCUS_ROT.slice(); userZoom = 1;
    flyTo(focusTarget, FOCUS_ROT, 1700);
  }
  function select(id) {
    S.sel = id || null;
    $('#territory-select').value = id || '';
    renderPanel(); requestDraw();
    $('#panel').classList.toggle('open', !!id);
    if (!id) $('#panel').classList.remove('expanded');
  }
  function setYear(y, animate) {
    if (y === S.year) return;
    S.year = y; renderYears(); recolor(animate);
    if (S.motion) { scan = { t0: performance.now() }; pulseStart = performance.now(); }
    renderLegend(); renderPanel(); renderTable(); requestDraw();
  }
  let playTimer = null;
  function togglePlay() {
    S.playing = !S.playing;
    $('#play-icon').setAttribute('d', S.playing ? 'M4 2.5h3v11H4zM9 2.5h3v11H9z' : 'M4 2.5v11l9-5.5z');
    $('#play').setAttribute('aria-label', S.playing ? t('pause') : t('play'));
    if (S.playing) {
      if (!S.focused) focus();
      const step = () => {
        const ys = D.meta.years; const i = ys.indexOf(S.year);
        setYear(ys[(i + 1) % ys.length], true);
        playTimer = setTimeout(step, 1700);
      };
      step();
    } else clearTimeout(playTimer);
  }

  function renderModes() {
    const el = $('#modes');
    el.innerHTML = MODES.map((m) => `<button class="mode" role="tab" id="mode-${m.k}" aria-selected="${S.mode === m.k}" data-mode="${m.k}" style="--c:${m.c}"><span class="sw" aria-hidden="true"></span>${esc(t('modes.' + m.k))}</button>`).join('');
    el.querySelectorAll('.mode').forEach((b) => b.addEventListener('click', () => setMode(b.dataset.mode)));
    el.addEventListener('keydown', (e) => {
      if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
      const i = MODES.findIndex((m) => m.k === S.mode) + (e.key === 'ArrowRight' ? 1 : -1);
      const m = MODES[(i + MODES.length) % MODES.length]; setMode(m.k); $('#mode-' + m.k).focus();
    });
    $('#mode-hint').textContent = t('mode_hint.' + S.mode);
  }
  function setMode(k) {
    S.mode = k; S.sub = k === 'G' ? 'g_veda_area' : 'pillar';
    if (!S.focused) focus();
    renderModes(); renderSubs(); recolor(true); renderLegend(); renderPanel(); renderTable();
  }
  function renderSubs() {
    const el = $('#subs');
    let opts = subsFor(S.mode).map((k) => ({ k, label: k === 'pillar' ? t('pillar_score') : lbl(k), ctx: k !== 'pillar' && !vars()[k].in_index && S.mode !== 'G' }));
    if (S.mode === 'srti') opts = [{ k: 'srti', label: t('variant_srti') }, { k: 'rbi', label: t('variant_rbi') }];
    if (!opts.length) { el.innerHTML = ''; return; }
    el.innerHTML = opts.map((o) => {
      const on = S.mode === 'srti' ? S.variant === o.k : S.sub === o.k;
      return `<button class="sub" type="button" aria-pressed="${on}" data-k="${o.k}">${esc(o.label)}${o.ctx ? ` <span class="ctx">· ${esc(t('not_in_index'))}</span>` : ''}</button>`;
    }).join('');
    el.querySelectorAll('.sub').forEach((b) => b.addEventListener('click', () => {
      if (S.mode === 'srti') S.variant = b.dataset.k; else S.sub = b.dataset.k;
      renderSubs(); recolor(true); renderLegend(); renderPanel(); renderTable();
    }));
  }
  function renderYears() {
    const el = $('#years');
    el.innerHTML = D.meta.years.map((y) => {
      const note = y === 2026 ? t('year_partial') : y === 2027 ? t('year_projection') : '';
      return `<button class="year" role="radio" aria-checked="${y === S.year}" tabindex="${y === S.year ? 0 : -1}" data-y="${y}">${y}${note ? `<small>${esc(note)}</small>` : '<small>&nbsp;</small>'}</button>`;
    }).join('');
    el.querySelectorAll('.year').forEach((b) => b.addEventListener('click', () => { if (!S.focused) focus(); setYear(+b.dataset.y, true); }));
  }
  $('#years').addEventListener('keydown', (e) => {
    const ys = D.meta.years; let i = ys.indexOf(S.year);
    if (e.key === 'ArrowRight' || e.key === 'ArrowUp') i = Math.min(ys.length - 1, i + 1);
    else if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') i = Math.max(0, i - 1);
    else return;
    e.preventDefault(); setYear(ys[i], true); $(`.year[data-y="${ys[i]}"]`).focus();
  });

  function legendSpec() {
    const v = valueOf(D.territories[0].id, S.year);
    if (S.mode === 'srti' || (S.sub === 'pillar' && S.mode !== 'G' && S.mode !== 'cov')) return { title: v.label + (S.mode === 'srti' ? '' : ' · ' + t('modes.' + S.mode)), lo: '0', mid: '50', hi: '100', tierTex: true };
    if (S.mode === 'cov') return { title: t('coverage_label'), lo: '0', mid: '0.5', hi: '1', tierTex: true };
    const k = S.mode === 'G' ? S.sub : S.sub; const sc = varScale[k]; const dir = vars()[k].direction;
    const a = fmt(sc.lo), b = fmt(sc.hi);
    return { title: `${lbl(k)} (${vars()[k].unit})`, lo: dir < 0 ? b : a, mid: sc.log ? 'log' : '', hi: dir < 0 ? a : b, tierTex: false, dir };
  }
  function renderLegend() {
    const sp = legendSpec(), rk = rampKey();
    const stops = d3.range(0, 1.0001, 0.1).map((x) => interp[rk](x)).join(',');
    const texKeys = sp.tierTex
      ? [['solid', t('tiers.high')], ['stipple', t('tiers.moderate')], ['hatch', t('tiers.limited')], ['none', t('tiers.insufficient')]]
      : [['solid', t('ledger.known') + ' / ' + t('status.derived')], ['stipple', t('status.estimated') + ' / ' + t('status.modelled')], ['hatch', t('legend_hatch_var')], ['none', t('legend_nodata')]];
    const el = $('#legend');
    el.innerHTML = `<p class="lg-title">${esc(sp.title)} · ${S.year}</p><div class="ramp" style="background:linear-gradient(90deg,${stops})"></div>
      <div class="ticks mono"><span>${esc(sp.lo)}</span><span>${esc(sp.mid)}</span><span>${esc(sp.hi)}</span></div>
      <p class="note">${esc(t('legend_tiers'))}</p><div class="keys"></div>`;
    const keys = el.querySelector('.keys'); const mid = interp[rk](0.65);
    texKeys.forEach(([k, l]) => { const d = document.createElement('div'); d.className = 'key'; d.appendChild(swatchCanvas(mid, k)); const s = document.createElement('span'); s.textContent = l; d.appendChild(s); keys.appendChild(d); });
    if (S.mode === 'srti' || S.mode === 'D') {
      const n = document.createElement('p'); n.className = 'note';
      n.textContent = '○ ' + lbl('d_cloud_regions') + (S.lang === 'es' ? ' (punto en el centroide del estado, no en la instalación)' : ' (marker at state centroid, not facility location)');
      el.appendChild(n);
    }
  }

  function badge(st) {
    const cls = 's-' + (LEDGER_OF[st] || 'unknown');
    return `<span class="badge ${cls}" title="${esc(t('status.' + st))}">${esc(t('status_code.' + st))}</span>`;
  }
  function srcLinks(ids) { return String(ids).split('|').map((s) => `<a class="src-chip" href="#src-${esc(s)}">${esc(s)}</a>`).join(' '); }

  function renderPanel() {
    const el = $('#panel-body');
    if (!S.sel) { el.innerHTML = panelOverview(); bindStrip(el); return; }
    const id = S.sel, y = S.year, rec = D.data[id][y], tr = D.territories.find((x) => x.id === id);
    const v = S.variant === 'rbi' ? rec.rbi : rec.srti;
    const ex = D.explanations[id][y][S.lang];
    const tiers = `<span class="pill"><canvas width="36" height="24"></canvas>${esc(t('tiers.' + rec.tier))} · ${nf(rec.cov, 2)}</span>`;
    const iv = rec.mc[0] != null && v != null ? `<div class="iv" aria-hidden="true"><div class="track"></div><div class="band" style="left:${rec.mc[0]}%;width:${Math.max(0.6, rec.mc[1] - rec.mc[0])}%"></div><div class="pt" style="left:calc(${rec.srti}% - 1px)"></div></div>
       <p class="caption">${esc(t('interval_label'))}: <span class="mono">${fmt(rec.mc[0])}–${fmt(rec.mc[1])}</span></p>` : '';
    const pillars = ['W', 'E', 'D', 'V'].map((p) => {
      const pv = rec.P[p]; const c = MODES.find((m) => m.k === p).c;
      return `<div class="bar"><span class="lab">${esc(D.meta.pillars[p][S.lang])}</span><span class="tr"><span class="fi" style="width:${pv == null ? 0 : pv}%;background:${c}"></span></span><span class="v">${pv == null ? '—' : fmt(pv)}</span></div>`;
    }).join('');
    const ledger = ['known', 'derived', 'estimated', 'modelled', 'unknown'].map((k) => `<div style="--lc:${LEDGER_COLORS[k]}"><b>${rec.ledger[k].length}</b>${esc(t('ledger.' + k))}</div>`).join('');
    const rows = Object.keys(vars()).filter((k) => vars()[k].pillar !== 'G').map((k) => {
      const ind = rec.ind[k], vv = vars()[k];
      return `<tr class="${vv.in_index ? '' : 'ctxrow'}"><td>${esc(vv.label[S.lang])}${vv.in_index ? '' : ` <em>(${esc(t('not_in_index'))})</em>`}<br><small>${esc(vv.unit)}</small></td>
        <td class="n">${fmt(ind[0])}</td><td class="n">${ind[1] == null ? '' : fmt(ind[1])}</td><td>${badge(ind[2])}</td><td class="n">${ind[5] == null ? '' : ind[5]}</td><td>${srcLinks(ind[4])}</td></tr>`;
    }).join('');
    const scen = Object.keys(D.meta.scenarios).map((k) => `<div><span>${esc(D.meta.scenarios[k].label)}</span><span>${fmt(rec.scen[k])}</span></div>`).join('');
    const gov = ['g_veda_area', 'g_groundwater_ordinance_area', 'g_climate_instruments'].map((k) => `<dt>${esc(lbl(k))}</dt><dd>${fmt(rec.ind[k][0])}${k === 'g_climate_instruments' ? '' : '%'}</dd>`).join('');
    const warn = rec.flags.includes('PILLARS_RENORMALIZED') ? `<p class="warn-line">⚠ ${esc(t('comparability_warning'))}</p>` : '';
    el.innerHTML = `
      <div class="p-head"><div><h2 class="p-name">${esc(tr.name)}</h2><p class="p-meta mono">${esc(tr.iso)} · ${y}</p></div>
        <button class="p-close" type="button" aria-label="${esc(t('close'))}" id="p-close">✕</button></div>
      <div class="p-score"><div class="p-big ${v == null ? 'muted' : ''}">${v == null ? esc(t('insufficient_note')) : fmt(v) + '<small>/100</small>'}</div>
        <div class="p-rank">${esc(S.variant === 'rbi' ? t('rbi_label') : 'SRTI')}${rec.rank != null && S.variant !== 'rbi' ? `<br>${esc(t('rank_label'))} <span class="mono">${rec.rank}</span> ${esc(t('of32'))} · ${esc(t('rank_range'))} <span class="mono">${rec.rank_iv[0]}–${rec.rank_iv[2]}</span>` : ''}</div></div>
      ${S.variant === 'rbi' ? '' : iv}
      <p style="margin:8px 0 0">${tiers}</p>${warn}
      <div class="p-sec"><h3>${esc(t('pillars_title'))}</h3><div class="bars">${pillars}</div></div>
      <div class="p-sec"><h3>${esc(t('why_title'))}</h3><p class="why">${esc(ex)}</p></div>
      <div class="p-sec"><div class="ledger">${ledger}</div></div>
      <div class="p-sec"><h3>${esc(t('indicators_title'))}</h3><div class="scroll-x"><table class="ind"><thead><tr><th>${esc(t('col_indicator'))}</th><th>${esc(t('col_value'))}</th><th>${esc(t('col_norm'))}</th><th>${esc(t('col_status'))}</th><th>${esc(t('col_vintage'))}</th><th>${esc(t('col_source'))}</th></tr></thead><tbody>${rows}</tbody></table></div></div>
      <div class="p-sec"><h3>${esc(t('scenarios_title'))}</h3><div class="scen">${scen}</div></div>
      <div class="p-sec"><h3>${esc(t('governance_title'))}</h3><dl class="kv">${gov}</dl></div>`;
    const pc = el.querySelector('.pill canvas'); const g = pc.getContext('2d'); g.drawImage(swatchCanvas(interp.srti(0.65), TIER_TEX[rec.tier]), 0, 0);
    $('#p-close').addEventListener('click', () => { select(null); canvas.focus(); });
  }
  function panelOverview() {
    const y = S.year;
    const vals = D.territories.map((tr) => ({ id: tr.id, name: tr.name, ...valueOf(tr.id, y) }));
    const tierCounts = {}; D.territories.forEach((tr) => { const k = D.data[tr.id][y].tier; tierCounts[k] = (tierCounts[k] || 0) + 1; });
    const nat = D.national.series.find((s) => s.year === y);
    const dots = vals.filter((v) => v.t != null).map((v) => `<button class="dot" data-id="${v.id}" style="left:${(Math.max(0, Math.min(1, v.t)) * 100).toFixed(2)}%;background:${interp[rampKey()](v.t)}" aria-label="${esc(v.name)}: ${fmt(v.v)}" title="${esc(v.name)}: ${fmt(v.v)}"></button>`).join('');
    const sp = legendSpec();
    return `<div class="p-head"><div><h2 class="p-name">${esc(t('panel_empty_title'))}</h2><p class="p-meta mono">32 · ${y}</p></div></div>
      <p class="why" style="margin-top:12px">${esc(t('panel_empty_body'))}</p>
      <div class="p-sec"><h3>${esc(t('distribution_title'))} · ${esc(sp.title)}</h3><div class="strip"><div class="axis"></div>${dots}</div><div class="strip-ticks"><span>${esc(sp.lo)}</span><span>${esc(sp.hi)}</span></div></div>
      <div class="p-sec"><h3>${esc(t('coverage_label'))}</h3><dl class="kv">${['high', 'moderate', 'limited', 'insufficient'].map((k) => `<dt>${esc(t('tiers.' + k))}</dt><dd>${tierCounts[k] || 0}</dd>`).join('')}</dl></div>
      <div class="p-sec"><h3>${esc(t('national_context'))}</h3><dl class="kv"><dt>${y} · CFE (S11)</dt><dd>${nat ? fmt(nat.value) + ' TWh' : '—'}</dd></dl></div>
      <div class="p-sec"><p class="caption">${esc(t('disclaimer'))}</p></div>`;
  }
  function bindStrip(el) { el.querySelectorAll('.dot').forEach((b) => b.addEventListener('click', () => select(b.dataset.id))); }

  function renderTable() {
    const view = $('#table-view'); if (view.hidden) return;
    const y = S.year; const sp = legendSpec();
    $('#table-title').textContent = `${sp.title} · ${y}`;
    const rows = D.territories.map((tr) => ({ tr, v: valueOf(tr.id, y), rec: D.data[tr.id][y] }))
      .sort((a, b) => (b.v.v == null) - (a.v.v == null) || (b.v.v || 0) - (a.v.v || 0));
    const pill = S.mode === 'srti';
    $('#data-table').innerHTML = `<thead><tr><th>${esc(t('col_state'))}</th><th class="n">${esc(t('col_value'))}</th>${pill ? ['W', 'E', 'D', 'V'].map((p) => `<th class="n">${p}</th>`).join('') : ''}<th>${esc(t(S.mode === 'srti' || S.sub === 'pillar' || S.mode === 'cov' ? 'coverage_label' : 'col_status'))}</th></tr></thead><tbody>` +
      rows.map((r) => `<tr><td><button class="linkish" data-id="${r.tr.id}">${esc(r.tr.name)}</button></td><td class="n">${fmt(r.v.v)}</td>${pill ? ['W', 'E', 'D', 'V'].map((p) => `<td class="n">${fmt(r.rec.P[p])}</td>`).join('') : ''}<td>${r.v.status ? badge(r.v.status) : esc(t('tier_short.' + r.rec.tier))}</td></tr>`).join('') + '</tbody>';
    $('#data-table').querySelectorAll('.linkish').forEach((b) => b.addEventListener('click', () => { focus(); select(b.dataset.id); $('#observatory').scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth' }); }));
  }

  // ------------------------------------------------------------------ narrative & reference sections
  function svgEl(w, h, inner, label) { return `<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="${esc(label || '')}">${inner}</svg>`; }
  function chartRegions() {
    const years = d3.range(2019, 2027), reg = D.register;
    const states = [...new Set(reg.map((r) => r.cve_ent.padStart(2, '0')))];
    const asOf = new Date(D.meta.as_of);
    const count = (st, y) => reg.filter((r) => r.cve_ent.padStart(2, '0') === st && r.operational_date && new Date(r.operational_date.length === 4 ? r.operational_date + '-12-31' : (r.operational_date.length === 7 ? r.operational_date + '-28' : r.operational_date)) <= (y === 2026 ? asOf : new Date(y + '-12-31'))).length;
    const series = states.map((st) => ({ st, name: nameOf(st), v: years.map((y) => count(st, y)) })).sort((a, b) => b.v[b.v.length - 1] - a.v[a.v.length - 1]);
    const w = 560, h = 190, m = { l: 28, r: 120, t: 10, b: 24 };
    const x = d3.scalePoint().domain(years).range([m.l, w - m.r]);
    const ymax = d3.max(series, (s) => d3.max(s.v));
    const yS = d3.scaleLinear().domain([0, ymax]).range([h - m.b, m.t]);
    const shades = ['#a796ff', '#d6ceff', '#6f5fd0'], dashes = ['', '5 3', '2 3'];
    let g = yS.ticks(ymax).map((v) => `<line x1="${m.l}" x2="${w - m.r}" y1="${yS(v)}" y2="${yS(v)}" stroke="rgba(148,176,214,.10)"/><text x="${m.l - 8}" y="${yS(v) + 3}" text-anchor="end">${v}</text>`).join('');
    g += years.map((y) => `<text x="${x(y)}" y="${h - 6}" text-anchor="middle">${y}${y === 2026 ? '*' : ''}</text>`).join('');
    series.forEach((s, i) => {
      const line = d3.line().x((_, j) => x(years[j])).y((v) => yS(v)).curve(d3.curveStepAfter)(s.v);
      g += `<path d="${line}" fill="none" stroke="${shades[i % 3]}" stroke-width="2" stroke-dasharray="${dashes[i % 3]}"/>`;
      g += `<text class="lbl" x="${w - m.r + 8}" y="${yS(s.v[s.v.length - 1]) + 3 + i * 0}">${esc(s.name)} · ${s.v[s.v.length - 1]}</text>`;
    });
    return `<figure class="fig"><figcaption>${esc(t('chart_regions'))} · *${esc(S.lang === 'es' ? 'al' : 'as of')} ${esc(D.meta.as_of)}</figcaption>${svgEl(w, h, g, t('chart_regions'))}</figure>`;
  }
  function chartBars(data, cap, color, unit) {
    const w = 280, h = 150, m = { l: 34, r: 8, t: 10, b: 22 };
    const x = d3.scaleBand().domain(data.map((d) => d.year)).range([m.l, w - m.r]).padding(0.18);
    const yS = d3.scaleLinear().domain([0, d3.max(data, (d) => d.value) * 1.08]).nice().range([h - m.b, m.t]);
    let g = yS.ticks(4).map((v) => `<line x1="${m.l}" x2="${w - m.r}" y1="${yS(v)}" y2="${yS(v)}" stroke="rgba(148,176,214,.10)"/><text x="${m.l - 6}" y="${yS(v) + 3}" text-anchor="end">${v}</text>`).join('');
    data.forEach((d, i) => {
      const bh = yS(0) - yS(d.value), bx = x(d.year), bw = x.bandwidth();
      g += `<path d="M${bx},${yS(0)}v${-Math.max(0, bh - 3)}q0,-3 3,-3h${bw - 6}q3,0 3,3v${Math.max(0, bh - 3)}z" fill="${color}" opacity="${d.complete === false ? 0.45 : 1}"><title>${d.year}: ${fmt(d.value)} ${unit}</title></path>`;
      if (i % 2 === 0 || i === data.length - 1) g += `<text x="${bx + bw / 2}" y="${h - 6}" text-anchor="middle">${String(d.year).slice(2)}</text>`;
    });
    const last = data[data.length - 1];
    g += `<text class="lbl" x="${x(last.year) + x.bandwidth() / 2}" y="${yS(last.value) - 6}" text-anchor="middle">${fmt(last.value)}</text>`;
    return `<figure class="fig"><figcaption>${esc(cap)}</figcaption>${svgEl(w, h, g, cap)}</figure>`;
  }
  function chartTiers() {
    const ys = D.meta.years, tiers = ['high', 'moderate', 'limited', 'insufficient'];
    const col = { high: '#a9dcff', moderate: '#5f88ad', limited: '#f2c46d', insufficient: '#3a4558' };
    const w = 560, h = 120, m = { l: 34, r: 8, t: 8, b: 22 };
    const x = d3.scaleBand().domain(ys).range([m.l, w - m.r]).padding(0.2);
    const yS = d3.scaleLinear().domain([0, 32]).range([h - m.b, m.t]);
    let g = [0, 16, 32].map((v) => `<line x1="${m.l}" x2="${w - m.r}" y1="${yS(v)}" y2="${yS(v)}" stroke="rgba(148,176,214,.10)"/><text x="${m.l - 6}" y="${yS(v) + 3}" text-anchor="end">${v}</text>`).join('');
    ys.forEach((y) => {
      let acc = 0;
      tiers.forEach((k) => {
        const n = D.territories.filter((tr) => D.data[tr.id][y].tier === k).length; if (!n) return;
        g += `<rect x="${x(y)}" y="${yS(acc + n) + 1}" width="${x.bandwidth()}" height="${Math.max(0, yS(acc) - yS(acc + n) - 2)}" fill="${col[k]}"><title>${y} · ${esc(t('tiers.' + k))}: ${n}</title></rect>`;
        acc += n;
      });
      g += `<text x="${x(y) + x.bandwidth() / 2}" y="${h - 6}" text-anchor="middle">${y}</text>`;
    });
    const legend = tiers.map((k) => `<span class="cat"><b style="color:${col[k]}">■</b>${esc(t('tiers.' + k))}</span>`).join('');
    return `<figure class="fig"><figcaption>${esc(t('chart_tiers'))}</figcaption>${svgEl(w, h, g, t('chart_tiers'))}<div class="cat-grid" style="margin-top:8px">${legend}</div></figure>`;
  }
  function renderStory() {
    const parts = T[S.lang].story.map((c, i) => {
      let fig = '';
      if (c.k === 'territory') fig = chartRegions();
      if (c.k === 'resources') {
        const elec = D.national.series.filter((s) => s.year >= 2016);
        const dr = D.meta.years.filter((y) => y <= 2026).map((y) => ({ year: y, value: d3.mean(D.territories, (tr) => D.data[tr.id][y].ind.w_drought_intensity[0]), complete: y !== 2026 }));
        fig = `<div class="fig fig-row">${chartBars(elec, t('chart_elec'), '#f0b452', 'TWh')}${chartBars(dr, t('chart_drought') + ' · 2026: ' + t('incomplete_year'), '#5ec2ef', '')}</div>`;
      }
      if (c.k === 'governance') {
        const cats = d3.rollups(D.governance, (v) => v.length, (d) => d.category).sort((a, b) => b[1] - a[1]);
        fig = `<div class="fig cat-grid">${cats.map(([k, n]) => `<span class="cat"><b>${n}</b>${esc(k)}</span>`).join('')}</div>`;
      }
      if (c.k === 'data') {
        const idx = Object.keys(vars()).filter((k) => vars()[k].in_index);
        fig = `<div class="fig scroll-x"><table class="data-table"><thead><tr><th>${esc(t('col_indicator'))}</th><th>${esc(t('pillars_title'))}</th><th>${esc(t('col_status'))}</th><th class="n">${S.lang === 'es' ? 'Años con dato' : 'Years with data'}</th><th>${esc(t('col_source'))}</th></tr></thead><tbody>` +
          idx.map((k) => { const n = D.meta.years.filter((y) => D.territories.some((tr) => D.data[tr.id][y].ind[k][0] != null)).length; return `<tr><td>${esc(lbl(k))}</td><td>${esc(D.meta.pillars[vars()[k].pillar][S.lang])}</td><td>${badge(vars()[k].epistemic_status)}</td><td class="n">${n} / ${D.meta.years.length}</td><td>${srcLinks(vars()[k].source_ids.join('|'))}</td></tr>`; }).join('') + '</tbody></table></div>';
      }
      if (c.k === 'model') fig = `<div class="fig">${sensTable()}</div>`;
      if (c.k === 'uncertainty') fig = chartTiers();
      if (c.k === 'explore') fig = `<div class="fig"><button class="cta-ghost" type="button" id="back-to-map">${esc(t('explore_cta'))} ↑</button></div>`;
      return `<article class="chapter" id="ch-${c.k}"><div class="num">${String(i + 1).padStart(2, '0')}</div><div><h2>${esc(c.h)}</h2><p>${esc(c.p)}</p>${fig}</div></article>`;
    });
    $('#story-body').innerHTML = `<p class="section-label mono">${esc(t('sec.story_label'))}</p>` + parts.join('');
    $('#back-to-map').addEventListener('click', () => { focus(); $('#observatory').scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth' }); });
  }
  function sensTable() {
    const sens = Object.fromEntries(D.sensitivity.map((s) => [s.scenario, s]));
    return `<div class="scroll-x"><table class="data-table"><thead><tr><th>${esc(t('col_scenario'))}</th><th class="n">W</th><th class="n">E</th><th class="n">D</th><th class="n">V</th><th class="n">${esc(t('col_rho_min'))}</th><th class="n">${esc(t('col_rho_med'))}</th></tr></thead><tbody>` +
      Object.entries(D.meta.scenarios).map(([k, s]) => `<tr><td>${esc(s.label)}</td>${['W', 'E', 'D', 'V'].map((p) => `<td class="n">${nf(s.weights[p], 2)}</td>`).join('')}<td class="n">${k === 'baseline' ? '—' : nf(sens[k] && sens[k].min, 3)}</td><td class="n">${k === 'baseline' ? '—' : nf(sens[k] && sens[k].median, 3)}</td></tr>`).join('') + '</tbody></table></div>';
  }
  function renderReference() {
    $('#method-grid').innerHTML = T[S.lang].method.map((m) => `<div><dt>${esc(m.h)}</dt><dd>${esc(m.p)}</dd></div>`).join('');
    $('#sens').innerHTML = `<h3 class="sub-title">${esc(t('sens_title'))}</h3>${sensTable()}`;
    const src = Object.entries(D.sources);
    $('#src-table').innerHTML = `<thead><tr><th>ID</th><th>${esc(t('col_institution'))}</th><th>${esc(t('col_title'))}</th><th>${esc(t('col_type'))}</th><th>${esc(t('col_license'))}</th><th>${esc(t('col_redistribution'))}</th><th>${esc(t('col_access'))}</th></tr></thead><tbody>` +
      src.map(([id, s]) => `<tr id="src-${esc(id)}"><td class="mono">${esc(id)}</td><td>${esc(s.institution)}</td><td><a href="${esc(s.url_landing)}" rel="noopener" target="_blank">${esc(s.title)}</a></td><td>${badge(s.dataset_type)}</td><td>${esc(s.license)}</td><td class="mono">${esc(s.redistribution)}</td><td class="mono">${esc(s.access_date)}</td></tr>`).join('') + '</tbody>';
    $('#reg-table').innerHTML = `<thead><tr><th>ID</th><th>${esc(t('col_state'))}</th><th>${esc(t('col_announced'))}</th><th>${esc(t('col_operational'))}</th><th>${esc(t('col_confidence'))}</th><th>${esc(t('col_source'))}</th></tr></thead><tbody>` +
      D.register.map((r) => `<tr><td class="mono">${esc(r.record_id)}</td><td>${esc(nameOf(r.cve_ent.padStart(2, '0')))}</td><td class="mono">${esc(r.announced_date || '—')}</td><td class="mono">${esc(r.operational_date)}</td><td>${esc(r.location_confidence)}</td><td>${srcLinks(r.source_ids)}</td></tr>`).join('') + '</tbody>';
    $('#gov-list').innerHTML = D.governance.map((g) => {
      const q = S.lang === 'es' ? g.open_question_es : g.open_question_en;
      return `<div class="gov"><p class="meta">${esc(g.category)} · ${esc(g.level)} · ${esc(g.date)} · ${esc(g.source_id)}</p><h4>${esc(S.lang === 'es' ? g.name_es : g.name_en)}</h4><p>${esc(S.lang === 'es' ? g.description_es : g.description_en)}</p>${q ? `<p class="q">${esc(q)}</p>` : ''}</div>`;
    }).join('');
    $('#qa-table').innerHTML = `<thead><tr><th>${esc(t('col_check'))}</th><th>${esc(t('col_status'))}</th><th class="n">${esc(t('col_count'))}</th><th>${esc(t('col_detail'))}</th></tr></thead><tbody>` +
      D.qa_checks.map((c) => `<tr><td class="mono">${esc(c.check)}</td><td>${esc(c.status)}</td><td class="n">${c.count == null ? '' : c.count}</td><td>${esc(c.detail)}</td></tr>`).join('') + '</tbody>';
    $('.method .section-label').textContent = t('sec.method_label'); $('#method-title').textContent = t('sec.method_title');
    $('.sources .section-label').textContent = t('sec.sources_label'); $('#sources-title').textContent = t('sec.sources_title');
    $('.quality .section-label').textContent = t('sec.quality_label'); $('#quality-title').textContent = t('sec.quality_title');
    $('.qa-details summary').textContent = t('sec.all_checks');
  }
  function applyI18n() {
    document.documentElement.lang = S.lang;
    document.querySelectorAll('[data-i18n]').forEach((el) => { const v = t(el.dataset.i18n); if (typeof v === 'string') el.textContent = v; });
    $('#strands').textContent = t('strands').join(' · ');
    $('#lang-toggle').textContent = t('lang_toggle'); $('#lang-toggle').lang = S.lang === 'en' ? 'es' : 'en';
    $('#motion-toggle span:last-child').textContent = S.motion ? t('motion_pause') : t('motion_play');
    $('#table-toggle').textContent = $('#table-view').hidden ? t('table_toggle') : t('table_close');
    const sel = $('#territory-select');
    sel.innerHTML = `<option value="">${esc(t('territory_select'))}</option>` + D.territories.map((tr) => `<option value="${tr.id}">${esc(tr.name)}</option>`).join('');
    sel.value = S.sel || '';
  }
  function renderAll() {
    applyI18n(); renderModes(); renderSubs(); renderYears(); renderLegend(); renderPanel(); renderTable(); renderStory(); renderReference();
  }

  // ------------------------------------------------------------------ boot
  function wire() {
    $('#explore-btn').addEventListener('click', focus);
    $('#play').addEventListener('click', togglePlay);
    $('#territory-select').addEventListener('change', (e) => { if (!S.focused) focus(); select(e.target.value || null); });
    $('#lang-toggle').addEventListener('click', () => { S.lang = S.lang === 'en' ? 'es' : 'en'; try { localStorage.setItem('dirg-lang', S.lang); } catch (_) { /* storage unavailable */ } renderAll(); });
    $('#motion-toggle').addEventListener('click', () => {
      S.motion = !S.motion; $('#motion-toggle').setAttribute('aria-pressed', String(!S.motion));
      $('#motion-toggle span:last-child').textContent = S.motion ? t('motion_pause') : t('motion_play');
      if (!S.motion && S.playing) togglePlay();
      requestDraw();
    });
    const toggleTable = (open) => { const v = $('#table-view'); v.hidden = !open; $('#table-toggle').textContent = open ? t('table_close') : t('table_toggle'); if (open) { renderTable(); v.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth' }); } };
    $('#table-toggle').addEventListener('click', () => toggleTable($('#table-view').hidden));
    $('#table-close').addEventListener('click', () => toggleTable(false));
    $('#sheet-handle').addEventListener('click', () => $('#panel').classList.toggle('expanded'));
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && S.sel) select(null); });
    window.addEventListener('resize', () => { resize(); });
    document.addEventListener('visibilitychange', () => { visible = !document.hidden; if (visible) requestDraw(); });
    if ('IntersectionObserver' in window) new IntersectionObserver((en) => { visible = en[0].isIntersecting && !document.hidden; if (visible) requestDraw(); }).observe(canvas);
  }
  Promise.all(['data/observatory.json', 'data/mexico_states.topo.json', 'data/land-110m.topo.json'].map((u) => fetch(u).then((r) => { if (!r.ok) throw new Error(u + ' ' + r.status); return r.json(); })))
    .then(([data, states, landTopo]) => {
      D = data; T = D.i18n;
      try { const l = localStorage.getItem('dirg-lang'); S.lang = l || ((navigator.language || 'en').toLowerCase().startsWith('es') ? 'es' : 'en'); } catch (_) { S.lang = (navigator.language || 'en').toLowerCase().startsWith('es') ? 'es' : 'en'; }
      features = topojson.feature(states, states.objects.states).features.map((f) => { f.id = f.properties.id; byId[f.id] = f; return f; });
      mexicoFC = { type: 'FeatureCollection', features };
      land = topojson.feature(landTopo, landTopo.objects.land);
      S.year = D.meta.years.filter((y) => y <= 2025).slice(-1)[0];
      buildScales(); wire(); renderAll(); resize(); recolor(false);
      if (!S.motion) $('#motion-toggle').setAttribute('aria-pressed', 'true');
      if (location.hash === '#explore' || location.hash === '#explorer') focus();
      requestDraw();
    })
    .catch((err) => {
      const p = document.createElement('p'); p.className = 'noscript';
      p.textContent = 'The observatory data could not be loaded (' + err.message + '). The CSV files in /downloads contain the same data.';
      $('#observatory').appendChild(p);
    });
})();
