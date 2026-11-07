"""Build 'Physical AI and Scientific Machine Learning in three goes' (static site) from content/m*.json.  Usage: python3 build.py"""
import json, glob, os, html, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "content"))
from qbank import Q as QB
from qhooks import H as QH, PALACE
from threads import THREADS
from challenges import CH
from models import MODELS
ICONS = json.load(open(os.path.join(ROOT, "content", "icons.json")))
# Course "systems" are written in the content with their own keys and mapped onto the six colour slots of the stylesheet.
CMAP = dict(learn="economy", physics="energy", system="land", data="water", risk="climate", apply="policy", model="neutral", neutral="neutral")
def cm(k): return CMAP.get(k, k)
SYSICON = dict(economy="cpu", energy="flask", land="gear", water="radar", climate="shield", policy="car", neutral="layers", data="chart")
LEAFKW = [("network", "cpu"), ("neuron", "cpu"), ("layer", "layers"), ("weight", "sliders"), ("loss", "target"), ("gradient", "arrows"), ("optimis", "sliders"), ("adam", "sliders"),
          ("autodiff", "spark"), ("derivative", "spark"), ("equation", "flask"), ("law", "flask"), ("physics", "flask"), ("residual", "flask"), ("pinn", "flask"), ("collocation", "pin"),
          ("data", "chart"), ("noise", "waves"), ("measure", "ruler"), ("sensor", "radar"), ("detector", "radar"), ("gps", "radar"), ("camera", "camera"), ("video", "camera"),
          ("uncertain", "dice"), ("band", "dice"), ("coverage", "target"), ("calibrat", "sliders"), ("valid", "target"), ("test", "target"), ("baseline", "ruler"),
          ("surrogate", "box"), ("emulat", "box"), ("operator", "layers"), ("kernel", "grid"), ("gp", "chart"), ("sindy", "search"), ("discover", "search"), ("sparse", "search"),
          ("traffic", "car"), ("vehicle", "car"), ("car", "car"), ("platoon", "car"), ("jam", "warn"), ("wave", "pulse"), ("safety", "shield"), ("crash", "siren"), ("conflict", "siren"),
          ("risk", "warn"), ("energy", "bolt"), ("emission", "leaf"), ("co₂", "leaf"), ("electric", "bolt"), ("gcam", "globe"), ("climate", "globe"), ("carbon", "leaf"),
          ("crowd", "crowd"), ("pedestrian", "walk"), ("twin", "layers"), ("signal", "signal"), ("queue", "timer"), ("time", "timer"), ("step", "timer"),
          ("grid", "grid4"), ("solver", "gear"), ("model", "layers"), ("simulat", "cpu"), ("code", "code"), ("python", "code"), ("pytorch", "code"), ("paper", "pen"), ("research", "flask")]


def leaf_icon(t):
    tl = t.lower()
    return next((ic for k, ic in LEAFKW if k in tl), None)


FIGDIR = os.path.join(ROOT, "assets", "img", "fig")
FIGCAP = json.load(open(os.path.join(FIGDIR, "captions.json"))) if os.path.exists(os.path.join(FIGDIR, "captions.json")) else {}


def figure_html(mid):
    f = os.path.join(FIGDIR, f"m{mid}.svg")
    if not os.path.exists(f): return ""
    t, cap = FIGCAP.get(mid, ["", ""])
    return (f'<figure class="figure-card">{open(f, encoding="utf-8").read()}<figcaption><b>Picture it: {esc(t)}.</b> <span>{esc(cap)}</span>'
            f'<button class="btn quiet fig-play" type="button">Pause animation</button></figcaption></figure>')


def icon_svg(name, cls=""):
    return f'<svg viewBox="0 0 24 24" class="{cls}" aria-hidden="true"><path d="{ICONS.get(name, "")}"/></svg>'


def threads_html(mid):
    out = []
    for t in THREADS:
        stops = t["stops"]
        idx = next((i for i, st in enumerate(stops) if st[0] == mid), None)
        if idx is None: continue
        steps = "".join(f'<div class="thread-step g{i + 1}{" here" if i == idx else ""}"><div class="tgo">Go {i + 1} · <a href="{slug_of(st[0])}.html">{st[0]}</a></div>{esc(st[1])}</div>' for i, st in enumerate(stops))
        rec = ""
        if idx > 0:
            q, a = stops[idx - 1][2], stops[idx - 1][3]
            rec = f'<div class="thread-recall"><b>Recall from Go {idx}:</b> {esc(q)} <button class="btn quiet" type="button">Show answer</button><div class="ans">{esc(a)}</div></div>'
        else:
            rec = f'<div class="thread-recall"><b>Looking ahead:</b> this idea returns in Go 2 (module {stops[1][0]}) and Go 3 (module {stops[2][0]}), each time deeper.</div>'
        out.append(f'<div class="thread"><h4>{icon_svg(t["icon"])}Concept thread: {esc(t["name"])}</h4><div class="thread-steps">{steps}</div>{rec}</div>')
    if not out: return ""
    return '<h3>The same idea in three goes</h3><p class="small muted">Every core idea comes back in each go, one level deeper. <a href="../spiral.html">See all concept threads</a>.</p>' + "".join(out)


SLUGS = {}


def slug_of(mid):
    return SLUGS.get(mid, "")
SYS = ["economy", "energy", "land", "water", "climate", "policy"]
SYSNAME = dict(economy="Learning and optimisation", energy="Physics and equations", land="Systems and models", water="Data and sensing", climate="Uncertainty and risk", policy="Applications")
SITE = "Physical AI and SciML in three goes"
VER = "20261107a"  # cache-busting tag for CSS/JS
esc = lambda s: html.escape(str(s), quote=True)

# ------------------------------------------------------------------ the three goes
GO = {
    1: dict(name="Foundations", short="Foundations", depth="Introductory",
            promise="Understand what scientific machine learning and Physical AI are, and the building blocks behind them: differential equations, neural networks, optimisation, physics-informed losses, noise, surrogates and the sense–act loop.",
            style="Pictures and simulations first. Every idea has an animated diagram, a simulator where you predict and then check, and a small worked calculation. Code is optional.",
            need="Nothing beyond school mathematics and curiosity. Every idea comes with an animation and a simulator you can play with.",
            produce=["Plain-language explanations of SciML and Physical AI", "Small calculations you can do by hand: an Euler step, a gradient step, a Kalman correction", "Intuition for when physics, data or both should be trusted"],
            entry=[("A differential equation describes…", ["A fixed number", "How a quantity changes", "A table of data", "A type of neural network"], 1, "It is a rule for change."),
                   ("Training a neural network means…", ["Writing its equations by hand", "Adjusting its weights to reduce a loss", "Collecting more sensors", "Running a classical solver"], 1, "Minimise the loss."),
                   ("A model that fits its training data perfectly…", ["Is always the best", "May be overfitting the noise", "Cannot be wrong", "Has no parameters"], 1, "Judge on unseen data.")],
            exit=["I can explain SciML and Physical AI in one sentence each", "I can do an Euler step and a gradient-descent step by hand",
                  "I can explain how a physics-informed loss fills gaps in data", "I can say when to trust physics, data or both", "I can describe the sense–estimate–decide–act loop"],
            handbook="downloads/Go1-Handbook-SciML-Foundations.pdf", kit=None),
    2: dict(name="Build and Implement", short="Build", depth="Intermediate",
            promise="Build the main SciML tools step by step: an honest workflow, physics-informed neural networks, PDE solvers, equation discovery, neural operators, Gaussian processes, hybrid models and calibrated uncertainty.",
            style="Step-by-step builds. Each module walks through the method, then you build it in Python that runs in your browser, with a PyTorch version to download.",
            need="Go 1, or its exit check. Basic Python. Every lab runs in your browser with NumPy; PyTorch versions are provided to download.",
            produce=["A PINN written from scratch, including an inverse problem", "A finite-difference PDE solver and a PINN for the same PDE", "SINDy, a DeepONet, a Gaussian process, a hybrid model and conformal intervals"],
            entry=[("A physics-informed loss contains…", ["Only a data term", "A data term and an equation-residual term", "Only random noise", "The test set"], 1, "Data + physics."),
                   ("For traffic time series, an honest validation split is…", ["Random hours", "By time", "By detector name", "No split"], 1, "Avoid leakage."),
                   ("Automatic differentiation computes…", ["Approximate derivatives", "Exact derivatives by the chain rule", "Integrals", "Random numbers"], 1, "Chain rule, exactly.")],
            exit=["I can set up a leakage-free SciML workflow with baselines", "I can build and train a PINN, including an inverse problem",
                  "I can solve a PDE classically and check stability", "I can discover an equation with SINDy and learn an operator", "I can attach calibrated uncertainty to predictions"],
            handbook="downloads/Go2-Handbook-SciML-Build.pdf", kit="downloads/go2-kit.zip"),
    3: dict(name="Research Frontier: Transportation", short="Research", depth="Advanced",
            promise="Apply SciML and Physical AI to transportation research: traffic state estimation, automated vehicles, road safety, energy and emissions, GCAM emulators, crowd dynamics and digital twins.",
            style="Each module reads like a research brief for one transport application: the problem, the evidence, the method, a working lab, and open questions.",
            need="Go 2, or its exit check. Python; PyTorch for the larger labs. Access to transport data (open datasets such as highD or NGSIM are fine).",
            produce=["A research question and study design for a transport SciML project", "Working prototypes: physics-informed traffic estimation, platoon simulation, conflict analysis, hybrid emissions, an IAM emulator and a digital twin",
                     "A results section with baselines, uncertainty and limits"],
            entry=[("Time to collision is…", ["Gap divided by closing speed", "Speed times time", "Distance to the junction", "Reaction time"], 0, "Seconds to impact."),
                   ("An emulator of GCAM is…", ["A second GCAM", "A fast statistical stand-in trained on a few GCAM runs", "A traffic simulator", "A climate treaty"], 1, "A fast stand-in."),
                   ("A digital twin differs from a simulation because it…", ["Has better graphics", "Is continuously updated with live data and linked to decisions", "Has more vehicles", "Runs offline"], 1, "Two-way link.")],
            exit=["I can design a physics-informed traffic estimation study", "I can explain string stability and how automation affects it",
                  "I can use surrogate safety measures and their limits", "I can build hybrid emission models and IAM emulators", "I can report SciML results honestly, with baselines, uncertainty and limits"],
            handbook="downloads/Go3-Handbook-SciML-Transport.pdf", kit="downloads/go3-research-kit.zip"),
}

