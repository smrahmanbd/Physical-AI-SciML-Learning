"""Validate module JSON files against SCHEMA.md. Usage: python3 validate.py content/m*.json"""
import json, sys, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYS = {"physics", "data", "learn", "system", "risk", "apply"}
NSYS = SYS | {"model", "neutral"}
WIDGETS = set("spectrum ode nnfit gd pinn noise surrogate kalman split pinntrain heat sindy operator gp hybrid conformal trafficpinn idm ttc vsp emulator crowdfit twin".split())
TAGS = re.compile(r"</?([a-zA-Z0-9]+)")
OK_TAGS = set("p ul ol li b strong i em code a table thead tbody tr th td sub sup br div span".split())


def check(path):
    e = []
    try:
        d = json.load(open(path))
    except Exception as x:
        return [f"invalid JSON: {x}"]
    L = lambda k, s, n: e.append(f"{k}: {len(s)} > {n}") if s and len(s) > n else None
    for k in "id go slug title minutes tag systems summary outcomes narration_en narration_ar diagram sections takeaways quiz glossary resources".split():
        if k not in d: e.append(f"missing {k}")
    if e: return e
    L("title", d["title"], 60); L("tag", d["tag"], 14); L("summary", d["summary"], 220)
    if not set(d["systems"]) <= SYS: e.append("bad systems")
    if not 3 <= len(d["outcomes"]) <= 5: e.append("outcomes 3-5")
    w = len(d["narration_en"].split())
    if not 110 <= w <= 240: e.append(f"narration_en words {w}")
    if not re.search(r"[؀-ۿ]", d["narration_ar"]): e.append("narration_ar not Arabic")
    g = d["diagram"]; ids = {n["id"] for n in g["nodes"]}
    for n in g["nodes"]:
        if n.get("sys") not in NSYS: e.append(f"node {n['id']} sys")
        w_, h_ = n.get("w", 150), n.get("h", 60)
        if not (w_ / 2 <= n["x"] <= 900 - w_ / 2 and h_ / 2 <= n["y"] <= 520 - h_ / 2): e.append(f"node {n['id']} off canvas")
        L(f"node {n['id']} sub", n.get("sub", ""), 40); L(f"node {n['id']} detail", n.get("detail", ""), 450)
    for a in g["nodes"]:
        for b in g["nodes"]:
            if a is b: continue
            if abs(a["x"] - b["x"]) * 2 < (a.get("w", 150) + b.get("w", 150)) and abs(a["y"] - b["y"]) * 2 < (a.get("h", 60) + b.get("h", 60)):
                e.append(f"nodes {a['id']} and {b['id']} overlap")
    for ed in g.get("edges", []):
        if ed["from"] not in ids or ed["to"] not in ids: e.append(f"edge {ed} bad id")
        L("edge label", ed.get("label", ""), 24)
    if not 4 <= len(g.get("tour", [])) <= 8: e.append("tour 4-8 steps")
    for t in g.get("tour", []):
        if not set(t.get("focus", [])) <= ids: e.append("tour focus bad id")
        L("tour text", t["text"], 220)
    if not 3 <= len(d["sections"]) <= 7: e.append("sections 3-7")
    for s in d["sections"] + d.get("callouts", []):
        bad = {t.lower() for t in TAGS.findall(s["html"])} - OK_TAGS
        if bad: e.append(f"bad tags {bad} in {s.get('heading') or s.get('title')}")
    for c in d.get("callouts", []):
        if c["kind"] not in {"model", "trap", "gcam", "research", "try"}: e.append("callout kind")
        if not 0 <= c["after"] < len(d["sections"]): e.append("callout after index")
    if "explorer" in d and d["explorer"]["widget"] not in WIDGETS: e.append("unknown widget")
    for c in d.get("code", []):
        if c.get("file") and not os.path.exists(os.path.join(ROOT, c["file"])): e.append(f"missing file {c['file']}")
        if not c.get("file") and not c.get("source"): e.append("code needs file or source")
        if c.get("runnable") and c.get("lang") != "python": e.append("only python runnable")
    if not 3 <= len(d["takeaways"]) <= 6: e.append("takeaways 3-6")
    if not 3 <= len(d["quiz"]) <= 5: e.append("quiz 3-5")
    for q in d["quiz"]:
        if len(q["options"]) != 4 or q["answer"] not in range(4) or not q.get("explain"): e.append("quiz item malformed")
    for r in d["resources"]:
        if not r["url"].startswith("http"): e.append("resource url")
    for dl in d.get("downloads", []):
        p = dl["path"]
        if not (p.startswith("downloads/")): e.append(f"download path {p}")
    return e


ok = True
for p in sys.argv[1:]:
    e = check(p)
    print(p, "OK" if not e else f"{len(e)} problems")
    for x in e: print("  -", x)
    ok &= not e
sys.exit(0 if ok else 1)
