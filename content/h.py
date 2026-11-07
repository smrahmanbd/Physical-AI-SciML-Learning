"""Small helpers to write module content compactly."""
def N(id, label, sub, x, y, sys, detail, w=170, h=64):
    return dict(id=id, label=label, sub=sub, x=x, y=y, w=w, h=h, sys=sys, detail=detail)
def E(a, b, label="", sys=None):
    d = {"from": a, "to": b, "label": label}
    if sys: d["sys"] = sys
    return d
def T(focus, text, edges=None):
    d = dict(focus=focus, text=text)
    if edges: d["edges"] = edges
    return d
def Q(q, options, answer, explain):
    return dict(q=q, options=options, answer=answer, explain=explain)
def G(term, d): return dict(term=term, **{"def": d})
def RS(title, url, why): return dict(title=title, url=url, why=why)
def S(heading, html, mm): return dict(heading=heading, html=html, mm=mm)
def C(after, kind, title, html): return dict(after=after, kind=kind, title=title, html=html)