# module page section names differ by go: the same content, a different reading order and voice
LABELS = {
    1: dict(overview="Start here", picture="Look", explore="Predict, then check", challenge="Simulation challenges", parts="The parts", code="Try a quick calculation", take="Remember", quiz="Check yourself", more="Words and links"),
    2: dict(overview="Start here", picture="Connections map", explore="Play with it", challenge="Simulation challenges", parts="The parts", code="Build it", take="Remember", quiz="Check yourself", more="Words and links"),
    3: dict(overview="Research brief", picture="The system under study", explore="Stress-test it", challenge="Research challenges", parts="Key elements", code="Implement it", take="Research notes", quiz="Check yourself", more="Reading list"),
}
ORDER = {1: ["overview", "picture", "explore", "challenge", "sections", "parts", "code", "mindmap", "take", "quiz", "more"],
         2: ["overview", "picture", "parts", "sections", "code", "explore", "challenge", "mindmap", "take", "quiz", "more"],
         3: ["overview", "picture", "sections", "parts", "code", "explore", "challenge", "mindmap", "take", "quiz", "more"]}


def load():
    mods = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(ROOT, "content", "m*.json")))]
    for m in mods:
        m["systems"] = [cm(x) for x in m["systems"]]
        for n in m["diagram"]["nodes"]: n["sys"] = cm(n.get("sys", "neutral"))
        for e in m["diagram"].get("edges", []):
            if e.get("sys"): e["sys"] = cm(e["sys"])
    mods.sort(key=lambda m: (m["go"], [int(x) for x in m["id"].split(".")]))
    return mods


def head(title, desc, depth=0, extra=""):
    up = "../" * depth
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..800&family=Atkinson+Hyperlegible+Mono:wght@400;600&family=Atkinson+Hyperlegible+Next:wght@400;600;700&family=Noto+Naskh+Arabic:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{up}assets/css/site.css?v={VER}">
<link rel="icon" href="{up}assets/img/icon.svg" type="image/svg+xml">
<script src="{up}assets/js/icons.js?v={VER}"></script>
{extra}</head>
"""


def topbar(depth, current, bodyattr=""):
    up = "../" * depth
    items = [("go1.html", "Foundations"), ("go2.html", "Build and Implement"), ("go3.html", "Research Frontier"), ("models.html", "Method atlas"), ("spiral.html", "Concept spiral"), ("questions.html", "Questions"), ("toolkit.html", "Toolkit"), ("glossary.html", "Glossary")]
    nav = "".join(f'<a href="{up}{h}"{" aria-current=page" if h == current else ""}>{t}</a>' for h, t in items)
    dots = "".join(f'<i class="c-{s}"></i>' for s in SYS)
    return f"""<body{bodyattr}>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap">
