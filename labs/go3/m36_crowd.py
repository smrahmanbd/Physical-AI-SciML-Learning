"""3.6 Crowd dynamics with SciML: fit the Weidmann fundamental diagram (physics-shaped) vs an unconstrained cubic,
using only light-crowd data, and compare at dangerous densities."""
import numpy as np
rng = np.random.default_rng(141)
weid = lambda r, v0=1.34, g=1.913, rm=5.4: np.where(r >= rm, 0, v0*(1 - np.exp(-g*(1/r - 1/rm))))
r = rng.uniform(0.3, 2.5, 40); v = np.maximum(0, weid(r) + 0.08*rng.standard_normal(40))
cubic = np.polyfit(r, v, 3)
grid = [(v0, g, rm) for v0 in np.arange(1.0, 1.71, 0.02) for g in np.arange(1.0, 3.01, 0.05) for rm in np.arange(4.0, 7.01, 0.1)]
best = min(grid, key=lambda p: np.sum((weid(r, *p) - v)**2))
rd = np.linspace(2.6, 5.4, 60)
e = lambda f: np.sqrt(np.mean((f - weid(rd))**2))
print(f"fitted v0 = {best[0]:.2f} m/s, gamma = {best[1]:.2f}, rho_max = {best[2]:.1f} per m2")
print(f"error at 2.6-5.4 per m2: cubic {e(np.polyval(cubic, rd)):.2f} m/s, physics-shaped {e(weid(rd, *best)):.3f} m/s")
print(f"cubic predicts {np.polyval(cubic, 5.0):.2f} m/s at 5 per m2 (true {weid(5.0):.2f})")
