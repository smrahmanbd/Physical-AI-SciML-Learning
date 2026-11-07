"""3.4 Physics-based vehicle energy (road-load equation) plus a learned correction for engine efficiency."""
import numpy as np
rng = np.random.default_rng(3); m, g, cr, cdA, rho = 1500, 9.81, 0.012, 0.7, 1.2
def cycle(aggr):
    v = []
    for vc, cs in [(14, 40), (17, 60), (11, 30), (20, 70), (14, 45)]:
        v += [min(vc, 1.2*aggr*t) for t in range(int(vc/(1.2*aggr)))] + [vc]*cs + [max(0, vc - 1.5*aggr*t) for t in range(int(vc/(1.5*aggr)))] + [0]*15
    return np.array(v, float)
def power(v, grade=0.0):
    a = np.r_[0, np.diff(v)]; th = np.arctan(grade/100)
    return m*v*(a + g*np.sin(th)) + m*g*cr*v*np.cos(th) + 0.5*rho*cdA*v**3   # watts
def true_fuel(P):                      # 'measured' fuel power: efficiency varies with load (unknown to the physics model)
    eff = 0.12 + 0.2*np.tanh(np.maximum(P, 0)/15000)
    return np.where(P > 0, P/eff, 0) + 1200
phys_fuel = lambda P: np.where(P > 0, P/0.25, 0) + 1200        # constant 25% efficiency
v = np.r_[cycle(1.0), cycle(1.6)]; P = power(v); F = true_fuel(P)*(1 + 0.03*rng.standard_normal(len(P)))   # training: two driving styles
X = np.c_[np.ones_like(P), P/1e4, (P/1e4)**2]                  # learn the residual as a function of power
c = np.linalg.lstsq(X, F - phys_fuel(P), rcond=None)[0]
for aggr in [1.3, 2.0]:                                       # test: unseen styles
    v2 = cycle(aggr); P2 = power(v2); km = v2.sum()/1000; X2 = np.c_[np.ones_like(P2), P2/1e4, (P2/1e4)**2]
    co2 = lambda Fw: Fw.sum()/1e6*73/km                       # 73 g CO2 per MJ of petrol
    print(f"style x{aggr}: true {co2(true_fuel(P2)):5.0f} g/km, physics {co2(phys_fuel(P2)):5.0f} g/km, hybrid {co2(phys_fuel(P2) + X2 @ c):5.0f} g/km")