<a class="brand" href="{up}index.html"><span class="dots" aria-hidden="true">{dots}</span>Physical AI and SciML in three goes</a>
<nav class="nav" aria-label="Main">{nav}<button class="iconbtn" id="theme" type="button" aria-label="Switch between light and dark theme">Light / dark</button></nav>
</div></header>
"""


def foot(depth, scripts=True):
    up = "../" * depth
    s = f'<script src="{up}assets/js/diagrams.js?v={VER}"></script><script src="{up}assets/js/core.js?v={VER}"></script><script src="{up}assets/js/widgets.js?v={VER}"></script><script src="{up}assets/js/widgets2.js?v={VER}"></script><script src="{up}assets/js/site.js?v={VER}"></script><script src="{up}assets/js/challenges.js?v={VER}"></script>' if scripts else ""
    return f"""<footer class="site"><div class="wrap">An open course on Physical AI and scientific machine learning, taught in three goes, with transportation as the research case. Methods follow the cited literature (Raissi, Perdikaris and Karniadakis; Brunton, Proctor and Kutz; Lu and colleagues; Rasmussen and Williams; Kalman; Treiber and colleagues; among others). Explorers use synthetic teaching data: never use them on their own for engineering or safety decisions.</div></footer>
{s}
</body></html>"""


def sysdots(systems):
    return '<span class="sysdots" aria-hidden="true">' + "".join(f'<i class="c-{s}"></i>' for s in systems) + "</span>"


def chips(systems):
    return "".join(f'<span class="sys-chip"><i class="c-{s}"></i>{SYSNAME[s]}</span>' for s in systems)


def module_list(mods, depth=0):
    up = "../" * depth
    out = ['<ol class="mlist">']
    for m in mods:
        out.append(f'<li><a href="{up}modules/{m["slug"]}.html"><span class="num">{m["id"]}</span>'
                   f'<span><span class="t">{esc(m["title"])}</span>{sysdots(m["systems"])}<span class="state" data-progress-for="{m["id"]}" aria-hidden="true"></span>'
                   f'<span class="d">{esc(m["summary"])}</span></span><span class="meta">{m["minutes"]} min<br>{esc(m["tag"])}</span></a></li>')
    out.append("</ol>")
    return "".join(out)


def code_html(c, mid, depth=1):
    up = "../" * depth
    src = c.get("source")
    if c.get("file"):
        src = open(os.path.join(ROOT, c["file"]), encoding="utf-8").read()
    runnable = c.get("runnable") and c.get("lang") == "python"
    lang = {"python": "Python", "r": "R", "xml": "XML", "bash": "Shell"}.get(c.get("lang"), c.get("lang", ""))
    btns = '<button class="btn quiet code-copy" type="button">Copy</button>'
    if c.get("file"): btns += f'<a class="btn quiet" href="{up}{c["file"]}" download>Download</a>'
    if runnable:
        btns = '<button class="btn code-run" type="button">Run in browser</button><button class="btn quiet code-reset" type="button">Reset</button>' + btns
        body = f'<textarea spellcheck="false" aria-label="Editable Python code">{esc(src)}</textarea>'
    else:
        body = f"<pre><code>{esc(src)}</code></pre>"
    exp = f'<div class="expected"><p class="small muted" style="margin:0 0 4px">Expected output</p><pre>{esc(c["expected"])}</pre></div>' if c.get("expected") else ""
    runs = '<span class="runs">Runs in your browser</span>' if runnable else ""
    return (f'<div class="codeblock" data-module="{mid}"><div class="codehead"><b>{esc(c["title"])}</b><span class="lang">{lang}</span>{runs}{btns}</div>'
            f'{body}<div class="explain-code">{c.get("explain", "")}</div>{exp}<div class="code-out" hidden aria-live="polite"></div></div>')


def module_page(m, prev, nxt, diagrams):
    mid, depth, g = m["id"], 1, m["go"]
    L = LABELS[g]
    diagrams[f"m{mid}"] = m["diagram"]
    toc, body = [], []

    def sec(anchor, title, content):
        toc.append(f'<li><a href="#{anchor}">{esc(title)}</a></li>')
        body.append(f'<section id="{anchor}"><h2>{esc(title)}</h2>{content}</section>')

    narr = (f'<div class="narration" data-module="{mid}"><div class="narr-bar"><button class="btn narr-play" type="button">Listen</button>'
            f'<button class="btn quiet narr-stop" type="button">Stop</button><span class="muted small">Spoken overview</span>'
            f'<button class="narr-lang" type="button" data-lang="en" aria-pressed="true">English</button><button class="narr-lang" type="button" data-lang="ar" aria-pressed="false">العربية</button>'
            f'<span class="narr-status" aria-live="polite"></span></div><details><summary>Read the transcript</summary>'
            f'<p class="narr-en">{esc(m["narration_en"])}</p><p class="narr-ar" lang="ar" dir="rtl" hidden>{esc(m["narration_ar"])}</p></details></div>')
    lead = {1: "By the end you can", 2: "By the end you can", 3: "In this module you will"}[g]
    outcomes = "<ul class='outcomes'>" + "".join(f"<li>{esc(o)}</li>" for o in m["outcomes"]) + "</ul>"
    d = m["diagram"]
    blocks = {}
    blocks["overview"] = lambda: sec("start", L["overview"], f'<h3 style="margin-top:0">{lead}</h3>{outcomes}{narr}{threads_html(mid)}')
    intro = {1: "Select any box to see what it is, or play the walkthrough to see the idea unfold.",
             2: "This mechanism and the parts of the system it connects to. Select a box for detail, or play the walkthrough to follow the mechanism.",
             3: "Select a box for detail, or play the walkthrough."}[g]
    blocks["picture"] = lambda: sec("picture", L["picture"], figure_html(mid) + f'<p class="prose"><b>{esc(d.get("title", ""))}.</b> {intro}</p>'
                                    f'<div class="diagram-box"><div id="dg-{mid.replace(".", "-")}" data-diagram="m{mid}"><p class="muted">This diagram needs JavaScript. {esc(d.get("caption", ""))}</p></div></div>')

    def parts():
        if not m.get("components"): return
        rows = "".join(f'<tr><td><b>{esc(r["name"])}</b></td><td>{esc(r["purpose"])}</td><td>{esc(r["analogy"])}</td></tr>' for r in m["components"]["rows"])
        sec("parts", L["parts"], f'<p class="prose">{esc(m["components"].get("caption", ""))}</p><div class="tscroll"><table class="tbl"><thead><tr><th>Part</th><th>What it does</th><th>Think of it as</th></tr></thead><tbody>{rows}</tbody></table></div>')
    blocks["parts"] = parts

    def sections():
        callouts = m.get("callouts", [])
        for i, s in enumerate(m["sections"]):
            extra = "".join(f'<div class="callout {c["kind"]}"><h4>{esc(c["title"])}</h4>{c["html"]}</div>' for c in callouts if c["after"] == i)
            sec(f"s{i + 1}", s["heading"], f'<div class="prose">{s["html"]}</div>{extra}')
    blocks["sections"] = sections

    def explore():
        if not m.get("explorer"): return
        e = m["explorer"]
        pr = f'<div class="predict"><b>Predict first:</b> {esc(e.get("predict", ""))}</div>' if e.get("predict") else ""
        sec("explore", L["explore"], f'<div class="explorer" data-widget="{e["widget"]}" data-module="{mid}"><p class="prose">{esc(e.get("intro", ""))}</p>{pr}<div class="explorer-box"><p class="muted">This explorer needs JavaScript.</p></div></div>')
    blocks["explore"] = explore

    def challenge():
        if mid not in CH: return
        lead3 = {1: "Steer a small model to a goal. Predict first, then move the sliders until the gauge turns green, and press Check. Stars reward first-try solves.",
                 2: "The same ideas as Go 1, one level deeper: hit each target with the mechanism you just studied.",
                 3: "Research-style tasks: reproduce, calibrate or stress-test a result with a toy version of the method."}[g]
        sec("challenges", L["challenge"], f'<p class="prose">{lead3}</p><div class="challenges" data-module="{mid}"><noscript>These challenges need JavaScript.</noscript></div>'
            f'<script>window.CHALLENGES = window.CHALLENGES || {{}}; window.CHALLENGES[{json.dumps(mid)}] = {json.dumps(CH[mid], ensure_ascii=False)};</script>')
    blocks["challenge"] = challenge

    def code():
        if not m.get("code"): return
        lead2 = {1: "A few lines of Python that do the arithmetic above. Press Run: nothing to install.",
                 2: "Examples marked 'Runs in your browser' run here; edit a number and run again. The R version is identical; download it for RStudio.",
                 3: "Code from the Go 3 research kit. Python marked 'Runs in your browser' runs here; the longer scripts are for your own machine."}[g]
        sec("code", L["code"], f'<p class="prose">{lead2}</p>' + "".join(code_html(c, mid) for c in m["code"]))
    blocks["code"] = code
    def mmap():
        tip = {1: "The whole module on one zooming map. Use it to preview before reading, or to recall afterwards with Test yourself.",
               2: "Each branch is a section of this module; each box an idea to recall. Try Test yourself before the quiz.",
               3: "A map of the research module: each branch a section, each box a point to be able to defend."}[g]
        sec("mindmap", "Mind map", f'<p class="prose">{tip}</p>' + mm_markup(f"m{mid}", "", embed=True, label=f"Mind map of module {mid}"))
    blocks["mindmap"] = mmap
    def take():
        st = next((x for x in PALACE[g]["stations"] if x[0] == mid), None)
        box = (f'<div class="callout try remember"><h4>Remember it: memory palace, {esc(PALACE[g]["place"].lower())} · {esc(st[1].lower())}</h4>'
               f'<p>{esc(st[2])}</p><p class="small">Picture the scene for ten seconds. Then <a href="../questions.html?m={mid}">test yourself on this module</a>, with an intuition and a memory hook for every answer, or <a href="../questions.html?go={g}&amp;view=palace">walk the whole Go {g} palace</a>.</p></div>') if st else ""
        sec("takeaways", L["take"], "<ul class='takeaways'>" + "".join(f"<li>{esc(t)}</li>" for t in m["takeaways"]) + "</ul>" + box)
    blocks["take"] = take

    def quiz():
        qs = []
        for i, q in enumerate(m["quiz"]):
            opts = "".join(f'<button class="opt" type="button">{esc(o)}</button>' for o in q["options"])
            qs.append(f'<div class="q" data-answer="{q["answer"]}"><p>{i + 1}. {esc(q["q"])}</p><div class="opts">{opts}</div><p class="fb" hidden><b class="verdict"></b>{esc(q["explain"])}</p></div>')
        sec("check", L["quiz"], f'<div class="quiz" data-module="{mid}">{"".join(qs)}<p class="quiz-result" hidden aria-live="polite"></p><button class="btn quiet quiz-again" type="button">Try the questions again</button></div><p class="prose">More practice: <a href="../questions.html?m={mid}">{sum(1 for q in QB if q[0] == mid)} short-answer questions with model answers</a> for this module in the question bank.</p>')
    blocks["quiz"] = quiz

    def more():
        words = "<dl class='glist'>" + "".join(f'<div class="gterm"><dt>{esc(x["term"])}</dt><dd>{esc(x["def"])}</dd></div>' for x in m["glossary"]) + "</dl>"
        res = "<ul class='reslist'>" + "".join(f'<li><a href="{esc(r["url"])}" target="_blank" rel="noopener">{esc(r["title"])}</a><span class="why">{esc(r["why"])}</span></li>' for r in m["resources"]) + "</ul>"
        dls = ("<h3>Downloads</h3><div class='dl'>" + "".join(f'<a class="btn quiet" href="../{esc(x["path"])}">{esc(x["label"])}</a>' for x in m["downloads"]) + "</div>") if m.get("downloads") else ""
        sec("more", L["more"], f"<h3 style='margin-top:0'>New words</h3>{words}<h3>Read further</h3>{res}{dls}")
    blocks["more"] = more
    for k in ORDER[g]: blocks[k]()

    pager = '<nav class="pager" aria-label="Module navigation">'
    pager += f'<a href="{prev["slug"]}.html"><span class="dir">Previous</span>{prev["id"]} {esc(prev["title"])}</a>' if prev else f'<a href="../go{g}.html"><span class="dir">Back to</span>Go {g}: {esc(GO[g]["name"])}</a>'
    pager += f'<a class="next" href="{nxt["slug"]}.html"><span class="dir">Next</span>{nxt["id"]} {esc(nxt["title"])}</a>' if nxt else f'<a class="next" href="../go{g}.html#exit"><span class="dir">End of Go {g}</span>Take the exit check</a>'
    pager += "</nav>"
    page = head(f'{mid} {m["title"]} · {SITE}', m["summary"], depth) + topbar(depth, f"go{g}.html", f' data-module="{mid}" data-go="{g}"')
    page += f"""<main id="main" class="wrap">
