"""3.5 A Gaussian process emulator for an integrated assessment model output, with active learning.
The 'full model' is a smooth toy curve standing in for GCAM transport CO2 in 2050 versus carbon price."""
import numpy as np
iam = lambda p: 1.6*(0.38 + 0.62*np.exp(-p/110)) + 0.12*np.sin(p/35)*np.exp(-p/180)
xs = np.linspace(0, 400, 401)
def gp(x, y, ell=0.9, sn=0.005, sf=0.5):
    k = lambda a, b: sf**2*np.exp(-0.5*((a[:, None] - b[None, :])/100/ell)**2)
    mu0 = y.mean(); L = np.linalg.cholesky(k(x, x) + sn**2*np.eye(len(x)))
    al = np.linalg.solve(L.T, np.linalg.solve(L, y - mu0)); Ks = k(xs, x); v = np.linalg.solve(L, Ks.T)
    return Ks @ al + mu0, np.sqrt(np.maximum(sf**2 - (v**2).sum(0), 1e-12))
x = np.array([0.0, 200.0, 400.0])                             # three initial 'GCAM runs'
for it in range(5):
    mu, sd = gp(x, iam(x)); err = np.sqrt(np.mean((mu - iam(xs))**2))
    print(f"{len(x)} runs: emulator error {err:.4f} Gt, largest uncertainty at {xs[sd.argmax()]:.0f} $/t")
    x = np.r_[x, xs[sd.argmax()]]                              # active learning: run where most uncertain
