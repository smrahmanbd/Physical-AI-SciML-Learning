"""Build downloads: Go handbooks (PDF), mind-map zoom-path PDFs and lab kits (zip)."""
import json, glob, os, sys, html, zipfile, asyncio
sys.path.insert(0, os.path.dirname(__file__))
from mindmaps import MM
from qbank import Q as QB
from qhooks import PALACE
ROOT = os.path.join(os.path.dirname(__file__), "..")
DL = os.path.join(ROOT, "downloads")
os.makedirs(os.path.join(DL, "mindmaps"), exist_ok=True)
esc = html.escape
COL = dict(learn="#8f3520", physics="#0b3954", system="#2f5a1c", data="#04505a", risk="#7a4412", apply="#3f3266", model="#4a4a5a", neutral="#4a4a5a")
GOS = {1: ("Foundations", "Go1-Handbook-SciML-Foundations.pdf"), 2: ("Build and Implement", "Go2-Handbook-SciML-Build.pdf"), 3: ("Research Frontier: Transportation", "Go3-Handbook-SciML-Transport.pdf")}
mods = sorted((json.load(open(f)) for f in glob.glob(os.path.join(os.path.dirname(__file__), "m*.json"))), key=lambda m: [int(x) for x in m["id"].split(".")])
CSS = """@page{size:A4;margin:18mm 17mm 20mm}body{font-family:Carlito,Arial,sans-serif;font-size:11pt;line-height:1.45;color:#14283a}
h1,h2,h3{font-family:Poppins,Arial,sans-serif;line-height:1.15}h1{font-size:26pt;margin:0 0 6pt}h2{font-size:17pt;margin:18pt 0 6pt;page-break-before:always}
h3{font-size:12.5pt;margin:12pt 0 4pt;color:#0b3954}.cover{height:250mm;display:flex;flex-direction:column;justify-content:center;background:#0b3954;color:#fff;padding:0 18mm;margin:-18mm -17mm 0;page-break-after:always}
.cover h1{font-size:34pt;color:#fff}.cover p{font-size:14pt;color:#dfe8ef}.box{border:1.5pt solid #d5dde3;border-radius:6pt;padding:6pt 10pt;margin:8pt 0;page-break-inside:avoid}
.try{border-color:#2f5a1c}.trap{border-color:#8f3520}.research{border-color:#3f3266}.tag{font:600 8.5pt Poppins,Arial;letter-spacing:.06em;text-transform:uppercase;color:#4a4a5a}
.eq{font-family:"TeX Gyre Pagella",serif;font-size:12pt;text-align:center;margin:6pt 0}table{border-collapse:collapse;margin:6pt 0}td,th{border:1px solid #d5dde3;padding:3pt 6pt;font-size:10pt}
pre{background:#f1f4f7;padding:6pt 8pt;font-size:8.6pt;white-space:pre-wrap;page-break-inside:avoid}.meta{color:#4a4a5a}.ans{font-size:10pt}li{margin:2pt 0}
.toc li{margin:3pt 0}.mmfig{page-break-inside:avoid;text-align:center}.mmfig svg{width:100%}"""