<p class="crumbs"><a href="../index.html">Home</a> / <a href="../go{g}.html">Go {g}: {esc(GO[g]["name"])}</a> / Module {mid}</p>
<header class="mhead go{g}"><p class="eyebrow"><span class="golevel">Go {g} · {GO[g]["depth"]}</span> Module {mid}, {m["minutes"]} minutes, {esc(m["tag"].lower())}</p><h1>{esc(m["title"])}</h1><p class="summary">{esc(m["summary"])}</p><div>{chips(m["systems"])}</div></header>
<div class="mlayout"><nav class="outline" aria-label="On this page"><p>On this page</p><ol>{"".join(toc)}</ol><p><a href="#mindmap">This module's mind map</a><br><a href="../mindmap-go{g}.html">Go {g} mind map</a></p></nav>
<div class="mmain">{"".join(body)}
<div class="done-row"><button class="btn" id="mark-done" type="button" aria-pressed="false">Mark this module as studied</button><span class="muted small">Saved in this browser only.</span></div>
{pager}</div></div></main>
""" + mm_script(f"m{mid}", module_mindmap_data(m), depth) + foot(depth)
    return page


# ------------------------------------------------------------------ the SciML system, seen at three depths
def node(id, label, sub, x, y, sys, d1, d2, d3, w=200):
    return {"id": id, "label": label, "sub": sub, "x": x, "y": y, "w": w, "h": 64, "sys": cm(sys), "detail": {"1": d1, "2": d2, "3": d3}}


HERO = {
    "title": "Scientific machine learning and Physical AI", "caption": "Physics gives structure and data give detail; scientific machine learning combines them into models that are accurate, fast and honest about uncertainty, and Physical AI puts them to work in transport.",
    "nodes": [
        node("phy", "Physical laws", "equations we trust", 140, 90, "physics",
             "Laws such as conservation of vehicles, Newton's laws and energy balances. They hold even where we have no data.",
             "ODEs and PDEs: the LWR traffic model, car-following models, the road-load equation. Solved by classical solvers or used as residuals in learning.",
             "Research angle: which parts of the physics are trusted, and which need learning? That choice shapes every SciML design."),
        node("dat", "Data", "sensors, video, simulations", 140, 260, "data",
             "Measurements from detectors, GPS, cameras and experiments, and outputs of simulators.",
             "Noisy, sparse and biased towards normal conditions. Split honestly, look for leakage, and keep test data untouched.",
             "Research angle: rare events (crashes, crushes, extreme weather) are where data are thinnest and physics matters most."),
        node("ml", "Machine learning", "networks, GPs, regression", 140, 430, "learn",
             "Flexible functions whose parameters are learned from examples by minimising a loss.",
             "Neural networks, Gaussian processes and sparse regression, trained by gradient descent with automatic differentiation.",
             "Research angle: physics-aware architectures and losses that keep learned models within physical limits."),
        node("sci", "Scientific ML", "PINNs, operators, hybrids", 450, 260, "learn",
             "Machine learning that respects physics.",
             "Physics-informed networks, equation discovery, neural operators, surrogates, hybrid models and data assimilation.",
             "Research angle: when does adding physics actually help? Ablations against strong baselines answer this."),
        node("unc", "Uncertainty", "how sure are we?", 450, 440, "risk",
             "Every prediction should say how sure it is.",
             "Gaussian processes, ensembles and conformal prediction give intervals; calibration checks that they are honest.",
             "Research angle: conditional coverage, rare events and decision-relevant uncertainty."),
        node("pai", "Physical AI", "sense, decide, act", 760, 160, "apply",
             "Machines that sense and act in the physical world: automated vehicles, robots, adaptive signals.",
             "Estimation (Kalman filters), learned perception, model-based and learned control, with safety layers.",
             "Research angle: verifying learned controllers and training them safely in digital twins."),
        node("trn", "Transport decisions", "safety, sustainability, operations", 760, 360, "apply",
             "Safer roads, lower emissions and smoother traffic.",
             "Traffic estimation, car following, conflict analysis, emissions, GCAM emulators, crowd safety and digital twins.",
             "Research angle: honest evaluation and fairness when models trained in one place are used in another.")],
    "edges": [
        {"from": "phy", "to": "sci", "label": "structure"}, {"from": "dat", "to": "sci", "label": "detail"}, {"from": "ml", "to": "sci", "label": "flexibility"},
        {"from": "sci", "to": "pai", "label": "models"}, {"from": "sci", "to": "trn", "label": "insight"}, {"from": "unc", "to": "trn", "label": "honesty", "sys": "climate"},
        {"from": "sci", "to": "unc", "label": "quantified"}, {"from": "pai", "to": "dat", "label": "new data", "sys": "water"}],
    "tour": [
        {"focus": ["phy", "dat", "ml"], "text": "Three ingredients: physical laws, data, and machine learning."},
        {"focus": ["sci"], "edges": [["phy", "sci"], ["dat", "sci"], ["ml", "sci"]], "text": "Scientific machine learning combines them: physics for structure, data for detail, learning for flexibility."},
        {"focus": ["unc"], "edges": [["sci", "unc"]], "text": "Its predictions come with honest uncertainty."},
        {"focus": ["pai"], "edges": [["sci", "pai"], ["pai", "dat"]], "text": "Physical AI puts the models into machines that sense and act, and they in turn produce new data."},
        {"focus": ["trn"], "edges": [["sci", "trn"], ["unc", "trn"]], "text": "In transport, this supports safer, cleaner and smoother systems."}]}


# ------------------------------------------------------------------ zooming mind maps (Prezi-style)
def short(t, n=46):
    t = re.sub(r"<[^>]+>", "", t).strip()
    return t if len(t) <= n else t[:n - 1].rsplit(" ", 1)[0] + "…"


def mindmap_data(g, mods):
    return {"title": f"Go {g}: {GO[g]['name']}", "center": f"Go {g}", "subtitle": GO[g]["name"], "promise": GO[g]["promise"],
            "branches": [{"id": m["id"], "title": m["title"], "sys": m["systems"][0], "href": f"modules/{m['slug']}.html", "summary": m["summary"], "hrefLabel": f"Open module {m['id']}",
                          "img": f"assets/img/fig/m{m['id']}.svg" if os.path.exists(os.path.join(FIGDIR, f"m{m['id']}.svg")) else None,
                          "leaves": [b[0] for b in __import__("mindmaps").MM[m["id"]]][:6], "notes": m["takeaways"][:4]} for m in mods]}


MM_HELP = "Press Start, then Next (or the arrow keys) to zoom into each branch. Select any box to zoom to it, and any idea for its explanation. Scroll or pinch to zoom, drag to move, F for full screen. Test yourself hides the ideas until you select them."


def mm_markup(key, title_html, extra_btn="", embed=False, label="Zooming mind map"):
    return f"""<div class="mm{' embed' if embed else ''}" data-mm="{key}">
<div class="mm-bar{'' if embed else ' wrap'}"><div>{title_html}<p class="muted small">{MM_HELP}</p></div>
<div class="btnrow"><button class="btn mm-start" type="button">Start</button><button class="btn quiet mm-prev" type="button">Back</button><button class="btn quiet mm-next" type="button">Next</button><button class="btn quiet mm-all" type="button">Whole map</button><button class="btn quiet mm-recall" type="button" aria-pressed="false">Test yourself</button><button class="btn quiet mm-full" type="button">Full screen</button>{extra_btn}</div></div>
<div class="mm-stage" tabindex="0" aria-label="{esc(label)}"><svg class="mm-svg" role="img" aria-label="{esc(label)}"></svg>
<aside class="mm-notes" aria-live="polite"></aside><p class="mm-step"></p></div></div>"""


def mm_script(key, data, depth):
    up = "../" * depth
    return f'<script>window.MINDMAPS = window.MINDMAPS || {{}}; window.MINDMAPS[{json.dumps(key)}] = {json.dumps(data, ensure_ascii=False)};</script><script src="{up}assets/js/mindmap.js?v={VER}"></script>'


def module_mindmap_data(m):
    from mindmaps import MM
    branches = []
    for i, (title, sysk, summary, leaves) in enumerate(MM[m["id"]]):
        fig = f"../assets/img/fig/m{m['id']}.svg" if os.path.exists(os.path.join(FIGDIR, f"m{m['id']}.svg")) else None
        branches.append({"id": str(i + 1), "title": title, "sys": cm(sysk) if sysk else m["systems"][0], "href": f"#s{i + 1}", "img": fig,
                         "hrefLabel": "Read this section: " + re.sub(r"<[^>]+>", "", m["sections"][i]["heading"]),
                         "summary": summary, "leaves": [dict({"t": t, "n": n}, **({"i": leaf_icon(t + " " + n)} if leaf_icon(t + " " + n) else {})) for t, n in leaves]})
    return {"title": f"Module {m['id']}: {m['title']}", "center": m["title"], "subtitle": f"Go {m['go']} · Module {m['id']}", "icon": SYSICON.get(m["systems"][0], "globe"),
            "promise": m["summary"], "branches": branches}


def mindmap_page(g, data):
    page = head(f"Go {g} mind map · {SITE}", f"Zooming mind map of Go {g}: {GO[g]['name']}", 0) + topbar(0, f"go{g}.html", ' class="mm-page"')
    page += f"""<main id="main" class="mm-main">
{mm_markup(f"go{g}", f'<h1 class="mm-title">Go {g} mind map</h1>', f'<a class="btn quiet" href="downloads/mindmaps/Go{g}-mind-map-path.pdf">PDF (for Prezi import)</a>', label=f"Mind map of Go {g}")}
</main>
{mm_script(f"go{g}", data, 0)}
""" + foot(0)
    return page


# ------------------------------------------------------------------ question bank
def questions_page(mods):
    import csv
    titles = {m["id"]: m["title"] for m in mods}
    slugs = {m["id"]: m["slug"] for m in mods}
    seen = {}
    data = []
    for i, (m, k, q, a) in enumerate(QB):
        j = seen.get(m, 0); seen[m] = j + 1
        it, hk = QH[m][j]
        data.append({"i": i, "m": m, "g": int(m.split(".")[0]), "k": k, "q": q, "a": a, "it": it, "hk": hk})
    os.makedirs(os.path.join(ROOT, "downloads"), exist_ok=True)
    with open(os.path.join(ROOT, "downloads", "SciML-question-bank.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["number", "go", "module", "module title", "kind", "question", "model answer", "intuition", "memory hook"])
        for d in data: w.writerow([d["i"] + 1, d["g"], d["m"], titles[d["m"]], d["k"], d["q"], d["a"], d["it"], d["hk"]])
    counts = {g: sum(1 for d in data if d["g"] == g) for g in (1, 2, 3)}
    modopts = "".join(f'<option value="{m["id"]}" data-go="{m["go"]}">{m["id"]} {esc(m["title"])}</option>' for m in mods)
    gobtns = '<button class="narr-lang qb-go" type="button" data-go="0" aria-pressed="true">All goes</button>' + "".join(
        f'<button class="narr-lang qb-go" type="button" data-go="{g}" aria-pressed="false">Go {g} · {esc(GO[g]["short"])} ({counts[g]})</button>' for g in (1, 2, 3))
    kinds = "".join(f'<label class="qb-kind"><input type="checkbox" value="{k}" checked> {k}</label>' for k in ("Recall", "Explain", "Calculate", "Apply"))
    meta = {"titles": titles, "slugs": slugs, "goes": {g: GO[g]["name"] for g in (1, 2, 3)}}
    page = head(f"Question bank · {SITE}", f"{len(data)} short-answer questions with model answers across the three goes of the Physical AI and SciML course.", 0) + topbar(0, "questions.html")
    page += f"""<main id="main" class="wrap qb">
