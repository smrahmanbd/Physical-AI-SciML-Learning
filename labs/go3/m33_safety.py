"""3.3 Surrogate safety: simulate many car-following encounters at two sites and count conflicts (minimum TTC below 3 s and 1.5 s)
and crashes. Conflicts are far more frequent than crashes and rise with them, which is why they are used as surrogates."""
import numpy as np
rng = np.random.default_rng(7)
def min_ttc(gap, dv, react, decel, vl=15.0, dt=0.02):
    vf, g, t, m = vl + dv, gap, 0.0, 99.0
    while t < 30:
        if vf > vl: m = min(m, g/(vf - vl))
        if t >= react and vf > vl: vf = max(vl, vf - decel*dt)
        g -= (vf - vl)*dt; t += dt
        if g <= 0: return 0.0
        if vf <= vl and t > react: break
    return m
N = 6000
for site, gmin in [("site A (longer gaps) ", 25), ("site B (shorter gaps)", 15)]:
    ttc = np.array([min_ttc(rng.uniform(gmin, gmin + 55), rng.uniform(2, 10), rng.lognormal(0.0, 0.3), rng.uniform(3, 7)) for _ in range(N)])
    c3, c15, crash = np.mean(ttc < 3), np.mean(ttc < 1.5), np.mean(ttc == 0)
    print(f"{site}: TTC < 3 s {c3:6.2%}, TTC < 1.5 s {c15:6.2%}, crashes {crash:6.3%}, conflicts (TTC < 3 s) per crash {c3/max(crash, 1e-9):5.1f}")
