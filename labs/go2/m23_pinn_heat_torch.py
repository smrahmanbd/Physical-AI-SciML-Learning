"""2.3 A PINN for the heat equation u_t = u_xx on [0,1] x [0,0.1], u(0,t) = u(1,t) = 0, u(x,0) = sin(pi x).
No data inside the domain: physics, boundary and initial conditions only (a forward problem). Install: pip install torch."""
import torch, math
torch.manual_seed(1)
net = torch.nn.Sequential(torch.nn.Linear(2, 40), torch.nn.Tanh(), torch.nn.Linear(40, 40), torch.nn.Tanh(), torch.nn.Linear(40, 1))
opt = torch.optim.Adam(net.parameters(), lr=2e-3)
for it in range(1, 4001):
    xt = torch.rand(1000, 2) * torch.tensor([1.0, 0.1]); xt.requires_grad_(True)
    u = net(xt); g = torch.autograd.grad(u, xt, torch.ones_like(u), create_graph=True)[0]
    u_xx = torch.autograd.grad(g[:, :1], xt, torch.ones_like(u), create_graph=True)[0][:, :1]
    res = g[:, 1:] - u_xx                                         # u_t - u_xx
    xb = torch.rand(200, 1); tb = 0.1*torch.rand(200, 1)
    loss = (res**2).mean() + (net(torch.cat([torch.zeros_like(tb), tb], 1))**2).mean() + (net(torch.cat([torch.ones_like(tb), tb], 1))**2).mean() \
        + ((net(torch.cat([xb, torch.zeros_like(xb)], 1)) - torch.sin(math.pi*xb))**2).mean()
    opt.zero_grad(); loss.backward(); opt.step()
    if it % 1000 == 0: print(f"iteration {it}: loss {loss.item():.2e}")
xs = torch.linspace(0, 1, 101).reshape(-1, 1); tt = torch.full_like(xs, 0.1)
with torch.no_grad():
    err = (net(torch.cat([xs, tt], 1)) - math.exp(-math.pi**2*0.1)*torch.sin(math.pi*xs)).abs().max().item()
print(f"max error at t = 0.1: {err:.4f}")
