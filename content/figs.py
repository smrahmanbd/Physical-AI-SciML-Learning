"""Animated teaching figures (SMIL, so pauseAnimations() works): one per module (assets/img/fig/m{id}.svg) plus the
seven method-atlas figures (model-{key}.svg, copied from the matching module figure). Colours use the site's CSS variables."""
import math, os, json, shutil
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "img", "fig")
os.makedirs(OUT, exist_ok=True)
C = dict(l="var(--economy,#8f3520)", p="var(--energy,#0b3954)", s="var(--land,#2f5a1c)", d="var(--water,#04505a)", r="var(--climate,#7a4412)", a="var(--policy,#3f3266)",
         ink="var(--ink,#14283a)", mu="var(--muted,#5d6f7d)", line="var(--line,#d5dde3)", paper="var(--paper,#fff)")
STY = """<style>.t{font-family:"Atkinson Hyperlegible Next",Arial,sans-serif;font-size:15px;fill:var(--ink,#14283a)}.h{font-family:Archivo,Arial,sans-serif;font-weight:700;font-size:18px;fill:var(--ink,#14283a)}
.s{font-family:"Atkinson Hyperlegible Next",Arial,sans-serif;font-size:12.5px;fill:var(--muted,#5d6f7d)}.ax{stroke:var(--line,#d5dde3);stroke-width:1.5}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}</style>"""
CAP = {}


def fig(mid, title, cap, body):
    s = f'<svg class="fig-anim" viewBox="0 0 900 360" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{title}"><title>{title}</title>{STY}<text class="h" x="24" y="32">{title}</text>{body}</svg>'
    open(os.path.join(OUT, f"m{mid}.svg"), "w").write(s); CAP[mid] = [title, cap]


def T(x, y, t, cls="t", anchor="start", fill=None):
    return f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}"{f' style="fill:{fill}"' if fill else ''}>{t}</text>'


def path(f, x0, x1, X, Y, n=120):
    pts = [(x0 + (x1 - x0) * i / n) for i in range(n + 1)]
    return "M" + " L".join(f"{X(t):.1f},{Y(f(t)):.1f}" for t in pts)


def axes(x, y, w, h, xl="", yl=""):
    return f'<line class="ax" x1="{x}" y1="{y + h}" x2="{x + w}" y2="{y + h}"/><line class="ax" x1="{x}" y1="{y}" x2="{x}" y2="{y + h}"/>' + T(x + w, y + h + 18, xl, "s", "end") + T(x - 6, y + 4, yl, "s", "end")


def draw(d, col, w=3, dur=3, dash="", begin="0s", extra=""):  # a line that draws itself, repeating
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100"{extra}><animate attributeName="stroke-dashoffset" values="100;0;0;100" keyTimes="0;0.45;0.9;1" dur="{dur}s" begin="{begin}" repeatCount="indefinite"/></path>'


def dots(pts, col, r=5):
    return "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}"/>' for x, y in pts)


def morph(ds, col, dur=6, w=3, dash=""):
    vals = ";".join(ds + [ds[0]])
    return f'<path d="{ds[0]}" fill="none" stroke="{col}" stroke-width="{w}" stroke-dasharray="{dash}"><animate attributeName="d" values="{vals}" dur="{dur}s" repeatCount="indefinite"/></path>'


def blink(x, y, t, col, begin, dur=6, cls="t"):
    return f'<text class="{cls}" x="{x}" y="{y}" style="fill:{col}" opacity="0">{t}<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.3;0.4" dur="{dur}s" begin="{begin}" repeatCount="indefinite"/></text>'