<header class="gohead"><p class="eyebrow">Practice</p><h1>Question bank</h1>
<p class="summary">{len(data)} short-answer questions with model answers, covering every module of the three goes: {counts[1]} for Go 1, {counts[2]} for Go 2 and {counts[3]} for Go 3. Answer in your own words first, then reveal the model answer with its intuition and a memory hook, and mark how you did. Marked questions come back on a spaced-repetition schedule; your marks are saved in this browser.</p>
<div class="cta"><a class="btn quiet" href="downloads/SciML-question-bank.csv">Download all questions (CSV)</a><button class="btn quiet qb-print" type="button">Print with answers</button></div></header>
<details class="qb-howto"><summary><b>How to make it stick:</b> six memory techniques built into this page</summary>
<div class="qb-howto-grid">
<div><h3>1. Retrieve before you read</h3><p>Answer from memory first, aloud or with <i>Write my answer first</i>. Struggling to recall is what strengthens memory; rereading feels productive but fades fast.</p></div>
<div><h3>2. Space it out</h3><p>Mark each question honestly. <i>I knew it</i> sends it away for longer (1, 3, 7, 14, then 30 days); <i>Review again</i> brings it back tomorrow. Choose <i>Due for review</i> to see only what is due today.</p></div>
<div><h3>3. Understand the why</h3><p>Every answer comes with an <b>intuition</b>: one line on why it must be so. A fact you can rebuild from a reason is a fact you cannot lose.</p></div>
<div><h3>4. Picture it</h3><p>Every answer also has a <b>memory hook</b>, a vivid and slightly absurd image. Strange pictures stick; dry sentences slide off. Use <i>Hint</i> to see the hook as a cue before the answer.</p></div>
<div><h3>5. Place it</h3><p>The <b>memory palace</b> view parks each module in a room of a place you know. Walk the route in your head and each room hands you its module.</p></div>
<div><h3>6. Mix it up</h3><p><i>Shuffle</i> across modules and goes. Mixing topics forces you to decide which idea applies, which is exactly what an exam or a research problem asks of you.</p></div>
</div></details>
<section class="qb-controls" aria-label="Filter questions">
<div class="btnrow" role="group" aria-label="Go">{gobtns}</div>
<div class="qb-row"><label>Module <select class="qb-module"><option value="">All modules</option>{modopts}</select></label>
<label>Search <input class="qb-search" type="search" placeholder="e.g. PINN, Kalman, traffic"></label>
<label>Show <select class="qb-status"><option value="all">All questions</option><option value="due">Due for review (spaced)</option><option value="new">Not yet marked</option><option value="review">Marked 'review again'</option><option value="known">Marked 'I knew it'</option></select></label></div>
<div class="qb-row"><span class="muted small">Kind:</span>{kinds}</div>
<div class="qb-row"><div class="btnrow" role="group" aria-label="View"><button class="narr-lang qb-view" type="button" data-view="list" aria-pressed="true">List</button><button class="narr-lang qb-view" type="button" data-view="cards" aria-pressed="false">Flashcards</button><button class="narr-lang qb-view" type="button" data-view="palace" aria-pressed="false">Memory palace</button></div>
<button class="btn quiet qb-shuffle" type="button">Shuffle</button><button class="btn quiet qb-expand" type="button">Reveal all answers</button><button class="btn quiet qb-reset" type="button">Clear my marks</button></div>
<p class="qb-summary" aria-live="polite"></p><div class="qb-bar" aria-hidden="true"><span class="qb-bar-known"></span><span class="qb-bar-review"></span></div>
</section>
<section class="qb-list" aria-label="Questions"></section>
<section class="qb-cards" hidden aria-label="Flashcards"></section>
<section class="qb-palace" hidden aria-label="Memory palace"></section>
<noscript><p>This page needs JavaScript; the <a href="downloads/SciML-question-bank.csv">CSV</a> has every question and answer.</p></noscript>
</main>
<script>window.QBANK = {json.dumps(data, ensure_ascii=False)}; window.QBMETA = {json.dumps(meta, ensure_ascii=False)}; window.QBPALACE = {json.dumps(PALACE, ensure_ascii=False)};</script>
<script src="assets/js/qbank.js?v={VER}"></script>
""" + foot(0)
    return page


# ------------------------------------------------------------------ build
def build():
    mods = load()
    SLUGS.update({m["id"]: m["slug"] for m in mods})
    open(os.path.join(ROOT, "assets/js/icons.js"), "w").write("window.GCAM_ICONS = " + json.dumps(ICONS) + ";\n")
    os.makedirs(os.path.join(ROOT, "modules"), exist_ok=True)
    for f in glob.glob(os.path.join(ROOT, "modules", "*.html")): os.remove(f)
    diagrams = {"hero": HERO}
    for i, m in enumerate(mods):
        same = [x for x in mods if x["go"] == m["go"]]
        j = same.index(m)
        open(os.path.join(ROOT, "modules", m["slug"] + ".html"), "w").write(module_page(m, same[j - 1] if j else None, same[j + 1] if j + 1 < len(same) else None, diagrams))
    open(os.path.join(ROOT, "questions.html"), "w").write(questions_page(mods))
    open(os.path.join(ROOT, "assets/js/diagrams.js"), "w").write("window.GCAM_DIAGRAMS = " + json.dumps(diagrams, ensure_ascii=False) + ";\n")
    for f in ("progress.html", "labs.html", "resources.html", "downloads.html"):
        p = os.path.join(ROOT, f)
        if os.path.exists(p): os.remove(p)

    ncode = sum(len(m.get("code", [])) for m in mods); nrun = sum(1 for m in mods for c in m.get("code", []) if c.get("runnable"))
    terms = {}
    for m in mods:
        for x in m["glossary"]: terms.setdefault(x["term"].strip(), (x["def"], m))

    # ---- home
    bands = []
    for g in (1, 2, 3):
        ms = [m for m in mods if m["go"] == g]
        hrs = round(sum(m["minutes"] for m in ms) / 60, 1) if ms else 0
        bands.append(f"""<a class="goband go{g}" href="go{g}.html"><span class="gb-n">Go {g}</span><span class="gb-body"><span class="gb-depth">{GO[g]["depth"]}</span>
<span class="gb-name">{esc(GO[g]["name"])}</span><span class="gb-promise">{esc(GO[g]["promise"])}</span>
<span class="gb-meta">{(str(len(ms)) + " modules · about " + str(hrs) + " hours") if ms else "Modules being added"} · you need: {esc(GO[g]["need"].split(".")[0].lower())}</span></span></a>""")
    idx = head(f"{SITE}: learn Physical AI and scientific machine learning", "Learn Physical AI and scientific machine learning three times, each time deeper: the foundations, how to build the tools, and transportation research.", 0) + topbar(0, "index.html")
    idx += f"""<main id="main">
