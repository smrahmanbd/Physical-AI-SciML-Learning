"""2.2 A physics-informed neural network written from scratch in NumPy (runs in the browser).
Law: dy/dt = -k y, y(0) = 1. Six noisy measurements in [0, 1]; predict on [0, 5].
Network: one hidden layer of tanh neurons. Gradients are derived by hand (autodiff does this for you in PyTorch/JAX).
Set LEARN_K = True to solve the inverse problem: also learn k from the data."""
import numpy as np
rng = np.random.default_rng(0)
K_TRUE, LEARN_K, H = 0.8, True, 16
td = np.linspace(0, 1, 6); yd = np.exp(-K_TRUE*td) + 0.01*rng.standard_normal(6)
tc = np.linspace(0, 5, 40)                                  # collocation points
p = {"w": rng.standard_normal(H), "b": rng.standard_normal(H), "v": 0.1*rng.standard_normal(H), "c": np.array(0.0), "k": np.array(0.3 if LEARN_K else K_TRUE)}
lam, lr, m_, v_ = 1.0, 0.01, {q: 0*p[q] for q in p}, {q: 0*p[q] for q in p}

def forward(t):
    s = np.tanh(np.outer(t, p["w"]) + p["b"])             # (n, H)
    y = s @ p["v"] + p["c"]
    dy = ((1 - s**2) * p["w"]) @ p["v"]                     # dy/dt by the chain rule
    return s, y, dy

for epoch in range(1, 8001):
    g = {q: 0*p[q] for q in p}
    s, y, _ = forward(td); r = y - yd                       # data residual
    d = 1 - s**2
    g["v"] += 2*(r @ s)/len(td); g["c"] += 2*r.mean()
    g["w"] += 2*((r[:, None]*d*p["v"]*td[:, None]).sum(0))/len(td); g["b"] += 2*((r[:, None]*d*p["v"]).sum(0))/len(td)
    s, y, dy = forward(tc); d = 1 - s**2; R = dy + p["k"]*y  # physics residual
    dR_dv = d*p["w"] + p["k"]*s
    dR_dw = p["v"]*(d + p["w"]*(-2*s*d)*tc[:, None]) + p["k"]*p["v"]*d*tc[:, None]
    dR_db = p["v"]*p["w"]*(-2*s*d) + p["k"]*p["v"]*d
    sc = 2*lam/len(tc)
    g["v"] += sc*(R @ dR_dv); g["w"] += sc*(R @ dR_dw); g["b"] += sc*(R @ dR_db); g["c"] += sc*(R.sum()*p["k"])
    if LEARN_K: g["k"] = np.array(sc*(R @ y))
    s0, y0, _ = forward(np.array([0.0])); r0 = y0[0] - 1.0  # initial condition y(0) = 1
    g["v"] += 2*r0*s0[0]; g["c"] += 2*r0; g["w"] += 0; g["b"] += 2*r0*(1 - s0[0]**2)*p["v"]
    for q in p:                                             # Adam update
        m_[q] = 0.9*m_[q] + 0.1*g[q]; v_[q] = 0.999*v_[q] + 0.001*g[q]**2
        p[q] = p[q] - lr*(m_[q]/(1 - 0.9**epoch))/(np.sqrt(v_[q]/(1 - 0.999**epoch)) + 1e-8)
    if epoch in (1, 2000, 8000):
        print(f"epoch {epoch:5d}: data loss {np.mean((forward(td)[1] - yd)**2):.2e}, physics loss {np.mean(R**2):.2e}, k = {float(p['k']):.3f}")
tt = np.linspace(1, 5, 50)
print(f"error beyond the data: {np.sqrt(np.mean((forward(tt)[1] - np.exp(-K_TRUE*tt))**2)):.4f}")