def mm_svg(center, branches, W=None):
    """Left/right tree: branches = [(title, sys, [leaf, ...])]; width from text extents."""
    if W is None:
        bw = max(9.2 * len(b[0]) + 24 for b in branches); lw = max([7.6 * len(l) for b in branches for l in b[2]] + [0])
        W = int(2 * ((9.5 * len(center) + 40) / 2 + 60 + bw + 26 + lw) + 30)
    n = len(branches); right = branches[::2]; left = branches[1::2]
    rows = max(sum(1 + len(b[2]) for b in right), sum(1 + len(b[2]) for b in left), 1)
    lh = 30; H = max(rows * lh + 60, int(W * 0.52)); cx, cy = W / 2, H / 2; cw = 9.5 * len(center) + 40
    out = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="Carlito,Arial">']
    def side(bs, sgn):
        tot = sum(1 + len(b[2]) for b in bs); y = cy - tot * lh / 2 + lh / 2
        for t, sy, lv in bs:
            c = COL.get(sy, "#4a4a5a"); bx = cx + sgn * (cw / 2 + 60)
            out.append(f'<path d="M{cx},{cy} C{cx + sgn * (cw / 2 + 20)},{cy} {bx - sgn * 40},{y} {bx},{y}" stroke="{c}" stroke-width="3" fill="none"/>')
            w = 9.2 * len(t) + 24; x0 = bx if sgn > 0 else bx - w
            out.append(f'<rect x="{x0}" y="{y - 13}" width="{w}" height="26" rx="13" fill="{c}"/><text x="{x0 + w / 2}" y="{y + 5}" text-anchor="middle" fill="#fff" font-size="15" font-weight="700">{esc(t)}</text>')
            ly = y
            for l in lv:
                ly += lh; lx = bx + sgn * (w + 18)
                out.append(f'<path d="M{bx + sgn * w},{y} C{bx + sgn * (w + 8)},{y} {lx - sgn * 10},{ly} {lx},{ly}" stroke="{c}" stroke-width="1.6" fill="none" opacity=".7"/>')
                out.append(f'<text x="{lx + sgn * 4}" y="{ly + 5}" text-anchor="{"start" if sgn > 0 else "end"}" font-size="14" fill="#14283a">{esc(l)}</text>')
            y = ly + lh
    side(right, 1); side(left, -1)
    w = cw
    out.append(f'<rect x="{cx - w / 2}" y="{cy - 20}" width="{w}" height="40" rx="20" fill="#14283a"/><text x="{cx}" y="{cy + 6}" text-anchor="middle" fill="#fff" font-size="17" font-weight="700">{esc(center)}</text></svg>')
    return "".join(out)


def handbook(g):
    name, fn = GOS[g]; ms = [m for m in mods if m["go"] == g]
    h = [f'<html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="cover"><p class="tag" style="color:#cfe0ea">Physical AI and SciML in three goes · Handbook</p><h1>Go {g}: {esc(name)}</h1><p>{len(ms)} modules · about {sum(m["minutes"] for m in ms) / 60:.1f} hours of study</p><p style="font-size:11pt">Companion to the website. Explorers, simulations, challenges and runnable code are online; this handbook keeps the text, worked numbers, mind maps and questions for reading offline.</p></div>']
    h.append('<h1 style="font-size:20pt">Contents</h1><ol class="toc">' + "".join(f'<li><b>{m["id"]} {esc(m["title"])}</b> · {m["minutes"]} min<br><span class="meta">{esc(m["summary"])}</span></li>' for m in ms) + "</ol>")
    h.append('<div class="mmfig"><h3>Mind map of the go</h3>' + mm_svg(f"Go {g}", [(f'{m["id"]} {m["title"]}', m["systems"][0], [b[0] for b in MM[m["id"]]][:4]) for m in ms]) + "</div>")
    for m in ms:
        h.append(f'<h2>{m["id"]} {esc(m["title"])}</h2><p class="meta">{m["minutes"]} minutes · {esc(m["tag"])}</p><p><b>{esc(m["summary"])}</b></p>')
        h.append("<h3>By the end you can</h3><ul>" + "".join(f"<li>{esc(o)}</li>" for o in m["outcomes"]) + "</ul>")
        h.append(f'<h3>Overview</h3><p>{esc(m["narration_en"])}</p>')
        h.append('<div class="mmfig">' + mm_svg("Module " + m["id"], [(b[0], b[1], [l[0] for l in b[3]]) for b in MM[m["id"]]]) + "</div>")
        cal = {}
        for c in m.get("callouts", []): cal.setdefault(c["after"], []).append(c)
        for i, s in enumerate(m["sections"]):
            h.append(f'<h3>{esc(s["heading"])}</h3>{s["html"]}')
            for c in cal.get(i, []): h.append(f'<div class="box {c["kind"]}"><span class="tag">{esc(c["kind"])}</span> <b>{esc(c["title"])}</b>{c["html"]}</div>')
        for c in m.get("code", []):
            if c.get("expected"): h.append(f'<div class="box"><span class="tag">Lab</span> <b>{esc(c["title"])}</b>{"<br><code>" + esc(c["file"]) + "</code>" if c.get("file") else ""}<p>{esc(c["explain"])}</p><pre>{esc(c["expected"])}</pre></div>')
        h.append("<h3>Takeaways</h3><ul>" + "".join(f"<li>{esc(t)}</li>" for t in m["takeaways"]) + "</ul>")
        st, sc = PALACE.get(m["id"], ("", ""))
        if st: h.append(f'<div class="box research"><span class="tag">Memory palace</span> <b>{esc(st)}</b><p>{esc(sc)}</p></div>')
        h.append("<h3>Check yourself</h3><ol>" + "".join(f'<li>{esc(q["q"])}<br>' + " · ".join(f"({chr(97 + k)}) {esc(o)}" for k, o in enumerate(q["options"])) + "</li>" for q in m["quiz"]) + "</ol>")
        h.append('<p class="ans"><b>Answers:</b> ' + "; ".join(f'{k + 1} ({chr(97 + q["answer"])}) {esc(q.get("explain", ""))}' for k, q in enumerate(m["quiz"])) + "</p>")
        h.append("<h3>Words</h3><ul>" + "".join(f'<li><b>{esc(x["term"])}</b>: {esc(x["def"])}</li>' for x in m["glossary"]) + "</ul>")
        h.append("<h3>Reading</h3><ul>" + "".join(f'<li>{esc(r["title"])}: {esc(r["why"])} <span class="meta">{esc(r["url"])}</span></li>' for r in m["resources"]) + "</ul>")
    h.append("<h2>Questions for spaced practice</h2><p>From the question bank: answer from memory, then check. Revisit after 1, 3, 7 and 14 days.</p>")
    for m in ms:
        h.append(f'<h3>{m["id"]} {esc(m["title"])}</h3><ol>' + "".join(f'<li><b>{esc(q[0])}:</b> {esc(q[1])}<br><span class="ans">→ {esc(q[2])}</span></li>' for q in [x[1:] for x in QB if x[0] == m["id"]]) + "</ol>")
    h.append("</body></html>")
    return fn, "".join(h)