<section class="hero3"><div class="wrap">
<h1>Learn Physical AI and scientific machine learning three times, each time deeper</h1>
<p class="lede">Scientific machine learning blends physical laws with learning from data; Physical AI puts the results to work in machines that sense and act. You will meet it three times: first as pictures and simulations, then as tools you build step by step, then as research on transportation: safety, sustainability, GCAM, crowds and digital twins.</p>
<div class="gobands">{"".join(bands)}</div>
</div></section>
<section class="section"><div class="wrap">
<h2>The same system, three depths</h2>
<p class="prose muted">Every go covers the whole system. Choose a depth and select any part of it to see how the course treats it at that level.</p>
<div class="levels"><div class="btnrow" role="group" aria-label="Choose a depth">
<button class="narr-lang lv" type="button" data-level="1" aria-pressed="true" data-blurb="Go 1: what each part is and why it matters.">Go 1 · Foundations</button>
<button class="narr-lang lv" type="button" data-level="2" aria-pressed="false" data-blurb="Go 2: the rule or model each part follows, and what it feeds into.">Go 2 · Build and Implement</button>
<button class="narr-lang lv" type="button" data-level="3" aria-pressed="false" data-blurb="Go 3: what a mass-gathering researcher changes, measures or worries about here.">Go 3 · Research Frontier</button></div>
<p class="lv-blurb muted">Go 1: what each part is and why it matters.</p>
<div class="diagram-box"><div id="dg-hero" data-diagram="hero" data-intro="1" data-level="1" data-hint="Select a part of the system."><p class="muted">Physics, data, machine learning, uncertainty, Physical AI and transport decisions, linked.</p></div></div></div>
</div></section>
<section class="section"><div class="wrap"><h2>How the goes fit together</h2>
<div class="cols3">
<div><h3>Start where you are</h3><p>Each go opens with a three-question check. If you already know the answers, skip ahead. Each go closes with an exit check: tick off what you can do before moving on.</p></div>
<div><h3>Each go works differently</h3><p>Go 1 is pictures, animations and predict-then-check simulators. Go 2 is step-by-step builds with code that runs in your browser. Go 3 is a research brief for each transport application, with labs.</p></div>
<div><h3>Real science, honest toys</h3><p>Methods come from the cited papers. Explorers and labs use synthetic data with fixed seeds, so every number can be reproduced; they teach the ideas and are not engineering tools.</p></div></div>
<p style="margin-top:18px"><a href="models.html">Method atlas: seven SciML families with animations, simulators and mind maps</a> · <a href="spiral.html">Concept spiral: {len(THREADS)} ideas traced through all three goes</a> · <a href="mindmap-go1.html">Go 1 mind map</a> · <a href="mindmap-go2.html">Go 2 mind map</a> · <a href="mindmap-go3.html">Go 3 mind map</a> · <a href="toolkit.html">Toolkit: {ncode} code examples, handbooks and slides</a> · <a href="glossary.html">Glossary: {len(terms)} terms</a></p>
</div></section>
</main>
""" + foot(0)
    open(os.path.join(ROOT, "index.html"), "w").write(idx)

    # ---- go landing pages
    for g in (1, 2, 3):
        ms = [m for m in mods if m["go"] == g]
        info = GO[g]
        def rot(opts, a, i):
            k = (i * 2 + g) % len(opts)
            o = opts[k:] + opts[:k]
            return o, (a - k) % len(opts)
        eq = ""
        for i, (q, opts, a, ex) in enumerate(info["entry"]):
            opts, a = rot(opts, a, i)
            eq += f'<div class="q" data-answer="{a}"><p>{i + 1}. {esc(q)}</p><div class="opts">' + "".join(f'<button class="opt" type="button">{esc(o)}</button>' for o in opts) + f'</div><p class="fb" hidden><b class="verdict"></b>{esc(ex)}</p></div>'

        seen, res = set(), []
        for m in ms:
            for r in m["resources"]:
                if r["url"] in seen: continue
                seen.add(r["url"]); res.append(f'<li><a href="{esc(r["url"])}" target="_blank" rel="noopener">{esc(r["title"])}</a><span class="why">{esc(r["why"])} <span class="muted">· module {m["id"]}</span></span></li>')
        mats = [f'<a class="btn" href="{info["handbook"]}">Go {g} handbook (PDF)</a>', f'<a class="btn quiet" href="mindmap-go{g}.html">Zooming mind map</a>', f'<a class="btn quiet" href="questions.html?go={g}">Question bank ({sum(1 for q in QB if q[0].startswith(str(g) + "."))} questions)</a>']
        if info["kit"]: mats.append(f'<a class="btn quiet" href="{info["kit"]}">Go {g} code kit (zip)</a>')
        if g >= 2: mats.append('<a class="btn quiet" href="models.html">Method atlas: 7 SciML families</a>')
        mats.append('<a class="btn quiet" href="spiral.html">Concept spiral</a>')
        prev_go = f'<a href="go{g - 1}.html">Go {g - 1}</a>' if g > 1 else ""
        nxt = f'<a class="btn" href="go{g + 1}.html">Go on to Go {g + 1}: {esc(GO[g + 1]["name"])}</a>' if g < 3 else '<a class="btn" href="toolkit.html">Start your project with the toolkit</a>'
        skip = f'All three right? You could <a href="go{g + 1}.html">skip ahead to Go {g + 1}</a>, or use this go as revision.' if g < 3 else "All three right? You are ready for the research modules."
        exitl = "".join(f'<li><label><input type="checkbox"> {esc(x)}</label></li>' for x in info["exit"])
        first = ms[0]["slug"] if ms else ""
        page = head(f"Go {g}: {info['name']} · {SITE}", info["promise"], 0) + topbar(0, f"go{g}.html", f' data-go="{g}"')
        page += f"""<main id="main" class="wrap">
<header class="gohead go{g}"><p class="eyebrow"><span class="golevel">Go {g} · {info["depth"]}</span></p><h1>{esc(info["name"])}</h1><p class="summary">{esc(info["promise"])}</p>
<div class="cta">{"<a class='btn' href='modules/" + first + ".html'>Start module " + str(g) + ".1</a>" if first else ""}{"".join(mats)}</div></header>
<div class="go-grid">
<section><h2>Is this go for you?</h2><p class="prose"><b>You need:</b> {esc(info["need"])}</p><p class="prose"><b>How it works:</b> {esc(info["style"])}</p>
<h3>Quick entry check</h3><div class="quiz" data-module="go{g}-entry">{eq}<p class="quiz-result" hidden aria-live="polite"></p></div><p class="small muted">{skip} {("Not sure? Revisit " + prev_go + ".") if prev_go else ""}</p></section>
<section><h2>What you will produce</h2><ul class="prose">{"".join(f"<li>{esc(x)}</li>" for x in info["produce"])}</ul>
<h2>The path</h2>{module_list(ms)}</section></div>
<section id="exit"><h2>Exit check</h2><p class="prose muted">Tick each statement you can honestly say. Your ticks are saved in this browser.</p>
<ul class="exitcheck checklist" data-key="go{g}-exit">{exitl}</ul><p class="exit-msg muted"></p><div class="cta">{nxt}</div></section>
<section><h2>Readings and tools for Go {g}</h2><ul class="reslist">{"".join(res)}</ul></section>
</main>""" + foot(0)
        open(os.path.join(ROOT, f"go{g}.html"), "w").write(page)
        open(os.path.join(ROOT, f"mindmap-go{g}.html"), "w").write(mindmap_page(g, mindmap_data(g, ms)))

    # ---- toolkit (code, handbooks, kits, slides, tools, progress)
    rows = []
    for m in mods:
        for c in m.get("code", []):
            run = c.get("runnable") and c.get("lang") == "python"
            tags = f'go{m["go"]} {c.get("lang", "")} {"browser" if run else "local"}'
            where = '<span class="runs">Runs in your browser</span>' if run else ("Download" if c.get("file") else "Copy from the page")
            fl = f' · <a href="{esc(c["file"])}" download>file</a>' if c.get("file") else ""
            rows.append(f'<tr class="labrow" data-tags="{tags}"><td>Go {m["go"]} · {m["id"]}</td><td><a href="modules/{m["slug"]}.html#code">{esc(c["title"])}</a>{fl}</td><td>{ {"python": "Python", "r": "R", "xml": "XML", "bash": "Shell"}.get(c.get("lang"), c.get("lang"))}</td><td>{where}</td></tr>')
    flt = "".join(f'<button class="lab-filter" type="button" data-filter="{f}" aria-pressed="{"true" if f == "all" else "false"}">{t}</button>' for f, t in [("all", "All"), ("go1", "Go 1"), ("go2", "Go 2"), ("go3", "Go 3"), ("browser", "Runs in browser"), ("python", "Python")])

    def size(p):
        try: return f'{os.path.getsize(os.path.join(ROOT, p)) / 1e6:.1f} MB'
        except OSError: return ""

    def item(p, t, d):
        return f'<li><a href="{p}">{esc(t)}</a> <span class="muted small">{size(p)}</span><span class="why">{esc(d)}</span></li>' if os.path.exists(os.path.join(ROOT, p)) else ""
    hand = "".join([item(GO[1]["handbook"], "Go 1 handbook: Foundations", "Every Go 1 module in print: pictures, worked numbers, memory scenes, quizzes and a cheat sheet."),
                    item(GO[2]["handbook"], "Go 2 handbook: Build and Implement", "Step-by-step builds of each SciML tool, with the code labs."),
                    item(GO[3]["handbook"], "Go 3 handbook: Research Frontier", "Transportation research briefs: traffic, vehicles, safety, energy, GCAM, crowds and digital twins.")])
    kits = "".join([item("downloads/go2-kit.zip", "Go 2 kit: SciML tools in Python", "Workflow, PINN (NumPy and PyTorch), heat-equation solver and PINN, SINDy, operator learning and DeepONet, Gaussian processes, hybrid model and conformal prediction."),
                    item("downloads/go3-research-kit.zip", "Go 3 transport research kit", "Traffic state estimation, car-following platoons, conflict analysis, hybrid emissions, IAM emulator with active learning, crowd fundamental diagram and a digital twin.")])
    mm = "".join(item(f"downloads/mindmaps/Go{g}-mind-map-path.pdf", f"Go {g} mind map, zoom path (PDF)", "Each zoom step as a page; import into Prezi or present as is.") for g in (1, 2, 3))
    slides = "".join(item(f"downloads/slides/{os.path.basename(p)}", os.path.basename(p)[:-4].replace("-", " ").replace("Week", "Week "), "Lecture and lab slides (PDF); the editable PowerPoint has the same name.") for p in sorted(glob.glob(os.path.join(ROOT, "downloads", "slides", "*.pdf"))))
    trs = "".join(f'<tr data-id="{m["id"]}"><td>{m["id"]}</td><td><a href="modules/{m["slug"]}.html">{esc(m["title"])}</a></td>' + '<td class="k">–</td>' * 7 + "</tr>" for m in mods)
    page = head(f"Toolkit · {SITE}", "Code, handbooks, kits and tools for learning Physical AI and SciML in three goes.", 0) + topbar(0, "toolkit.html")
    page += f"""<main id="main" class="wrap"><header class="page-head"><h1>Toolkit</h1><p>Everything you can run, download or install, in one place. The browser labs teach the ideas with NumPy; the PyTorch labs and libraries below scale them to real studies.</p></header>
