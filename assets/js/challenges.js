/* Simulation challenges: predict, then steer a small model to a goal, with animated feedback.
   Also adds progress bars, animations and a celebration to every multiple-choice quiz on the page.
   Challenge data: window.CHALLENGES[module] = [{title, level, icon, model, fixed, controls[], metric, op, target, tol, view, gmin, gmax, unit,
   goal, predict:{q, options[], answer}, hint, explain, solution}]. All numbers are teaching toys. */
(function () {
  "use strict";
  const NS = "http://www.w3.org/2000/svg";
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  const fmt = (x, d = 0) => (isFinite(x) ? Number(x).toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d }) : "–");
  const reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  const h = (tag, attrs = {}, ...kids) => { const e = document.createElement(tag); for (const [k, v] of Object.entries(attrs)) { if (k === "class") e.className = v; else if (k === "html") e.innerHTML = v; else if (k.startsWith("on")) e.addEventListener(k.slice(2), v); else e.setAttribute(k, v); } kids.flat().forEach((c) => c != null && e.append(c.nodeType ? c : document.createTextNode(c))); return e; };
  const sv = (t, a, p) => { const e = document.createElementNS(NS, t); for (const k in a) e.setAttribute(k, a[k]); if (p) p.append(e); return e; };
  const icon = (name) => `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="${(window.GCAM_ICONS || {})[name] || ""}"/></svg>`;
  const range = (a, b, s = 1) => { const r = []; for (let x = a; x <= b + 1e-9; x += s) r.push(+x.toFixed(6)); return r; };
  const logit = (costs, lam) => { const w = costs.map((c) => Math.pow(Math.max(c, 1e-6), lam)); const s = w.reduce((a, b) => a + b, 0); return w.map((x) => x / s); };

  // ------------------------------------------------------------------ toy models: (params) -> {value, line?, bars?}; all call the shared cores in core.js
  const SC = () => window.SCIML;
  const ln = (xs, series, extra) => Object.assign({ xs, series }, extra || {});
  const M = {
    spectrum(p) { const r = SC().spectrum(p); return { value: { errOut: r.errOut, errIn: r.errIn }, line: ln(r.ts, [{ name: "Truth", values: r.truth }, { name: "Model", values: r.pred }], { yTitle: "y", xTitle: "time (s)", yMax: 1.2, yMin: -1.2 }) }; },
    ode(p) { const r = SC().ode(p); return { value: { err: r.err, steps: r.steps }, line: ln(r.ex, [{ name: "Exact", values: r.exact }], { yTitle: "y", xTitle: "time (s)" }) }; },
    nnfit(p) { const r = SC().nnfit(p); return { value: { err: r.err, params: r.params }, line: ln(r.xs, [{ name: "True", values: r.truth }, { name: "Network", values: r.pred }], { yTitle: "output", xTitle: "x", yMin: -1.5, yMax: 1.5 }) }; },
    gd(p) { const r = SC().gd(p); return { value: { gap: r.gap, L: r.L }, line: ln(r.it, [{ name: "Loss", values: r.Ls }], { yTitle: "loss", xTitle: "step", yMin: -0.5 }) }; },
    pinn(p) { const q = Object.assign({}, p, { lam: Math.pow(10, p.loglam) }); const r = SC().pinn(q); return { value: { errOut: r.errOut }, line: ln(r.ts, [{ name: "Truth", values: r.truth }, { name: "Fit", values: r.pred }], { yTitle: "y", xTitle: "time (s)", yMin: -0.5, yMax: 1.5 }) }; },
    noise(p) { const r = SC().noise(p); return { value: { test: r.test, train: r.train }, line: ln(r.xs, [{ name: "Truth", values: r.truth }, { name: "Fit", values: r.fit }], { yTitle: "y", xTitle: "x", yMin: -2, yMax: 2 }) }; },
    surrogate(p) { const r = SC().surrogate(p); return { value: { err: r.err }, line: ln(r.xs, [{ name: "Expensive model", values: r.truth }, { name: "Surrogate", values: r.pred }], { yTitle: "output", xTitle: "input", yMin: -1.5, yMax: 3.5 }) }; },
    kalman(p) { const r = SC().kalman({ sd: p.sd, q: Math.pow(10, p.logq) }); return { value: { errEst: r.errEst, ratio: r.errEst / r.errMeas }, bars: { labels: ["GPS alone", "Kalman filter"], values: [r.errMeas, r.errEst], yTitle: "position error (m)", digits: 1 } }; },
    split(p) { const r = SC().split({ frac: p.frac, mode: p.mode === true || p.mode === "time" ? "time" : "random" }); return { value: { gap: Math.abs(r.futErr - r.valErr) / r.futErr, valErr: r.valErr }, bars: { labels: ["Validation error", "Next-week error"], values: [r.valErr, r.futErr], yTitle: "veh/h" } }; },
    pinntrain(p) { const q = Object.assign({}, p, { lam: Math.pow(10, p.loglam) }); const r = SC().pinntrain(q); return { value: { errOut: r.errOut }, line: ln(r.ep, [{ name: "Data loss", values: r.Ld }, { name: "Physics loss", values: r.Lp }], { yTitle: "loss", xTitle: "epoch" }) }; },
    heat(p) { const r = SC().heat(p); return { value: { err: r.err, steps: r.steps }, line: ln(r.xs, [{ name: "Final", values: r.snaps[r.snaps.length - 1] }, { name: "Exact", values: r.exact }], { yTitle: "u", xTitle: "x", yMin: -1, yMax: 1.6 }) }; },
    sindy(p) { const r = SC().sindy(p); return { value: { ok: r.ok ? 1 : 0, nterms: r.nterms }, bars: { labels: r.names, values: r.w.map(Math.abs), yTitle: "|coefficient|", digits: 2 } }; },
    operator(p) { const r = SC().operator(p); return { value: { err: r.err }, line: ln(r.xs, [{ name: "True u", values: r.u }, { name: "Learned", values: r.pred }], { yTitle: "u", xTitle: "x" }) }; },
    gp(p) { const r = SC().gp(p); return { value: { cover: r.cover, err: r.err, width: r.width }, line: ln(r.xs, [{ name: "Truth", values: r.truth }, { name: "GP mean", values: r.mu }], { yTitle: "y", xTitle: "x", yMin: -3, yMax: 3 }) }; },
    hybrid(p) { const r = SC().hybrid(p); return { value: { eHy: r.eHy, eML: r.eML }, line: ln(r.rs, [{ name: "Truth", values: r.truth }, { name: "Hybrid", values: r.hy }], { yTitle: "km/h", xTitle: "veh/km", yMin: -10, yMax: 120 }) }; },
    conformal(p) { const r = SC().conformal({ ncal: p.ncal, alpha: 1 - p.target / 100 }); return { value: { cover: 100 * r.cover, high: 100 * r.coverHigh }, bars: { labels: ["Target", "Achieved", "Large inputs"], values: [p.target, 100 * r.cover, 100 * r.coverHigh], yTitle: "% covered", yMax: 100 } }; },
    trafficpinn(p) { const r = SC().trafficpinn(p); return { value: { errEst: r.errEst, errInt: r.errInt }, line: ln(r.xs, [{ name: "Truth", values: r.truth }, { name: "Estimate", values: r.est }], { yTitle: "veh/km", xTitle: "km", yMin: 0, yMax: 150 }) }; },
    idm(p) { const r = SC().idm({ T: p.T, ctrl: ["human", "acc", "cacc"][p.ctrl] }); return { value: { amp: r.amp, minLast: r.minLast * 3.6 }, line: ln(r.t, r.vs.map((v, i) => ({ name: r.labels[i], values: v.map((x) => x * 3.6) })), { yTitle: "km/h", xTitle: "time (s)", yMin: 0, yMax: 100 }) }; },
    ttc(p) { const r = SC().ttc(p); return { value: { minTTC: r.minTTC, drac: r.drac }, line: ln(r.ts, [{ name: "TTC", values: r.ttc }], { yTitle: "s", xTitle: "time (s)", yMin: 0, yMax: 10 }) }; },
    vsp(p) { const r = SC().vsp({ aggr: p.aggr, grade: p.grade, ev: !!p.ev }); return { value: { co2: r.co2, kWh100: r.kWh100 }, bars: { labels: ["CO₂ g/km", "kWh/100 km"], values: [r.co2, r.kWh100], yTitle: "value" } }; },
    emulator(p) { const r = SC().emulator({ n: p.n, design: p.clustered ? "clustered" : "uniform" }); return { value: { err: r.err, hours: r.hours }, line: ln(r.xs, [{ name: "Full model", values: r.truth }, { name: "Emulator", values: r.mu }], { yTitle: "Gt CO₂", xTitle: "$/t", yMin: 0.4, yMax: 1.9 }) }; },
    crowdfit(p) { const r = SC().crowdfit(p); return { value: { ePhys: r.ePhys, ePoly: r.ePoly }, line: ln(r.rs, [{ name: "Truth", values: r.truth }, { name: "Physics-shaped", values: r.phys }, { name: "Cubic", values: r.poly }], { yTitle: "m/s", xTitle: "per m²", yMin: -0.3, yMax: 1.7 }) }; },
    twin(p) { const r = SC().twin({ noise: p.noise, gain: p.gain, fail: !!p.fail }); return { value: { errTwin: r.errTwin, errFc: r.errFc }, line: ln(r.ks, [{ name: "True queue", values: r.truth }, { name: "Twin", values: r.twin }], { yTitle: "vehicles", xTitle: "cycle", yMin: 0 }) }; },
  };
  window.IAMToyModels = M;

  // ------------------------------------------------------------------ gauge view
  function gauge(box, v, c) {
    const lo = c.gmin, hi = c.gmax, ang = (x) => Math.PI * (1 - (Math.max(lo, Math.min(hi, x)) - lo) / (hi - lo));
    let s = box.querySelector("svg.ch-gauge");
    if (!s) {
      box.innerHTML = ""; s = sv("svg", { viewBox: "0 0 320 190", class: "ch-gauge", role: "img" }, box);
      const arc = (a0, a1, r) => { const p = (a) => [160 + r * Math.cos(a), 150 - r * Math.sin(a)]; const [x0, y0] = p(a0), [x1, y1] = p(a1); return `M${x0},${y0} A${r},${r} 0 0 1 ${x1},${y1}`; };
      sv("path", { d: arc(Math.PI, 0, 110), stroke: css("--line"), "stroke-width": 22, fill: "none" }, s);
      let t0 = c.op === "<=" ? lo : c.op === ">=" ? c.target : c.target - c.tol, t1 = c.op === "<=" ? c.target : c.op === ">=" ? hi : c.target + c.tol;
      sv("path", { d: arc(ang(t0), ang(t1), 110), stroke: css("--land"), "stroke-width": 22, fill: "none", opacity: 0.55 }, s);
      [lo, (lo + hi) / 2, hi].forEach((x) => { const a = ang(x), t = sv("text", { x: 160 + 140 * Math.cos(a), y: 154 - 140 * Math.sin(a) + 4, "text-anchor": "middle", style: `font:12px var(--body);fill:${css("--muted")}` }, s); t.textContent = fmt(x, hi - lo < 10 ? 1 : 0); });
      const n = sv("g", { class: "needle" }, s);
      sv("line", { x1: 160, y1: 150, x2: 260, y2: 150, stroke: css("--ink"), "stroke-width": 5, "stroke-linecap": "round" }, n);
      sv("circle", { cx: 160, cy: 150, r: 10, fill: css("--ink") }, s);
      const lab = sv("text", { x: 160, y: 182, "text-anchor": "middle", style: `font:600 13px var(--body);fill:${css("--ink-soft")}` }, s); lab.textContent = "green band = goal";
    }
    $(".needle", s).style.transform = `rotate(${-(ang(v) * 180) / Math.PI}deg)`;
  }

  function hit(c, v) { return c.op === "<=" ? v <= c.target + 1e-9 : c.op === ">=" ? v >= c.target - 1e-9 : Math.abs(v - c.target) <= c.tol; }
  function burst(card) {
    if (reduce) return; const fx = h("div", { class: "ch-fx" }); card.append(fx);
    const cols = [css("--water"), css("--energy"), css("--land"), css("--economy"), css("--climate")];
    for (let i = 0; i < 36; i++) { const a = (Math.PI * 2 * i) / 36, r = 120 + Math.random() * 160; const p = h("i"); p.style.background = cols[i % cols.length]; p.style.setProperty("--x", Math.cos(a) * r + "px"); p.style.setProperty("--y", Math.sin(a) * r + "px"); p.style.animationDelay = Math.random() * 0.15 + "s"; fx.append(p); }
    setTimeout(() => fx.remove(), 1500);
  }
  const KEY = "sciml-challenges";
  const store = { load() { try { return JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) { return {}; } }, save(d) { try { localStorage.setItem(KEY, JSON.stringify(d)); } catch (e) { } } };

  function countUp(el, to, d, unit) {
    const from = parseFloat(el.dataset.v || to); el.dataset.v = to;
    if (reduce || !isFinite(from)) { el.firstChild.textContent = fmt(to, d) + unit; return; }
    const t0 = performance.now(); const tick = (n) => { const t = Math.min(1, (n - t0) / 350); el.firstChild.textContent = fmt(from + (to - from) * t, d) + unit; if (t < 1) requestAnimationFrame(tick); }; requestAnimationFrame(tick);
  }

  function card(c, idx, mid, onScore) {
    const st = store.load(), key = `${mid}:${idx}`;
    const live = h("div", { class: "ch-live" }, h("span", {}, "–"), h("small", {}, c.metricLabel || ""));
    const view = h("div", { class: "ch-view" }), fb = h("div", { class: "ch-fb", "aria-live": "polite" });
    const params = Object.assign({}, c.fixed || {});
    let tries = 0, solved = !!st[key], predicted = !c.predict;
    const ctrls = c.controls.map((k) => {
      params[k.id] = k.value;
      if (k.type === "toggle") { const cb = h("input", { type: "checkbox" }); cb.checked = !!k.value; params[k.id] = cb.checked; cb.addEventListener("change", () => { params[k.id] = cb.checked; draw(); }); return h("div", { class: "ctrl" }, h("label", {}, cb, " " + k.label)); }
      const out = h("output"), inp = h("input", { type: "range", min: k.min, max: k.max, step: k.step || 1, value: k.value, "aria-label": k.label });
      const show = () => (out.textContent = fmt(+inp.value, k.digits || 0) + (k.unit || ""));
      inp.addEventListener("input", () => { params[k.id] = +inp.value; show(); draw(); }); show();
      const w = h("div", { class: "ctrl" }, h("label", {}, h("span", {}, k.label), out), inp, k.hint ? h("div", { class: "hint" }, k.hint) : null);
      w.inp = inp; w.k = k; return w;
    });
    const lockable = h("div", {}, ctrls);
    function draw() {
      const r = M[c.model](params), v = r.value[c.metric];
      countUp(live, v, c.digits || 0, c.unit || ""); live.classList.toggle("hit", hit(c, v));
      if (c.view === "gauge") gauge(view, v, c);
      else if (r.line && window.IAMChart) window.IAMChart.lineChart(view, Object.assign({ xTitle: c.xTitle || "", label: c.title }, r.line));
      else if (r.bars && window.IAMChart) window.IAMChart.barChart(view, Object.assign({ label: c.title }, r.bars));
      return v;
    }
    const stars = h("span", { class: "ch-stars", "aria-label": "stars" }, solved ? "★".repeat(st[key]) + "☆".repeat(3 - st[key]) : "");
    const check = h("button", { class: "btn", type: "button" }, "Check my answer");
    const hintB = h("button", { class: "btn quiet", type: "button", hidden: "" }, "Hint");
    const solB = h("button", { class: "btn quiet", type: "button", hidden: "" }, "Show a solution");
    const el = h("article", { class: "ch-card" + (solved ? " won" : "") },
      h("header", { class: "ch-head" }, h("span", { class: "ch-badge", html: icon(c.icon || "target") }), h("h4", {}, `Challenge ${idx + 1}: ${c.title}`), h("span", { class: "ch-level" }, c.level || "Core"), stars),
      h("div", { class: "ch-body" },
        h("div", {}, h("p", { class: "ch-goal", html: "<b>Goal:</b> " + c.goal }), lockable, h("div", { class: "ch-actions" }, check, hintB, solB), fb),
        h("div", {}, live, view)));
    // predict-first step
    if (c.predict) {
      lockable.style.opacity = 0.35; lockable.style.pointerEvents = "none"; check.disabled = true;
      const pq = h("div", { class: "q ch-predict" }, h("p", {}, h("b", {}, "Predict first: "), c.predict.q));
      const opts = h("div", { class: "opts" });
      c.predict.options.forEach((o, i) => opts.append(h("button", { class: "opt", type: "button", onclick: (e) => {
        if (predicted) return; predicted = true; $$(".opt", opts).forEach((b, j) => { b.disabled = true; if (j === c.predict.answer) b.classList.add("right"); });
        if (i !== c.predict.answer) e.currentTarget.classList.add("wrong");
        pq.append(h("p", { class: "small muted" }, (i === c.predict.answer ? "Good instinct. " : "Not quite, but now test it. ") + "Now use the sliders to check it with the model."));
        lockable.style.opacity = 1; lockable.style.pointerEvents = "auto"; check.disabled = false;
      } }, o)));
      pq.append(opts); lockable.before(pq);
    }
    check.addEventListener("click", () => {
      const v = draw(); tries++;
      if (hit(c, v)) {
        const s = Math.max(1, 4 - tries); if (!solved || s > (store.load()[key] || 0)) { const d = store.load(); d[key] = Math.max(s, d[key] || 0); store.save(d); }
        solved = true; el.classList.add("won"); stars.textContent = "★".repeat(store.load()[key]) + "☆".repeat(3 - store.load()[key]);
        fb.className = "ch-fb ok"; fb.innerHTML = `<b>Goal reached${tries === 1 ? " on the first try" : ""}.</b> ${c.explain}`; burst(el); onScore();
      } else {
        el.classList.remove("shake"); void el.offsetWidth; el.classList.add("shake");
        const dir = c.op === "<=" ? "too high" : c.op === ">=" ? "too low" : v > c.target ? "too high" : "too low";
        fb.className = "ch-fb no"; fb.innerHTML = `<b>Not yet:</b> ${c.metricLabel || "the result"} is ${fmt(v, c.digits || 0)}${c.unit || ""}, ${dir}. ${tries >= 1 && c.hint ? "Try the hint." : ""}`;
        if (c.hint) hintB.hidden = false; if (tries >= 3 && c.solution) solB.hidden = false;
      }
    });
    hintB.addEventListener("click", () => { fb.className = "ch-fb no"; fb.innerHTML = `<b>Hint:</b> ${c.hint}`; });
    solB.addEventListener("click", () => {
      Object.entries(c.solution).forEach(([k, val]) => { const w = ctrls.find((x) => x.k && x.k.id === k); if (w) { w.inp.value = val; w.inp.dispatchEvent(new Event("input")); } });
      fb.className = "ch-fb no"; fb.innerHTML = "<b>One solution is set on the sliders.</b> Press Check to confirm it, then try to find another.";
    });
    draw();
    return el;
  }

  function mountChallenges() {
    $$(".challenges[data-module]").forEach((root) => {
      const mid = root.dataset.module, list = (window.CHALLENGES || {})[mid]; if (!list) return;
      const ring = h("div", { class: "ch-score" }), cards = [];
      const upd = () => {
        const d = store.load(), got = list.reduce((a, _, i) => a + (d[`${mid}:${i}`] || 0), 0), max = list.length * 3, frac = got / max, C = 2 * Math.PI * 26;
        ring.innerHTML = `<svg class="ch-ring" viewBox="0 0 64 64"><circle class="bg" cx="32" cy="32" r="26"/><circle class="fg" cx="32" cy="32" r="26" stroke-dasharray="${C}" stroke-dashoffset="${C * (1 - frac)}"/><text x="32" y="37" text-anchor="middle">${got}/${max}</text></svg><div><b>Your simulation score</b><br><span class="small muted">${list.length} challenges · three stars for a first-try solve, fewer after misses. Saved in this browser.</span></div>`;
      };
      upd(); root.append(ring); list.forEach((c, i) => { const el = card(c, i, mid, upd); cards.push(el); root.append(el); });
    });
  }

  // ------------------------------------------------------------------ every quiz: progress bar, animations, celebration
  function quizFx() {
    $$(".quiz").forEach((qz) => {
      const items = $$(".q", qz); if (!items.length || qz.querySelector(".quiz-progress")) return;
      const bar = h("div", { class: "quiz-progress", "aria-hidden": "true" }, h("span")); qz.prepend(bar);
      const upd = () => { const n = items.filter((q) => q.dataset.done).length; bar.firstChild.style.width = (100 * n) / items.length + "%"; };
      qz.addEventListener("click", (e) => {
        const b = e.target.closest(".opt"); if (!b) return;
        setTimeout(() => {
          b.classList.add(b.classList.contains("wrong") ? "fx-wrong" : "fx-right"); upd();
          const res = $(".quiz-result", qz); if (res && !res.hidden && items.every((q) => q.dataset.done === "right")) { qz.style.position = "relative"; burst(qz); }
        }, 0);
      });
      const again = $(".quiz-again", qz); again && again.addEventListener("click", () => { setTimeout(upd, 0); $$(".opt", qz).forEach((o) => o.classList.remove("fx-right", "fx-wrong")); });
    });
  }

  // ------------------------------------------------------------------ concept-thread recall buttons and figure pause
  function misc() {
    $$(".thread-recall button").forEach((b) => b.addEventListener("click", () => { const r = b.closest(".thread-recall"); r.classList.toggle("open"); b.textContent = r.classList.contains("open") ? "Hide" : "Show answer"; }));
    $$(".figure-card .fig-play").forEach((b) => b.addEventListener("click", () => { const f = b.closest(".figure-card"); const p = f.classList.toggle("paused"); b.textContent = p ? "Play animation" : "Pause animation"; const s = f.querySelector("svg"); if (s && s.pauseAnimations) p ? s.pauseAnimations() : s.unpauseAnimations(); }));
  }
  function init() { mountChallenges(); quizFx(); misc(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