def mm_path(g):
    ms = [m for m in mods if m["go"] == g]
    pages = ['<div class="mmfig"><h1>Go ' + str(g) + ' mind map</h1>' + mm_svg(f"Go {g}", [(f'{m["id"]} {m["title"]}', m["systems"][0], [b[0] for b in MM[m["id"]]][:4]) for m in ms]) + "</div>"]
    for m in ms:
        pages.append(f'<div class="mmfig" style="page-break-before:always"><h1 style="font-size:18pt">{m["id"]} {esc(m["title"])}</h1>' + mm_svg("Module " + m["id"], [(b[0], b[1], [l[0] for l in b[3]]) for b in MM[m["id"]]]) + "</div>")
    return f'<html><head><meta charset="utf-8"><style>{CSS} @page{{size:A4 landscape;margin:12mm}}</style></head><body>' + "".join(pages) + "</body></html>"


async def render(jobs):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        for path, doc, land in jobs:
            await pg.set_content(doc, wait_until="load")
            await pg.pdf(path=path, format="A4", landscape=land, print_background=True, prefer_css_page_size=True,
                         display_header_footer=not land, header_template="<span></span>",
                         footer_template='<div style="font:8pt Carlito,Arial;color:#666;width:100%;text-align:center">Physical AI and SciML in three goes · <span class="pageNumber"></span></div>')
        await b.close()


def kits():
    for g, fn in ((2, "go2-kit.zip"), (3, "go3-research-kit.zip")):
        d = os.path.join(ROOT, "labs", f"go{g}")
        with zipfile.ZipFile(os.path.join(DL, fn), "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(os.listdir(d)):
                if f.endswith(".py"): z.write(os.path.join(d, f), f"go{g}-kit/{f}")
            req = "numpy\nscipy\nmatplotlib\n" + ("torch\n" if g == 2 else "")
            z.writestr(f"go{g}-kit/requirements.txt", req)
            z.writestr(f"go{g}-kit/README.txt", f"Physical AI and SciML in three goes: Go {g} lab kit\n\nInstall: pip install -r requirements.txt\nRun any lab: python <file>.py\nEach script prints the numbers quoted on its module page. All data are synthetic teaching data.\n" + ("Files ending in _torch.py need PyTorch (pip install torch); the others need only NumPy.\n" if g == 2 else ""))


if __name__ == "__main__":
    jobs = []
    for g in (1, 2, 3):
        fn, doc = handbook(g); jobs.append((os.path.join(DL, fn), doc, False))
        jobs.append((os.path.join(DL, "mindmaps", f"Go{g}-mind-map-path.pdf"), mm_path(g), True))
    asyncio.run(render(jobs)); kits()
    for f in sorted(glob.glob(os.path.join(DL, "**", "*.*"), recursive=True)): print(os.path.relpath(f, ROOT), os.path.getsize(f) // 1024, "KB")
