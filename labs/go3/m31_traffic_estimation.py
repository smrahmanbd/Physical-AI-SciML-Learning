"""3.1 Physics-informed traffic state estimation: LWR model (Godunov / cell transmission) + loop detectors.
Compare straight-line interpolation between detectors with a physics model nudged towards detector readings."""
import numpy as np
nx, L, dt, steps = 100, 10.0, 2.0, 300                     # cells, km, s, steps (10 minutes)
dx, vf, rj = L/nx, 100/3600, 150.0                          # km, km/s, veh/km
Q = lambda r: vf*r*(1 - r/rj); rc = rj/2
def flux(a, b):                                             # Godunov flux = min(upstream demand, downstream supply)
    return np.minimum(np.where(a <= rc, Q(a), Q(rc)), np.where(b >= rc, Q(b), Q(rc)))
def step(r):
    F = flux(r, np.roll(r, -1)); return np.clip(r - dt/dx*(F - np.roll(F, 1)), 0, rj)
def run(ndet, gain, seed=121):
    rng = np.random.default_rng(seed)
    truth = np.where((np.arange(nx) >= 30) & (np.arange(nx) < 42), 120.0, 30.0); est = np.full(nx, 45.0)
    det = ((np.arange(ndet) + 0.5)*nx/ndet).astype(int)
    for _ in range(steps):
        truth, est = step(truth), step(est)
        z = truth[det] + 3*rng.standard_normal(ndet)
        for d, w in [(0, 1.0), (-1, 0.5), (1, 0.5)]:
            j = (det + d) % nx; est[j] += gain*w*(z - est[j])
    xs = np.arange(nx); xd = np.r_[det - nx, det, det + nx]; zd = np.tile(truth[det], 3)
    interp = np.interp(xs, xd, zd)
    rmse = lambda a: np.sqrt(np.mean((a - truth)**2))
    return rmse(interp), rmse(est)
for ndet in [2, 4, 10]:
    i, e = run(ndet, 0.5)
    print(f"{ndet:2d} detectors: interpolation error {i:5.1f} veh/km, physics-informed estimate {e:4.1f} veh/km")
