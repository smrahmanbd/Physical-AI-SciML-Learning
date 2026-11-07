"""2.2 The same PINN in PyTorch: automatic differentiation replaces the hand-derived gradients.
Install: pip install torch. Runs on a laptop CPU in under a minute. Also learns k (inverse problem)."""
import torch
torch.manual_seed(0)
K_TRUE = 0.8
td = torch.linspace(0, 1, 6).reshape(-1, 1); yd = torch.exp(-K_TRUE*td) + 0.01*torch.randn_like(td)
tc = torch.linspace(0, 5, 40).reshape(-1, 1).requires_grad_(True)       # collocation points
net = torch.nn.Sequential(torch.nn.Linear(1, 32), torch.nn.Tanh(), torch.nn.Linear(32, 32), torch.nn.Tanh(), torch.nn.Linear(32, 1))
k = torch.nn.Parameter(torch.tensor(0.3))                               # unknown decay rate
opt = torch.optim.Adam(list(net.parameters()) + [k], lr=1e-3)
for epoch in range(1, 6001):
    opt.zero_grad()
    y = net(tc)
    dy = torch.autograd.grad(y, tc, torch.ones_like(y), create_graph=True)[0]   # dy/dt by autodiff
    loss_phys = ((dy + k*y)**2).mean()
    loss_data = ((net(td) - yd)**2).mean()
    loss_ic = ((net(torch.zeros(1, 1)) - 1)**2).mean()
    loss = loss_data + loss_phys + loss_ic
    loss.backward(); opt.step()
    if epoch % 2000 == 0:
        print(f"epoch {epoch}: data {loss_data.item():.2e}, physics {loss_phys.item():.2e}, k = {k.item():.3f}")
tt = torch.linspace(1, 5, 50).reshape(-1, 1)
with torch.no_grad():
    print(f"error beyond the data: {torch.sqrt(((net(tt) - torch.exp(-K_TRUE*tt))**2).mean()).item():.4f}")