def box(x, y, w, h, label, col, sub=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{col}" opacity=".14" stroke="{col}" stroke-width="2"/>' + T(x + w / 2, y + h / 2 + (0 if sub else 5), label, "t", "middle") + (T(x + w / 2, y + h / 2 + 18, sub, "s", "middle") if sub else "")


def token(pathd, col, dur, r=8, begin="0s"):
    return f'<circle r="{r}" fill="{col}"><animateMotion path="{pathd}" dur="{dur}s" begin="{begin}" repeatCount="indefinite"/></circle>'


# ---------- Go 1
X = lambda t: 70 + t * 130; Y = lambda v: 200 - v * 110
truth = lambda t: math.exp(-0.3 * t) * math.cos(2 * t)
data = [(X(t), Y(truth(t) + 0.04 * math.sin(7 * t))) for t in [0, 0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.0]]
b = axes(70, 80, 790, 240, "time", "y") + f'<line x1="{X(2)}" y1="70" x2="{X(2)}" y2="320" stroke="{C["mu"]}" stroke-dasharray="4 4"/>' + T(X(2) + 6, 84, "data end here", "s")
b += f'<path d="{path(truth, 0, 6, X, Y)}" fill="none" stroke="{C["mu"]}" stroke-dasharray="6 5" stroke-width="2"/>' + dots(data, C["ink"])
b += draw(path(lambda t: truth(t) if t < 2 else truth(t) + 0.55 * (t - 2) ** 2, 0, 3.4, X, Y), C["r"], dur=6) + draw(path(lambda t: math.exp(-0.45 * t) * math.cos(1.85 * t), 0, 6, X, Y), C["p"], dur=6, begin="1s")
b += T(560, 70, "data fit: flies off", "t", fill=C["r"]) + T(640, 300, "physics: stays sensible", "t", fill=C["p"])
fig("1.1", "Physics and data, side by side", "Measurements stop at the dashed line. A pure data fit (brown) leaves the truth; a physics model (blue) keeps following it. SciML uses both.", b)

X = lambda t: 70 + t * 75; Y = lambda v: 310 - v * 230
b = axes(70, 70, 780, 240, "time (s)", "y") + f'<path d="{path(lambda t: math.exp(-0.5 * t), 0, 10, X, Y)}" fill="none" stroke="{C["mu"]}" stroke-dasharray="6 5" stroke-width="2"/>'
st, y, pts = [], 1.0, []
for i in range(11): pts.append((X(i), Y(y))); y += 1 * (-0.5 * y)
stair = "M" + " L".join(f"{x:.1f},{yy:.1f}" for x, yy in pts)
b += draw(stair, C["l"], dur=7) + "".join(f'<circle cx="{x:.1f}" cy="{yy:.1f}" r="5" fill="{C["l"]}" opacity="0"><animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{i/24:.3f};{i/24+0.02:.3f};0.9;1" dur="7s" repeatCount="indefinite"/></circle>' for i, (x, yy) in enumerate(pts))
b += T(500, 110, "Euler: y ← y + Δt × slope", "t") + T(500, 134, "big steps undershoot the exact curve", "s") + T(140, 100, "exact e^(−0.5t)", "s")
fig("1.2", "Euler's method, one step at a time", "Each dot follows the slope for one time step. With Δt = 1 s the steps fall below the exact decay (dashed): smaller steps follow it more closely.", b)

b = ""
hid = [(450, 80 + 50 * i) for i in range(5)]
b += f'<circle cx="150" cy="180" r="26" fill="{C["d"]}" opacity=".85"/>' + T(150, 185, "x", "t", "middle", C["paper"]) + f'<circle cx="760" cy="180" r="26" fill="{C["s"]}" opacity=".85"/>' + T(760, 185, "ŷ", "t", "middle", C["paper"])
for i, (x, y) in enumerate(hid):
    b += f'<line x1="176" y1="180" x2="{x - 22}" y2="{y}" stroke="{C["line"]}" stroke-width="2"/><line x1="{x + 22}" y1="{y}" x2="734" y2="180" stroke="{C["line"]}" stroke-width="2"/>'
    b += f'<circle cx="{x}" cy="{y}" r="20" fill="{C["l"]}"><animate attributeName="opacity" values=".25;1;.25" dur="2.4s" begin="{i * 0.3:.1f}s" repeatCount="indefinite"/></circle>'
    b += f'<path d="M{x - 12},{y + 7} C{x - 4},{y + 7} {x + 2},{y - 7} {x + 12},{y - 7}" stroke="{C["paper"]}" stroke-width="2.5" fill="none"/>'
    b += token(f"M176,180 L{x - 22},{y} M{x + 22},{y} L734,180", C["ink"], 2.4, 4, f"{i * 0.3:.1f}s")
b += T(450, 345, "each neuron: tanh(w·x + b), a soft step", "s", "middle") + T(150, 230, "input", "s", "middle") + T(760, 230, "weighted sum", "s", "middle")
fig("1.3", "Signals flowing through a small network", "An input passes to hidden neurons, each a soft step tanh(w·x + b); the output adds them with weights. Training adjusts the weights.", b)

X = lambda w: 80 + (w + 4) * 62; Y = lambda L: 300 - (L + 0.5) * 55
Lf = lambda w: 0.1 * (w - 3) ** 2 + 0.4 * math.sin(2.5 * w)
curve = path(Lf, -4, 8, X, Y, 240)
b = axes(80, 60, 750, 250, "weight w", "loss") + f'<path d="{curve}" fill="none" stroke="{C["mu"]}" stroke-width="3"/>'
w, v, ps = -2.0, 0.0, []
for i in range(70): v = 0.9 * v - 0.1 * (0.2 * (w - 3) + math.cos(2.5 * w)); w += v; ps.append((X(w), Y(Lf(w)) - 9))
b += token("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in ps), C["r"], 7, 9)
b += T(X(-0.3), Y(Lf(-0.3)) + 30, "local minimum", "s", "middle") + T(X(4.3), Y(Lf(4.3)) + 30, "deeper valley", "s", "middle") + T(560, 90, "a ball with momentum rolls past the small dip", "t")
fig("1.4", "Gradient descent with momentum", "The ball steps downhill along the loss; momentum lets it roll past the shallow valley into the deeper one.", b)

X = lambda t: 70 + t * 150; Y = lambda v: 300 - v * 210
b = axes(70, 70, 780, 240, "time (s)", "y") + f'<line x1="{X(1)}" y1="70" x2="{X(1)}" y2="310" stroke="{C["mu"]}" stroke-dasharray="4 4"/>'
b += dots([(X(t), Y(math.exp(-0.8 * t))) for t in [0, 0.2, 0.4, 0.6, 0.8, 1.0]], C["ink"])
good = path(lambda t: math.exp(-0.8 * t), 0, 5, X, Y); bad = path(lambda t: math.exp(-0.8 * t) if t < 1 else math.exp(-0.8) + 0.25 * math.sin(2.2 * (t - 1)) + 0.05 * (t - 1), 0, 5, X, Y)
b += morph([bad, bad, good, good], C["p"], 6)
b += "".join(f'<line x1="{X(t):.1f}" y1="305" x2="{X(t):.1f}" y2="315" stroke="{C["r"]}" stroke-width="3"><animate attributeName="stroke-opacity" values=".2;1;.2" dur="1.5s" begin="{t / 5:.2f}s" repeatCount="indefinite"/></line>' for t in [i * 0.25 for i in range(21)])
b += blink(420, 120, "no physics: the curve wanders", C["r"], "0s") + blink(420, 120, "λ > 0: the law fills the gap", C["p"], "3s") + T(450, 345, "ticks: collocation points where dy/dt + 0.8 y = 0 is checked", "s", "middle")
fig("1.5", "Physics fills the gap after the data", "Six measurements in the first second. Without physics the curve wanders; checking the law at collocation points (ticks) locks it onto the true decay.", b)

X = lambda x: 80 + x * 740; Y = lambda v: 190 - v * 95
pts = [(i / 14, math.sin(2 * math.pi * i / 14) + 0.25 * math.sin(37 * i)) for i in range(15)]
under = path(lambda x: 0.9 - 1.8 * x, 0, 1, X, Y); right = path(lambda x: math.sin(2 * math.pi * x), 0, 1, X, Y)
wig = "M" + " L".join(f"{X(x):.1f},{Y(yv):.1f}" for x, yv in pts)
b = axes(80, 70, 740, 250, "x", "y") + dots([(X(x), Y(yv)) for x, yv in pts], C["ink"]) + morph([under, under, right, right, wig, wig], C["l"], 9)
b += blink(330, 70, "too simple: underfitting", C["r"], "0s", 9) + blink(330, 70, "about right", C["s"], "3s", 9) + blink(330, 70, "too flexible: overfitting", C["r"], "6s", 9)
fig("1.6", "From underfitting to overfitting", "The same noisy points fitted by a line (misses the wave), a smooth curve (about right) and a wiggly curve through every point (fits the noise).", b)

b = f'<g transform="translate(160,190)"><g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="24s" repeatCount="indefinite"/>' + "".join(f'<rect x="-10" y="-82" width="20" height="24" fill="{C["mu"]}" transform="rotate({k * 30})"/>' for k in range(12)) + f'<circle r="64" fill="{C["mu"]}"/></g>' + T(0, 5, "slow model", "t", "middle", C["paper"]) + "</g>"
b += T(160, 300, "hours per run", "s", "middle")
X = lambda x: 360 + x * 160; Y = lambda v: 250 - v * 45
f = lambda x: math.sin(3 * x) + 0.3 * x * x
runs = [0, 0.6, 1.2, 1.8, 2.4, 3.0]
for i, r in enumerate(runs): b += f'<circle r="7" fill="{C["d"]}"><animate attributeName="cx" values="230;{X(r):.0f}" dur="1s" begin="{i * 0.8}s" fill="freeze"/><animate attributeName="cy" values="190;{Y(f(r)):.0f}" dur="1s" begin="{i * 0.8}s" fill="freeze"/></circle>'
b += f'<path d="{path(f, 0, 3, X, Y)}" fill="none" stroke="{C["s"]}" stroke-width="3" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100"><animate attributeName="stroke-dashoffset" values="100;0" dur="2s" begin="5s" fill="freeze"/></path>'
b += T(620, 80, "a few runs → a fast surrogate", "t", "middle") + T(620, 330, "milliseconds per query", "s", "middle")
fig("1.7", "A slow model and its fast surrogate", "A slow simulator produces a few runs; a surrogate (green) stretches smoothly through them and then answers new questions almost instantly.", b)

b = ""
cx, cy, R = 230, 195, 110
lab = [("Sense", -90, C["d"]), ("Estimate", 0, C["p"]), ("Decide", 90, C["l"]), ("Act", 180, C["a"])]
b += f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{C["line"]}" stroke-width="10"/>'
for t, ang, col in lab:
    x, y = cx + R * math.cos(math.radians(ang)), cy + R * math.sin(math.radians(ang)); b += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="34" fill="{col}"/>' + T(x, y + 5, t, "s", "middle", C["paper"])
b += token(f"M{cx},{cy - R} A{R},{R} 0 1 1 {cx - 0.1},{cy - R}", C["ink"], 4, 7)
b += f'<line x1="470" y1="250" x2="860" y2="250" stroke="{C["mu"]}" stroke-width="3"/>' + T(665, 285, "true car · GPS readings · Kalman estimate", "s", "middle")
b += f'<rect y="226" width="34" height="18" rx="4" fill="{C["ink"]}"><animate attributeName="x" values="470;820" dur="6s" repeatCount="indefinite"/></rect>'
for k in range(8):
    b += f'<circle r="5" fill="{C["r"]}" opacity="0"><animate attributeName="cx" values="{480 + 45 * k}" dur="6s" repeatCount="indefinite"/><animate attributeName="cy" values="{200 + (k * 37 % 60) - 30}" dur="6s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;{k / 9:.2f};{k / 9 + 0.1:.2f};1" dur="6s" repeatCount="indefinite"/></circle>'
b += f'<circle cy="215" r="8" fill="{C["p"]}"><animate attributeName="cx" values="480;835" dur="6s" repeatCount="indefinite"/></circle>'
fig("1.8", "The Physical AI loop", "Left: the loop runs again and again: sense, estimate, decide, act. Right: noisy GPS readings (brown) around a car; the Kalman estimate (blue) follows it smoothly.", b)

# ---------- Go 2
b = ""; xs = [60, 180, 300, 420, 540, 660, 780]
names = ["Question", "Data", "Split", "Baseline", "Build", "Validate", "Share"]
for i, (x, n) in enumerate(zip(xs, names)): b += box(x, 120, 100, 56, f"{i + 1}. {n}", [C["a"], C["d"], C["r"], C["s"], C["l"], C["r"], C["s"]][i])
b += token("M60,100 L880,100", C["ink"], 7, 7)
b += f'<rect x="80" y="240" width="500" height="26" fill="{C["s"]}" opacity=".7"/><rect x="580" y="240" width="130" height="26" fill="{C["r"]}" opacity=".7"/><rect x="710" y="240" width="130" height="26" fill="{C["a"]}" opacity=".7"/>'
b += T(330, 258, "train (the past)", "s", "middle", C["paper"]) + T(645, 258, "validate", "s", "middle", C["paper"]) + T(775, 258, "test (last)", "s", "middle", C["paper"]) + T(460, 300, "time →  split time series by time, never at random", "s", "middle")
fig("2.1", "A SciML project, step by step", "Seven steps from question to shared code, and a time-ordered split: train on the past, validate later, test last.", b)

b = box(60, 140, 130, 70, "t", C["d"]) + box(260, 140, 160, 70, "network", C["l"], "tanh layers") + box(490, 90, 170, 60, "data loss", C["d"]) + box(490, 200, 170, 60, "physics loss", C["p"])
b += f'<line x1="190" y1="175" x2="260" y2="175" stroke="{C["mu"]}" stroke-width="3"/><line x1="420" y1="160" x2="490" y2="120" stroke="{C["mu"]}" stroke-width="3"/><line x1="420" y1="190" x2="490" y2="230" stroke="{C["mu"]}" stroke-width="3"/>'
for i, (y, col) in enumerate([(120, C["d"]), (230, C["p"])]):
    b += f'<rect x="690" y="{y - 12}" height="24" fill="{col}"><animate attributeName="width" values="170;20;20;170" keyTimes="0;0.6;0.95;1" dur="6s" begin="{i * 0.4}s" repeatCount="indefinite"/></rect>'
b += f'<g transform="translate(560,320)"><circle r="30" fill="none" stroke="{C["mu"]}" stroke-width="3"/><line x1="0" y1="0" x2="0" y2="-26" stroke="{C["r"]}" stroke-width="4"><animateTransform attributeName="transform" type="rotate" values="-60;60;60;-60" keyTimes="0;0.6;0.95;1" dur="6s" repeatCount="indefinite"/></line></g>'
b += T(610, 325, "k learned: 0.3 → 0.8", "t") + T(250, 300, "autodiff gives dŷ/dt for the residual dŷ/dt + kŷ", "s")
fig("2.2", "Training a PINN: both losses fall", "The network feeds a data loss and a physics loss; both shrink during training while the unknown decay rate k is learned.", b)

X = lambda x: 80 + x * 740; Y = lambda u: 300 - u * 160
prof = lambda t: (lambda x: math.exp(-(math.pi ** 2) * t) * math.sin(math.pi * x) + 0.5 * math.exp(-25 * math.pi ** 2 * t) * math.sin(5 * math.pi * x))
b = axes(80, 60, 740, 240, "position x", "u") + morph([path(prof(t), 0, 1, X, Y) for t in [0, 0.003, 0.01, 0.03, 0.06, 0.06]], C["r"], 6)
b += "".join(f'<circle cx="{X(i / 20):.0f}" cy="{Y(0):.0f}" r="3" fill="{C["mu"]}"/>' for i in range(21)) + T(600, 90, "heat spreads and fades", "t") + T(600, 114, "explicit steps need r = αΔt/Δx² ≤ 0.5", "s")
fig("2.3", "Heat diffusing on a grid", "A temperature profile on grid points smooths and fades as heat flows to the cold ends; the fine ripple disappears first.", b)

terms = ["1", "x", "v", "x²", "x·v", "v²", "x³"]; keep = {"x", "v"}
b = ""
for i, t in enumerate(terms):
    x = 90 + i * 110; col = C["p"] if t in keep else C["mu"]
    anim = "" if t in keep else '<animate attributeName="opacity" values="1;1;0.08;0.08;1" keyTimes="0;0.3;0.5;0.9;1" dur="6s" repeatCount="indefinite"/>'
    b += f'<g>{anim}<rect x="{x}" y="120" width="80" height="60" rx="10" fill="{col}" opacity=".9"/>' + T(x + 40, 157, t, "t", "middle", C["paper"]) + "</g>"
b += blink(450, 250, "dv/dt = −4.00 x − 0.30 v", C["p"], "3s", 6, "h") + T(450, 300, "fit all seven, cut the small ones, refit", "s", "middle") + T(450, 90, "candidate terms", "s", "middle")
fig("2.4", "SINDy keeps only the terms that matter", "Seven candidate terms are fitted; the small ones fade away, leaving the law dv/dt = −4x − 0.3v.", b)

X = lambda x: 60 + x * 200; Y = lambda v, y0: y0 - v * 40
fin = lambda s: path(lambda x: math.sin(2 * math.pi * x + s) + 0.5 * math.sin(6 * math.pi * x), 0, 1, X, lambda v: Y(v, 140))
b = morph([fin(0), fin(1), fin(2), fin(0)], C["d"], 6) + box(320, 90, 140, 60, "branch net", C["l"], "reads f") + box(320, 220, 140, 60, "trunk net", C["l"], "reads x")
b += f'<circle cx="540" cy="185" r="22" fill="{C["ink"]}"/>' + T(540, 191, "·", "h", "middle", C["paper"])
b += f'<line x1="460" y1="120" x2="520" y2="175" stroke="{C["mu"]}" stroke-width="3"/><line x1="460" y1="250" x2="520" y2="195" stroke="{C["mu"]}" stroke-width="3"/><line x1="270" y1="120" x2="320" y2="120" stroke="{C["mu"]}" stroke-width="3"/>'
Xo = lambda x: 620 + x * 230
fout = lambda s: path(lambda x: (math.sin(2 * math.pi * x + s) / 4 + 0.5 * math.sin(6 * math.pi * x) / 36) * 3, 0, 1, Xo, lambda v: Y(v, 190))
b += morph([fout(0), fout(1), fout(2), fout(0)], C["s"], 6) + T(160, 70, "input function f(x)", "s", "middle") + T(735, 110, "solution u(x)", "s", "middle")
fig("2.5", "A neural operator maps functions to functions", "Each new input function (left) is read by the branch net; the trunk net reads the location; their product gives the whole solution (right) at once.", b)

X = lambda x: 70 + x * 190; Y = lambda v: 190 - v * 60
f = lambda x: math.sin(3 * x) + 0.5 * x - 1
obs = [0.3, 1.0, 1.4, 2.6, 3.7]
def sd(x): return 0.08 + 0.9 * min(1, min(abs(x - o) for o in obs) / 0.9)
hi = [(X(i / 30 * 4), Y(f(i / 30 * 4) + 1.96 * sd(i / 30 * 4))) for i in range(31)]; lo = [(X(i / 30 * 4), Y(f(i / 30 * 4) - 1.96 * sd(i / 30 * 4))) for i in range(31)]
band = "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in hi) + " L" + " L".join(f"{x:.0f},{y:.0f}" for x, y in reversed(lo)) + " Z"
b = axes(70, 50, 760, 280, "x", "y") + f'<path d="{band}" fill="{C["p"]}" opacity=".15"><animate attributeName="opacity" values=".05;.22;.05" dur="4s" repeatCount="indefinite"/></path>'
b += f'<path d="{path(f, 0, 4, X, Y)}" fill="none" stroke="{C["p"]}" stroke-width="3"/>' + "".join(f'<circle cx="{X(o):.0f}" cy="{Y(f(o)):.0f}" r="6" fill="{C["ink"]}"><animate attributeName="r" values="0;6" dur="0.6s" begin="{i * 0.5}s" fill="freeze"/></circle>' for i, o in enumerate(obs))
b += T(600, 80, "the band widens far from the data", "t")
fig("2.6", "A Gaussian process and its uncertainty", "Observations pin the mean curve; the shaded 95% band is narrow near data and widens in the gaps.", b)

X = lambda r: 80 + r * 5.3; Y = lambda v: 320 - v * 2.4
b = axes(80, 60, 750, 260, "density (veh/km)", "speed") + f'<line x1="{X(60)}" y1="60" x2="{X(60)}" y2="320" stroke="{C["mu"]}" stroke-dasharray="4 4"/>' + T(X(60) + 6, 74, "no data beyond", "s")
b += f'<path d="{path(lambda r: 100 * (1 - r / 140), 0, 140, X, Y)}" fill="none" stroke="{C["mu"]}" stroke-width="2" stroke-dasharray="3 4"/>'
b += draw(path(lambda r: 100 * (1 - (r / 140) ** 1.6), 0, 140, X, Y), C["s"], 4, 6) + draw(path(lambda r: 100 * (1 - (r / 140) ** 1.6) + (0 if r < 60 else 0.03 * (r - 60) ** 2), 0, 110, X, Y), C["r"], 3, 6, begin="0.5s")
b += dots([(X(r), Y(100 * (1 - (r / 140) ** 1.6) + 2 * math.sin(r))) for r in range(8, 60, 5)], C["ink"], 4) + T(560, 100, "ML only: flies off", "t", fill=C["r"]) + T(560, 280, "hybrid: physics + correction", "t", fill=C["s"]) + T(130, 330, "dashed: Greenshields straight line", "s")
fig("2.7", "Hybrid modelling beyond the data", "A straight physics line (dashed), plus a small learned correction (green), follows the true curve far beyond the data; pure ML (brown) does not.", b)

X = lambda x: 80 + x * 245; Y = lambda v: 300 - v * 38
b = axes(80, 60, 740, 240, "input x", "y") + f'<path d="M{X(0)},{Y(1.3)} L{X(3)},{Y(7.3)} L{X(3)},{Y(4.7)} L{X(0)},{Y(-1.3)} Z" fill="{C["a"]}" opacity=".15"/>' + f'<line x1="{X(0)}" y1="{Y(0)}" x2="{X(3)}" y2="{Y(6)}" stroke="{C["a"]}" stroke-width="3"/>'
import random
random.seed(3)
for k in range(40):
    x = 3 * random.random(); yv = 2 * x + (0.3 + 0.3 * x) * random.gauss(0, 1); inside = abs(yv - 2 * x) <= 1.3
    b += f'<circle cx="{X(x):.0f}" cy="{Y(yv):.0f}" r="5" fill="{C["s"] if inside else C["r"]}" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.3s" begin="{k * 0.12:.2f}s" fill="freeze"/></circle>'
b += T(560, 90, "±q band: covers 90% on average", "t") + T(560, 114, "brown points outside: mostly at large x", "s")
fig("2.8", "Conformal intervals: right on average", "A constant ± band calibrated on held-out errors covers about 90% of new points overall, but misses more where the noise is larger.", b)

# ---------- Go 3
b = f'<defs><linearGradient id="g31" x1="0" x2="1"><stop offset="0" stop-color="{C["s"]}" stop-opacity=".3"/><stop offset="0.3" stop-color="{C["r"]}" stop-opacity=".9"><animate attributeName="offset" values="0.45;0.15;0.45" dur="7s" repeatCount="indefinite"/></stop><stop offset="0.5" stop-color="{C["s"]}" stop-opacity=".3"><animate attributeName="offset" values="0.6;0.3;0.6" dur="7s" repeatCount="indefinite"/></stop><stop offset="1" stop-color="{C["s"]}" stop-opacity=".3"/></linearGradient></defs>'
b += f'<rect x="60" y="150" width="780" height="60" rx="8" fill="url(#g31)"/>' + "".join(f'<g><rect x="{x - 6}" y="110" width="12" height="40" fill="{C["ink"]}"/><circle cx="{x}" cy="104" r="9" fill="{C["d"]}"><animate attributeName="opacity" values=".3;1;.3" dur="1.6s" repeatCount="indefinite"/></circle></g>' for x in [200, 600])
b += T(450, 250, "a jam (brown) moves upstream between two detectors", "t", "middle") + T(450, 274, "the LWR model carries it where the sensors cannot see", "s", "middle") + T(840, 140, "traffic →", "s", "end")
fig("3.1", "A jam travelling between detectors", "Density along a road: the dark band is a jam moving against the traffic. Two detectors see it only when it passes them; the physics fills the gap.", b)

b = f'<line x1="40" y1="220" x2="860" y2="220" stroke="{C["mu"]}" stroke-width="3"/>'
for i in range(8):
    x0 = 780 - i * 95; dip = 25 + 6 * i
    b += f'<rect y="196" width="44" height="20" rx="5" fill="{C["r"] if i == 0 else C["p"]}"><animate attributeName="x" values="{x0};{x0 + 10};{x0 + 10 + dip * 0.2};{x0 + 10}" keyTimes="0;{0.15 + i * 0.07:.2f};{0.3 + i * 0.07:.2f};1" dur="7s" repeatCount="indefinite"/></rect>'
    b += f'<circle cx="{x0 + 40}" cy="200" r="4" fill="{C["r"]}" opacity="0"><animate attributeName="opacity" values="0;1;0" keyTimes="0;{0.2 + i * 0.07:.2f};{0.35 + i * 0.07:.2f}" dur="7s" repeatCount="indefinite"/></circle>'
b += T(450, 120, "the leader brakes; the wave travels back along the line", "t", "middle") + T(450, 290, "human drivers amplify it · cooperative ACC damps it", "s", "middle") + T(820, 250, "leader", "s", "middle")
fig("3.2", "A braking wave along a platoon", "The red leader brakes; brake lights flash one car after another down the line. Whether the wave grows or fades depends on reaction and control.", b)

b = f'<line x1="60" y1="210" x2="840" y2="210" stroke="{C["mu"]}" stroke-width="3"/>'
b += f'<rect y="186" width="60" height="22" rx="5" fill="{C["p"]}"><animate attributeName="x" values="600;720" dur="6s" repeatCount="indefinite"/></rect>'
b += f'<rect y="186" width="60" height="22" rx="5" fill="{C["r"]}"><animate attributeName="x" values="150;640;655" keyTimes="0;0.8;1" dur="6s" repeatCount="indefinite"/></rect>'
for i, t in enumerate(["TTC 6.0 s", "TTC 3.5 s", "TTC 1.8 s", "TTC 1.2 s: conflict!"]):
    b += blink(450, 120, t, C["r"] if i == 3 else C["ink"], f"{i * 1.4}s", 6, "h")
b += T(450, 270, "time to collision = gap ÷ closing speed", "t", "middle") + T(450, 296, "near misses are counted to estimate risk before crashes happen", "s", "middle")
fig("3.3", "Time to collision counts down", "A faster car closes on a slower one; the time to collision falls until it brakes. Values below about 1.5 s are serious conflicts.", b)

b = f'<path d="M60,300 L840,170" stroke="{C["mu"]}" stroke-width="4"/>' + f'<g><animateMotion path="M80,282 L780,166" dur="7s" repeatCount="indefinite" rotate="auto"/><rect x="-30" y="-26" width="60" height="22" rx="5" fill="{C["p"]}"/></g>'
for k in range(6): b += f'<circle r="6" fill="{C["mu"]}" opacity="0"><animateMotion path="M80,290 L780,174" dur="7s" begin="{k * 1.1:.1f}s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;.7;0" dur="1.2s" begin="{k * 1.1:.1f}s" repeatCount="indefinite"/></circle>'
b += T(120, 110, "P = m v (a + g sin θ) + rolling + ½ ρ C_d A v³", "t") + T(120, 136, "inertia · hill · tyres · wind", "s") + T(620, 320, "grey puffs: CO₂ from the energy used", "s")
fig("3.4", "Climbing costs energy", "A car climbing a grade must lift its weight as well as overcome inertia, tyres and air; the road-load equation turns this into energy and CO₂.", b)

b = f'<g transform="translate(170,190)"><circle r="85" fill="{C["d"]}" opacity=".2" stroke="{C["d"]}" stroke-width="3"/>' + "".join(f'<ellipse rx="{abs(85 * math.cos(math.radians(a))) + 1:.0f}" ry="85" fill="none" stroke="{C["d"]}" stroke-width="1.5"><animate attributeName="rx" values="{abs(85 * math.cos(math.radians(a))) + 1:.0f};{abs(85 * math.cos(math.radians(a + 90))) + 1:.0f};{abs(85 * math.cos(math.radians(a))) + 1:.0f}" dur="8s" repeatCount="indefinite"/></ellipse>' for a in (0, 45, 90)) + T(0, 125, "GCAM: hours per run", "s", "middle") + "</g>"
X = lambda p: 370 + p * 1.2; Y = lambda v: 300 - (v - 0.4) * 160
iam = lambda p: 1.6 * (0.38 + 0.62 * math.exp(-p / 110)) + 0.12 * math.sin(p / 35) * math.exp(-p / 180)
for i, p in enumerate([0, 100, 200, 300, 400]): b += f'<circle r="7" fill="{C["ink"]}"><animate attributeName="cx" values="255;{X(p):.0f}" dur="1s" begin="{i * 0.9}s" fill="freeze"/><animate attributeName="cy" values="190;{Y(iam(p)):.0f}" dur="1s" begin="{i * 0.9}s" fill="freeze"/></circle>'
b += f'<path d="{path(iam, 0, 400, X, Y)}" fill="none" stroke="{C["s"]}" stroke-width="3" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100"><animate attributeName="stroke-dashoffset" values="100;0" dur="2s" begin="5s" fill="freeze"/></path>'
b += axes(370, 80, 480, 220, "carbon price", "transport CO₂") + T(610, 70, "five runs → an emulator", "t", "middle")
fig("3.5", "Emulating GCAM", "The integrated assessment model is run at a few carbon prices; an emulator (green) through those runs answers thousands of policy questions quickly.", b)

b = f'<rect x="60" y="80" width="330" height="220" rx="10" fill="none" stroke="{C["line"]}" stroke-width="2"/>'
random.seed(5)
for k in range(60):
    x0, y0 = 80 + 290 * random.random(), 100 + 180 * random.random(); x1, y1 = 180 + 90 * random.random(), 150 + 80 * random.random()
    b += f'<circle r="5" fill="{C["l"]}"><animate attributeName="cx" values="{x0:.0f};{x1:.0f};{x0:.0f}" dur="8s" repeatCount="indefinite"/><animate attributeName="cy" values="{y0:.0f};{y1:.0f};{y0:.0f}" dur="8s" repeatCount="indefinite"/></circle>'
X = lambda r: 470 + r * 70; Y = lambda v: 300 - v * 150
w = lambda r: 0 if r >= 5.4 else 1.34 * (1 - math.exp(-1.913 * (1 / r - 1 / 5.4)))
b += axes(470, 80, 380, 220, "density", "speed") + f'<path d="{path(w, 0.3, 5.4, X, Y)}" fill="none" stroke="{C["p"]}" stroke-width="3"/>' + f'<circle r="8" fill="{C["l"]}"><animateMotion path="{path(w, 0.4, 5.3, X, Y)}" dur="8s" keyPoints="0;1;0" keyTimes="0;0.5;1" calcMode="linear" repeatCount="indefinite"/></circle>'
b += T(225, 330, "people pack together", "s", "middle") + T(660, 70, "physics-shaped law: speed → 0 at jam density", "s", "middle")
fig("3.6", "Crowding slows everyone down", "As the crowd packs together (left), walking speed falls along Weidmann's physics-shaped curve (right), reaching zero at jam density.", b)

b = box(60, 90, 300, 200, "", C["mu"]) + box(540, 90, 300, 200, "", C["p"]) + T(210, 80, "real junction", "s", "middle") + T(690, 80, "digital twin", "s", "middle")
for x0, col in [(110, C["mu"]), (590, C["p"])]:
    b += f'<rect x="{x0}" y="180" height="30" fill="{col}" opacity=".8"><animate attributeName="width" values="40;180;60;40" dur="6s" repeatCount="indefinite"/></rect>'
b += token("M360,140 L540,140", C["d"], 1.5, 7) + T(450, 128, "live data", "s", "middle") + token("M540,250 L360,250", C["a"], 1.5, 7, "0.7s") + T(450, 274, "tested actions", "s", "middle")
b += T(450, 330, "the twin's queue follows the real queue, corrected every cycle", "s", "middle")
fig("3.7", "A digital twin stays in step", "Live detector data flow from the real junction to its twin, keeping the twin's queue in step; actions tested in the twin flow back.", b)

b = ""
for i, (t, col) in enumerate([("FOUNDATION", C["l"]), ("WORLD", C["d"]), ("VERIFY", C["r"]), ("RARE", C["a"]), ("FAIR", C["s"])]):
    x = 120 + i * 165
    b += f'<line x1="{x}" y1="300" x2="{x}" y2="140" stroke="{C["mu"]}" stroke-width="5"/><g><animateTransform attributeName="transform" type="rotate" values="-4 {x} 150;4 {x} 150;-4 {x} 150" dur="{3 + i * 0.4:.1f}s" repeatCount="indefinite"/><rect x="{x - 66}" y="110" width="132" height="36" rx="6" fill="{col}"/>' + T(x, 133, t, "s", "middle", C["paper"]) + "</g>"
b += T(450, 70, "five open research fronts", "t", "middle") + T(450, 335, "report every result with a baseline [and an interval]", "s", "middle")
fig("3.8", "Signposts to the research frontier", "Five open fronts: foundation models, world models, verification of learned control, rare events, and fairness and transfer.", b)

json.dump(CAP, open(os.path.join(OUT, "captions.json"), "w"), ensure_ascii=False, indent=1)
for k, m in [("pinn", "1.5"), ("sindy", "2.4"), ("operator", "2.5"), ("gp", "2.6"), ("hybrid", "2.7"), ("surrogate", "1.7"), ("kalman", "1.8")]:
    shutil.copy(os.path.join(OUT, f"m{m}.svg"), os.path.join(OUT, f"model-{k}.svg"))
print(len(CAP), "figures")
