/* viz.js — data-driven SVG/HTML visualization primitives for concept pages.
   Each primitive is pure: viz<Kind>(el, data). Theme comes from CSS classes (app.css),
   so a theme toggle restyles them with no re-render. Static + stepped state only — no loops.
   Payloads are validated server-side (schema I25); this renders trusted data. */

const SVGNS = 'http://www.w3.org/2000/svg';
function svg(tag, attrs = {}, children = []) {
  const e = document.createElementNS(SVGNS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  for (const c of children) e.appendChild(c);
  return e;
}
function esc2(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, c => (
  { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }

/* ── truthtable — HTML table, matching columns boxed, predict/reveal toggle ── */
function vizTruthtable(el, d) {
  const inputs = d.inputs != null ? d.inputs : 2;
  const match = new Set(d.match || []);
  const wrap = document.createElement('div');
  wrap.className = 'viz-tt-wrap';
  const table = document.createElement('table');
  table.className = 'viz-tt';
  const thead = document.createElement('tr');
  d.columns.forEach((c, i) => {
    const th = document.createElement('th');
    th.innerHTML = c;
    if (match.has(i)) th.classList.add('match');
    if (i < inputs) th.classList.add('input');
    thead.appendChild(th);
  });
  table.appendChild(thead);
  d.rows.forEach(r => {
    const tr = document.createElement('tr');
    r.forEach((cell, i) => {
      const td = document.createElement('td');
      td.textContent = cell;
      td.classList.add(cell === 'T' ? 't' : cell === 'F' ? 'f' : 'o');
      if (match.has(i)) td.classList.add('match');
      if (i >= inputs) td.classList.add('output');
      tr.appendChild(td);
    });
    table.appendChild(tr);
  });
  const btn = document.createElement('button');
  btn.className = 'btn ghost sm viz-toggle';
  let hidden = false;
  btn.textContent = 'Predict (hide answers)';
  btn.onclick = () => {
    hidden = !hidden;
    wrap.classList.toggle('predicting', hidden);
    btn.textContent = hidden ? 'Reveal answers' : 'Predict (hide answers)';
  };
  wrap.appendChild(table);
  wrap.appendChild(btn);
  el.appendChild(wrap);
  renderMathIn(table);
}

/* ── proofsteps — annotated model proof: each line + why it earns the mark ─── */
function vizProofsteps(el, d) {
  const wrap = document.createElement('div');
  wrap.className = 'proofsteps-wrap';
  if (d.claim) {
    const c = document.createElement('div');
    c.className = 'ps-claim';
    c.innerHTML = '<span class="lbl">Claim</span>' + d.claim;
    wrap.appendChild(c);
  }
  const ol = document.createElement('ol');
  ol.className = 'proofsteps';
  d.steps.forEach(s => {
    const li = document.createElement('li');
    const line = document.createElement('div');
    line.className = 'ps-line';
    line.innerHTML = s.line;
    li.appendChild(line);
    if (s.tag || s.mark) {
      const tag = document.createElement('div');
      tag.className = 'ps-tag';
      tag.innerHTML = (s.tag || '') + (s.mark ? `<span class="ps-mark">${esc2(s.mark)}</span>` : '');
      li.appendChild(tag);
    }
    ol.appendChild(li);
  });
  wrap.appendChild(ol);
  const btn = document.createElement('button');
  btn.className = 'btn ghost sm viz-toggle';
  let hidden = false;
  btn.textContent = 'Hide the lines — write them yourself';
  btn.onclick = () => {
    hidden = !hidden;
    wrap.classList.toggle('drilling', hidden);
    btn.textContent = hidden ? 'Show the model proof' : 'Hide the lines — write them yourself';
  };
  wrap.appendChild(btn);
  el.appendChild(wrap);
  renderMathIn(wrap);
}

/* ── reftable — reference table with predict/reveal (hide answer columns) ──── */
function vizReftable(el, d) {
  const hide = new Set(d.hide || []);
  const wrap = document.createElement('div');
  wrap.className = 'viz-tt-wrap';
  const scroll = document.createElement('div');
  scroll.className = 'viz-scroll';
  const table = document.createElement('table');
  table.className = 'viz-ref';
  const thead = document.createElement('tr');
  d.columns.forEach((c, i) => {
    const th = document.createElement('th');
    th.innerHTML = c;
    if (hide.has(i)) th.classList.add('answer');
    thead.appendChild(th);
  });
  table.appendChild(thead);
  d.rows.forEach(r => {
    const tr = document.createElement('tr');
    r.forEach((cell, i) => {
      const td = document.createElement('td');
      td.innerHTML = cell;
      if (i === 0) td.classList.add('rowhead');
      if (hide.has(i)) td.classList.add('answer');
      tr.appendChild(td);
    });
    table.appendChild(tr);
  });
  scroll.appendChild(table);
  wrap.appendChild(scroll);
  if (hide.size) {
    const btn = document.createElement('button');
    btn.className = 'btn ghost sm viz-toggle';
    let hidden = false;
    btn.textContent = 'Predict (hide conditions)';
    btn.onclick = () => {
      hidden = !hidden;
      wrap.classList.toggle('predicting', hidden);
      btn.textContent = hidden ? 'Reveal conditions' : 'Predict (hide conditions)';
    };
    wrap.appendChild(btn);
  }
  el.appendChild(wrap);
  renderMathIn(table);
}

/* ── venn — 2 (full) or 3 (outlines + single-set) sets, shaded regions ─────── */
function vizVenn(el, d) {
  const n = d.sets.length;
  const shaded = new Set(d.shaded || []);
  const W = 460, H = 250;
  const s = svg('svg', { viewBox: `0 0 ${W} ${H}`, class: 'viz-svg venn', role: 'img' });
  const defs = svg('defs');
  s.appendChild(defs);
  const rect = () => svg('rect', { x: 0, y: 0, width: W, height: H, fill: 'white' });

  if (n === 2) {
    const A = { cx: 185, cy: 125, r: 92 }, B = { cx: 275, cy: 125, r: 92 };
    // masks
    const mk = (id, keep, cut) => {
      const m = svg('mask', { id });
      m.appendChild(rect());
      keep.forEach(c => m.appendChild(svg('circle', { cx: c.cx, cy: c.cy, r: c.r, fill: 'white' })));
      cut.forEach(c => m.appendChild(svg('circle', { cx: c.cx, cy: c.cy, r: c.r, fill: 'black' })));
      defs.appendChild(m);
    };
    mk('m-onlyA', [A], [B]); mk('m-onlyB', [B], [A]);
    const cp = svg('clipPath', { id: 'cp-B' }); cp.appendChild(svg('circle', { cx: B.cx, cy: B.cy, r: B.r })); defs.appendChild(cp);
    // outside
    if (shaded.has('U')) {
      const m = svg('mask', { id: 'm-out' }); m.appendChild(rect());
      m.appendChild(svg('circle', { cx: A.cx, cy: A.cy, r: A.r, fill: 'black' }));
      m.appendChild(svg('circle', { cx: B.cx, cy: B.cy, r: B.r, fill: 'black' }));
      defs.appendChild(m);
      s.appendChild(svg('rect', { x: 0, y: 0, width: W, height: H, class: 'venn-fill', mask: 'url(#m-out)' }));
    }
    if (shaded.has('A')) s.appendChild(svg('circle', { cx: A.cx, cy: A.cy, r: A.r, class: 'venn-fill', mask: 'url(#m-onlyA)' }));
    if (shaded.has('B')) s.appendChild(svg('circle', { cx: B.cx, cy: B.cy, r: B.r, class: 'venn-fill', mask: 'url(#m-onlyB)' }));
    if (shaded.has('AB')) s.appendChild(svg('circle', { cx: A.cx, cy: A.cy, r: A.r, class: 'venn-fill', 'clip-path': 'url(#cp-B)' }));
    s.appendChild(svg('circle', { cx: A.cx, cy: A.cy, r: A.r, class: 'venn-outline' }));
    s.appendChild(svg('circle', { cx: B.cx, cy: B.cy, r: B.r, class: 'venn-outline' }));
    s.appendChild(label(120, 60, d.sets[0])); s.appendChild(label(340, 60, d.sets[1]));
  } else {
    // 3 sets: single circles + pairwise/triple overlaps via nested clipPaths (intersection).
    const c = { A: { cx: 190, cy: 100, r: 82 }, B: { cx: 270, cy: 100, r: 82 }, C: { cx: 230, cy: 165, r: 82 } };
    for (const k of "ABC") {
      const cp = svg('clipPath', { id: 'cp3-' + k });
      cp.appendChild(svg('circle', { cx: c[k].cx, cy: c[k].cy, r: c[k].r }));
      defs.appendChild(cp);
    }
    const fill = (extra = {}) => svg('circle', { cx: c.A.cx, cy: c.A.cy, r: c.A.r, class: 'venn-fill', ...extra });
    shaded.forEach(id => {
      if (id.length === 1) {
        s.appendChild(svg('circle', { cx: c[id].cx, cy: c[id].cy, r: c[id].r, class: 'venn-fill' }));
      } else if (id.length === 2) {  // pairwise intersection = one circle clipped by the other
        s.appendChild(svg('circle', { cx: c[id[0]].cx, cy: c[id[0]].cy, r: c[id[0]].r, class: 'venn-fill', 'clip-path': `url(#cp3-${id[1]})` }));
      } else if (id === 'ABC') {      // triple = A clipped by B, inside a group clipped by C
        const g = svg('g', { 'clip-path': 'url(#cp3-C)' });
        g.appendChild(svg('circle', { cx: c.A.cx, cy: c.A.cy, r: c.A.r, class: 'venn-fill', 'clip-path': 'url(#cp3-B)' }));
        s.appendChild(g);
      }
    });
    for (const k of "ABC") s.appendChild(svg('circle', { cx: c[k].cx, cy: c[k].cy, r: c[k].r, class: 'venn-outline' }));
    s.appendChild(label(135, 55, d.sets[0])); s.appendChild(label(325, 55, d.sets[1])); s.appendChild(label(230, 240, d.sets[2]));
  }
  el.appendChild(s);
  function label(x, y, t) { const e = svg('text', { x, y, class: 'venn-label' }); e.textContent = t; return e; }
}

/* ── mapping — two columns of dots + arrows; variant switcher ──────────────── */
function vizMapping(el, d) {
  const variants = d.variants || [{ label: '', maps: d.maps || [] }];
  const W = 420, H = Math.max(d.domain.length, d.codomain.length) * 56 + 30;
  const s = svg('svg', { viewBox: `0 0 ${W} ${H}`, class: 'viz-svg mapping' });
  defsArrow(s);
  const xL = 120, xR = 300;
  const yOf = (i, n) => 40 + i * ((H - 60) / Math.max(1, n - 1 || 1));
  const domPts = d.domain.map((_, i) => ({ x: xL, y: yOf(i, d.domain.length) }));
  const codPts = d.codomain.map((_, i) => ({ x: xR, y: yOf(i, d.codomain.length) }));
  const gArrows = svg('g', { class: 'map-arrows' });
  s.appendChild(gArrows);
  d.domain.forEach((t, i) => { s.appendChild(dot(domPts[i], t, 'left')); });
  d.codomain.forEach((t, i) => { s.appendChild(dot(codPts[i], t, 'right')); });
  s.appendChild(txt(xL, 22, 'Domain')); s.appendChild(txt(xR, 22, 'Codomain'));

  const draw = (vi) => {
    gArrows.replaceChildren();
    variants[vi].maps.forEach(m => {
      const a = domPts[m[0]], b = codPts[m[1]];
      gArrows.appendChild(svg('line', { x1: a.x + 12, y1: a.y, x2: b.x - 12, y2: b.y, class: 'map-arrow', 'marker-end': 'url(#arrow)' }));
    });
  };
  const wrap = document.createElement('div');
  wrap.className = 'viz-mapping-wrap';
  wrap.appendChild(s);
  if (variants.length > 1 || variants[0].label) {
    const bar = document.createElement('div'); bar.className = 'viz-variants';
    variants.forEach((v, i) => {
      const b = document.createElement('button');
      b.className = 'viz-variant' + (i === 0 ? ' sel' : '');
      b.textContent = v.label || `Variant ${i + 1}`;
      b.onclick = () => { bar.querySelectorAll('.viz-variant').forEach(x => x.classList.remove('sel')); b.classList.add('sel'); draw(i); };
      bar.appendChild(b);
    });
    wrap.appendChild(bar);
  }
  el.appendChild(wrap);
  draw(0);
  function dot(p, t, side) {
    const g = svg('g');
    g.appendChild(svg('circle', { cx: p.x, cy: p.y, r: 8, class: 'map-dot' }));
    const e = svg('text', { x: side === 'left' ? p.x - 20 : p.x + 20, y: p.y + 4, class: 'map-dot-label ' + side });
    e.textContent = t; g.appendChild(e); return g;
  }
  function txt(x, y, t) { const e = svg('text', { x, y, class: 'viz-col-head' }); e.textContent = t; return e; }
}

/* ── flow — layered left→right DAG; foreignObject node labels ──────────────── */
function vizFlow(el, d) {
  const nodes = Object.fromEntries(d.nodes.map(n => [n.id, { ...n }]));
  const outEdges = {};
  d.nodes.forEach(n => (outEdges[n.id] = []));
  d.edges.forEach(e => outEdges[e.from].push(e));
  // depth = longest path from start
  const depth = {};
  const start = d.start || d.nodes[0].id;
  (function dfs(id, dp, seen) {
    if (seen.has(id)) return;
    depth[id] = Math.max(depth[id] || 0, dp);
    outEdges[id].forEach(e => dfs(e.to, dp + 1, new Set(seen).add(id)));
  })(start, 0, new Set());
  d.nodes.forEach(n => { if (depth[n.id] == null) depth[n.id] = 0; });
  const byDepth = {};
  d.nodes.forEach(n => (byDepth[depth[n.id]] = byDepth[depth[n.id]] || []).push(n.id));
  const cols = Math.max(...Object.keys(byDepth).map(Number)) + 1;
  const NW = 150, NH = 62, GX = 44, GY = 26;
  const rows = Math.max(...Object.values(byDepth).map(a => a.length));
  const W = cols * NW + (cols - 1) * GX + 20;
  const H = rows * NH + (rows - 1) * GY + 20;
  const pos = {};
  Object.entries(byDepth).forEach(([dp, ids]) => {
    const colH = ids.length * NH + (ids.length - 1) * GY;
    const y0 = (H - colH) / 2;
    ids.forEach((id, i) => { pos[id] = { x: 10 + dp * (NW + GX), y: y0 + i * (NH + GY) }; });
  });
  const s = svg('svg', { viewBox: `0 0 ${W} ${H}`, class: 'viz-svg flow' });
  defsArrow(s);
  // edges
  d.edges.forEach(e => {
    const a = pos[e.from], b = pos[e.to];
    const x1 = a.x + NW, y1 = a.y + NH / 2, x2 = b.x, y2 = b.y + NH / 2;
    const mx = (x1 + x2) / 2;
    s.appendChild(svg('path', { d: `M ${x1} ${y1} C ${mx} ${y1}, ${mx} ${y2}, ${x2} ${y2}`, class: 'flow-edge', 'marker-end': 'url(#arrow)' }));
    if (e.label) {
      const t = svg('text', { x: mx, y: (y1 + y2) / 2 - 4, class: 'flow-edge-label' });
      t.textContent = e.label; s.appendChild(t);
    }
  });
  // nodes
  d.nodes.forEach(n => {
    const p = pos[n.id];
    const fo = svg('foreignObject', { x: p.x, y: p.y, width: NW, height: NH });
    const div = document.createElement('div');
    div.className = 'flow-node ' + (n.kind === 'leaf' ? 'leaf' : 'decision');
    div.textContent = n.label;
    fo.appendChild(div);
    s.appendChild(fo);
  });
  const scroll = document.createElement('div');
  scroll.className = 'viz-scroll';
  scroll.appendChild(s);
  el.appendChild(scroll);
}

/* ── pascal — binomial triangle; hover a cell to see its two parents ───────── */
function vizPascal(el, d) {
  const rows = d.rows;
  const tri = [];
  for (let n = 0; n < rows; n++) {
    tri.push([]);
    for (let k = 0; k <= n; k++) tri[n].push(k === 0 || k === n ? 1 : tri[n - 1][k - 1] + tri[n - 1][k]);
  }
  const cell = 46, W = rows * cell + 70, H = rows * cell + 30;
  const s = svg('svg', { viewBox: `0 0 ${W} ${H}`, class: 'viz-svg pascal' });
  const cells = [];
  for (let n = 0; n < rows; n++) for (let k = 0; k <= n; k++) {
    const x = (W - 60) / 2 - (n * cell) / 2 + k * cell, y = 24 + n * cell;
    const g = svg('g', { class: 'pascal-cell' });
    g.appendChild(svg('circle', { cx: x, cy: y, r: 19, class: 'pascal-node' }));
    const t = svg('text', { x, y: y + 5, class: 'pascal-num' }); t.textContent = tri[n][k];
    g.appendChild(t); s.appendChild(g);
    cells.push({ g, n, k, x, y });
  }
  // row-sum overlay (2^n) toggle
  const sums = svg('g', { class: 'pascal-sums', style: 'display:none' });
  for (let n = 0; n < rows; n++) {
    const y = 24 + n * cell;
    const t = svg('text', { x: W - 46, y: y + 5, class: 'pascal-sum' }); t.textContent = '= ' + (2 ** n);
    sums.appendChild(t);
  }
  s.appendChild(sums);
  cells.forEach(c => {
    c.g.addEventListener('mouseenter', () => {
      cells.forEach(o => o.g.classList.remove('hi', 'parent'));
      c.g.classList.add('hi');
      if (c.n > 0) cells.filter(o => o.n === c.n - 1 && (o.k === c.k - 1 || o.k === c.k)).forEach(o => o.g.classList.add('parent'));
    });
    c.g.addEventListener('mouseleave', () => cells.forEach(o => o.g.classList.remove('hi', 'parent')));
  });
  const wrap = document.createElement('div'); wrap.className = 'viz-tt-wrap';
  wrap.appendChild(wrapScroll(s));
  const btn = document.createElement('button'); btn.className = 'btn ghost sm viz-toggle';
  let on = false; btn.textContent = 'Show row sums (2ⁿ)';
  btn.onclick = () => { on = !on; sums.setAttribute('style', on ? '' : 'display:none'); btn.textContent = on ? 'Hide row sums' : 'Show row sums (2ⁿ)'; };
  wrap.appendChild(btn);
  el.appendChild(wrap);
}

/* ── gridpaths — lattice grid, paths (R/U words), optional diagonal ────────── */
function vizGridpaths(el, d) {
  const W = d.width, Hh = d.height, cell = 42, pad = 26;
  const sw = W * cell + 2 * pad, sh = Hh * cell + 2 * pad;
  const X = i => pad + i * cell, Y = j => sh - pad - j * cell;
  const s = svg('svg', { viewBox: `0 0 ${sw} ${sh}`, class: 'viz-svg gridpaths' });
  for (let i = 0; i <= W; i++) s.appendChild(svg('line', { x1: X(i), y1: Y(0), x2: X(i), y2: Y(Hh), class: 'grid-line' }));
  for (let j = 0; j <= Hh; j++) s.appendChild(svg('line', { x1: X(0), y1: Y(j), x2: X(W), y2: Y(j), class: 'grid-line' }));
  if (d.diagonal) { const m = Math.min(W, Hh); s.appendChild(svg('line', { x1: X(0), y1: Y(0), x2: X(m), y2: Y(m), class: 'diag-line' })); }
  const gPath = svg('g'); s.appendChild(gPath);
  const paths = d.paths || [];
  const draw = pi => {
    gPath.replaceChildren();
    let i = 0, j = 0; const pts = [[X(0), Y(0)]];
    for (const st of paths[pi].steps) { if (st === 'R') i++; else j++; pts.push([X(i), Y(j)]); }
    gPath.appendChild(svg('polyline', { points: pts.map(p => p.join(',')).join(' '),
      class: 'path-line' + (paths[pi].valid === false ? ' bad' : '') }));
  };
  const wrap = document.createElement('div'); wrap.className = 'viz-mapping-wrap';
  wrap.appendChild(wrapScroll(s));
  if (paths.length > 1) {
    const bar = document.createElement('div'); bar.className = 'viz-variants';
    paths.forEach((p, i) => {
      const b = document.createElement('button');
      b.className = 'viz-variant' + (i === 0 ? ' sel' : '');
      b.textContent = p.label || `Path ${i + 1}`;
      b.onclick = () => { bar.querySelectorAll('.viz-variant').forEach(x => x.classList.remove('sel')); b.classList.add('sel'); draw(i); };
      bar.appendChild(b);
    });
    wrap.appendChild(bar);
  }
  el.appendChild(wrap); if (paths.length) draw(0);
}

/* ── plot — (x,y) points/lines on axes; horizontal asymptote; view switcher ── */
function vizPlot(el, d) {
  const views = d.views || [{ series: d.series || [], asymptote: d.asymptote }];
  const W = 480, H = 300, padL = 46, padR = 14, padT = 14, padB = 36;
  const s = svg('svg', { viewBox: `0 0 ${W} ${H}`, class: 'viz-svg plot' });
  const gPlot = svg('g'); s.appendChild(gPlot);
  const legend = document.createElement('div'); legend.className = 'plot-legend';
  const fmt = v => (Math.abs(v) >= 1000 || (v !== 0 && Math.abs(v) < 0.01)) ? v.toExponential(0)
    : (Number.isInteger(v) ? String(v) : v.toFixed(2).replace(/0+$/, '').replace(/\.$/, ''));

  const draw = vi => {
    gPlot.replaceChildren();
    const v = views[vi];
    // bounds for THIS view (each example gets an honest frame)
    let xs = [], ys = [];
    v.series.forEach(se => se.points.forEach(p => { xs.push(p[0]); ys.push(p[1]); }));
    if (v.asymptote) ys.push(v.asymptote.y);
    let xmin = Math.min(...xs), xmax = Math.max(...xs);
    let ymin = Math.min(...ys), ymax = Math.max(...ys);
    const yr = (ymax - ymin) || 1; ymin -= yr * 0.12; ymax += yr * 0.12;
    if (ymin > 0) ymin = 0; if (ymax < 0) ymax = 0;               // keep zero line in view
    const px = x => padL + (x - xmin) / ((xmax - xmin) || 1) * (W - padL - padR);
    const py = y => H - padB - (y - ymin) / ((ymax - ymin) || 1) * (H - padT - padB);
    const baseY = (ymin <= 0 && ymax >= 0) ? 0 : ymin;
    // axes
    gPlot.appendChild(svg('line', { x1: padL, y1: padT, x2: padL, y2: H - padB, class: 'plot-axis' }));
    gPlot.appendChild(svg('line', { x1: padL, y1: py(baseY), x2: W - padR, y2: py(baseY), class: 'plot-axis' }));
    // x ticks — integer marks across the domain
    for (let t = Math.ceil(xmin); t <= Math.floor(xmax); t++) {
      if (xmax - xmin > 12 && t % 2) continue;
      gPlot.appendChild(txt(px(t), H - padB + 15, fmt(t), 'plot-tick'));
    }
    // y ticks — bottom + top of frame
    [ymin, ymax].forEach(t => gPlot.appendChild(txt(padL - 6, py(t) + 4, fmt(t), 'plot-tick end')));
    if (baseY !== ymin && baseY !== ymax) gPlot.appendChild(txt(padL - 6, py(baseY) + 4, '0', 'plot-tick end'));
    // asymptote (the limit / sum the terms approach)
    if (v.asymptote) {
      gPlot.appendChild(svg('line', { x1: padL, y1: py(v.asymptote.y), x2: W - padR, y2: py(v.asymptote.y), class: 'plot-asymptote' }));
      if (v.asymptote.label) gPlot.appendChild(txt(W - padR, py(v.asymptote.y) - 6, v.asymptote.label, 'plot-asym-label'));
    }
    // series
    v.series.forEach(se => {
      const cls = se.cls || 'good';
      if ((se.kind || 'points') === 'line') {
        gPlot.appendChild(svg('polyline', { points: se.points.map(p => `${px(p[0])},${py(p[1])}`).join(' '), class: 'plot-series ' + cls }));
      } else {
        se.points.forEach(p => gPlot.appendChild(svg('circle', { cx: px(p[0]), cy: py(p[1]), r: 3.4, class: 'plot-pt ' + cls })));
      }
    });
    // labels
    if (d.xlabel) gPlot.appendChild(txt((padL + W - padR) / 2, H - 4, d.xlabel, 'plot-axis-label'));
    // legend
    legend.replaceChildren();
    v.series.forEach(se => {
      const sw = document.createElement('span');
      sw.innerHTML = `<i class="${se.cls || 'good'}"></i>${esc2(se.label || '')}`;
      legend.appendChild(sw);
    });
    renderMathIn(legend);
  };
  const wrap = document.createElement('div'); wrap.className = 'viz-mapping-wrap';
  wrap.appendChild(wrapScroll(s));
  wrap.appendChild(legend);
  if (views.length > 1) {
    const bar = document.createElement('div'); bar.className = 'viz-variants';
    views.forEach((v, i) => {
      const b = document.createElement('button');
      b.className = 'viz-variant' + (i === 0 ? ' sel' : '');
      b.innerHTML = v.label || `View ${i + 1}`;
      b.onclick = () => { bar.querySelectorAll('.viz-variant').forEach(x => x.classList.remove('sel')); b.classList.add('sel'); draw(i); };
      bar.appendChild(b);
    });
    wrap.appendChild(bar);
    renderMathIn(bar);
  }
  el.appendChild(wrap);
  draw(0);
  function txt(x, y, t, cls) { const e = svg('text', { x, y, class: cls }); e.textContent = t; return e; }
}

/* ── numberline — intervals with open/closed ends; radius/interval switcher ── */
function vizNumberline(el, d) {
  const views = d.views || [{ intervals: d.intervals || [], points: d.points || [] }];
  const min = d.min, max = d.max, W = 480, H = 96, pad = 34, axisY = 52;
  const px = x => pad + (Math.max(min, Math.min(max, x)) - min) / ((max - min) || 1) * (W - 2 * pad);
  const s = svg('svg', { viewBox: `0 0 ${W} ${H}`, class: 'viz-svg numberline' });
  defsArrow(s);
  const gView = svg('g'); s.appendChild(gView);
  const note = document.createElement('div'); note.className = 'cap';
  // fixed axis + ticks (shared across views)
  s.insertBefore(mkAxis(), gView);
  function mkAxis() {
    const g = svg('g');
    g.appendChild(svg('line', { x1: pad - 8, y1: axisY, x2: W - pad + 8, y2: axisY, class: 'nl-axis', 'marker-start': 'url(#arrow)', 'marker-end': 'url(#arrow)' }));
    (d.ticks || []).forEach(t => {
      g.appendChild(svg('line', { x1: px(t), y1: axisY - 4, x2: px(t), y2: axisY + 4, class: 'nl-tick' }));
      const e = svg('text', { x: px(t), y: axisY + 18, class: 'nl-tick-label' }); e.textContent = t;
      g.appendChild(e);
    });
    return g;
  }
  const draw = vi => {
    gView.replaceChildren();
    const v = views[vi];
    note.innerHTML = v.note || '';
    if (v.note) renderMathIn(note);
    (v.intervals || []).forEach(iv => {
      const cls = iv.cls || 'good';
      const x1 = px(iv.lo), x2 = px(iv.hi);
      gView.appendChild(svg('line', { x1, y1: axisY, x2, y2: axisY, class: 'nl-band ' + cls,
        ...(iv.arrowLo ? { 'marker-start': 'url(#arrow)' } : {}), ...(iv.arrowHi ? { 'marker-end': 'url(#arrow)' } : {}) }));
      if (!iv.arrowLo) gView.appendChild(endpoint(x1, cls, iv.loOpen));
      if (!iv.arrowHi) gView.appendChild(endpoint(x2, cls, iv.hiOpen));
      if (iv.label) { const e = svg('text', { x: (x1 + x2) / 2, y: axisY - 12, class: 'nl-label' }); e.textContent = iv.label; gView.appendChild(e); }
    });
    (v.points || []).forEach(p => {
      gView.appendChild(svg('circle', { cx: px(p.x), cy: axisY, r: 5, class: 'nl-endpoint closed ' + (p.cls || 'center') }));
      if (p.label) { const e = svg('text', { x: px(p.x), y: axisY - 12, class: 'nl-label' }); e.textContent = p.label; gView.appendChild(e); }
    });
  };
  function endpoint(x, cls, open) {
    return svg('circle', { cx: x, cy: axisY, r: 5, class: 'nl-endpoint ' + (open ? 'open ' : 'closed ') + cls });
  }
  const wrap = document.createElement('div'); wrap.className = 'viz-mapping-wrap';
  wrap.appendChild(wrapScroll(s));
  if (views.length > 1) {
    const bar = document.createElement('div'); bar.className = 'viz-variants';
    views.forEach((v, i) => {
      const b = document.createElement('button');
      b.className = 'viz-variant' + (i === 0 ? ' sel' : '');
      b.innerHTML = v.label || `Case ${i + 1}`;
      b.onclick = () => { bar.querySelectorAll('.viz-variant').forEach(x => x.classList.remove('sel')); b.classList.add('sel'); draw(i); };
      bar.appendChild(b);
    });
    wrap.appendChild(bar);
    renderMathIn(bar);
  }
  wrap.appendChild(note);
  el.appendChild(wrap);
  draw(0);
}

function wrapScroll(s) { const d = document.createElement('div'); d.className = 'viz-scroll'; d.appendChild(s); return d; }

function defsArrow(s) {
  const defs = svg('defs');
  const m = svg('marker', { id: 'arrow', viewBox: '0 0 10 10', refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: 'auto-start-reverse' });
  m.appendChild(svg('path', { d: 'M 0 1 L 9 5 L 0 9 z', class: 'arrowhead' }));
  defs.appendChild(m); s.appendChild(defs);
}
function renderMathIn(node) { if (window.renderMathInElement) { try { renderMathInElement(node, { delimiters: [{ left: '$', right: '$', display: false }], throwOnError: false, macros: window.KATEX_MACROS || {} }); } catch (e) { } } }

const VIZ = { truthtable: vizTruthtable, venn: vizVenn, mapping: vizMapping, flow: vizFlow,
              pascal: vizPascal, gridpaths: vizGridpaths, plot: vizPlot, numberline: vizNumberline,
              reftable: vizReftable, proofsteps: vizProofsteps };
function renderViz(el, kind, data) {
  el.classList.add('viz-block');
  const fn = VIZ[kind];
  if (!fn) { el.innerHTML = `<div class="empty">viz “${esc2(kind)}” not available yet</div>`; return; }
  try { fn(el, data); } catch (e) { el.innerHTML = `<div class="empty">viz render error</div>`; }
}
window.renderViz = renderViz;
