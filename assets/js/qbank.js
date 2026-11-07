/* Question bank: filter, reveal (answer + intuition + memory hook), spaced repetition (Leitner boxes, saved in localStorage),
   flashcards and memory-palace walks. Data: window.QBANK, window.QBMETA, window.QBPALACE */
(function () {
  "use strict";
  const Q = window.QBANK || [], META = window.QBMETA || {}, PAL = window.QBPALACE || {};
  const root = document.querySelector(".qb"); if (!root) return;
  const $ = (s) => root.querySelector(s), $$ = (s) => [...root.querySelectorAll(s)];
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const KEY = "sciml-qbank-v1", DAY = 864e5, INTERVALS = [1, 3, 7, 14, 30];
  const hash = (s) => { let h = 5381; for (let i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0; return (h >>> 0).toString(36); };
  Q.forEach((d) => (d.id = d.m + "|" + hash(d.q)));
  let marks = {};
  try { marks = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { marks = {}; }
  for (const k in marks) if (typeof marks[k] === "string") marks[k] = { s: marks[k], b: marks[k] === "known" ? 1 : 0, d: Date.now() };
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(marks)); } catch (e) { /* storage unavailable */ } };
  const stat = (id) => (marks[id] ? marks[id].s : undefined);
  const isDue = (id) => !marks[id] || marks[id].d <= Date.now();
  const when = (id) => {
    const m = marks[id]; if (!m) return "";
    const days = Math.round((m.d - Date.now()) / DAY);
    return days <= 0 ? "Due for review now." : `Next review in ${days} day${days === 1 ? "" : "s"} (box ${m.b} of 5).`;
  };

  const params = new URLSearchParams(location.search);
  const st = { go: 0, module: "", search: "", status: "all", kinds: new Set(["Recall", "Explain", "Calculate", "Apply"]), view: "list", order: null, card: 0, revealAll: false, hideScenes: false };
  if (params.get("m")) { st.module = params.get("m"); st.go = +st.module.split(".")[0]; }
  else if (params.get("go")) st.go = +params.get("go") || 0;
  if (["list", "cards", "palace"].includes(params.get("view"))) st.view = params.get("view");

  const modSel = $(".qb-module"), search = $(".qb-search"), status = $(".qb-status");
  modSel.value = st.module;

  function filtered() {
    const s = st.search.trim().toLowerCase();
    let list = Q.filter((d) => (!st.go || d.g === st.go) && (!st.module || d.m === st.module) && st.kinds.has(d.k)
      && (!s || (d.q + " " + d.a + " " + d.it + " " + d.hk + " " + (META.titles[d.m] || "")).toLowerCase().includes(s))
      && (st.status === "all" || (st.status === "due" ? isDue(d.id) : st.status === "new" ? !marks[d.id] : stat(d.id) === st.status)));
    if (st.order) { const pos = new Map(st.order.map((i, j) => [i, j])); list = list.slice().sort((a, b) => pos.get(a.i) - pos.get(b.i)); }
    return list;
  }

  function markBtns(d) {
    const m = stat(d.id);
    return `<div class="qb-mark" role="group" aria-label="How did you do?"><button class="btn quiet qb-known" type="button" aria-pressed="${m === "known"}" data-id="${d.id}">I knew it</button><button class="btn quiet qb-review" type="button" aria-pressed="${m === "review"}" data-id="${d.id}">Review again</button><span class="qb-when small muted" data-when="${d.id}">${when(d.id)}</span></div>`;
  }
  const answerHtml = (d) => `<p><b>Model answer.</b> ${esc(d.a)}</p>
<p class="qb-intuition"><b>Intuition.</b> ${esc(d.it)}</p>
<p class="qb-hook"><b>Memory hook.</b> ${esc(d.hk)}</p>${markBtns(d)}`;
  function tag(d) {
    return `<p class="qb-meta"><span class="golevel">Go ${d.g}</span> <a href="modules/${META.slugs[d.m]}.html">Module ${d.m} · ${esc(META.titles[d.m])}</a> <span class="qb-k qb-k-${d.k.toLowerCase()}">${d.k}</span></p>`;
  }
  function itemHtml(d, n) {
    const m = stat(d.id);
    return `<article class="qb-item ${m ? "is-" + m : ""}" data-id="${d.id}">${tag(d)}
<h3><span class="qb-n">${n}.</span> ${esc(d.q)}</h3>
<div class="qb-actions"><button class="btn qb-show" type="button" aria-expanded="${st.revealAll}">${st.revealAll ? "Hide answer" : "Show answer"}</button><button class="btn quiet qb-hint" type="button">Hint</button><button class="btn quiet qb-write" type="button">Write my answer first</button></div>
<p class="qb-hintbox" hidden><b>Hint (memory hook).</b> ${esc(d.hk)}</p>
<textarea class="qb-draft" rows="3" hidden aria-label="Your answer (not saved)" placeholder="Your answer, in your own words (not saved)"></textarea>
<div class="qb-answer"${st.revealAll ? "" : " hidden"}>${answerHtml(d)}</div></article>`;
  }

  function renderList(list) {
    let html = "", last = "";
    list.forEach((d, j) => {
      if (!st.order && d.m !== last) { html += `<h2 class="qb-mod">Module ${d.m}: ${esc(META.titles[d.m])}</h2>`; last = d.m; }
      html += itemHtml(d, j + 1);
    });
    $(".qb-list").innerHTML = html || `<p class="muted">No questions match these filters.${st.status === "due" ? " Nothing is due: well done. Come back tomorrow." : ""}</p>`;
  }

  function renderCards(list) {
    const box = $(".qb-cards");
    if (!list.length) { box.innerHTML = `<p class="muted">No questions match these filters.${st.status === "due" ? " Nothing is due: well done." : ""}</p>`; return; }
    st.card = Math.max(0, Math.min(list.length - 1, st.card));
    const d = list[st.card];
    box.innerHTML = `<div class="qb-card" tabindex="0" data-id="${d.id}">${tag(d)}<p class="qb-count muted small">Card ${st.card + 1} of ${list.length}</p>
<h3 class="qb-front">${esc(d.q)}</h3>
<p class="qb-hintbox" hidden><b>Hint (memory hook).</b> ${esc(d.hk)}</p>
<div class="qb-answer" hidden>${answerHtml(d)}</div>
<div class="btnrow"><button class="btn quiet qb-prev" type="button">Previous</button><button class="btn quiet qb-hint" type="button">Hint</button><button class="btn qb-flip" type="button">Show answer</button><button class="btn quiet qb-next" type="button">Next</button></div>
<p class="muted small">Keys: Space to flip, H for a hint, arrows to move, 1 = I knew it, 2 = Review again.</p></div>`;
  }

  function renderPalace() {
    const goes = st.go ? [st.go] : [1, 2, 3];
    let html = `<p class="prose">A memory palace (the method of loci) uses a route you already know as shelves for new ideas. Walk each route slowly in your head, stop in every room and see the scene as vividly and absurdly as you can. To test yourself, hide the scenes and try to recall each room's picture and its module before revealing it.</p>
<div class="btnrow"><button class="btn quiet qb-scenes" type="button" aria-pressed="${st.hideScenes}">${st.hideScenes ? "Show all scenes" : "Hide scenes: test yourself"}</button></div>`;
    goes.forEach((g) => {
      const P = PAL[g]; if (!P) return;
      html += `<h2 class="qb-mod">Go ${g}: ${esc(META.goes[g])} · the palace is ${esc(P.place.toLowerCase())}</h2><p class="muted">${esc(P.intro)}</p><ol class="qb-route">`;
      P.stations.forEach(([m, loc, img], i) => {
        html += `<li class="qb-station"><span class="qb-step">${i + 1}</span><div><p class="qb-loc"><b>${esc(loc)}</b> → <a href="modules/${META.slugs[m]}.html">Module ${m}: ${esc(META.titles[m])}</a></p>
<p class="qb-scene"${st.hideScenes ? " hidden" : ""}>${esc(img)}</p>${st.hideScenes ? `<button class="btn quiet qb-reveal-scene" type="button">Picture it, then reveal</button>` : ""}
<p class="small"><a href="questions.html?m=${m}" class="qb-mod-link" data-m="${m}">Practise module ${m} (${Q.filter((d) => d.m === m).length} questions)</a></p></div></li>`;
      });
      html += "</ol>";
    });
    $(".qb-palace").innerHTML = html;
  }

  function summary(list) {
    const known = list.filter((d) => stat(d.id) === "known").length, rev = list.filter((d) => stat(d.id) === "review").length;
    const due = list.filter((d) => marks[d.id] && isDue(d.id)).length;
    $(".qb-summary").textContent = `${list.length} question${list.length === 1 ? "" : "s"} shown · ${known} known · ${rev} to review · ${list.length - known - rev} not yet marked · ${due} marked and due again now`;
    const pc = (x) => (list.length ? (100 * x) / list.length : 0) + "%";
    $(".qb-bar-known").style.width = pc(known); $(".qb-bar-review").style.width = pc(rev);
  }

  function render() {
    $$(".qb-go").forEach((b) => b.setAttribute("aria-pressed", +b.dataset.go === st.go));
    [...modSel.options].forEach((o) => (o.hidden = !!o.value && !!st.go && +o.dataset.go !== st.go));
    $$(".qb-view").forEach((b) => b.setAttribute("aria-pressed", b.dataset.view === st.view));
    $(".qb-list").hidden = st.view !== "list"; $(".qb-cards").hidden = st.view !== "cards"; $(".qb-palace").hidden = st.view !== "palace";
    $(".qb-expand").hidden = st.view !== "list";
    $(".qb-expand").textContent = st.revealAll ? "Hide all answers" : "Reveal all answers";
    const list = filtered();
    if (st.view === "list") renderList(list); else if (st.view === "cards") renderCards(list); else renderPalace();
    summary(list);
    const u = new URL(location.href), sp = new URLSearchParams();
    if (st.module) sp.set("m", st.module); else if (st.go) sp.set("go", st.go);
    if (st.view !== "list") sp.set("view", st.view);
    u.search = sp.toString() ? "?" + sp.toString() : ""; history.replaceState(null, "", u);
  }

  function setMark(id, val) {
    const cur = marks[id];
    if (cur && cur.s === val && Date.now() - (cur.t || 0) < 6e4) delete marks[id];   // a second click soon after undoes the mark
    else if (val === "known") { const b = Math.min(5, (cur && cur.s === "known" ? cur.b : 0) + 1); marks[id] = { s: "known", b, d: Date.now() + INTERVALS[b - 1] * DAY, t: Date.now() }; }
    else marks[id] = { s: "review", b: 0, d: Date.now() + DAY, t: Date.now() };
    save();
    const m = stat(id), sel = CSS.escape(id);
    root.querySelectorAll(`.qb-item[data-id="${sel}"]`).forEach((el) => { el.classList.remove("is-known", "is-review"); if (m) el.classList.add("is-" + m); });
    root.querySelectorAll(`.qb-known[data-id="${sel}"]`).forEach((b) => b.setAttribute("aria-pressed", m === "known"));
    root.querySelectorAll(`.qb-review[data-id="${sel}"]`).forEach((b) => b.setAttribute("aria-pressed", m === "review"));
    root.querySelectorAll(`[data-when="${sel}"]`).forEach((x) => (x.textContent = when(id)));
    summary(filtered());
  }

  const holder = (t) => t.closest(".qb-item, .qb-card");
  root.addEventListener("click", (e) => {
    const t = e.target.closest("button"); if (!t) return;
    if (t.classList.contains("qb-go")) { st.go = +t.dataset.go; if (st.module && st.go && +st.module.split(".")[0] !== st.go) { st.module = ""; modSel.value = ""; } st.card = 0; render(); }
    else if (t.classList.contains("qb-view")) { st.view = t.dataset.view; st.card = 0; render(); }
    else if (t.classList.contains("qb-show")) { const a = holder(t).querySelector(".qb-answer"); a.hidden = !a.hidden; t.textContent = a.hidden ? "Show answer" : "Hide answer"; t.setAttribute("aria-expanded", !a.hidden); }
    else if (t.classList.contains("qb-hint")) { const h = holder(t).querySelector(".qb-hintbox"); h.hidden = !h.hidden; }
    else if (t.classList.contains("qb-write")) { const ta = holder(t).querySelector(".qb-draft"); ta.hidden = !ta.hidden; if (!ta.hidden) ta.focus(); }
    else if (t.classList.contains("qb-known")) setMark(t.dataset.id, "known");
    else if (t.classList.contains("qb-review")) setMark(t.dataset.id, "review");
    else if (t.classList.contains("qb-shuffle")) { const ids = Q.map((d) => d.i); for (let i = ids.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [ids[i], ids[j]] = [ids[j], ids[i]]; } st.order = ids; st.card = 0; t.textContent = "Shuffle again"; render(); }
    else if (t.classList.contains("qb-expand")) { st.revealAll = !st.revealAll; render(); }
    else if (t.classList.contains("qb-reset")) { if (Object.keys(marks).length && window.confirm && !confirm("Clear all your marks and review schedule on this device?")) return; marks = {}; save(); render(); }
    else if (t.classList.contains("qb-flip")) flip();
    else if (t.classList.contains("qb-next")) { st.card++; render(); focusCard(); }
    else if (t.classList.contains("qb-prev")) { st.card--; render(); focusCard(); }
    else if (t.classList.contains("qb-scenes")) { st.hideScenes = !st.hideScenes; render(); }
    else if (t.classList.contains("qb-reveal-scene")) { t.previousElementSibling.hidden = false; t.remove(); }
    else if (t.classList.contains("qb-print")) { const was = [st.view, st.revealAll]; st.view = "list"; st.revealAll = true; render(); setTimeout(() => { window.print(); st.view = was[0]; st.revealAll = was[1]; render(); }, 50); }
  });
  root.addEventListener("click", (e) => {   // palace links to a module's questions stay on this page
    const a = e.target.closest(".qb-mod-link"); if (!a) return;
    e.preventDefault(); st.module = a.dataset.m; st.go = +st.module.split(".")[0]; modSel.value = st.module; st.view = "list"; render(); $(".qb-controls").scrollIntoView();
  });
  function flip() { const c = $(".qb-card"); if (!c) return; const a = c.querySelector(".qb-answer"), b = c.querySelector(".qb-flip"); a.hidden = !a.hidden; b.textContent = a.hidden ? "Show answer" : "Hide answer"; }
  function focusCard() { const c = $(".qb-card"); if (c) c.focus(); }
  root.addEventListener("keydown", (e) => {
    if (st.view !== "cards" || !e.target.closest(".qb-cards")) return;
    if (e.key === " ") { e.preventDefault(); flip(); }
    else if (e.key === "h" || e.key === "H") { const h = $(".qb-card .qb-hintbox"); if (h) h.hidden = !h.hidden; }
    else if (e.key === "ArrowRight") { st.card++; render(); focusCard(); }
    else if (e.key === "ArrowLeft") { st.card--; render(); focusCard(); }
    else if (e.key === "1" || e.key === "2") { const c = $(".qb-card"); if (c) setMark(c.dataset.id, e.key === "1" ? "known" : "review"); }
  });
  modSel.addEventListener("change", () => { st.module = modSel.value; if (st.module) st.go = +st.module.split(".")[0]; st.card = 0; render(); });
  let tmr; search.addEventListener("input", () => { clearTimeout(tmr); tmr = setTimeout(() => { st.search = search.value; st.card = 0; render(); }, 150); });
  status.addEventListener("change", () => { st.status = status.value; st.card = 0; render(); });
  $$(".qb-kind input").forEach((c) => c.addEventListener("change", () => { c.checked ? st.kinds.add(c.value) : st.kinds.delete(c.value); st.card = 0; render(); }));
  render();
})();