<h2>Code examples</h2><p class="prose muted">{ncode} examples. Python marked "Runs in your browser" runs on its module page with nothing to install.</p>
<div class="filters" role="group" aria-label="Filter code examples">{flt}</div>
<div class="tscroll"><table class="tbl"><thead><tr><th>Where</th><th>Example</th><th>Language</th><th>How to use</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>
<h2>Handbooks</h2><ul class="reslist">{hand}</ul>
<h2>Code kits</h2><ul class="reslist">{kits}</ul>
<h2>Mind maps</h2><ul class="reslist">{mm}<li><a href="mindmap-go1.html">Zooming mind maps in the browser</a><span class="why">Go 1, Go 2 and Go 3, presentable full screen.</span></li></ul>
<h2>Open tools and data</h2><ul class="reslist">
<li><a href="https://pytorch.org/" target="_blank" rel="noopener">PyTorch</a><span class="why">Neural networks with automatic differentiation; used by the downloadable labs.</span></li>
<li><a href="https://deepxde.readthedocs.io/" target="_blank" rel="noopener">DeepXDE</a><span class="why">Library for physics-informed neural networks and DeepONet, with many examples.</span></li>
<li><a href="https://pysindy.readthedocs.io/" target="_blank" rel="noopener">PySINDy</a><span class="why">Sparse identification of nonlinear dynamics (equation discovery).</span></li>
<li><a href="https://github.com/NVIDIA/physicsnemo" target="_blank" rel="noopener">NVIDIA PhysicsNeMo</a><span class="why">Open-source framework for physics-ML models (formerly Modulus).</span></li>
<li><a href="https://eclipse.dev/sumo/" target="_blank" rel="noopener">SUMO</a><span class="why">Open-source traffic simulator for generating data and building digital twins.</span></li>
<li><a href="https://levelxdata.com/highd-dataset/" target="_blank" rel="noopener">highD dataset</a><span class="why">Drone-recorded vehicle trajectories for car following, safety and estimation studies.</span></li>
<li><a href="https://github.com/JGCRI/gcam-core" target="_blank" rel="noopener">GCAM</a><span class="why">The open-source Global Change Analysis Model, for emulator studies.</span></li></ul>
<h2 id="progress">Your progress</h2><p class="prose muted">Saved only in this browser on this device; nothing is sent anywhere.</p>
<p id="progress-summary" class="muted"></p><div class="meter"><i id="progress-meter" style="width:0"></i></div>
<div class="tscroll"><table class="tbl" id="progress-table"><thead><tr><th>Module</th><th>Title</th><th>Opened</th><th>Listened</th><th>Walkthrough</th><th>Explorer</th><th>Ran code</th><th>Quiz</th><th>Studied</th></tr></thead><tbody>{trs}</tbody></table></div>
<div class="btnrow"><button class="btn quiet" id="progress-export" type="button">Download my progress</button><button class="btn quiet" id="progress-reset" type="button">Clear my progress</button></div>
</main>""" + foot(0)
    open(os.path.join(ROOT, "toolkit.html"), "w").write(page)

    # ---- glossary
    gl = "".join(f'<div class="gterm"><dt>{esc(t)}</dt><dd>{esc(d)} <a class="small" href="modules/{m["slug"]}.html#more">Go {m["go"]}, module {m["id"]}</a></dd></div>' for t, (d, m) in sorted(terms.items(), key=lambda x: x[0].lower()))
    page = head(f"Glossary · {SITE}", "Plain-language glossary of Physical AI and scientific machine learning terms.", 0) + topbar(0, "glossary.html")
    page += f"""<main id="main" class="wrap"><header class="page-head"><h1>Glossary</h1><p>Every new word in the three goes, in plain language, with the module where it first appears.</p>
<input class="searchbox" id="glossary-search" type="search" placeholder="Search the glossary" aria-label="Search the glossary"><p class="small muted" id="glossary-count">{len(terms)} terms</p></header>
<dl class="glist" style="margin-top:20px">{gl}</dl></main>""" + foot(0)
    open(os.path.join(ROOT, "glossary.html"), "w").write(page)
    open(os.path.join(ROOT, "models.html"), "w").write(models_page(mods))
    open(os.path.join(ROOT, "spiral.html"), "w").write(spiral_page(mods))
    print(f"built {len(mods)} modules, {ncode} code blocks ({nrun} runnable), {len(terms)} terms")




# ------------------------------------------------------------------ model atlas and concept spiral (Nov 2026)
def models_page(mods):
    tabs, panels, maps = [], [], {}
    for i, M in enumerate(MODELS):
        k = M["key"]
        tabs.append(f'<button class="narr-lang atlas-tab" type="button" data-k="{k}" aria-pressed="{"true" if i == 0 else "false"}">{icon_svg(M["icon"])}{esc(M["name"])}</button>')
        facts = "".join(f'<div><b>{esc(a)}</b>{esc(b)}</div>' for a, b in M["facts"])
        anim = open(os.path.join(FIGDIR, f"model-{k}.svg"), encoding="utf-8").read()
        disc = "".join(f"<p>{esc(x)}</p>" for x in M["discussion"])
        maps[f"model-{k}"] = {"title": M["name"], "center": M["name"], "subtitle": "Method atlas", "icon": M["icon"], "promise": M["discussion"][0],
                              "branches": [{"id": "", "title": t, "sys": cm(sy), "summary": su, "leaves": [dict({"t": a, "n": b}, **({"i": leaf_icon(a + " " + b)} if leaf_icon(a + " " + b) else {})) for a, b in lv]} for t, sy, su, lv in M["mm"]]}
        panels.append(f"""<section class="atlas-panel" data-k="{k}"{"" if i == 0 else " hidden"}><div class="atlas-card">
<p class="eyebrow">{esc(M["inst"])}</p><h2 style="margin-top:0">{esc(M["name"])}</h2><div class="atlas-facts">{facts}</div>
<h3>How it works (animation)</h3><figure class="figure-card">{anim}<figcaption><b>Watch the solution concept.</b> <span>A teaching animation of the idea, not model output.</span><button class="btn quiet fig-play" type="button">Pause animation</button></figcaption></figure>
<h3>Discussion</h3><div class="prose">{disc}</div>
<h3>Simulate it</h3><div class="explorer" data-widget="{M["widget"]}" data-module="atlas-{k}"><div class="explorer-box"><p class="muted">This simulator needs JavaScript.</p></div></div>
<h3>Mind map</h3>{mm_markup(f"model-{k}", "", embed=True, label=f"Mind map of {M['name']}")}
</div></section>""")
    rows = "".join(f'<tr><td><b>{esc(M["name"])}</b></td>' + "".join(f"<td>{esc(dict(M['facts']).get(c, '–'))}</td>" for c in ("Learns", "Needs", "Strength", "Best for")) + "</tr>" for M in MODELS)
    whoq = [("I fit the data and, at many collocation points, penalise any breach of a known equation.", 0),
            ("I fit all candidate terms, throw away the small ones, and hand you a short readable equation.", 1),
            ("I learn a map from whole input functions to whole solutions, with a branch net and a trunk net.", 2),
            ("I give you a prediction and an honest error bar that widens far from the data.", 3),
            ("I keep a physics model and learn only what it gets wrong.", 4),
            ("I learn a slow simulator's input-output map from a few runs and answer in milliseconds.", 5),
            ("I predict with physics, then correct with each noisy measurement, weighted by trust.", 6)]
    names = [M["name"] for M in MODELS]
    quiz = ""
    for j, (q, a) in enumerate(whoq):
        opts = [a] + [x for x in ((a + 1) % len(MODELS), (a + 3) % len(MODELS), (a + 5) % len(MODELS))]
        rot = j % 4; opts = opts[rot:] + opts[:rot]; ans = opts.index(a)
        quiz += f'<div class="q" data-answer="{ans}"><p>{j + 1}. "{esc(q)}" Who am I?</p><div class="opts">' + "".join(f'<button class="opt" type="button">{esc(names[o])}</button>' for o in opts) + f'</div><p class="fb" hidden><b class="verdict"></b>It is {esc(names[a])}.</p></div>'
    page = head(f"Method atlas · {SITE}", "Seven SciML method families compared: how each works, animated, with a simulator, a mind map and a discussion.", 0) + topbar(0, "models.html")
    page += f"""<main id="main" class="wrap">
