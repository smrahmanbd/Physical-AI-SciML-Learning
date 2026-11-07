"""3.7 A digital twin of a signalised approach: a queue model corrected each cycle with detector data."""
import numpy as np
rng = np.random.default_rng(151); C, G, sat, n = 90, 40, 0.5, 60
lam = lambda k: 0.18 + 0.1*np.sin(k/9)
cyc = lambda q, l: max(0.0, q + l*C - sat*G)
truth, q = [], 0.0
for k in range(n): q = cyc(q, lam(k)*(1 + 0.15*rng.standard_normal())); truth.append(q)
truth = np.array(truth)
def twin(gain, noise=3.0, fail=False):
    qt, qm, est, model = 0.0, 0.0, [], []
    for k in range(n):
        qm = cyc(qm, 0.85*lam(k)); model.append(qm)            # model alone: arrivals 15% too low
        pred = cyc(qt, 0.85*lam(k)); z = truth[k] + noise*rng.standard_normal()
        qt = pred if (fail and 25 <= k < 45) else max(0.0, pred + gain*(z - pred)); est.append(qt)
    r = lambda a: np.sqrt(np.mean((np.array(a) - truth)**2))
    return r(model), r(est)
for gain, fail in [(0.0, False), (0.5, False), (0.5, True)]:
    m, t = twin(gain, fail=fail)
    print(f"gain {gain}, detector {'fails 20 cycles' if fail else 'working'}: model alone {m:5.1f} veh, twin {t:5.1f} veh")
