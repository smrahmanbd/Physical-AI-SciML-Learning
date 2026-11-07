/* Prezi-style zooming mind maps. Any element .mm[data-mm=KEY] is mounted with window.MINDMAPS[KEY].
   Data: {title, center, subtitle, promise, branches:[{id, title, sys, href, hrefLabel, summary, notes[], leaves:[string | {t, n}]}]}
   Interaction: guided path (Start/Back/Next), click a branch to zoom, click an idea for its explanation,
   "Test yourself" hides ideas until clicked, wheel or pinch to zoom, drag to pan, F for full screen. */
(function () {
  "use strict";
  const NS = "http://www.w3.org/2000/svg";
  const reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  const el = (t, a, p) => { const e = document.createElementNS(NS, t); for (const k in a) e.setAttribute(k, a[k]); if (p) p.append(e); return e; };
  const wrap = (t, n) => { const w = String(t).split(/\s+/), o = []; let c = ""; w.forEach((x) => { if (c && (c + " " + x).length > n) { o.push(c); c = x; } else c = (c + " " + x).trim(); }); if (c) o.push(c); return o; };
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  function texts(g, x, y, lines, size, cls, color) {
    const lh = size * 1.18; let ty = y - (lines.length * lh) / 2 + size * 0.85;
    lines.forEach((l) => { const t = el("text", { x, y: ty, "text-anchor": "middle", class: cls, style: `font-size:${size}px` + (color ? `;fill:${color}` : "") }, g); t.textContent = l; ty += lh; });
  }

  const SYSICON = { economy: "cpu", energy: "flask", land: "gear", water: "radar", climate: "shield", policy: "car", neutral: "layers", data: "chart" };
  function icon(g, name, cx, cy, r, sys) {
    const P = (window.GCAM_ICONS || {})[name]; if (!P) return;
    const ig = el("g", { class: `mm-icon sys-${sys}` }, g);
    el("circle", { cx, cy, r, class: "mm-icon-bg" }, ig);
    const k = (r * 1.15) / 24;
    el("path", { d: P, transform: `translate(${cx - 12 * k},${cy - 12 * k}) scale(${k})`, class: "mm-icon-path", fill: "none", "stroke-width": 1.9 / 1, "stroke-linecap": "round", "stroke-linejoin": "round" }, ig);
  }

  function mount(root, D) {
    const svg = root.querySelector(".mm-svg"), stage = root.querySelector(".mm-stage"), notes = root.querySelector(".mm-notes"), stepEl = root.querySelector(".mm-step");
    const btn = (c) => root.querySelector(".mm-" + c);
    const n = D.branches.length, R1 = n > 6 ? 700 : n > 5 ? 640 : 500, LW = 280, LH = 62, GAP = 14;
    const frames = [], bboxes = [], groups = [], leafGroups = [];
    const gl = el("g", {}, svg), gn = el("g", {}, svg);

    // centre: size grows with the title
    const cl = wrap(D.center, 18), sub = D.subtitle ? wrap(D.subtitle, 30) : [];
    const CW = 460, CH = Math.max(150, cl.length * 44 + sub.length * 30 + 44);
    const gc = el("g", { class: "node center" }, gn);
    el("rect", { x: -CW / 2, y: -CH / 2, width: CW, height: CH, rx: 18, style: "fill:var(--ink)" }, gc);
    const subH = sub.length * 30;
    texts(gc, 0, -subH / 2, cl, 38, "node-label", "var(--paper)");
    texts(gc, 0, (cl.length * 44) / 2, sub, 24, "node-sub", "var(--paper)");
    icon(gc, D.icon || "globe", 0, -CH / 2 - 58, 44, "center");
    gc.style.setProperty("--d", "0s");
    const all = { x0: -CW / 2, y0: -CH / 2, x1: CW / 2, y1: CH / 2 };
    const grow = (b, x0, y0, x1, y1) => { b.x0 = Math.min(b.x0, x0); b.y0 = Math.min(b.y0, y0); b.x1 = Math.max(b.x1, x1); b.y1 = Math.max(b.y1, y1); };

    D.branches.forEach((b, i) => {
      const a = -Math.PI / 2 + (2 * Math.PI * i) / n, ux = Math.cos(a), uy = Math.sin(a), side = Math.abs(ux) > 0.35;
      const bx = R1 * ux, by = R1 * uy, BW = 320, blines = wrap(b.title, 22).slice(0, 3), BH = 34 + 30 * (blines.length + (b.id ? 1 : 0));
      const g = el("g", { class: `node br sys-${b.sys}`, tabindex: 0, role: "button", "aria-label": `${b.id ? b.id + ": " : ""}${b.title}. Zoom in` }, gn);
      const dly = 0.25 + i * 0.12;
      g.style.setProperty("--d", dly + "s");
      const lk = el("path", { d: `M0,0 C${R1 * 0.45 * ux},${R1 * 0.45 * uy} ${bx - 140 * ux},${by - 140 * uy} ${bx},${by}`, class: `sysstroke-${b.sys} mm-link`, "data-b": i, fill: "none", "stroke-width": 7, opacity: 0.55 }, gl);
      lk.style.setProperty("--d", dly - 0.15 + "s");
      el("rect", { x: bx - BW / 2, y: by - BH / 2, width: BW, height: BH, rx: 16, class: "node-box", "stroke-width": 2.5 }, g);
      texts(g, bx, by, (b.id ? [String(b.id)] : []).concat(blines), 24, "node-label");
      icon(g, b.icon || SYSICON[b.sys] || "bulb", bx - BW / 2 + 10, by - BH / 2 + 6, 26, b.sys);
      const bb = { x0: bx - BW / 2, y0: by - BH / 2, x1: bx + BW / 2, y1: by + BH / 2 };
      const k = b.leaves.length, H = k * LH + (k - 1) * GAP;
      const ax = side ? bx + Math.sign(ux) * (BW / 2 + 90 + LW / 2) : bx;
      const ay = side ? by : by + Math.sign(uy) * (BH / 2 + 60 + H / 2);
      const lgs = [];
      b.leaves.forEach((lf, j) => {
        const t = typeof lf === "string" ? lf : lf.t, note = typeof lf === "string" ? "" : lf.n || "";
        const ly = ay - H / 2 + LH / 2 + j * (LH + GAP), lx = ax;
        const ll = el("path", { d: `M${bx + (side ? Math.sign(ux) * BW / 2 : 0)},${by + (side ? 0 : Math.sign(uy) * BH / 2)} L${lx - (side ? Math.sign(ux) * LW / 2 : 0)},${ly}`, class: `sysstroke-${b.sys} mm-link`, "data-b": i, fill: "none", "stroke-width": 2.5, opacity: 0.6 }, gl);
        const lg = el("g", { class: `node leaf sys-${b.sys}`, tabindex: 0, role: "button", "aria-label": t }, gn);
        const ld = dly + 0.35 + j * 0.08; lg.style.setProperty("--d", ld + "s"); ll.style.setProperty("--d", ld - 0.1 + "s");
        el("rect", { x: lx - LW / 2, y: ly - LH / 2, width: LW, height: LH, rx: 14, class: "node-box", "stroke-width": 2, style: "fill:var(--card)" }, lg);
        texts(lg, lx, ly, wrap(t, 26).slice(0, 2), 18, "node-label leaf-label", "var(--ink)");
        const q = el("text", { x: lx, y: ly + 8, "text-anchor": "middle", class: "leaf-q", style: "font-size:24px" }, lg); q.textContent = "?";
        if (typeof lf === "object" && lf.i) icon(lg, lf.i, lx - LW / 2 + 4, ly - LH / 2 + 4, 15, b.sys);
        grow(bb, lx - LW / 2, ly - LH / 2, lx + LW / 2, ly + LH / 2);
        const info = { g: lg, t, note, branch: i, view: { x: lx - LW * 1.8, y: ly - LW * 1.1, w: LW * 3.6, h: LW * 2.2 } };
        lgs.push(info);
        const pick = () => { lg.classList.add("shown"); showLeaf(info); };
        lg.addEventListener("click", (e) => { if (dragged) return; e.stopPropagation(); pick(); });
        lg.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); e.stopPropagation(); pick(); } });
      });
      leafGroups.push(lgs);
      grow(all, bb.x0, bb.y0, bb.x1, bb.y1);
      bboxes.push(bb); groups.push(g);
      g.addEventListener("click", () => { if (!dragged) go(i + 1); });
      g.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(i + 1); } });
    });

    const pad = (b, p) => ({ x: b.x0 - p, y: b.y0 - p, w: b.x1 - b.x0 + 2 * p, h: b.y1 - b.y0 + 2 * p });
    frames.push({ view: pad(all, 60), kind: "all" });
    D.branches.forEach((b, i) => frames.push({ view: pad(bboxes[i], 80), branch: i }));
    frames.push({ view: pad(all, 60), kind: "end" });
    let cur = 0, anim = null, view = Object.assign({}, frames[0].view), dragged = false;
    const setVB = (v) => svg.setAttribute("viewBox", `${v.x} ${v.y} ${v.w} ${v.h}`);
    setVB(view);
    function fly(to) {
      cancelAnimationFrame(anim);
      if (reduce) { view = Object.assign({}, to); setVB(view); return; }
      const from = Object.assign({}, view), t0 = performance.now(), dur = 900;
      const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
      const tick = (now) => { const t = Math.min(1, (now - t0) / dur), e = ease(t); ["x", "y", "w", "h"].forEach((k) => (view[k] = from[k] + (to[k] - from[k]) * e)); setVB(view); if (t < 1) anim = requestAnimationFrame(tick); };
      anim = requestAnimationFrame(tick);
    }
    const dim = (bi, leaf) => {
      groups.forEach((g, j) => (g.style.opacity = bi == null || bi === j ? 1 : 0.35));
      leafGroups.forEach((ls, j) => ls.forEach((l) => { l.g.style.opacity = bi == null || bi === j ? 1 : 0.35; l.g.classList.toggle("picked", l === leaf); }));
      gl.querySelectorAll(".mm-link").forEach((p) => p.classList.toggle("flow", bi != null && +p.dataset.b === bi));
    };
    const recall = () => root.classList.contains("recall");
    function branchNotes(b, i) {
      const items = leafGroups[i].map((l) => (recall() && !l.g.classList.contains("shown") ? `<li class="muted">? (select it on the map)</li>` : `<li><b>${esc(l.t)}</b>${l.note ? ". " + esc(l.note) : ""}</li>`)).join("");
      const rem = b.notes && b.notes.length ? `<b>Remember</b><ul>${b.notes.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>` : "";
      const img = b.img ? `<img class="mm-img" src="${esc(b.img)}" alt="" loading="lazy">` : "";
      return `${img}<h3>${b.id ? esc(b.id) + " · " : ""}${esc(b.title)}</h3><p>${esc(b.summary || "")}</p><ul class="mm-ideas">${items}</ul>${rem}${b.href ? `<a href="${b.href}">${esc(b.hrefLabel || "Open")}</a>` : ""}`;
    }
    function go(i) {
      cur = Math.max(0, Math.min(frames.length - 1, i)); const f = frames[cur];
      fly(f.view); dim(f.branch);
      stepEl.textContent = `${cur + 1} / ${frames.length}`;
      if (f.branch != null) notes.innerHTML = branchNotes(D.branches[f.branch], f.branch);
      else if (f.kind === "all") notes.innerHTML = `<h3>${esc(D.title)}</h3><p>${esc(D.promise || "")}</p><p class="small muted">${n} branches. Press Next to zoom into each one, or select any box. Turn on <i>Test yourself</i> to hide the ideas and recall them first.</p>`;
      else notes.innerHTML = `<h3>${esc(D.title)}</h3><p>That is the whole map.${recall() ? ` You revealed ${root.querySelectorAll(".leaf.shown").length} of ${root.querySelectorAll(".leaf").length} ideas.` : ""} Select any box to revisit it.</p>`;
    }
    function showLeaf(info) {
      const b = D.branches[info.branch];
      cur = info.branch + 1; stepEl.textContent = `${cur + 1} / ${frames.length}`;
      fly(info.view); dim(info.branch, info);
      notes.innerHTML = `<p class="small muted">${b.id ? esc(b.id) + " · " : ""}${esc(b.title)}</p><h3>${esc(info.t)}</h3><p>${esc(info.note || b.summary || "")}</p><p><button class="btn quiet mm-back-branch" type="button">Back to the branch</button></p>${b.href ? `<a href="${b.href}">${esc(b.hrefLabel || "Open")}</a>` : ""}`;
      notes.querySelector(".mm-back-branch").addEventListener("click", () => go(info.branch + 1));
    }

    btn("start").addEventListener("click", () => { go(0); stage.focus(); });
    btn("next").addEventListener("click", () => go(cur + 1));
    btn("prev").addEventListener("click", () => go(cur - 1));
    btn("all").addEventListener("click", () => go(0));
    const rb = btn("recall");
    if (rb) rb.addEventListener("click", () => {
      const on = root.classList.toggle("recall"); rb.setAttribute("aria-pressed", on);
      root.querySelectorAll(".leaf").forEach((l) => l.classList.remove("shown"));
      go(cur);
    });
    const full = () => { if (document.fullscreenElement) document.exitFullscreen(); else if (stage.requestFullscreen) stage.requestFullscreen(); };
    btn("full").addEventListener("click", full);
    stage.addEventListener("keydown", (e) => {
      if (e.target.closest && e.target.closest(".leaf") && (e.key === "Enter" || e.key === " ")) return;
      if (["ArrowRight", "PageDown"].includes(e.key) || (e.key === " " && e.target === stage)) { e.preventDefault(); go(cur + 1); }
      else if (["ArrowLeft", "PageUp"].includes(e.key)) { e.preventDefault(); go(cur - 1); }
      else if (e.key === "Escape" || e.key === "Home") go(0);
      else if (e.key === "f" || e.key === "F") full();
      else if (e.key === "+" || e.key === "=") zoomAt(0.8);
      else if (e.key === "-") zoomAt(1.25);
    });

    // free navigation: wheel/pinch zoom and drag to pan
    const toSvg = (cx, cy) => { const r = svg.getBoundingClientRect(), s = Math.max(view.w / r.width, view.h / r.height); return { x: view.x + (cx - r.left - (r.width - view.w / s) / 2) * s, y: view.y + (cy - r.top - (r.height - view.h / s) / 2) * s, s }; };
    function zoomAt(f, cx, cy) {
      cancelAnimationFrame(anim);
      const r = svg.getBoundingClientRect(); const p = toSvg(cx == null ? r.left + r.width / 2 : cx, cy == null ? r.top + r.height / 2 : cy);
      const w = Math.min(frames[0].view.w * 2.5, Math.max(300, view.w * f)), k = w / view.w;
      view = { x: p.x - (p.x - view.x) * k, y: p.y - (p.y - view.y) * k, w, h: view.h * k }; setVB(view);
    }
    svg.addEventListener("wheel", (e) => { e.preventDefault(); zoomAt(e.deltaY > 0 ? 1.12 : 1 / 1.12, e.clientX, e.clientY); }, { passive: false });
    const ptrs = new Map(); let start = null, pinch0 = 0;
    svg.addEventListener("pointerdown", (e) => { ptrs.set(e.pointerId, e); dragged = false; start = { x: e.clientX, y: e.clientY, v: Object.assign({}, view) }; if (ptrs.size === 2) { const [a, b] = [...ptrs.values()]; pinch0 = Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY); } });
    svg.addEventListener("pointermove", (e) => {
      if (!ptrs.has(e.pointerId) || !start) return;
      ptrs.set(e.pointerId, e);
      if (ptrs.size === 2) { const [a, b] = [...ptrs.values()], d = Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY); if (pinch0) { zoomAt(pinch0 / d, (a.clientX + b.clientX) / 2, (a.clientY + b.clientY) / 2); pinch0 = d; } dragged = true; return; }
      const dx = e.clientX - start.x, dy = e.clientY - start.y;
      if (!dragged && Math.hypot(dx, dy) < 6) return;
      if (!dragged) { dragged = true; svg.setPointerCapture(e.pointerId); cancelAnimationFrame(anim); }
      const r = svg.getBoundingClientRect(), s = Math.max(start.v.w / r.width, start.v.h / r.height);
      view = Object.assign({}, start.v, { x: start.v.x - dx * s, y: start.v.y - dy * s }); setVB(view); svg.classList.add("dragging");
    });
    const up = (e) => { ptrs.delete(e.pointerId); if (!ptrs.size) { start = null; pinch0 = 0; svg.classList.remove("dragging"); setTimeout(() => (dragged = false), 0); } };
    svg.addEventListener("pointerup", up); svg.addEventListener("pointercancel", up);

    if (!reduce) { svg.classList.add("mm-intro"); setTimeout(() => svg.classList.remove("mm-intro"), 4200); }
    go(0);
    return { go, frames: frames.length };
  }

  function init() {
    const maps = window.MINDMAPS || {};
    document.querySelectorAll(".mm[data-mm]").forEach((root, i) => {
      const D = maps[root.dataset.mm]; if (!D || root.dataset.mounted) return;
      root.dataset.mounted = "1";
      const api = mount(root, D);
      if (i === 0) { window.MINDMAP_GO = api.go; window.MINDMAP_FRAMES = api.frames; }
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
