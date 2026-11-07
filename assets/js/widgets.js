/* Physical AI and SciML explorers. Numerical cores are in core.js (window.SCIML). All data are synthetic teaching data. */
(function () {
  "use strict";
  const NS = "http://www.w3.org/2000/svg";
  const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  const fmt = (x, d = 0) => (isFinite(x) ? Number(x).toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d }) : "–");
  const h = (tag, attrs = {}, ...kids) => {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === "class") e.className = v; else if (k === "html") e.innerHTML = v;
      else if (k.startsWith("on")) e.addEventListener(k.slice(2), v); else e.setAttribute(k, v);
    }
    kids.flat().forEach((c) => c != null && e.append(c.nodeType ? c : document.createTextNode(c)));
    return e;
  };
  function slider(label, { min, max, step = 1, value, unit = "", digits = 0, hint }, onChange) {
    const out = h("output");
    const inp = h("input", { type: "range", min, max, step, value, "aria-label": label });
    const show = () => (out.textContent = fmt(+inp.value, digits) + unit);
    inp.addEventListener("input", () => { show(); onChange(); });
    show();
    const wrap = h("div", { class: "ctrl" }, h("label", {}, h("span", {}, label), out), inp, hint ? h("div", { class: "hint" }, hint) : null);
    wrap.get = () => +inp.value; wrap.set = (v) => { inp.value = v; show(); };
    return wrap;
  }
  function select(label, options, value, onChange) {
    const s = h("select", { "aria-label": label }, options.map(([v, t]) => h("option", { value: v }, t)));
    s.value = value; s.addEventListener("change", onChange);
    const wrap = h("div", { class: "ctrl" }, h("label", {}, h("span", {}, label)), s);
    wrap.get = () => s.value; return wrap;
  }
  function readout(items) {
    const box = h("div", { class: "readout" });
    const cells = items.map(([k, label]) => { const b = h("b"); const d = h("div", {}, b, h("span", {}, label)); box.append(d); return [k, b, d]; });
    box.set = (k, v, hot) => { const c = cells.find((x) => x[0] === k); if (c) { c[1].textContent = v; c[2].classList.toggle("hot", !!hot); } };
    return box;
  }
  function layout(el, controls, view, intro) {
    el.innerHTML = "";
    const w = h("div", { class: "widget" });
    if (intro) w.append(h("p", { class: "muted" }, intro));
    w.append(h("div", { class: "wgrid" }, h("div", {}, controls), h("div", {}, view)));
    el.append(w);
    return w;
  }
  // ---- SVG charts ----
  function svg(w, hgt) { const s = document.createElementNS(NS, "svg"); s.setAttribute("viewBox", `0 0 ${w} ${hgt}`); s.setAttribute("class", "chart"); s.setAttribute("role", "img"); return s; }
  function el(tag, attrs, parent) { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.append(e); return e; }
  function niceMax(v) { if (v <= 0) return 1; const p = Math.pow(10, Math.floor(Math.log10(v))); const m = v / p; return (m <= 1 ? 1 : m <= 2 ? 2 : m <= 2.5 ? 2.5 : m <= 5 ? 5 : 10) * p; }
  function colors() { return [css("--c1"), css("--c2"), css("--c3"), css("--c4")]; }
  /** line chart: xs numeric, series [{name, values, color, dash}] */
  function lineChart(target, { xs, series, xTitle, yTitle, yMax, yMin = 0, label, vline, hline, area }) {
    const W = 640, H = 340, L = 58, R = 16, T = 16, B = 46;
    const s = svg(W, H); if (label) s.setAttribute("aria-label", label);
    const all = series.flatMap((x) => x.values).filter(isFinite);
    const top = yMax != null ? yMax : niceMax(Math.max(...all, hline ? hline.y : 0) * 1.05);
    const x0 = xs[0], x1 = xs[xs.length - 1];
    const X = (x) => L + ((x - x0) / (x1 - x0 || 1)) * (W - L - R), Y = (y) => T + (1 - (y - yMin) / (top - yMin)) * (H - T - B);
    const g = el("g", { class: "grid" }, s);
    for (let i = 0; i <= 4; i++) { const v = yMin + ((top - yMin) * i) / 4; el("line", { x1: L, x2: W - R, y1: Y(v), y2: Y(v) }, g); const t = el("text", { x: L - 8, y: Y(v) + 4, "text-anchor": "end" }, s); t.textContent = fmt(v, top - yMin < 5 ? 1 : 0); }
    const ticks = 6; for (let i = 0; i <= ticks; i++) { const v = x0 + ((x1 - x0) * i) / ticks; const t = el("text", { x: X(v), y: H - B + 18, "text-anchor": "middle" }, s); t.textContent = x0 >= 1800 && x1 <= 2300 ? String(Math.round(v)) : fmt(v, Math.abs(x1 - x0) < 10 ? 1 : 0); }
    el("line", { x1: L, x2: W - R, y1: Y(yMin), y2: Y(yMin), class: "axis" }, s);
    if (xTitle) { const t = el("text", { x: (L + W - R) / 2, y: H - 6, "text-anchor": "middle", class: "ttl" }, s); t.textContent = xTitle; }
    if (yTitle) { const t = el("text", { x: 14, y: (T + H - B) / 2, "text-anchor": "middle", transform: `rotate(-90 14 ${(T + H - B) / 2})`, class: "ttl" }, s); t.textContent = yTitle; }
    const cs = colors();
    if (hline) { el("line", { x1: L, x2: W - R, y1: Y(hline.y), y2: Y(hline.y), stroke: css("--orange"), "stroke-dasharray": "6 5", "stroke-width": 2 }, s); const t = el("text", { x: W - R - 4, y: Y(hline.y) - 6, "text-anchor": "end" }, s); t.textContent = hline.label; t.style.fill = css("--orange"); }
    if (vline) { el("line", { x1: X(vline.x), x2: X(vline.x), y1: T, y2: H - B, stroke: css("--muted"), "stroke-dasharray": "4 4" }, s); const t = el("text", { x: X(vline.x) + 4, y: T + 12 }, s); t.textContent = vline.label; }
    series.forEach((se, i) => {
      const c = se.color || cs[i % 4];
      const pts = xs.map((x, j) => [X(x), Y(Math.max(yMin, Math.min(top, se.values[j])))]).filter((p, j) => isFinite(se.values[j]));
      if (area && i === 0) el("path", { d: `M${pts[0][0]},${Y(yMin)} ` + pts.map((p) => `L${p[0]},${p[1]}`).join(" ") + ` L${pts[pts.length - 1][0]},${Y(yMin)} Z`, fill: c, opacity: 0.15 }, s);
      el("path", { d: pts.map((p, k) => (k ? "L" : "M") + p[0] + "," + p[1]).join(" "), fill: "none", stroke: c, "stroke-width": 3, "stroke-dasharray": se.dash || "", "stroke-linejoin": "round" }, s);
    });
    target.innerHTML = "";
    if (series.length > 1) target.append(legend(series));
    target.append(s);
  }
  function barChart(target, { labels, values, colorsFor, yTitle, yMax, digits = 0, label, suffix = "" }) {
    const W = 640, H = 300, L = 58, R = 16, T = 24, B = 40;
    const s = svg(W, H); if (label) s.setAttribute("aria-label", label);
    const top = yMax != null ? yMax : niceMax(Math.max(...values, 0) * 1.1);
    const Y = (y) => T + (1 - y / top) * (H - T - B);
    const g = el("g", { class: "grid" }, s);
    for (let i = 0; i <= 4; i++) { const v = (top * i) / 4; el("line", { x1: L, x2: W - R, y1: Y(v), y2: Y(v) }, g); const t = el("text", { x: L - 8, y: Y(v) + 4, "text-anchor": "end" }, s); t.textContent = fmt(v, top < 5 ? 1 : 0); }
    const n = values.length, bw = ((W - L - R) / n) * 0.62, cs = colors();
    values.forEach((v, i) => {
      const cx = L + ((i + 0.5) * (W - L - R)) / n, vv = Math.max(0, Math.min(top, v));
      el("rect", { x: cx - bw / 2, y: Y(vv), width: bw, height: Y(0) - Y(vv), rx: 4, fill: colorsFor ? colorsFor(i, v) : cs[0] }, s);
      const t = el("text", { x: cx, y: Y(vv) - 6, "text-anchor": "middle" }, s); t.textContent = fmt(v, digits) + suffix; t.style.fill = css("--ink"); t.style.fontWeight = 600;
      const l = el("text", { x: cx, y: H - B + 18, "text-anchor": "middle" }, s); l.textContent = labels[i];
    });
    el("line", { x1: L, x2: W - R, y1: Y(0), y2: Y(0), class: "axis" }, s);
    if (yTitle) { const t = el("text", { x: 14, y: (T + H - B) / 2, "text-anchor": "middle", transform: `rotate(-90 14 ${(T + H - B) / 2})`, class: "ttl" }, s); t.textContent = yTitle; }
    target.innerHTML = ""; target.append(s);
  }
  function legend(series) {
    const cs = colors();
    return h("div", { class: "legend" }, series.map((se, i) => h("span", {}, h("i", { style: `background:${se.color || cs[i % 4]}` }), se.name)));
  }
  const range = (a, b, step = 1) => { const r = []; for (let x = a; x <= b + 1e-9; x += step) r.push(+x.toFixed(6)); return r; };

  // ---- general plot: lines, scatter points, an uncertainty band, any y range
  function plot(target, { xs, series = [], points = [], band, xTitle, yTitle, yMin, yMax, hline, vline, label, logy }) {
    const W0 = 640, H = 340, L = 60, R = 16, T = 16, B = 46, s = svg(W0, H); if (label) s.setAttribute("aria-label", label);
    const tf = (v) => (logy ? Math.log10(Math.max(v, 1e-12)) : v);
    const vals = series.flatMap((x) => x.values).concat(points.flatMap((p) => p.ys)).concat(band ? band.lo.concat(band.hi) : []).filter(isFinite).map(tf);
    let lo = yMin != null ? tf(yMin) : Math.min(...vals), hi = yMax != null ? tf(yMax) : Math.max(...vals);
    if (hline) { lo = Math.min(lo, tf(hline.y)); hi = Math.max(hi, tf(hline.y)); }
    if (hi - lo < 1e-9) { hi += 1; lo -= 1; } const pad = (hi - lo) * 0.06; if (yMin == null) lo -= pad; if (yMax == null) hi += pad;
    const allx = xs.concat(points.flatMap((p) => p.xs)), x0 = Math.min(...allx), x1 = Math.max(...allx);
    const X = (x) => L + ((x - x0) / (x1 - x0 || 1)) * (W0 - L - R), Y = (y) => T + (1 - (Math.max(lo, Math.min(hi, tf(y))) - lo) / (hi - lo)) * (H - T - B);
    const g = el("g", { class: "grid" }, s);
    for (let i = 0; i <= 4; i++) { const v = lo + ((hi - lo) * i) / 4, yy = T + (1 - i / 4) * (H - T - B); el("line", { x1: L, x2: W0 - R, y1: yy, y2: yy }, g); const t = el("text", { x: L - 8, y: yy + 4, "text-anchor": "end" }, s); t.textContent = logy ? "1e" + v.toFixed(1) : fmt(v, Math.abs(hi - lo) < 3 ? 2 : Math.abs(hi - lo) < 30 ? 1 : 0); }
    for (let i = 0; i <= 6; i++) { const v = x0 + ((x1 - x0) * i) / 6, t = el("text", { x: X(v), y: H - B + 18, "text-anchor": "middle" }, s); t.textContent = fmt(v, Math.abs(x1 - x0) < 10 ? 1 : 0); }
    if (xTitle) { const t = el("text", { x: (L + W0 - R) / 2, y: H - 6, "text-anchor": "middle", class: "ttl" }, s); t.textContent = xTitle; }
    if (yTitle) { const t = el("text", { x: 14, y: (T + H - B) / 2, "text-anchor": "middle", transform: `rotate(-90 14 ${(T + H - B) / 2})`, class: "ttl" }, s); t.textContent = yTitle; }
    const cs = colors();
    if (band) el("path", { d: xs.map((x, i) => (i ? "L" : "M") + X(x) + "," + Y(band.hi[i])).join(" ") + " " + xs.slice().reverse().map((x, j) => "L" + X(x) + "," + Y(band.lo[xs.length - 1 - j])).join(" ") + " Z", fill: band.color || cs[0], opacity: 0.18 }, s);
    if (hline) { el("line", { x1: L, x2: W0 - R, y1: Y(hline.y), y2: Y(hline.y), stroke: css("--orange"), "stroke-dasharray": "6 5", "stroke-width": 2 }, s); const t = el("text", { x: W0 - R - 4, y: Y(hline.y) - 6, "text-anchor": "end" }, s); t.textContent = hline.label; t.style.fill = css("--orange"); }
    if (vline) { el("line", { x1: X(vline.x), x2: X(vline.x), y1: T, y2: H - B, stroke: css("--muted"), "stroke-dasharray": "4 4" }, s); const t = el("text", { x: X(vline.x) + 4, y: T + 12 }, s); t.textContent = vline.label; }
    series.forEach((se, i) => { const c = se.color || cs[i % 4], sx = se.xs || xs; el("path", { d: sx.map((x, j) => (isFinite(se.values[j]) ? (j && isFinite(se.values[j - 1]) ? "L" : "M") + X(x) + "," + Y(se.values[j]) : "")).join(" "), fill: "none", stroke: c, "stroke-width": se.width || 3, "stroke-dasharray": se.dash || "", "stroke-linejoin": "round" }, s); });
    points.forEach((p) => p.xs.forEach((x, j) => el("circle", { cx: X(x), cy: Y(p.ys[j]), r: p.r || 5, fill: p.color || css("--ink"), stroke: css("--paper"), "stroke-width": 1.5 }, s)));
    target.innerHTML = "";
    const leg = series.concat(points.filter((p) => p.name).map((p) => ({ name: p.name, color: p.color || css("--ink") })));
    if (leg.length > 1) target.append(legend(leg));
    target.append(s);
  }
  const C = () => window.SCIML;
  const W = {};
  const note = (t) => h("p", { class: "note" }, t), explain = (t) => h("div", { class: "explain", html: t });
  const pct = (x) => fmt(100 * x, 0) + "%";

  // 1.1 the physics–data spectrum
  W.spectrum = (root) => {
    const chart = h("div"), out = readout([["in", "Error where we have data (t ≤ 2)"], ["out", "Error when predicting ahead (t > 2)"], ["kind", "This model is"]]);
    const w = slider("Trust in physics", { min: 0, max: 1, step: 0.05, value: 0, digits: 2, hint: "0 = pure data fit, 1 = pure physics model" }, draw);
    const n = slider("Data points (all in 0 ≤ t ≤ 2)", { min: 4, max: 20, value: 8 }, draw);
    function draw() {
      const r = C().spectrum({ w: w.get(), n: n.get() });
      out.set("in", fmt(r.errIn, 3)); out.set("out", fmt(r.errOut, 3), r.errOut > 0.3); out.set("kind", w.get() < 0.2 ? "data-driven" : w.get() > 0.8 ? "physics-based" : "hybrid");
      plot(chart, { xs: r.ts, series: [{ name: "What really happens", values: r.truth, color: css("--muted"), dash: "6 5" }, { name: "Model prediction", values: r.pred }], points: [{ xs: r.data[0], ys: r.data[1], name: "Measurements" }], vline: { x: 2, label: "data stop here" }, xTitle: "time t (s)", yTitle: "displacement", yMin: -1.2, yMax: 1.2, label: "physics versus data" });
    }
    layout(root, [w, n, explain("A pure data fit (a polynomial) matches the measurements but goes wild beyond them. A physics model with slightly wrong parameters extrapolates well but misses details. <b>Scientific machine learning</b> sits in between: it uses both.")], [out, chart, note("Truth: a damped oscillator. The physics model has a 15% error in damping and frequency. Data are synthetic.")]);
    draw();
  };
  // 1.2 ODEs and Euler steps
  W.ode = (root) => {
    const chart = h("div"), out = readout([["err", "Largest error"], ["n", "Steps needed"]]);
    const m = select("Equation", [["decay", "Decay: dy/dt = −k y"], ["logistic", "Logistic growth: dy/dt = k y (1 − y)"], ["osc", "Oscillator: d²x/dt² = −(2k)² x"]], "decay", draw);
    const dt = slider("Time step Δt", { min: 0.02, max: 1.5, step: 0.02, value: 0.5, unit: " s", digits: 2 }, draw), k = slider("Rate k", { min: 0.1, max: 1.5, step: 0.05, value: 0.5, digits: 2 }, draw);
    function draw() {
      const r = C().ode({ model: m.get(), dt: dt.get(), k: k.get() });
      out.set("err", fmt(r.err, 3), r.err > 0.1); out.set("n", fmt(r.steps));
      plot(chart, { xs: r.ex, series: [{ name: "Exact solution", values: r.exact, color: css("--muted"), dash: "6 5" }, { name: "Euler's method", xs: r.te, values: r.euler }], points: [{ xs: r.te, ys: r.euler, r: 3.5, color: css("--c1") }], xTitle: "time (s)", yTitle: "y", yMin: m.get() === "osc" ? -2 : -0.2, yMax: m.get() === "osc" ? 2 : 1.2, label: "Euler method" });
    }
    layout(root, [m, dt, k, explain("A differential equation says how a quantity <b>changes</b>. Euler's method follows that rule in small steps: new value = old value + Δt × rate of change. Smaller steps are more accurate but take more work; for the oscillator, Euler even adds energy.")], [out, chart]);
    draw();
  };
  // 1.3 a small neural network
  W.nnfit = (root) => {
    const chart = h("div"), out = readout([["err", "Error on the true curve"], ["p", "Parameters"]]);
    const u = slider("Hidden neurons", { min: 1, max: 40, value: 4 }, draw);
    const t = select("Function to learn", [["sine", "A smooth wave"], ["bump", "A bump"], ["step", "A jump (step)"]], "sine", draw);
    function draw() {
      const r = C().nnfit({ units: u.get(), target: t.get() });
      out.set("err", fmt(r.err, 3), r.err > 0.1); out.set("p", fmt(r.params));
      plot(chart, { xs: r.xs, series: [{ name: "True function", values: r.truth, color: css("--muted"), dash: "6 5" }, { name: "Network output", values: r.pred }], points: [{ xs: r.data[0], ys: r.data[1], r: 3.5, name: "Training data" }], xTitle: "input x", yTitle: "output", yMin: -1.5, yMax: 1.5, label: "network fit" });
    }
    layout(root, [u, t, explain("Each hidden neuron is a soft step, <code>tanh(w·x + b)</code>. The output adds them up with weights. More neurons can bend into more shapes: this is the <b>universal approximation</b> idea. A jump is hard for smooth neurons.")], [out, chart, note("Teaching shortcut: hidden weights are random and only the output weights are fitted (exactly, by least squares). Real networks train all weights by gradient descent (module 1.4).")]);
    draw();
  };
  // 1.4 gradient descent
  W.gd = (root) => {
    const c1 = h("div"), c2 = h("div"), out = readout([["w", "Final weight w"], ["L", "Final loss"], ["gap", "Above the best possible loss"]]);
    const lr = slider("Learning rate", { min: 0.01, max: 2, step: 0.01, value: 0.1, digits: 2 }, draw), mo = slider("Momentum", { min: 0, max: 0.95, step: 0.05, value: 0, digits: 2 }, draw), st = slider("Steps", { min: 5, max: 200, value: 60 }, draw);
    function draw() {
      const r = C().gd({ lr: lr.get(), mom: mo.get(), steps: st.get() });
      out.set("w", fmt(r.w, 2)); out.set("L", fmt(r.L, 3)); out.set("gap", fmt(r.gap, 3), r.gap > 0.1);
      plot(c1, { xs: r.grid, series: [{ name: "Loss L(w)", values: r.curve, color: css("--muted") }], points: [{ xs: r.ws.filter((w) => w >= -4 && w <= 8), ys: r.ws.filter((w) => w >= -4 && w <= 8).map((w) => 0.1 * (w - 3) ** 2 + 0.4 * Math.sin(2.5 * w)), r: 4, color: css("--c1"), name: "Steps taken" }], xTitle: "weight w", yTitle: "loss", yMin: -0.5, yMax: 4, label: "loss landscape" });
      plot(c2, { xs: r.it, series: [{ name: "Loss at each step", values: r.Ls }], hline: { y: r.best, label: "best possible" }, xTitle: "step", yTitle: "loss", yMin: -0.5, label: "training curve" });
    }
    layout(root, [lr, mo, st, explain("Training means walking downhill on the loss. Each step: w ← w − learning rate × slope. Too small and it crawls; too large and it jumps around. This loss has a <b>local minimum</b> near w = −0.3; momentum can carry you past it.")], [out, c1, c2]);
    draw();
  };
  // 1.5 physics-informed fit
  W.pinn = (root) => {
    const chart = h("div"), out = readout([["out", "Error beyond the data (t > 1)"], ["all", "Error over 0–5 s"]]);
    const lam = slider("Physics weight λ (log₁₀)", { min: -4, max: 3, step: 0.5, value: -4, digits: 1, hint: "−4 ≈ almost no physics; 0 = equal weight" }, draw);
    const nc = slider("Collocation points (where physics is checked)", { min: 0, max: 40, value: 20 }, draw), nd = slider("Measurements (all in 0–1 s)", { min: 3, max: 12, value: 6 }, draw);
    function draw() {
      const r = C().pinn({ lam: Math.pow(10, lam.get()), nc: nc.get(), nd: nd.get() });
      out.set("out", fmt(r.errOut, 3), r.errOut > 0.1); out.set("all", fmt(r.errAll, 3));
      plot(chart, { xs: r.ts, series: [{ name: "True solution e^(−0.8t)", values: r.truth, color: css("--muted"), dash: "6 5" }, { name: "Physics-informed fit", values: r.pred }], points: [{ xs: r.data[0], ys: r.data[1], name: "Measurements" }], vline: { x: 1, label: "data end" }, xTitle: "time (s)", yTitle: "y", yMin: -0.5, yMax: 1.5, label: "physics-informed fit" });
    }
    layout(root, [lam, nc, nd, explain("The loss has two parts: <b>fit the data</b> and <b>obey the equation</b> dy/dt + 0.8 y = 0 at collocation points. With almost no physics weight, the curve is free to wander after the data end. Turn λ up and the equation fills the gap.")], [out, chart, note("Teaching version: the model is a sum of 14 Gaussian bumps, so the loss can be minimised exactly. A real PINN uses a neural network and gradient descent (module 2.2).")]);
    draw();
  };
  // 1.6 noise and overfitting
  W.noise = (root) => {
    const chart = h("div"), out = readout([["tr", "Training error"], ["te", "Error on new data"], ["v", "Verdict"]]);
    const d = slider("Model complexity (polynomial degree)", { min: 0, max: 14, value: 3 }, draw), s = slider("Noise in the data", { min: 0, max: 0.5, step: 0.01, value: 0.15, digits: 2 }, draw), n = slider("Data points", { min: 6, max: 40, value: 15 }, draw);
    function draw() {
      const r = C().noise({ deg: d.get(), sigma: s.get(), n: n.get() });
      out.set("tr", fmt(r.train, 3)); out.set("te", fmt(r.test, 3), r.test > 0.3); out.set("v", r.test > 1.6 * r.train && r.test > 0.15 ? "overfitting" : r.train > 0.3 ? "underfitting" : "about right");
      plot(chart, { xs: r.xs, series: [{ name: "True signal", values: r.truth, color: css("--muted"), dash: "6 5" }, { name: "Fitted model", values: r.fit }], points: [{ xs: r.data[0], ys: r.data[1], name: "Noisy data" }], xTitle: "x", yTitle: "y", yMin: -2, yMax: 2, label: "overfitting" });
    }
    layout(root, [d, s, n, explain("A model that is too simple misses the pattern (<b>underfitting</b>). One that is too flexible follows the noise (<b>overfitting</b>): training error falls, but error on new data rises. Always judge a model on data it has not seen.")], [out, chart]);
    draw();
  };
  // 1.7 surrogate model
  W.surrogate = (root) => {
    const chart = h("div"), out = readout([["err", "Surrogate error"], ["runs", "Expensive runs used"], ["save", "Time saved for 10,000 queries"]]);
    const n = slider("Runs of the expensive model", { min: 3, max: 16, value: 5 }, draw), e = slider("Smoothness setting ε", { min: 0.3, max: 6, step: 0.1, value: 1.5, digits: 1 }, draw), d = select("Where to run it", [["uniform", "Evenly spaced"], ["random", "Random"]], "uniform", draw);
    function draw() {
      const r = C().surrogate({ n: n.get(), eps: e.get(), design: d.get() });
      out.set("err", fmt(r.err, 3), r.err > 0.1); out.set("runs", fmt(n.get())); out.set("save", fmt((10000 - n.get()) / 60, 0) + " hours");
      plot(chart, { xs: r.xs, series: [{ name: "Expensive model", values: r.truth, color: css("--muted"), dash: "6 5" }, { name: "Surrogate", values: r.pred }], points: [{ xs: r.data[0], ys: r.data[1], name: "Runs used" }], xTitle: "input (e.g. a design parameter)", yTitle: "output", yMin: -1.5, yMax: 3.5, label: "surrogate" });
    }
    layout(root, [n, e, d, explain("Some simulations take hours. A <b>surrogate</b> (or emulator) learns the input–output map from a few runs, then answers new questions in milliseconds. Where you place the runs, and how smooth you assume the map is, both matter.")], [out, chart, note("Assumes one expensive run takes one minute. Surrogate: Gaussian radial basis interpolation.")]);
    draw();
  };
  // 1.8 Kalman filter
  W.kalman = (root) => {
    const chart = h("div"), out = readout([["m", "GPS error"], ["e", "Filter error"], ["g", "Improvement"]]);
    const sd = slider("GPS noise (m)", { min: 1, max: 25, value: 8 }, draw), q = slider("How much the filter expects the car to change speed (log₁₀ q)", { min: -2, max: 1.5, step: 0.1, value: -0.3, digits: 1 }, draw);
    function draw() {
      const r = C().kalman({ sd: sd.get(), q: Math.pow(10, q.get()) });
      out.set("m", fmt(r.errMeas, 1) + " m"); out.set("e", fmt(r.errEst, 1) + " m", r.errEst > r.errMeas); out.set("g", pct(1 - r.errEst / r.errMeas));
      const k = r.ts.slice(20, 41);
      plot(chart, { xs: k, series: [{ name: "True position", values: r.truth.slice(20, 41), color: css("--muted"), dash: "6 5" }, { name: "Kalman estimate", values: r.est.slice(20, 41) }], points: [{ xs: k, ys: r.meas.slice(20, 41), r: 4, color: css("--climate"), name: "GPS readings" }], xTitle: "time (s), seconds 20–40 shown", yTitle: "position (m)", label: "Kalman filter" });
    }
    layout(root, [sd, q, explain("Physical AI must <b>sense</b> the world before it acts. A Kalman filter blends a physics prediction (position + speed × time) with noisy measurements, weighting each by how much it trusts it. Expect too little change and it lags; expect too much and it just follows the noise.")], [out, chart]);
    draw();
  };
  // 2.1 splitting data honestly
  W.split = (root) => {
    const chart = h("div"), out = readout([["v", "Validation error (what you report)"], ["f", "Error next week (what you get)"], ["gap", "Over-optimism"]]);
    const m = select("How to split the history", [["random", "Random hours"], ["time", "By time: train first, validate last"]], "random", draw), f = slider("Share used for training", { min: 0.4, max: 0.9, step: 0.05, value: 0.7, digits: 2 }, draw);
    function draw() {
      const r = C().split({ frac: f.get(), mode: m.get() });
      out.set("v", fmt(r.valErr) + " veh/h"); out.set("f", fmt(r.futErr) + " veh/h"); out.set("gap", pct(Math.max(0, 1 - r.valErr / r.futErr)), r.valErr < 0.5 * r.futErr);
      plot(chart, { xs: r.ts, series: [{ name: "Hourly traffic flow", values: r.flow }], vline: { x: r.hist, label: "today" }, xTitle: "hour", yTitle: "vehicles per hour", label: "traffic series" });
    }
    layout(root, [m, f, explain("A forecaster that averages the nearest hours looks brilliant if validation hours sit <b>between</b> training hours: it is peeking at the answer. Splitting by time mimics real use and gives an honest error.")], [out, chart, note("Three weeks of synthetic hourly flow with a daily pattern and a slow upward trend. Model: average of the three nearest known hours.")]);
    draw();
  };
  // 2.2 training a PINN
  W.pinntrain = (root) => {
    const chart = h("div"), c2 = h("div"), out = readout([["out", "Error beyond the data"], ["ld", "Final data loss"], ["lp", "Final physics loss"]]);
    const lam = slider("Physics weight λ (log₁₀)", { min: -3, max: 2, step: 0.5, value: 0, digits: 1 }, draw), lr = slider("Learning rate (Adam)", { min: 0.005, max: 0.3, step: 0.005, value: 0.05, digits: 3 }, draw), ep = slider("Epochs", { min: 20, max: 1500, step: 20, value: 400 }, draw);
    function draw() {
      const r = C().pinntrain({ lam: Math.pow(10, lam.get()), lr: lr.get(), epochs: ep.get() });
      out.set("out", fmt(r.errOut, 3), r.errOut > 0.1); out.set("ld", r.Ld[r.Ld.length - 1].toExponential(1)); out.set("lp", r.Lp[r.Lp.length - 1].toExponential(1));
      plot(chart, { xs: r.ep, series: [{ name: "Data loss", values: r.Ld }, { name: "Physics loss", values: r.Lp, color: css("--climate") }], xTitle: "epoch", yTitle: "loss (log scale)", logy: true, label: "loss curves" });
      plot(c2, { xs: r.ts, series: [{ name: "True solution", values: r.truth, color: css("--muted"), dash: "6 5" }, { name: "Model after training", values: r.pred }], points: [{ xs: r.data[0], ys: r.data[1], name: "Measurements" }], xTitle: "time (s)", yTitle: "y", yMin: -0.5, yMax: 1.5, label: "trained fit" });
    }
    layout(root, [lam, lr, ep, explain("Watch both parts of the loss fall. If the physics loss stays high, the model fits the data but breaks the law; if the data loss stays high, the physics weight is drowning the data. Balancing the two is the main practical skill in training PINNs.")], [out, chart, c2]);
    draw();
  };
  // 2.3 heat equation solver
  W.heat = (root) => {
    const chart = h("div"), out = readout([["r", "Stability number r = αΔt/Δx²"], ["e", "Error at the end"], ["n", "Time steps"]]);
    const r = slider("Stability number r", { min: 0.1, max: 0.6, step: 0.01, value: 0.4, digits: 2 }, draw);
    function draw() {
      const s = C().heat({ r: r.get() }), cs = [css("--c1"), css("--c2"), css("--c3"), css("--c4")];
      out.set("r", fmt(r.get(), 2) + (s.stable ? " (stable)" : " (unstable!)"), !s.stable); out.set("e", s.err >= 999 ? "blew up" : fmt(s.err, 4), s.err > 0.01); out.set("n", fmt(s.steps));
      plot(chart, { xs: s.xs, series: s.snaps.map((u, i) => ({ name: `t = ${fmt(s.times[i], 3)} s`, values: u, color: cs[i] })), xTitle: "position x", yTitle: "temperature u", yMin: -1, yMax: 1.6, label: "heat equation" });
    }
    layout(root, [r, explain("Classical solvers make the training data and the reference answers for SciML. The explicit finite-difference scheme for ∂u/∂t = α ∂²u/∂x² is stable only if <b>r ≤ 0.5</b>. Push r past 0.5 and tiny wiggles grow until the solution explodes.")], [out, chart]);
    draw();
  };
  // 2.4 SINDy
  W.sindy = (root) => {
    const chart = h("div"), bars = h("div"), out = readout([["eq", "Discovered equation"], ["ok", "Right terms found?"]]);
    const nz = slider("Measurement noise", { min: 0, max: 0.08, step: 0.002, value: 0.01, digits: 3 }, draw), th = slider("Sparsity threshold", { min: 0.005, max: 1, step: 0.005, value: 0.1, digits: 3 }, draw);
    function draw() {
      const r = C().sindy({ noise: nz.get(), thr: th.get() });
      out.set("eq", r.eq); out.set("ok", r.ok ? "Yes" : "No", !r.ok);
      if (window.IAMChart) barChart(bars, { labels: r.names, values: r.w.map((x) => Math.abs(x)), yTitle: "|coefficient| found (true: x 4.00, v 0.30)", digits: 2, label: "coefficients" });
      plot(chart, { xs: r.ts.slice(0, 600), series: [{ name: "Position x (noisy)", values: r.X.slice(0, 600) }, { name: "Velocity v (noisy)", values: r.V.slice(0, 600), color: css("--climate") }], xTitle: "time (s)", yTitle: "value", label: "oscillator data" });
    }
    layout(root, [nz, th, explain("SINDy guesses that the law is a <b>short</b> sum of candidate terms (1, x, v, x², …). It fits all of them, then throws away the small ones and refits. The true law here is dv/dt = −4 x − 0.3 v. Too low a threshold keeps junk terms; too high deletes real ones.")], [out, bars, chart]);
    draw();
  };
  // 2.5 operator learning
  W.operator = (root) => {
    const chart = h("div"), out = readout([["e", "Average error on new inputs"], ["n", "Training pairs"]]);
    const n = slider("Training pairs (input → solution)", { min: 1, max: 16, value: 3 }, draw), m = slider("Grid points", { min: 12, max: 48, step: 4, value: 24 }, draw);
    function draw() {
      const r = C().operator({ ntrain: n.get(), m: m.get() });
      out.set("e", pct(Math.min(r.err, 9.99)), r.err > 0.1); out.set("n", fmt(n.get()));
      const sc = Math.max(...r.f.map(Math.abs)) / (Math.max(...r.u.map(Math.abs)) || 1);
      plot(chart, { xs: r.xs, series: [{ name: "New input f(x) (scaled)", values: r.f.map((v) => v / sc), color: css("--muted"), dash: "3 4" }, { name: "True solution u(x)", values: r.u, color: css("--ink") }, { name: "Learned operator's answer", values: r.pred, dash: "6 4" }], xTitle: "x", yTitle: "u", label: "operator learning" });
    }
    layout(root, [n, m, explain("An <b>operator</b> maps a whole function to a whole function: here a heat source f(x) to the temperature u(x) it causes (−u″ = f). After learning from example pairs, it solves new cases instantly. These inputs are built from 8 shapes, so about 8 good examples are enough.")], [out, chart, note("Teaching version: a linear operator learned by ridge regression. DeepONet and Fourier neural operators learn nonlinear operators with neural networks.")]);
    draw();
  };
  // 2.6 Gaussian process
  W.gp = (root) => {
    const chart = h("div"), out = readout([["e", "Error of the mean"], ["c", "Truth inside the 95% band"], ["w", "Average band width"]]);
    const n = slider("Observations", { min: 2, max: 20, value: 6 }, draw), l = slider("Length scale ℓ", { min: 0.1, max: 3, step: 0.05, value: 0.6, digits: 2, hint: "how far apart two inputs can be and still be similar" }, draw), s = slider("Assumed noise", { min: 0.01, max: 0.5, step: 0.01, value: 0.1, digits: 2 }, draw);
    function draw() {
      const r = C().gp({ n: n.get(), ell: l.get(), sn: s.get() });
      out.set("e", fmt(r.err, 3)); out.set("c", pct(r.cover), r.cover < 0.85); out.set("w", fmt(r.width, 2));
      plot(chart, { xs: r.xs, band: { lo: r.lo, hi: r.hi }, series: [{ name: "Truth", values: r.truth, color: css("--muted"), dash: "6 5" }, { name: "GP mean", values: r.mu }], points: [{ xs: r.data[0], ys: r.data[1], name: "Observations" }], xTitle: "x", yTitle: "y", yMin: -3, yMax: 3, label: "Gaussian process" });
    }
    layout(root, [n, l, s, explain("A Gaussian process predicts a value <b>and</b> how sure it is. Far from data the band widens. A good model has a band that contains the truth about 95% of the time: too narrow is overconfident, too wide is useless.")], [out, chart]);
    draw();
  };
  // 2.7 hybrid model
  W.hybrid = (root) => {
    const chart = h("div"), out = readout([["p", "Physics only"], ["m", "Machine learning only"], ["y", "Hybrid (physics + learned correction)"]]);
    const n = slider("Speed–density observations", { min: 5, max: 80, value: 20 }, draw), r = slider("Highest density observed", { min: 30, max: 130, value: 60, unit: " veh/km" }, draw);
    function draw() {
      const s = C().hybrid({ n: n.get(), rmaxObs: r.get() });
      out.set("p", fmt(s.ePhys, 1) + " km/h"); out.set("m", fmt(s.eML, 1) + " km/h", s.eML > 10); out.set("y", fmt(s.eHy, 1) + " km/h", s.eHy > 10);
      plot(chart, { xs: s.rs, series: [{ name: "True relation", values: s.truth, color: css("--muted"), dash: "6 5" }, { name: "Physics (Greenshields)", values: s.phys, color: css("--c2") }, { name: "ML only", values: s.ml, color: css("--climate") }, { name: "Hybrid", values: s.hy, color: css("--c1") }], points: [{ xs: s.data[0], ys: s.data[1], r: 3.5 }], vline: { x: r.get(), label: "no data beyond" }, xTitle: "density (vehicles per km)", yTitle: "speed (km/h)", yMin: -10, yMax: 120, label: "hybrid model" });
    }
    layout(root, [n, r, explain("Errors are measured where there are <b>no data</b> (beyond the dashed line). Pure machine learning extrapolates badly. The simple physics model is biased but sensible. A hybrid keeps the physics and learns only a small correction, so it inherits the physics' good behaviour.")], [out, chart]);
    draw();
  };
  // 2.8 conformal prediction
  W.conformal = (root) => {
    const chart = h("div"), out = readout([["c", "Coverage on new data"], ["lo", "Coverage for small inputs"], ["hi", "Coverage for large inputs"], ["w", "Interval width"]]);
    const n = slider("Calibration examples", { min: 10, max: 500, step: 10, value: 50 }, draw), a = slider("Target coverage", { min: 0.5, max: 0.98, step: 0.01, value: 0.9, digits: 2 }, draw);
    function draw() {
      const r = C().conformal({ ncal: n.get(), alpha: 1 - a.get() });
      out.set("c", pct(r.cover), Math.abs(r.cover - r.target) > 0.05); out.set("lo", pct(r.coverLow)); out.set("hi", pct(r.coverHigh), r.coverHigh < r.target - 0.05); out.set("w", "± " + fmt(r.q, 2));
      barChart(chart, { labels: ["Target", "All new data", "Small inputs", "Large inputs"], values: [r.target, r.cover, r.coverLow, r.coverHigh].map((x) => 100 * x), yTitle: "% of new cases inside the interval", yMax: 100, label: "coverage" });
    }
    layout(root, [n, a, explain("Split conformal prediction: look at the model's errors on a calibration set, take the error that is beaten (1 − α) of the time, and use it as ± interval. It guarantees coverage <b>on average</b>, with no assumptions about the model, but not for every kind of input: here the noise grows with x.")], [out, chart]);
    draw();
  };
  // 3.1 traffic state estimation
  W.trafficpinn = (root) => {
    const chart = h("div"), out = readout([["i", "Interpolating detectors"], ["e", "Physics model + detectors"], ["g", "Improvement"]]);
    const nd = slider("Loop detectors on the 10 km ring road", { min: 2, max: 20, value: 4 }, draw), g = slider("Trust in detectors (nudging gain)", { min: 0, max: 1, step: 0.05, value: 0.5, digits: 2 }, draw);
    function draw() {
      const r = C().trafficpinn({ ndet: nd.get(), gain: g.get() });
      out.set("i", fmt(r.errInt, 1) + " veh/km"); out.set("e", fmt(r.errEst, 1) + " veh/km", r.errEst > r.errInt); out.set("g", pct(Math.max(0, 1 - r.errEst / r.errInt)));
      plot(chart, { xs: r.xs, series: [{ name: "True density", values: r.truth, color: css("--muted"), dash: "6 5" }, { name: "Interpolation", values: r.interp, color: css("--climate") }, { name: "Physics-informed estimate", values: r.est }], points: [{ xs: r.det, ys: r.det.map(() => 4), r: 6, color: css("--ink"), name: "Detectors" }], xTitle: "position along the road (km)", yTitle: "density (veh/km)", yMin: 0, yMax: 150, label: "traffic state estimation" });
    }
    layout(root, [nd, g, explain("Detectors see only a few points. Straight lines between them miss the shock waves of a jam. Running the <b>LWR traffic-flow model</b> and nudging it towards the detector readings keeps the physics of waves and fills the gaps, the same idea as physics-informed deep learning for traffic.")], [out, chart, note("LWR model with Greenshields' flux, solved by Godunov's scheme; after 10 minutes. The model starts with no knowledge of the jam.")]);
    draw();
  };
  // 3.2 car following and automation
  W.idm = (root) => {
    const chart = h("div"), out = readout([["l", "Lowest speed of the last car"], ["a", "Amplification of the braking wave"], ["s", "String stable?"]]);
    const c = select("Who is driving", [["human", "Humans (0.8 s reaction, gentle acceleration)"], ["acc", "Adaptive cruise control (radar only)"], ["cacc", "Cooperative ACC (radar + V2V messages)"]], "human", draw), T = slider("Desired time gap", { min: 0.6, max: 2.5, step: 0.1, value: 1.2, unit: " s", digits: 1 }, draw);
    function draw() {
      const r = C().idm({ T: T.get(), ctrl: c.get() });
      out.set("l", fmt(r.minLast * 3.6, 0) + " km/h", r.minLast < 5); out.set("a", fmt(r.amp, 2) + "×", r.amp > 1); out.set("s", r.amp <= 1 ? "Yes" : "No", r.amp > 1);
      plot(chart, { xs: r.t, series: r.vs.map((v, i) => ({ name: r.labels[i], values: v.map((x) => x * 3.6) })), xTitle: "time (s)", yTitle: "speed (km/h)", yMin: 0, yMax: 100, label: "platoon speeds" });
    }
    layout(root, [c, T, explain("The lead car brakes hard for 4 seconds. With human drivers, each follower brakes a little harder than the one ahead and the wave <b>grows</b> down the line (string instability). Automated controllers, especially cooperative ones that hear the leader's braking by radio, can damp it.")], [out, chart, note("Intelligent Driver Model (Treiber, Hennecke and Helbing 2000) for all followers; human reaction delay 0.8 s. Cooperative ACC adds 0.6 × the acceleration of the car ahead.")]);
    draw();
  };
  // 3.3 surrogate safety measures
  W.ttc = (root) => {
    const chart = h("div"), out = readout([["t", "Minimum time to collision"], ["d", "Deceleration needed to avoid crash (DRAC)"], ["c", "Outcome"]]);
    const g = slider("Initial gap", { min: 5, max: 80, value: 40, unit: " m" }, draw), dv = slider("Closing speed", { min: 1, max: 20, value: 8, unit: " m/s" }, draw), rt = slider("Reaction time", { min: 0.5, max: 3, step: 0.1, value: 1.5, unit: " s", digits: 1 }, draw), de = slider("Braking", { min: 1, max: 8, step: 0.5, value: 4, unit: " m/s²", digits: 1 }, draw);
    function draw() {
      const r = C().ttc({ gap: g.get(), dv: dv.get(), react: rt.get(), decel: de.get() });
      out.set("t", r.crash ? "0 (crash)" : fmt(r.minTTC, 2) + " s", r.minTTC < 1.5); out.set("d", fmt(r.drac, 1) + " m/s²", r.drac > 3.4); out.set("c", r.crash ? "Crash" : r.minTTC < 1.5 ? "Serious conflict" : "Safe", r.conflict);
      plot(chart, { xs: r.ts, series: [{ name: "Time to collision", values: r.ttc }], hline: { y: 1.5, label: "1.5 s conflict threshold" }, xTitle: "time (s)", yTitle: "TTC (s)", yMin: 0, yMax: 10, label: "time to collision" });
    }
    layout(root, [g, dv, rt, de, explain("Crashes are rare, so safety studies count <b>near misses</b> instead. Time to collision = gap ÷ closing speed: how long until impact if nothing changes. A value under about 1.5 s is a serious conflict. Physics gives the measure; machine learning finds conflicts in video at scale.")], [out, chart, note("Lead vehicle at 15 m/s; follower starts braking after the reaction time. DRAC above 3.4 m/s² is a common conflict criterion.")]);
    draw();
  };
  // 3.4 vehicle energy and emissions
  W.vsp = (root) => {
    const chart = h("div"), out = readout([["e", "Energy used (fuel or battery)"], ["c", "CO₂ per km"], ["k", "Trip length"]]);
    const a = slider("Driving style (acceleration ×)", { min: 0.5, max: 2.5, step: 0.1, value: 1, digits: 1 }, draw), g = slider("Road grade", { min: -4, max: 6, step: 0.5, value: 0, unit: "%", digits: 1 }, draw), e = select("Vehicle", [["ice", "Petrol car"], ["ev", "Electric car (with regenerative braking)"]], "ice", draw);
    function draw() {
      const r = C().vsp({ aggr: a.get(), grade: g.get(), ev: e.get() === "ev" });
      out.set("e", fmt(r.kWh100, 1) + " kWh/100 km"); out.set("c", fmt(r.co2) + " g/km", r.co2 > 180); out.set("k", fmt(r.km, 1) + " km");
      plot(chart, { xs: r.ts, series: [{ name: "Power at the wheels (kW)", values: r.P }, { name: "Speed (km/h)", values: r.vs.map((v) => v * 3.6), color: css("--muted") }], xTitle: "time (s)", yTitle: "kW / km/h", label: "vehicle power" });
    }
    layout(root, [a, g, e, explain("Power = mass × speed × (acceleration + gravity × grade) + rolling resistance + air drag. This <b>physics</b> explains most of fuel use; machine learning then corrects for what it misses, such as engine maps and traffic. Electric cars recover part of the braking energy.")], [out, chart, note("1,500 kg car, synthetic urban cycle. Petrol engine efficiency 25%; electricity at 450 g CO₂/kWh (illustrative grid). Values are teaching estimates, not certified figures.")]);
    draw();
  };
  // 3.5 emulating an integrated assessment model
  W.emulator = (root) => {
    const chart = h("div"), out = readout([["e", "Emulator error"], ["h", "Computer time for the runs"], ["q", "Time for 10,000 emulator queries"]]);
    const n = slider("Full model runs", { min: 2, max: 12, value: 4 }, draw), d = select("Which carbon prices to run", [["uniform", "Spread evenly over 0–400 $/t"], ["clustered", "Mostly low prices"]], "uniform", draw);
    function draw() {
      const r = C().emulator({ n: n.get(), design: d.get() });
      out.set("e", fmt(r.err, 3) + " Gt CO₂", r.err > 0.05); out.set("h", fmt(r.hours) + " h"); out.set("q", "under 1 s");
      plot(chart, { xs: r.xs, band: { lo: r.lo, hi: r.hi }, series: [{ name: "Full model", values: r.truth, color: css("--muted"), dash: "6 5" }, { name: "GP emulator", values: r.mu }], points: [{ xs: r.data[0], ys: r.data[1], name: "Runs" }], xTitle: "carbon price ($ per tonne CO₂)", yTitle: "transport CO₂ in 2050 (Gt)", yMin: 0.4, yMax: 1.9, label: "IAM emulator" });
    }
    layout(root, [n, d, explain("Integrated assessment models such as GCAM take hours per scenario. An <b>emulator</b> trained on a handful of runs lets you explore thousands of policy settings, with an uncertainty band that tells you where to run the full model next.")], [out, chart, note("The 'full model' is a smooth toy curve standing in for a GCAM transport output; 6 hours per run is illustrative.")]);
    draw();
  };
  // 3.6 crowd fundamental diagram
  W.crowdfit = (root) => {
    const chart = h("div"), out = readout([["p", "Unconstrained curve, beyond the data"], ["f", "Physics-shaped curve, beyond the data"], ["fit", "Fitted v₀, γ, ρ_max"]]);
    const r = slider("Highest crowd density observed", { min: 1.2, max: 4.5, step: 0.1, value: 2.5, unit: " /m²", digits: 1 }, draw), nz = slider("Measurement noise", { min: 0.02, max: 0.2, step: 0.01, value: 0.08, unit: " m/s", digits: 2 }, draw);
    function draw() {
      const s = C().crowdfit({ rmaxObs: r.get(), noise: nz.get() });
      out.set("p", fmt(s.ePoly, 2) + " m/s", s.ePoly > 0.2); out.set("f", fmt(s.ePhys, 2) + " m/s"); out.set("fit", s.fit.map((x) => fmt(x, 2)).join(", "));
      plot(chart, { xs: s.rs, series: [{ name: "True (Weidmann)", values: s.truth, color: css("--muted"), dash: "6 5" }, { name: "Cubic fit", values: s.poly, color: css("--climate") }, { name: "Physics-shaped fit", values: s.phys }], points: [{ xs: s.data[0], ys: s.data[1], r: 3.5 }], vline: { x: r.get(), label: "data end" }, xTitle: "density (persons per m²)", yTitle: "walking speed (m/s)", yMin: -0.3, yMax: 1.7, label: "crowd fit" });
    }
    layout(root, [r, nz, explain("Dangerous densities are exactly where we have the least data. A free curve fitted to light-crowd data can predict nonsense, even negative speeds. Fitting only the parameters of a physically shaped law (speed falls to zero at jam density) extrapolates safely.")], [out, chart, note("Weidmann (1993): v = v₀(1 − exp(−γ(1/ρ − 1/ρ_max))), with v₀ = 1.34 m/s, γ = 1.913, ρ_max = 5.4 per m². Synthetic data.")]);
    draw();
  };
  // 3.7 digital twin of a signalised junction
  W.twin = (root) => {
    const chart = h("div"), out = readout([["m", "Model alone"], ["t", "Digital twin (model + data)"], ["f", "Twin's 3-cycle-ahead forecast"]]);
    const nz = slider("Detector noise", { min: 0, max: 15, value: 3, unit: " veh" }, draw), g = slider("Correction gain", { min: 0, max: 1, step: 0.05, value: 0.5, digits: 2 }, draw), f = select("Detector status", [["ok", "Working"], ["fail", "Fails for 20 cycles"]], "ok", draw);
    function draw() {
      const r = C().twin({ noise: nz.get(), gain: g.get(), fail: f.get() === "fail" });
      out.set("m", fmt(r.errModel, 1) + " veh"); out.set("t", fmt(r.errTwin, 1) + " veh", r.errTwin > 10); out.set("f", fmt(r.errFc, 1) + " veh");
      plot(chart, { xs: r.ks, series: [{ name: "True queue", values: r.truth, color: css("--muted"), dash: "6 5" }, { name: "Model alone", values: r.model, color: css("--climate") }, { name: "Digital twin", values: r.twin }], xTitle: "signal cycle (90 s each)", yTitle: "queue (vehicles)", yMin: 0, label: "digital twin" });
    }
    layout(root, [nz, g, f, explain("A digital twin is a model that stays in step with reality. Alone, the model drifts because its arrival estimate is 15% low. Correcting it each cycle with detector data keeps it on track, and when the detector fails, the model carries the twin through the gap.")], [out, chart]);
    draw();
  };

  window.IAMWidgets = W;
  window.IAMChart = { lineChart, barChart, plot };
})();
