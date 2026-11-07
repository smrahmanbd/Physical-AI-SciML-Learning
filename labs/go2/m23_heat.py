"""2.3 The heat equation u_t = u_xx on [0, 1] by explicit finite differences, with a stability check.
Classical solvers like this generate training data and reference answers for SciML."""
import numpy as np
nx = 41; x = np.linspace(0, 1, nx); dx = x[1] - x[0]
exact = lambda x, t: np.exp(-np.pi**2*t)*np.sin(np.pi*x) + 0.5*np.exp(-25*np.pi**2*t)*np.sin(5*np.pi*x)
for r in [0.25, 0.5, 0.52, 0.6]:
    dt = r*dx**2; n = int(np.ceil(0.03/dt))
    u = exact(x, 0) + 1e-4*(-1)**np.arange(nx); u[0] = u[-1] = 0     # tiny wiggle reveals instability
    for _ in range(n):
        u[1:-1] = u[1:-1] + r*(u[2:] - 2*u[1:-1] + u[:-2])
    err = np.max(np.abs(u - exact(x, n*dt)))
    print(f"r = {r:4.2f}: {n:3d} steps, max error {err:.2e}{'  <- unstable' if r > 0.5 else ''}")
