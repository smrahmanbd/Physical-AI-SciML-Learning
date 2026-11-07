"""2.8 Split conformal prediction: distribution-free intervals with guaranteed average coverage."""
import numpy as np
rng = np.random.default_rng(111)
def draw(n):
    x = 3*rng.random(n); return x, 2*x + (0.3 + 0.3*x)*rng.standard_normal(n)   # noise grows with x
pred = lambda x: 2*x                                              # any trained model
xc, yc = draw(1000); scores = np.sort(np.abs(yc - pred(xc)))       # calibration set
xt, yt = draw(20000)
for alpha in [0.2, 0.1, 0.05]:
    q = scores[int(np.ceil((len(scores) + 1)*(1 - alpha))) - 1]
    inside = np.abs(yt - pred(xt)) <= q
    print(f"target {1-alpha:.0%}: interval ±{q:.2f}, coverage {inside.mean():.1%} (x<1: {inside[xt < 1].mean():.0%}, x>2: {inside[xt > 2].mean():.0%})")
