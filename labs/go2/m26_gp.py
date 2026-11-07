"""2.6 Gaussian process regression from scratch: prediction with uncertainty. (scikit-learn: GaussianProcessRegressor.)"""
import numpy as np
rng = np.random.default_rng(91)
f = lambda x: np.sin(3*x) + 0.5*x - 1
x = 4*rng.random(8); y = f(x) + 0.1*rng.standard_normal(8)
xs = np.linspace(0, 4, 121)
def gp(ell, sn):
    k = lambda a, b: np.exp(-0.5*((a[:, None] - b[None, :])/ell)**2)
    L = np.linalg.cholesky(k(x, x) + sn**2*np.eye(len(x)))
    al = np.linalg.solve(L.T, np.linalg.solve(L, y)); Ks = k(xs, x)
    mu = Ks @ al; v = np.linalg.solve(L, Ks.T); sd = np.sqrt(np.maximum(1 - (v**2).sum(0), 1e-12) + sn**2)
    nlml = 0.5*y @ al + np.log(np.diag(L)).sum() + 0.5*len(x)*np.log(2*np.pi)   # negative log marginal likelihood
    cover = np.mean(np.abs(f(xs) - mu) <= 1.96*sd)
    return mu, sd, nlml, cover
for ell in [0.1, 0.6, 3.0]:
    mu, sd, nlml, cover = gp(ell, 0.1)
    print(f"length scale {ell:3.1f}: error {np.sqrt(np.mean((mu - f(xs))**2)):.3f}, truth inside 95% band {cover:.0%}, -log likelihood {nlml:6.2f}")
best = min(np.linspace(0.1, 3, 59), key=lambda l: gp(l, 0.1)[2])
print(f"length scale chosen by maximum likelihood: {best:.2f}")
