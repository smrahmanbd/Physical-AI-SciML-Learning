"""2.7 Hybrid modelling: physics (Greenshields) + a learned correction, compared with pure ML, beyond the data."""
import numpy as np
rng = np.random.default_rng(101); vf, rj = 100, 140
truth = lambda r: vf*(1 - (r/rj)**1.6)                       # 'real' speed-density relation (unknown to the modeller)
phys = lambda r: vf*(1 - r/rj)                               # textbook Greenshields model
rd = 5 + 55*rng.random(20); vd = truth(rd) + 2*rng.standard_normal(20)    # data only up to 60 veh/km
P = lambda r, d: np.vander(r/100, d + 1, increasing=True)
cML = np.linalg.lstsq(P(rd, 4), vd, rcond=None)[0]
cH = np.linalg.solve(P(rd, 2).T @ P(rd, 2) + 1e-3*np.eye(3), P(rd, 2).T @ (vd - phys(rd)))
r = np.linspace(61, 140, 80)
for name, pred in [("physics only", phys(r)), ("ML only (degree-4 polynomial)", P(r, 4) @ cML), ("hybrid: physics + learned correction", phys(r) + P(r, 2) @ cH)]:
    print(f"{name:38s} error beyond the data: {np.sqrt(np.mean((pred - truth(r))**2)):6.1f} km/h")
