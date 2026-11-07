"""2.5 Operator learning in its simplest form: learn the map f -> u for -u'' = f (u(0) = u(1) = 0) from example pairs.
The map is linear, so ridge regression on discretised functions can learn it exactly once there are enough examples."""
import numpy as np
rng = np.random.default_rng(81); m, K = 24, 8
x = np.linspace(0, 1, m + 2)[1:-1]
A = (np.diag(2*np.ones(m)) - np.diag(np.ones(m - 1), 1) - np.diag(np.ones(m - 1), -1))*(m + 1)**2
def sample(n):                                              # random sources built from 8 sine shapes
    a = rng.standard_normal((n, K))/np.arange(1, K + 1)
    return a @ (np.sin(np.outer(np.arange(1, K + 1), np.pi*x))*(np.arange(1, K + 1)[:, None]*np.pi)**2*0.1)
Ft = sample(10); Ut = np.linalg.solve(A, Ft.T).T
for n in [2, 4, 8, 12]:
    F = sample(n); U = np.linalg.solve(A, F.T).T             # 'expensive' solver gives training pairs
    G = U.T @ np.linalg.solve(F @ F.T + 1e-6*np.eye(n), F)   # learned operator (m x m matrix)
    err = np.mean(np.linalg.norm(Ft @ G.T - Ut, axis=1)/np.linalg.norm(Ut, axis=1))
    print(f"{n:2d} training pairs: relative error on new inputs {err:.3f}")