<header class="gohead go2"><p class="eyebrow"><span class="golevel">Go 2 · Build and Implement</span> Companion to Go 2</p><h1>Method atlas</h1>
<p class="summary">Seven families of scientific machine learning, from physics-informed networks to data assimilation. Each has an animation of how it works, a simulator you can run, a zooming mind map and a discussion of strengths and limits. They are built step by step in <a href="go2.html">Go 2</a>.</p></header>
<section><h2>All seven at a glance</h2><div class="tscroll"><table class="tbl atlas-cmp"><thead><tr><th>Method</th><th>Learns</th><th>Needs</th><th>Strength</th><th>Best for</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="small muted">From the original papers cited on each card. The simulators are teaching versions that show each idea.</p></section>
<section><h2>Explore one method</h2><div class="atlas-tabs" role="group" aria-label="Choose a method">{"".join(tabs)}</div>{"".join(panels)}</section>
<section><h2>Quiz: who am I?</h2><div class="quiz" data-module="atlas-quiz">{quiz}<p class="quiz-result" hidden aria-live="polite"></p><button class="btn quiet quiz-again" type="button">Try again</button></div>
<p class="prose">Then try the simulation challenges in the <a href="go2.html">Go 2 modules</a>.</p></section>
</main>
<script>window.MINDMAPS = window.MINDMAPS || {{}}; Object.assign(window.MINDMAPS, {json.dumps(maps, ensure_ascii=False)});
document.querySelectorAll(".atlas-tab").forEach((b) => b.addEventListener("click", () => {{ document.querySelectorAll(".atlas-tab").forEach((x) => x.setAttribute("aria-pressed", x === b)); document.querySelectorAll(".atlas-panel").forEach((p) => (p.hidden = p.dataset.k !== b.dataset.k)); }}));</script>
<script src="assets/js/mindmap.js?v={VER}"></script>
""" + foot(0)
    return page


def spiral_page(mods):
    titles = {m["id"]: m["title"] for m in mods}
    data = [dict(id=t["id"], name=t["name"], icon=t["icon"], sys=cm(t["sys"]), stops=[dict(m=a, slug=SLUGS.get(a, ""), title=titles.get(a, ""), what=b, q=c, a=d) for a, b, c, d in t["stops"]]) for t in THREADS]
    chips_ = "".join(f'<button class="narr-lang sp-chip" type="button" data-t="{t["id"]}" aria-pressed="false">{esc(t["name"])}</button>' for t in THREADS)
    page = head(f"Concept spiral · {SITE}", "Every core idea of the course met three times, one level deeper each time.", 0) + topbar(0, "spiral.html")
    page += f"""<main id="main" class="wrap">
<header class="gohead"><p class="eyebrow">Spiral curriculum</p><h1>Concept spiral</h1>
<p class="summary">The course is a spiral: each core idea appears in Go 1 as a picture, returns in Go 2 as a mechanism, and again in Go 3 as a research tool. Select a thread to follow it outward, then test yourself with questions from every level.</p></header>
<div class="spiral-wrap"><div><svg class="spiral-svg" viewBox="-430 -340 860 680" role="img" aria-label="Concept spiral"></svg>
<p class="small muted">Inner ring: Go 1 · middle: Go 2 · outer: Go 3. Each coloured line is one idea; select it or a dot.</p></div>
<div><div class="thread-list" role="group" aria-label="Threads">{chips_}</div><div class="sp-panel atlas-card"><h3 style="margin-top:0">Pick a thread</h3><p>Or press <b>Quiz me</b> for a random question from any go.</p></div>
<div class="btnrow"><button class="btn sp-quiz" type="button">Quiz me</button><button class="btn quiet sp-play" type="button">Animate all threads</button></div><div class="sp-q"></div></div></div>
</main>
<script>
(function(){{
const T = {json.dumps(data, ensure_ascii=False)}, NS = "http://www.w3.org/2000/svg", R = [95, 185, 275], svg = document.querySelector(".spiral-svg");
const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim(), col = (s) => css("--" + (s === "neutral" ? "ink-soft" : s));
const el = (t, a, p) => {{ const e = document.createElementNS(NS, t); for (const k in a) e.setAttribute(k, a[k]); p && p.append(e); return e; }};
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}}[c]));
R.forEach((r, i) => {{ el("circle", {{ cx: 0, cy: 0, r, class: "ring" }}, svg); const t = el("text", {{ x: 0, y: -r + 16, "text-anchor": "middle", style: "font-size:12px;opacity:.6" }}, svg); t.textContent = "Go " + (i + 1); }});
const lines = {{}};
T.forEach((t, k) => {{
  const a0 = (2 * Math.PI * k) / T.length, pts = t.stops.map((s, i) => {{ const a = a0 + i * 0.32; return [R[i] * Math.cos(a), R[i] * Math.sin(a)]; }});
  const d = `M0,0 Q${{pts[0][0] * 0.5}},${{pts[0][1] * 0.5 - 10}} ${{pts[0][0]}},${{pts[0][1]}} ` + pts.slice(1).map((p, i) => `Q${{(pts[i][0] + p[0]) / 2 * 1.08}},${{(pts[i][1] + p[1]) / 2 * 1.08}} ${{p[0]}},${{p[1]}}`).join(" ");
  const pth = el("path", {{ d, class: "thr", stroke: col(t.sys) }}, svg); lines[t.id] = pth; pth.addEventListener("click", () => pick(t.id));
  pts.forEach((p, i) => {{ const g = el("g", {{ class: "stop", tabindex: 0 }}, svg); el("circle", {{ cx: p[0], cy: p[1], r: 9, fill: col(t.sys) }}, g); g.addEventListener("click", () => pick(t.id)); if (i === 2) {{ const tx = el("text", {{ x: p[0] * 1.1, y: p[1] * 1.1 + 4, "text-anchor": p[0] > 0 ? "start" : "end" }}, svg); tx.textContent = t.name; }} }});
}});
el("circle", {{ cx: 0, cy: 0, r: 26, fill: css("--ink") }}, svg); const c = el("text", {{ x: 0, y: 5, "text-anchor": "middle", style: `fill:${{css("--paper")}};font-weight:700` }}, svg); c.textContent = "SciML";
const panel = document.querySelector(".sp-panel");
function pick(id) {{
  const t = T.find((x) => x.id === id);
  Object.entries(lines).forEach(([k, p]) => p.classList.toggle("on", k === id));
  document.querySelectorAll(".sp-chip").forEach((b) => b.setAttribute("aria-pressed", b.dataset.t === id));
  panel.innerHTML = `<h3 style="margin-top:0">${{esc(t.name)}}</h3>` + t.stops.map((s, i) => `<div class="thread-step g${{i + 1}}" style="margin-bottom:8px"><div class="tgo">Go ${{i + 1}} · <a href="modules/${{s.slug}}.html">${{s.m}} ${{esc(s.title)}}</a></div>${{esc(s.what)}}<div class="thread-recall"><b>Recall:</b> ${{esc(s.q)}} <button class="btn quiet" type="button">Show answer</button><div class="ans">${{esc(s.a)}}</div></div></div>`).join("");
  panel.querySelectorAll(".thread-recall button").forEach((b) => b.addEventListener("click", () => {{ const r = b.closest(".thread-recall"); r.classList.toggle("open"); b.textContent = r.classList.contains("open") ? "Hide" : "Show answer"; }}));
}}
document.querySelectorAll(".sp-chip").forEach((b) => b.addEventListener("click", () => pick(b.dataset.t)));
document.querySelector(".sp-play").addEventListener("click", () => {{ T.forEach((t, i) => setTimeout(() => pick(t.id), i * 900)); }});
document.querySelector(".sp-quiz").addEventListener("click", () => {{
  const t = T[Math.floor(Math.random() * T.length)], i = Math.floor(Math.random() * 3), s = t.stops[i], box = document.querySelector(".sp-q");
  box.innerHTML = `<div class="thread-recall" style="margin-top:12px"><b>Go ${{i + 1}} · ${{esc(t.name)}}:</b> ${{esc(s.q)}} <button class="btn quiet" type="button">Show answer</button><div class="ans">${{esc(s.a)}} <a href="modules/${{s.slug}}.html">Open module ${{s.m}}</a></div></div>`;
  box.querySelector("button").addEventListener("click", (e) => {{ const r = e.target.closest(".thread-recall"); r.classList.toggle("open"); e.target.textContent = r.classList.contains("open") ? "Hide" : "Show answer"; }});
  pick(t.id);
}});
}})();
</script>
""" + foot(0)
    return page


if __name__ == "__main__":
    build()
