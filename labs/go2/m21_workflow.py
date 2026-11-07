"""2.1 Honest evaluation: random vs time-based splits for a traffic forecaster (NumPy only)."""
import numpy as np
rng = np.random.default_rng(61)
H = 24 * 21                                   # three weeks of hourly flow
t = np.arange(H)
flow = 800 + 600*np.maximum(0, np.sin(np.pi*((t % 24) - 6)/12)) + 1.2*t + 60*rng.standard_normal(H)
hist = H * 2 // 3                              # first two weeks are 'history', last week is the future

def knn(tq, pool, k=3):                       # average of the k nearest known hours
    idx = pool[np.argsort(np.abs(pool - tq))[:k]]
    return flow[idx].mean()

rmse = lambda p, y: np.sqrt(np.mean((np.array(p) - np.array(y))**2))
future = np.arange(hist, H)
for mode in ["random", "time"]:
    if mode == "random":
        m = np.random.default_rng(62).random(hist) < 0.7
        train, val = t[:hist][m], t[:hist][~m]
    else:
        cut = int(0.7 * hist); train, val = t[:cut], t[cut:hist]
    v = rmse([knn(x, train) for x in val], flow[val])
    f = rmse([knn(x, t[:hist]) for x in future], flow[future])
    print(f"{mode:6s} split: validation error {v:5.0f} veh/h, real error next week {f:5.0f} veh/h")
