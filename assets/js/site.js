/* GCAM Learning: diagrams, narration, in-browser Python, quizzes, progress. No build step needed. */
(function () {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const NS = "http://www.w3.org/2000/svg";
  const reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  const h = (tag, attrs = {}, ...kids) => { const e = document.createElement(tag); for (const [k, v] of Object.entries(attrs || {})) { if (v == null || v === false) continue; if (k === "class") e.className = v; else if (k === "html") e.innerHTML = v; else if (k.startsWith("on")) e.addEventListener(k.slice(2), v); else e.setAttribute(k, v); } kids.flat().forEach((c) => c != null && e.append(c.nodeType ? c : document.createTextNode(String(c)))); return e; };
  const s = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.append(e); return e; };

  // ---------------- progress (this browser only) ----------------
  const KEY = "sciml-learning-progress-v1";
  const P = { load() { try { return JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { return {}; } },
    save(d) { try { localStorage.setItem(KEY, JSON.stringify(d)); } catch (e) { /* storage blocked */ } },
    mark(id, k, v = true) { const d = P.load(); d[id] = d[id] || {}; d[id][k] = v; P.save(d); document.dispatchEvent(new CustomEvent("progress")); } };
  window.GCAMProgress = P;

  // ---------------- interactive diagrams ----------------
  function diagram(host, data, opts = {}) {
    const W = data.width || 900, H = data.height || 520;
    const svg = s("svg", { viewBox: `0 0 ${W} ${H}`, class: "dg", role: "img", "aria-label": data.title || "Diagram" });
    const defs = s("defs", {}, svg);
    ["economy", "energy", "land", "water", "climate", "policy", "data", "neutral"].forEach((k) => {
      const m = s("marker", { id: `ah-${k}-${host.id}`, viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: "auto-start-reverse" }, defs);
      s("path", { d: "M0,0 L10,5 L0,10 z", class: `sysfill-${k}` }, m);
    });
    const nodes = {}; (data.nodes || []).forEach((n) => (nodes[n.id] = Object.assign({ w: 150, h: 60, sys: "neutral" }, n)));
    const eg = s("g", { class: "edges" }, svg), ng = s("g", { class: "nodes" }, svg);
    const port = (n, tx, ty) => { const dx = tx - n.x, dy = ty - n.y; if (!dx && !dy) return [n.x, n.y]; const k = Math.min(dx ? (n.w / 2 + 3) / Math.abs(dx) : 1e9, dy ? (n.h / 2 + 3) / Math.abs(dy) : 1e9); return [n.x + dx * k, n.y + dy * k]; };
    const edgeEls = [];
    (data.edges || []).forEach((e, i) => {
      const a = nodes[e.from], b = nodes[e.to]; if (!a || !b) return;
      const back = (data.edges || []).some((f) => f.from === e.to && f.to === e.from);
      const [x1, y1] = port(a, b.x, b.y), [x2, y2] = port(b, a.x, a.y);
      const len = Math.hypot(x2 - x1, y2 - y1) || 1, bend = e.bend != null ? e.bend : back ? 0.32 : 0;
      const mx = (x1 + x2) / 2 - bend * (y2 - y1), my = (y1 + y2) / 2 + bend * (x2 - x1);
      const sys = e.sys || a.sys;
      const g = s("g", { class: "edge", "data-from": e.from, "data-to": e.to }, eg);
      s("path", { d: `M${x1},${y1} Q${mx},${my} ${x2},${y2}`, class: `edge-line sysstroke-${sys}`, "marker-end": `url(#ah-${sys}-${host.id})` }, g);
      s("path", { d: `M${x1},${y1} Q${mx},${my} ${x2},${y2}`, class: `edge-flow sysstroke-${sys}` }, g);
      if (e.label) {
        const lx = (x1 + 2 * mx + x2) / 4, ly = (y1 + 2 * my + y2) / 4;
        const t = s("text", { x: lx, y: ly + 4, class: "edge-label", "text-anchor": "middle" }, g); t.textContent = e.label;
        requestAnimationFrame(() => { try { const bb = t.getBBox(); const r = s("rect", { x: bb.x - 4, y: bb.y - 1, width: bb.width + 8, height: bb.height + 2, rx: 4, class: "edge-plate" }); g.insertBefore(r, t); } catch (err) { /* hidden */ } });
      }
      edgeEls.push(g);
    });
    const detail = h("div", { class: "dg-detail", "aria-live": "polite" }, h("p", { class: "muted" }, opts.hint || "Select a box to see what it does."));
    const nodeEls = {};
    Object.values(nodes).forEach((n) => {
      const g = s("g", { class: `node sys-${n.sys}`, tabindex: 0, role: "button", "aria-label": n.label + (n.sub ? ": " + n.sub : ""), "data-id": n.id }, ng);
      s("rect", { x: n.x - n.w / 2, y: n.y - n.h / 2, width: n.w, height: n.h, rx: 12, class: "node-box" }, g);
      const lines = wrap(n.label, Math.max(8, Math.floor(n.w / 9.5)));
      const subl = n.sub ? wrap(n.sub, Math.max(10, Math.floor(n.w / 7.4))) : [];
      const tot = lines.length * 17 + subl.length * 14; let y = n.y - tot / 2 + 13;
      lines.forEach((l) => { const t = s("text", { x: n.x, y, class: "node-label", "text-anchor": "middle" }, g); t.textContent = l; y += 17; });
      subl.forEach((l) => { const t = s("text", { x: n.x, y: y + 1, class: "node-sub", "text-anchor": "middle" }, g); t.textContent = l; y += 14; });
      const pick = () => { $$(".node", svg).forEach((x) => x.classList.remove("picked")); g.classList.add("picked"); focus([n.id], [], false);
        const lv = host.dataset.level; const dt = n.detail && typeof n.detail === "object" ? (n.detail[lv] || n.detail["1"]) : n.detail;
        detail.innerHTML = ""; detail.append(h("h4", { class: `sysink-${n.sys}` }, n.label), h("div", { html: dt || n.sub || "" })); if (opts.onPick) opts.onPick(n); };
      g.addEventListener("click", pick); g.addEventListener("keydown", (ev) => { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); pick(); } });
      nodeEls[n.id] = g;
    });
    function focus(ids, edges, dimOthers = true) {
      svg.classList.toggle("dimmed", dimOthers && ids.length > 0);
      Object.entries(nodeEls).forEach(([id, g]) => g.classList.toggle("on", ids.includes(id)));
      edgeEls.forEach((g) => { const on = edges.some(([a, b]) => g.dataset.from === a && g.dataset.to === b) || (!edges.length && ids.includes(g.dataset.from) && ids.includes(g.dataset.to)); g.classList.toggle("on", on); });
    }
    // tour controls
    const tour = data.tour || [];
    let k = -1, timer = null;
    const cap = h("p", { class: "dg-caption" }, data.caption || "");
    const counter = h("span", { class: "dg-count" }, tour.length ? `${tour.length} steps` : "");
    function show(i) {
      k = Math.max(0, Math.min(tour.length - 1, i)); const t = tour[k];
      focus(t.focus || [], t.edges || []); cap.textContent = t.text; counter.textContent = `Step ${k + 1} of ${tour.length}`;
      if (opts.id && k === tour.length - 1) P.mark(opts.id, "tour");
    }
    const bPlay = h("button", { class: "btn", type: "button" }, "Play the walkthrough");
    const bPrev = h("button", { class: "btn quiet", type: "button", "aria-label": "Previous step" }, "Back");
    const bNext = h("button", { class: "btn quiet", type: "button", "aria-label": "Next step" }, "Next");
    const bReset = h("button", { class: "btn quiet", type: "button" }, "Show all");
    const stop = () => { clearInterval(timer); timer = null; bPlay.textContent = "Play the walkthrough"; };
    bPlay.addEventListener("click", () => { if (timer) return stop(); bPlay.textContent = "Pause"; show(k < 0 || k >= tour.length - 1 ? 0 : k + 1); timer = setInterval(() => { if (k >= tour.length - 1) return stop(); show(k + 1); }, 4200); });
    bPrev.addEventListener("click", () => { stop(); show(k - 1); });
    bNext.addEventListener("click", () => { stop(); show(k + 1); });
    bReset.addEventListener("click", () => { stop(); k = -1; focus([], []); cap.textContent = data.caption || ""; counter.textContent = `${tour.length} steps`; $$(".node", svg).forEach((x) => x.classList.remove("picked")); });
    host.innerHTML = "";
    const controls = tour.length ? h("div", { class: "dg-controls" }, bPlay, bPrev, bNext, bReset, counter) : null;
    host.append(h("div", { class: "dg-stage" }, svg), controls, cap, opts.noDetail ? null : detail);
    if (opts.intro && !reduce) { svg.classList.add("intro"); setTimeout(() => svg.classList.remove("intro"), 2600); }
    host._api = { focus, show, repick: () => { const p = $(".node.picked", svg); if (p) p.dispatchEvent(new Event("click")); } };
    return host._api;
  }
  function wrap(t, n) { const w = String(t).split(/\s+/), out = []; let c = ""; w.forEach((x) => { if (c && (c + " " + x).length > n) { out.push(c); c = x; } else c = (c + " " + x).trim(); }); if (c) out.push(c); return out; }
  window.GCAMDiagram = diagram;

  // ---------------- narration (browser speech) ----------------
  function narration(box) {
    const id = box.dataset.module, texts = { en: $(".narr-en", box).textContent.trim(), ar: $(".narr-ar", box).textContent.trim() };
    let lang = "en";
    const status = $(".narr-status", box), play = $(".narr-play", box), stopB = $(".narr-stop", box);
    const supported = "speechSynthesis" in window;
    if (!supported) { status.textContent = "Your browser cannot read aloud. The transcript is below."; play.disabled = true; stopB.disabled = true; }
    $$(".narr-lang", box).forEach((b) => b.addEventListener("click", () => { lang = b.dataset.lang; $$(".narr-lang", box).forEach((x) => x.setAttribute("aria-pressed", x === b ? "true" : "false")); $(".narr-en", box).hidden = lang !== "en"; $(".narr-ar", box).hidden = lang !== "ar"; if (speechSynthesis.speaking) { speechSynthesis.cancel(); speak(); } }));
    function voiceFor(l) { const vs = speechSynthesis.getVoices(); return vs.find((v) => v.lang && v.lang.toLowerCase().startsWith(l)) || null; }
    function speak() {
      const u = new SpeechSynthesisUtterance(texts[lang]); u.lang = lang === "ar" ? "ar-SA" : "en-GB"; u.rate = lang === "ar" ? 0.95 : 1.0;
      const v = voiceFor(lang); if (v) u.voice = v; else if (lang === "ar") status.textContent = "No Arabic voice found on this device; your browser may use a default voice. Read the Arabic transcript below.";
      u.onstart = () => { play.textContent = "Pause"; status.textContent = lang === "ar" ? "Reading in Arabic" : "Reading in English"; };
      u.onend = () => { play.textContent = "Listen"; status.textContent = "Finished"; P.mark(id, "listened"); };
      speechSynthesis.speak(u);
    }
    play.addEventListener("click", () => {
      if (speechSynthesis.speaking && !speechSynthesis.paused) { speechSynthesis.pause(); play.textContent = "Resume"; return; }
      if (speechSynthesis.paused) { speechSynthesis.resume(); play.textContent = "Pause"; return; }
      speak();
    });
    stopB.addEventListener("click", () => { speechSynthesis.cancel(); play.textContent = "Listen"; status.textContent = ""; });
    window.addEventListener("pagehide", () => supported && speechSynthesis.cancel());
  }

  // ---------------- code blocks: copy, run Python in the browser ----------------
  let pyReady = null;
  function loadPy(status) {
    if (pyReady) return pyReady;
    pyReady = new Promise((res, rej) => {
      status("Loading Python in your browser (about 15 MB, first time only)…");
      const sc = document.createElement("script"); sc.src = "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js";
      sc.onload = async () => { try { const py = await loadPyodide(); status("Loading numpy, scipy and matplotlib…"); await py.loadPackage(["numpy", "scipy", "matplotlib", "pandas"]); await py.runPythonAsync("import matplotlib\nmatplotlib.use('AGG')"); res(py); } catch (e) { rej(e); } };
      sc.onerror = () => rej(new Error("Could not load Python from the CDN. Check your internet connection."));
      document.head.append(sc);
    });
    pyReady.catch(() => { pyReady = null; });
    return pyReady;
  }
  function codeBlocks() {
    $$(".codeblock").forEach((cb) => {
      const area = $("textarea", cb), pre = $("pre code", cb), out = $(".code-out", cb), runB = $(".code-run", cb), copyB = $(".code-copy", cb);
      const getCode = () => (area ? area.value : pre.textContent);
      copyB && copyB.addEventListener("click", async () => { try { await navigator.clipboard.writeText(getCode()); copyB.textContent = "Copied"; setTimeout(() => (copyB.textContent = "Copy"), 1500); } catch (e) { copyB.textContent = "Select and copy"; } });
      const resetB = $(".code-reset", cb); if (resetB && area) { const orig = area.value; resetB.addEventListener("click", () => (area.value = orig)); }
      if (area) { const fit = () => { area.style.height = "auto"; area.style.height = area.scrollHeight + 4 + "px"; }; area.addEventListener("input", fit); setTimeout(fit, 0); area.addEventListener("keydown", (e) => { if (e.key === "Tab") { e.preventDefault(); const p = area.selectionStart; area.setRangeText("    ", p, area.selectionEnd, "end"); } }); }
      runB && runB.addEventListener("click", async () => {
        out.hidden = false; out.innerHTML = ""; const st = h("p", { class: "muted" }); out.append(st);
        runB.disabled = true;
        try {
          const py = await loadPy((m) => (st.textContent = m));
          st.textContent = "Running…"; let text = "";
          py.setStdout({ batched: (x) => (text += x + "\n") }); py.setStderr({ batched: (x) => (text += x + "\n") });
          await py.runPythonAsync("import os, glob\nfor f in glob.glob('*.png'): os.remove(f)");
          await py.runPythonAsync(getCode());
          await py.runPythonAsync("import matplotlib.pyplot as _p\nif _p.get_fignums() and not glob.glob('*.png'): _p.savefig('figure.png', dpi=110)\n_p.close('all')");
          const pngs = py.runPython("import glob\nsorted(glob.glob('*.png'))").toJs();
          out.innerHTML = ""; out.append(h("pre", { class: "stdout" }, text || "(no printed output)"));
          for (const f of pngs) { const data = py.FS.readFile(f); const url = URL.createObjectURL(new Blob([data], { type: "image/png" })); out.append(h("img", { src: url, alt: "Figure produced by the code: " + f })); }
          P.mark(cb.dataset.module, "code");
        } catch (e) { out.innerHTML = ""; out.append(h("pre", { class: "stdout err" }, String(e.message || e).split("\n").slice(-12).join("\n"))); }
        runB.disabled = false;
      });
    });
  }

  // ---------------- quizzes ----------------
  function quizzes() {
    $$(".quiz").forEach((qz) => {
      const id = qz.dataset.module, items = $$(".q", qz), result = $(".quiz-result", qz);
      const score = () => { const ans = items.filter((q) => q.dataset.done); if (ans.length === items.length) { const right = ans.filter((q) => q.dataset.done === "right").length; result.hidden = false; result.textContent = `You got ${right} of ${items.length}. ` + (right === items.length ? "All correct." : "Read the explanations, then try the questions again."); const d = P.load(); const best = Math.max(right, ((d[id] || {}).quiz || {}).best || 0); P.mark(id, "quiz", { best, total: items.length }); } };
      items.forEach((q) => {
        const ans = +q.dataset.answer, btns = $$(".opt", q), fb = $(".fb", q);
        btns.forEach((b, i) => b.addEventListener("click", () => {
          if (q.dataset.done) return; btns.forEach((x, j) => { x.disabled = true; if (j === ans) x.classList.add("right"); });
          if (i !== ans) b.classList.add("wrong"); q.dataset.done = i === ans ? "right" : "wrong"; fb.hidden = false;
          $(".verdict", fb).textContent = i === ans ? "Correct. " : "Not this one. "; score();
        }));
      });
      const again = $(".quiz-again", qz); again && again.addEventListener("click", () => { items.forEach((q) => { delete q.dataset.done; $$(".opt", q).forEach((b) => { b.disabled = false; b.classList.remove("right", "wrong"); }); $(".fb", q).hidden = true; }); result.hidden = true; });
    });
  }

  // ---------------- explorers ----------------
  function explorers() {
    $$(".explorer[data-widget]").forEach((ex) => {
      const f = window.IAMWidgets && window.IAMWidgets[ex.dataset.widget]; const box = $(".explorer-box", ex);
      if (!f) { box.textContent = "This explorer needs JavaScript."; return; }
      f(box, { checklist: [] });
      box.addEventListener("input", () => P.mark(ex.dataset.module, "explorer"), { once: true });
      box.addEventListener("click", (e) => { if (e.target.closest("button")) P.mark(ex.dataset.module, "explorer"); });
    });
  }

  // ---------------- module page: progress marks, outline ----------------
  function modulePage() {
    const m = document.body.dataset.module; if (!m) return;
    P.mark(m, "visited");
    const done = $("#mark-done"); if (done) { const upd = () => { const d = P.load()[m] || {}; done.textContent = d.done ? "Marked as studied" : "Mark this module as studied"; done.setAttribute("aria-pressed", d.done ? "true" : "false"); }; upd(); done.addEventListener("click", () => { const d = P.load()[m] || {}; P.mark(m, "done", !d.done); upd(); }); }
    const links = $$(".outline a"); if ("IntersectionObserver" in window && links.length) {
      const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) links.forEach((a) => a.classList.toggle("here", a.getAttribute("href") === "#" + e.target.id)); }), { rootMargin: "-20% 0px -70% 0px" });
      links.forEach((a) => { const t = document.getElementById(a.getAttribute("href").slice(1)); if (t) io.observe(t); });
    }
  }

  // ---------------- progress page & module list badges ----------------
  function progressViews() {
    const d = P.load();
    $$("[data-progress-for]").forEach((el) => { const r = d[el.dataset.progressFor] || {}; const n = ["visited", "tour", "explorer", "quiz", "done"].filter((k) => r[k]).length; el.dataset.state = r.done ? "done" : n ? "started" : "new"; el.title = r.done ? "Studied" : n ? "Started" : "Not started"; });
    const tbl = $("#progress-table"); if (tbl) {
      $$("tbody tr", tbl).forEach((tr) => { const r = d[tr.dataset.id] || {}; const cells = $$("td.k", tr);
        ["visited", "listened", "tour", "explorer", "code", "quiz", "done"].forEach((k, i) => { const v = r[k]; cells[i].textContent = k === "quiz" ? (v ? `${v.best}/${v.total}` : "–") : v ? "Yes" : "–"; cells[i].classList.toggle("yes", !!v); }); });
      const total = $$("tbody tr", tbl).length, studied = $$("tbody tr", tbl).filter((tr) => (d[tr.dataset.id] || {}).done).length;
      const sum = $("#progress-summary"); if (sum) sum.textContent = `${studied} of ${total} modules marked as studied.`;
      const meter = $("#progress-meter"); if (meter) meter.style.width = (100 * studied / total) + "%";
    }
    const reset = $("#progress-reset"); reset && reset.addEventListener("click", () => { P.save({}); location.reload(); });
    const exp = $("#progress-export"); exp && exp.addEventListener("click", () => { const a = h("a", { href: URL.createObjectURL(new Blob([JSON.stringify(P.load(), null, 2)], { type: "application/json" })), download: "sciml-learning-progress.json" }); document.body.append(a); a.click(); a.remove(); });
  }

  // ---------------- glossary search, labs filter ----------------
  function filters() {
    const g = $("#glossary-search"); if (g) g.addEventListener("input", () => { const q = g.value.trim().toLowerCase(); let n = 0; $$(".gterm").forEach((t) => { const show = !q || t.textContent.toLowerCase().includes(q); t.hidden = !show; n += show; }); $("#glossary-count").textContent = `${n} terms`; });
    const lf = $$(".lab-filter"); lf.forEach((b) => b.addEventListener("click", () => { lf.forEach((x) => x.setAttribute("aria-pressed", x === b ? "true" : "false")); const f = b.dataset.filter; $$(".labrow").forEach((r) => (r.hidden = f !== "all" && !r.dataset.tags.includes(f))); }));
  }

  // ---------------- "same system, three depths" switch ----------------
  function levels() {
    $$(".levels").forEach((box) => {
      const host = $("[data-diagram]", box), btns = $$(".lv", box), blurb = $(".lv-blurb", box);
      btns.forEach((b) => b.addEventListener("click", () => {
        btns.forEach((x) => x.setAttribute("aria-pressed", x === b ? "true" : "false"));
        host.dataset.level = b.dataset.level; if (blurb) blurb.textContent = b.dataset.blurb || "";
        if (host._api) host._api.repick();
      }));
    });
  }
  // ---------------- exit checklists on go pages ----------------
  function exitChecks() {
    $$(".exitcheck").forEach((ul) => {
      const key = ul.dataset.key, d = P.load(), st = (d[key] || {}).items || {};
      const boxes = $$("input[type=checkbox]", ul), msg = $(".exit-msg", ul.parentElement);
      const upd = () => { const n = boxes.filter((b) => b.checked).length; if (msg) msg.textContent = n === boxes.length ? "You are ready for the next go." : `${n} of ${boxes.length} ticked.`; };
      boxes.forEach((b, i) => { b.checked = !!st[i]; b.addEventListener("change", () => { const cur = (P.load()[key] || {}).items || {}; cur[i] = b.checked; P.mark(key, "items", cur); upd(); }); });
      upd();
    });
  }

  // ---------------- theme toggle ----------------
  function theme() {
    const btn = $("#theme"); try { const t = localStorage.getItem("sciml-theme"); if (t) document.documentElement.dataset.theme = t; } catch (e) { }
    btn && btn.addEventListener("click", () => { const cur = document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"); const nx = cur === "dark" ? "light" : "dark"; document.documentElement.dataset.theme = nx; try { localStorage.setItem("sciml-theme", nx); } catch (e) { } $$(".explorer[data-widget]").forEach((ex) => { const f = window.IAMWidgets[ex.dataset.widget]; f && f($(".explorer-box", ex), { checklist: [] }); }); });
  }

  document.addEventListener("DOMContentLoaded", () => {
    theme();
    $$("[data-diagram]").forEach((host) => { const data = window.GCAM_DIAGRAMS && window.GCAM_DIAGRAMS[host.dataset.diagram]; if (data) diagram(host, data, { id: document.body.dataset.module, intro: host.dataset.intro === "1", hint: host.dataset.hint }); });
    $$(".narration").forEach(narration);
    codeBlocks(); quizzes(); explorers(); modulePage(); progressViews(); filters(); levels(); exitChecks();
    document.addEventListener("progress", progressViews);
  });
})();
