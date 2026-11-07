"""2.4 SINDy (Brunton, Proctor and Kutz 2016) from scratch: discover the law of a damped oscillator from noisy data.
For real work use PySINDy: pip install pysindy."""
import numpy as np
rng = np.random.default_rng(71)
om, c, dt, N = 2.0, 0.3, 0.01, 1000
f = lambda s: np.array([s[1], -om**2*s[0] - c*s[1]])
S = np.zeros((N, 2)); s = np.array([1.0, 0.0])
for i in range(N):                                           # RK4 simulation of the true system
    S[i] = s; k1 = f(s); k2 = f(s + dt/2*k1); k3 = f(s + dt/2*k2); k4 = f(s + dt*k3); s = s + dt/6*(k1 + 2*k2 + 2*k3 + k4)
names = ["1", "x", "v", "x^2", "x*v", "v^2", "x^3"]
def discover(noise, thr):
    Z = S + noise*rng.standard_normal(S.shape)
    Zs = np.array([np.convolve(Z[:, j], np.ones(11)/11, mode="same") for j in range(2)]).T   # smooth before differentiating
    x, v = Zs[6:-6, 0], Zs[6:-6, 1]
    dv = (Zs[7:-5, 1] - Zs[5:-7, 1])/(2*dt)
    Theta = np.c_[np.ones_like(x), x, v, x**2, x*v, v**2, x**3]
    xi = np.linalg.lstsq(Theta, dv, rcond=None)[0]
    for _ in range(10):                                      # sequential thresholded least squares
        small = np.abs(xi) < thr; xi[small] = 0
        big = ~small
        if big.any(): xi[big] = np.linalg.lstsq(Theta[:, big], dv, rcond=None)[0]
    return " ".join(f"{q:+.2f} {n}" for q, n in zip(xi, names) if q != 0)
for noise, thr in [(0.001, 0.1), (0.01, 0.1), (0.05, 0.1), (0.05, 0.5)]:
    print(f"noise {noise:5.3f}, threshold {thr}: dv/dt = {discover(noise, thr)}")
print("true law:                       dv/dt = -4.00 x -0.30 v")
