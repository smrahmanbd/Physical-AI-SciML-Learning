"""3.2 Car following: Intelligent Driver Model platoons for human drivers, ACC and cooperative ACC (string stability)."""
import numpy as np
def platoon(ctrl, T=1.2, n=10):
    v0, a, b, s0, ln, dt = 30, (0.8 if ctrl == "human" else 1.2), 2, 2, 5, 0.1
    lag = 8 if ctrl == "human" else 0                        # 0.8 s human reaction delay
    x = -np.arange(n)*(ln + s0 + 25*T); v = np.full(n, 25.0); acc = np.zeros(n); hist = []; vmin_last = 99
    for k in range(801):
        t = k*dt; hist.append(np.r_[x, v]); past = hist[max(0, len(hist) - 1 - lag)]
        na = np.zeros(n); na[0] = -3.5 if 20 < t < 24 else (1 if t >= 24 and v[0] < 25 else 0)
        xi, vi, xl, vl = past[1:n], past[n+1:], past[:n-1], past[n:2*n-1]
        s = np.maximum(0.1, xl - xi - ln); ss = s0 + np.maximum(0, vi*T + vi*(vi - vl)/(2*np.sqrt(a*b)))
        na[1:] = a*(1 - (vi/v0)**4 - (ss/s)**2) + (0.6*acc[:-1] if ctrl == "cacc" else 0)
        na = np.clip(na, -9, 3); v = np.maximum(0, v + na*dt); x = x + v*dt; acc = na; vmin_last = min(vmin_last, v[-1])
    return vmin_last
for ctrl in ["human", "acc", "cacc"]:
    m = platoon(ctrl)
    print(f"{ctrl:5s}: last car's lowest speed {m*3.6:5.1f} km/h, amplification {(25 - m)/(25 - 11.0):.2f}")
