"""2.5 A small DeepONet (Lu et al. 2021) for the same map f -> u, -u'' = f. Install: pip install torch.
Branch net encodes the input function at m sensor points; trunk net encodes the query location x; output = dot product."""
import torch, numpy as np
torch.manual_seed(0); rng = np.random.default_rng(0); m, K = 24, 8
x = np.linspace(0, 1, m + 2)[1:-1]
A = (np.diag(2*np.ones(m)) - np.diag(np.ones(m - 1), 1) - np.diag(np.ones(m - 1), -1))*(m + 1)**2
def sample(n):
    a = rng.standard_normal((n, K))/np.arange(1, K + 1)
    F = a @ (np.sin(np.outer(np.arange(1, K + 1), np.pi*x))*(np.arange(1, K + 1)[:, None]*np.pi)**2*0.1)
    return torch.tensor(F, dtype=torch.float32), torch.tensor(np.linalg.solve(A, F.T).T, dtype=torch.float32)
F, U = sample(500); Ft, Ut = sample(100)
branch = torch.nn.Sequential(torch.nn.Linear(m, 64), torch.nn.Tanh(), torch.nn.Linear(64, 40))
trunk = torch.nn.Sequential(torch.nn.Linear(1, 64), torch.nn.Tanh(), torch.nn.Linear(64, 64), torch.nn.Tanh(), torch.nn.Linear(64, 40))
X = torch.tensor(x, dtype=torch.float32).reshape(-1, 1)
opt = torch.optim.Adam(list(branch.parameters()) + list(trunk.parameters()), lr=1e-3)
scale = U.std(); fs = F.std()
for it in range(1, 4001):
    pred = branch(F/fs) @ trunk(X).T                             # (n_functions, m points)
    loss = ((pred - U/scale)**2).mean(); opt.zero_grad(); loss.backward(); opt.step()
    if it % 1000 == 0: print(f"iteration {it}: loss {loss.item():.2e}")
with torch.no_grad():
    pt = branch(Ft/fs) @ trunk(X).T*scale
    print(f"relative error on 100 new inputs: {((pt - Ut).norm(dim=1)/Ut.norm(dim=1)).mean().item():.3f}")
