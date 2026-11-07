/* Numerical cores for the Physical AI and Scientific Machine Learning course.
   Every explorer, every simulation challenge and the build-time checks call these same functions.
   All data are synthetic teaching data with fixed random seeds; formulas follow the sources named in the modules. */
(function (root) {
  "use strict";
  const S = {};
  // ---------------------------------------------------------------- helpers
  const rng = (seed) => () => ((seed = (seed * 1664525 + 1013904223) % 4294967296) / 4294967296);
  const gauss = (R) => { let u = 0, v = 0; while (u === 0) u = R(); v = R(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };
  const lin = (a, b, n) => Array.from({ length: n }, (_, i) => a + ((b - a) * i) / (n - 1));
  const rmse = (a, b) => Math.sqrt(a.reduce((s, x, i) => s + (x - b[i]) ** 2, 0) / a.length);
  /** solve A x = b (dense, partial pivoting); A is array of rows */
  function solve(A, b) {
    const n = b.length, M = A.map((r, i) => r.slice().concat([b[i]]));
    for (let c = 0; c < n; c++) {
      let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r;
      [M[c], M[p]] = [M[p], M[c]];
      const d = M[c][c] || 1e-12;
      for (let r = c + 1; r < n; r++) { const f = M[r][c] / d; if (f) for (let k = c; k <= n; k++) M[r][k] -= f * M[c][k]; }
    }
    const x = new Array(n).fill(0);
    for (let r = n - 1; r >= 0; r--) { let s = M[r][n]; for (let k = r + 1; k < n; k++) s -= M[r][k] * x[k]; x[r] = s / (M[r][r] || 1e-12); }
    return x;
  }
  /** least squares min ||Φw − y||² + ridge ||w||² via normal equations */
  function lstsq(Phi, y, ridge = 1e-9) {
    const m = Phi[0].length, A = Array.from({ length: m }, () => new Array(m).fill(0)), b = new Array(m).fill(0);
    Phi.forEach((row, i) => { for (let a = 0; a < m; a++) { b[a] += row[a] * y[i]; for (let c = 0; c < m; c++) A[a][c] += row[a] * row[c]; } });
    for (let a = 0; a < m; a++) A[a][a] += ridge;
    return solve(A, b);
  }
  const dot = (a, b) => a.reduce((s, x, i) => s + x * b[i], 0);
  function cholesky(K) { const n = K.length, L = K.map(() => new Array(n).fill(0)); for (let i = 0; i < n; i++) for (let j = 0; j <= i; j++) { let s = K[i][j]; for (let k = 0; k < j; k++) s -= L[i][k] * L[j][k]; L[i][j] = i === j ? Math.sqrt(Math.max(s, 1e-12)) : s / L[j][j]; } return L; }
  function cholSolve(L, b) { const n = b.length, y = new Array(n), x = new Array(n); for (let i = 0; i < n; i++) { let s = b[i]; for (let k = 0; k < i; k++) s -= L[i][k] * y[k]; y[i] = s / L[i][i]; } for (let i = n - 1; i >= 0; i--) { let s = y[i]; for (let k = i + 1; k < n; k++) s -= L[k][i] * x[k]; x[i] = s / L[i][i]; } return x; }
  S.util = { rng, gauss, lin, rmse, solve, lstsq, cholesky, cholSolve };

  // ---------------------------------------------------------------- 1.1 physics–data spectrum
  S.spectrum = ({ w = 0.5, n = 8 }) => {
    const truth = (t) => Math.exp(-0.3 * t) * Math.cos(2 * t), phys = (t) => Math.exp(-0.45 * t) * Math.cos(1.85 * t);
    const R = rng(11), td = lin(0, 2, n), yd = td.map((t) => truth(t) + 0.05 * gauss(R));
    const deg = Math.min(n - 1, 5), coef = lstsq(td.map((t) => Array.from({ length: deg + 1 }, (_, k) => t ** k)), yd, 1e-8);
    const poly = (t) => coef.reduce((s, c, k) => s + c * t ** k, 0);
    const ts = lin(0, 6, 121), pred = ts.map((t) => Math.max(-2, Math.min(2, (1 - w) * poly(t) + w * phys(t)))), tru = ts.map(truth);
    const inI = ts.map((t, i) => (t <= 2 ? i : -1)).filter((i) => i >= 0), outI = ts.map((t, i) => (t > 2 ? i : -1)).filter((i) => i >= 0);
    return { ts, truth: tru, pred: pred.map((v) => Math.max(-2, Math.min(2, v))), data: [td, yd], errIn: rmse(inI.map((i) => pred[i]), inI.map((i) => tru[i])), errOut: rmse(outI.map((i) => pred[i]), outI.map((i) => tru[i])) };
  };
  // ---------------------------------------------------------------- 1.2 ODEs and Euler's method
  S.ode = ({ model = "decay", dt = 0.5, k = 0.5 }) => {
    const T = 10, N = Math.round(T / dt), ex = lin(0, T, 201);
    let exact, euler = [], te = [];
    if (model === "decay") { exact = (t) => Math.exp(-k * t); let y = 1; for (let i = 0; i <= N; i++) { te.push(i * dt); euler.push(y); y += dt * (-k * y); } }
    else if (model === "logistic") { const y0 = 0.05; exact = (t) => 1 / (1 + ((1 - y0) / y0) * Math.exp(-k * t)); let y = y0; for (let i = 0; i <= N; i++) { te.push(i * dt); euler.push(y); y += dt * k * y * (1 - y); } }
    else { const om = 2 * k; exact = (t) => Math.cos(om * t); let x = 1, v = 0; for (let i = 0; i <= N; i++) { te.push(i * dt); euler.push(x); const nx = x + dt * v; v += dt * (-om * om * x); x = nx; } }
    const err = Math.max(...te.map((t, i) => Math.abs(euler[i] - exact(t))));
    return { ex, exact: ex.map(exact), te, euler, err, steps: N };
  };
  // ---------------------------------------------------------------- 1.3 a one-hidden-layer network (random features, output layer solved exactly)
  const targets = { sine: (x) => Math.sin(3 * x), step: (x) => (x > 0.1 ? 1 : -0.5), bump: (x) => Math.exp(-12 * x * x) - 0.3 * x };
  S.nnfit = ({ units = 8, target = "sine" }) => {
    const f = targets[target], R = rng(5), Wh = Array.from({ length: units }, () => 3 * gauss(R)), bh = Array.from({ length: units }, () => 6 * R() - 3);
    const feat = (x) => [1].concat(Wh.map((w, j) => Math.tanh(w * x + bh[j])));
    const R2 = rng(9), xt = lin(-1, 1, 30), yt = xt.map((x) => f(x) + 0.03 * gauss(R2));
    const wo = lstsq(xt.map(feat), yt, 1e-6), xs = lin(-1, 1, 161), pred = xs.map((x) => dot(feat(x), wo)), tru = xs.map(f);
    return { xs, pred, truth: tru, data: [xt, yt], err: rmse(pred, tru), params: 3 * units + 1 };
  };
  // ---------------------------------------------------------------- 1.4 gradient descent on a bumpy loss
  const Lf = (w) => 0.1 * (w - 3) ** 2 + 0.4 * Math.sin(2.5 * w), dLf = (w) => 0.2 * (w - 3) + Math.cos(2.5 * w);
  S.gd = ({ lr = 0.1, mom = 0, steps = 60 }) => {
    let w = -2, v = 0; const ws = [w], Ls = [Lf(w)];
    for (let i = 0; i < steps; i++) { v = mom * v - lr * dLf(w); w += v; w = Math.max(-50, Math.min(50, w)); ws.push(w); Ls.push(Lf(w)); }
    const grid = lin(-4, 8, 1201), best = Math.min(...grid.map(Lf));
    return { it: ws.map((_, i) => i), ws, Ls, w, L: Lf(w), gap: Lf(w) - best, best, grid, curve: grid.map(Lf) };
  };
  // ---------------------------------------------------------------- 1.5 / 2.2 physics-informed fit of y' = −k y (Gaussian basis, linear least squares)
  const KD = 0.8, centres = lin(0, 5, 14), WID = 0.5;
  const phi = (t) => [1].concat(centres.map((c) => Math.exp(-(((t - c) / WID) ** 2))));
  const dphi = (t) => [0].concat(centres.map((c) => -2 * ((t - c) / WID ** 2) * Math.exp(-(((t - c) / WID) ** 2))));
  function pinnRows(lam, nc, nd) {
    const R = rng(21), td = lin(0, 1, nd), yd = td.map((t) => Math.exp(-KD * t) + 0.02 * gauss(R));
    const rows = [], y = [];
    td.forEach((t, i) => { rows.push(phi(t)); y.push(yd[i]); });
    const s = Math.sqrt(lam);
    if (nc > 0) lin(0, 5, nc).forEach((t) => { const p = phi(t), d = dphi(t); rows.push(p.map((v, j) => s * (d[j] + KD * v))); y.push(0); });
    return { rows, y, td, yd };
  }
  function pinnEval(w, td, yd) {
    const ts = lin(0, 5, 101), pred = ts.map((t) => dot(phi(t), w)), tru = ts.map((t) => Math.exp(-KD * t));
    const out = ts.map((t, i) => (t >= 1 ? i : -1)).filter((i) => i >= 0);
    return { ts, pred: pred.map((v) => Math.max(-1, Math.min(2, v))), truth: tru, data: [td, yd], errOut: rmse(out.map((i) => pred[i]), out.map((i) => tru[i])), errAll: rmse(pred, tru) };
  }
  S.pinn = ({ lam = 1, nc = 20, nd = 6 }) => { const P = pinnRows(lam, nc, nd); return pinnEval(lstsq(P.rows, P.y, 1e-6), P.td, P.yd); };
  S.pinntrain = ({ lam = 1, lr = 0.05, epochs = 400 }) => { // Adam on the same loss, recording both parts
    const P = pinnRows(lam, 30, 6), nd = 6, m = P.rows[0].length; let w = new Array(m).fill(0), mo = new Array(m).fill(0), ve = new Array(m).fill(0);
    const ep = [], Ld = [], Lp = [];
    for (let e = 1; e <= epochs; e++) {
      const g = new Array(m).fill(0); let ld = 0, lp = 0;
      P.rows.forEach((r, i) => { const res = dot(r, w) - P.y[i]; if (i < nd) ld += res * res / nd; else lp += res * res / 30; const sc = 2 * res / (i < nd ? nd : 30); for (let j = 0; j < m; j++) g[j] += sc * r[j]; });
      for (let j = 0; j < m; j++) { mo[j] = 0.9 * mo[j] + 0.1 * g[j]; ve[j] = 0.999 * ve[j] + 0.001 * g[j] * g[j]; w[j] -= lr * (mo[j] / (1 - 0.9 ** e)) / (Math.sqrt(ve[j] / (1 - 0.999 ** e)) + 1e-8); }
      if (e === 1 || e % Math.max(1, Math.round(epochs / 80)) === 0) { ep.push(e); Ld.push(ld); Lp.push(lp / Math.max(lam, 1e-9)); }
    }
    return Object.assign(pinnEval(w, P.td, P.yd), { ep, Ld, Lp });
  };
  // ---------------------------------------------------------------- 1.6 noise, model size and overfitting
  S.noise = ({ deg = 3, sigma = 0.15, n = 15 }) => {
    const f = (x) => Math.sin(2 * Math.PI * x), R = rng(31), xt = lin(0, 1, n), yt = xt.map((x) => f(x) + sigma * gauss(R));
    const feat = (x) => Array.from({ length: deg + 1 }, (_, k) => (2 * x - 1) ** k), c = lstsq(xt.map(feat), yt, 1e-10);
    const xs = lin(0, 1, 201), fit = xs.map((x) => dot(feat(x), c));
    return { xs, fit: fit.map((v) => Math.max(-2.5, Math.min(2.5, v))), truth: xs.map(f), data: [xt, yt], train: rmse(xt.map((x) => dot(feat(x), c)), yt), test: rmse(fit, xs.map(f)) };
  };
  // ---------------------------------------------------------------- 1.7 surrogate of an "expensive" model by radial basis interpolation
  S.surrogate = ({ n = 6, eps = 1.5, design = "uniform" }) => {
    const f = (x) => Math.sin(3 * x) + 0.3 * x * x, R = rng(41);
    const xs0 = design === "uniform" ? lin(0, 3, n) : Array.from({ length: n }, () => 3 * R()).sort((a, b) => a - b);
    const K = xs0.map((a) => xs0.map((b) => Math.exp(-((eps * (a - b)) ** 2)))); K.forEach((r, i) => (r[i] += 1e-8));
    const w = solve(K, xs0.map(f)), xs = lin(0, 3, 151), pred = xs.map((x) => xs0.reduce((s, c, j) => s + w[j] * Math.exp(-((eps * (x - c)) ** 2)), 0));
    return { xs, pred: pred.map((v) => Math.max(-3, Math.min(5, v))), truth: xs.map(f), data: [xs0, xs0.map(f)], err: rmse(pred, xs.map(f)) };
  };
  // ---------------------------------------------------------------- 1.8 Kalman filter tracking a vehicle (sense → estimate)
  S.kalman = ({ sd = 8, q = 0.5 }) => {
    const R = rng(51), dt = 1, T = 60; let x = 0, v = 15; const tx = [], z = [];
    for (let t = 0; t <= T; t++) { tx.push(x); z.push(x + sd * gauss(R)); const a = 0.6 * gauss(R); x += v * dt + 0.5 * a; v += a; }
    let X = [z[0], 12], P = [[100, 0], [0, 25]]; const est = [], vel = [];
    const Q = [[q * 0.25, q * 0.5], [q * 0.5, q]], Rm = sd * sd;
    for (let t = 0; t <= T; t++) {
      if (t > 0) { X = [X[0] + X[1], X[1]]; P = [[P[0][0] + P[0][1] + P[1][0] + P[1][1] + Q[0][0], P[0][1] + P[1][1] + Q[0][1]], [P[1][0] + P[1][1] + Q[1][0], P[1][1] + Q[1][1]]]; }
      const Sx = P[0][0] + Rm, K = [P[0][0] / Sx, P[1][0] / Sx], y = z[t] - X[0];
      X = [X[0] + K[0] * y, X[1] + K[1] * y]; P = [[(1 - K[0]) * P[0][0], (1 - K[0]) * P[0][1]], [P[1][0] - K[1] * P[0][0], P[1][1] - K[1] * P[0][1]]];
      est.push(X[0]); vel.push(X[1]);
    }
    const ts = tx.map((_, i) => i);
    return { ts, truth: tx, meas: z, est, vel, errMeas: rmse(z, tx), errEst: rmse(est, tx) };
  };
  // ---------------------------------------------------------------- 2.1 train/validation split and leakage (k-nearest-neighbour forecaster)
  S.split = ({ frac = 0.7, mode = "random" }) => {
    const R = rng(61), H = 24 * 21, flow = Array.from({ length: H }, (_, t) => 800 + 600 * Math.max(0, Math.sin(Math.PI * ((t % 24) - 6) / 12)) + 1.2 * t + 60 * gauss(R));
    const train = [], val = [], R2 = rng(62), cut = Math.floor(frac * H * 2 / 3), hist = Math.floor(H * 2 / 3);
    for (let t = 0; t < hist; t++) { if (mode === "random" ? R2() < frac : t < cut) train.push(t); else val.push(t); }
    const knn = (t, pool) => { const nb = pool.slice().sort((a, b) => Math.abs(a - t) - Math.abs(b - t)).slice(0, 3); return nb.reduce((s, k) => s + flow[k], 0) / nb.length; };
    const all = train.concat(val), fut = Array.from({ length: H - hist }, (_, i) => hist + i);
    const valErr = rmse(val.map((t) => knn(t, train)), val.map((t) => flow[t])), futErr = rmse(fut.map((t) => knn(t, all)), fut.map((t) => flow[t]));
    return { ts: flow.map((_, i) => i), flow, valErr, futErr, ntrain: train.length, nval: val.length, hist };
  };
  // ---------------------------------------------------------------- 2.3 heat equation by finite differences (stability)
  S.heat = ({ r = 0.4 }) => {
    const nx = 41, dx = 1 / (nx - 1), dt = r * dx * dx, T = 0.03, N = Math.ceil(T / dt), xs = lin(0, 1, nx);
    const ex = (x, t) => Math.exp(-(Math.PI ** 2) * t) * Math.sin(Math.PI * x) + 0.5 * Math.exp(-25 * (Math.PI ** 2) * t) * Math.sin(5 * Math.PI * x);
    let u = xs.map((x, i) => ex(x, 0) + (i > 0 && i < nx - 1 ? 1e-4 * (i % 2 ? 1 : -1) : 0)); const snaps = [u.slice()], times = [0], every = Math.max(1, Math.floor(N / 3));
    for (let n = 1; n <= N; n++) { const nu = u.slice(); for (let i = 1; i < nx - 1; i++) nu[i] = u[i] + r * (u[i + 1] - 2 * u[i] + u[i - 1]); nu[0] = nu[nx - 1] = 0; u = nu; if (n % every === 0 || n === N) { snaps.push(u.slice()); times.push(n * dt); } }
    const err = Math.max(...xs.map((x, i) => Math.abs(u[i] - ex(x, N * dt))));
    return { xs, snaps: snaps.slice(0, 4).concat([u]).slice(-4), times: times.slice(0, 4).concat([N * dt]).slice(-4), exact: xs.map((x) => ex(x, N * dt)), err: isFinite(err) ? Math.min(err, 999) : 999, steps: N, stable: r <= 0.5 };
  };
  // ---------------------------------------------------------------- 2.4 SINDy: sparse regression finds the equation of a damped oscillator
  S.sindy = ({ noise = 0.01, thr = 0.1 }) => {
    const om = 2, c = 0.3, dt = 0.01, N = 1000, R = rng(71); let x = 1, v = 0; const X = [], V = [];
    const f = (x, v) => [v, -om * om * x - c * v];
    for (let i = 0; i < N; i++) { X.push(x); V.push(v); const k1 = f(x, v), k2 = f(x + dt / 2 * k1[0], v + dt / 2 * k1[1]), k3 = f(x + dt / 2 * k2[0], v + dt / 2 * k2[1]), k4 = f(x + dt * k3[0], v + dt * k3[1]); x += dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); v += dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]); }
    const Xn = X.map((a) => a + noise * gauss(R)), Vn = V.map((a) => a + noise * gauss(R));
    const sm = (a) => a.map((_, i) => { let s = 0, k = 0; for (let j = Math.max(0, i - 5); j <= Math.min(a.length - 1, i + 5); j++) { s += a[j]; k++; } return s / k; });
    const Xs = sm(Xn), Vs = sm(Vn), dV = [], rows = [];
    const names = ["1", "x", "v", "x²", "x·v", "v²", "x³"];
    for (let i = 6; i < N - 6; i++) { dV.push((Vs[i + 1] - Vs[i - 1]) / (2 * dt)); const a = Xs[i], b = Vs[i]; rows.push([1, a, b, a * a, a * b, b * b, a * a * a]); }
    let act = names.map(() => true), w = lstsq(rows, dV, 1e-9);
    for (let it = 0; it < 10; it++) { act = w.map((q, j) => act[j] && Math.abs(q) >= thr); const idx = act.map((a, j) => (a ? j : -1)).filter((j) => j >= 0); if (!idx.length) { w = w.map(() => 0); break; } const ws = lstsq(rows.map((r) => idx.map((j) => r[j])), dV, 1e-9); w = names.map(() => 0); idx.forEach((j, k) => (w[j] = ws[k])); }
    const truth = [0, -om * om, -c, 0, 0, 0, 0], ok = truth.map((t, j) => (t !== 0) === (w[j] !== 0)).every(Boolean);
    const eq = "dv/dt = " + (w.map((q, j) => (q ? `${q >= 0 ? "+ " : "− "}${Math.abs(q).toFixed(2)}${names[j] === "1" ? "" : " " + names[j]}` : "")).filter(Boolean).join(" ").replace(/^\+ /, "") || "0");
    return { names, w, truth, ok, nterms: w.filter((q) => q).length, eq, ts: X.map((_, i) => i * dt), X: Xn, V: Vn };
  };
  // ---------------------------------------------------------------- 2.5 operator learning: learn the map f ↦ u for −u'' = f
  function poissonSolve(f, m) { // tridiagonal FD, u(0)=u(1)=0
    const h2 = (1 / (m + 1)) ** 2, a = new Array(m).fill(-1), b = new Array(m).fill(2), c = new Array(m).fill(-1), d = f.map((v) => v * h2);
    for (let i = 1; i < m; i++) { const w = a[i] / b[i - 1]; b[i] -= w * c[i - 1]; d[i] -= w * d[i - 1]; }
    const u = new Array(m); u[m - 1] = d[m - 1] / b[m - 1]; for (let i = m - 2; i >= 0; i--) u[i] = (d[i] - c[i] * u[i + 1]) / b[i]; return u;
  }
  S.operator = ({ ntrain = 6, m = 24 }) => {
    const xs = lin(0, 1, m + 2).slice(1, -1), R = rng(81), K = 8;
    const sample = () => { const a = Array.from({ length: K }, (_, k) => gauss(R) / (k + 1)); return xs.map((x) => a.reduce((s, ak, k) => s + ak * Math.sin((k + 1) * Math.PI * x) * ((k + 1) * Math.PI) ** 2 * 0.1, 0)); };
    const F = Array.from({ length: ntrain }, sample), U = F.map((f) => poissonSolve(f, m));
    // ridge regression for each output point: u_i = Σ_j G_ij f_j  (dual form, ntrain × ntrain)
    const Kmat = F.map((a) => F.map((b) => dot(a, b))); Kmat.forEach((r, i) => (r[i] += 1e-6));
    const predict = (f) => { const kv = F.map((a) => dot(a, f)), al = solve(Kmat, kv); return xs.map((_, i) => al.reduce((s, q, n) => s + q * U[n][i], 0)); };
    const tests = Array.from({ length: 10 }, sample), errs = tests.map((f) => { const u = poissonSolve(f, m), p = predict(f); return rmse(p, u) / (Math.sqrt(u.reduce((s, x) => s + x * x, 0) / m) || 1); });
    const f0 = tests[0];
    return { xs, f: f0, u: poissonSolve(f0, m), pred: predict(f0), err: errs.reduce((a, b) => a + b, 0) / errs.length, K };
  };
  // ---------------------------------------------------------------- 2.6 Gaussian process regression (also used by the 3.5 emulator)
  function gpFit(x, y, ell, sn, sf = 1) {
    const k = (a, b) => sf * sf * Math.exp(-0.5 * ((a - b) / ell) ** 2), Kx = x.map((a) => x.map((b) => k(a, b))); Kx.forEach((r, i) => (r[i] += sn * sn + 1e-9));
    const L = cholesky(Kx), al = cholSolve(L, y);
    return (xs) => xs.map((t) => { const ks = x.map((a) => k(t, a)), mu = dot(ks, al), v = cholSolve(L, ks); return [mu, Math.sqrt(Math.max(1e-12, sf * sf - dot(ks, v)))]; });
  }
  S.util.gpFit = gpFit;
  S.gp = ({ n = 6, ell = 0.6, sn = 0.1 }) => {
    const f = (x) => Math.sin(3 * x) + 0.5 * x - 1, R = rng(91), x = Array.from({ length: n }, () => 4 * R()), y = x.map((a) => f(a) + 0.1 * gauss(R));
    const xs = lin(0, 4, 121), P = gpFit(x, y, ell, sn)(xs), mu = P.map((p) => p[0]), sd = P.map((p) => Math.sqrt(p[1] ** 2 + sn * sn)), tr = xs.map(f);
    const cover = tr.filter((t, i) => Math.abs(t - mu[i]) <= 1.96 * sd[i]).length / xs.length;
    return { xs, mu, lo: mu.map((m, i) => m - 1.96 * sd[i]), hi: mu.map((m, i) => m + 1.96 * sd[i]), truth: tr, data: [x, y], err: rmse(mu, tr), cover, width: 2 * 1.96 * sd.reduce((a, b) => a + b, 0) / sd.length };
  };
  // ---------------------------------------------------------------- 2.7 hybrid model: physics + learned residual (speed–density)
  S.hybrid = ({ n = 20, rmaxObs = 60 }) => {
    const vf = 100, rj = 140, truth = (r) => vf * (1 - Math.pow(r / rj, 1.6)), phys = (r) => vf * (1 - r / rj), R = rng(101);
    const rd = Array.from({ length: n }, () => 5 + (rmaxObs - 5) * R()), vd = rd.map((r) => truth(r) + 2 * gauss(R));
    const fp = (deg) => (r) => Array.from({ length: deg + 1 }, (_, k) => (r / 100) ** k);
    const f4 = fp(4), cML = lstsq(rd.map(f4), vd, 1e-6), f2 = fp(2), cH = lstsq(rd.map(f2), vd.map((v, i) => v - phys(rd[i])), 1e-3);
    const ml = (r) => dot(f4(r), cML), hy = (r) => phys(r) + dot(f2(r), cH), rs = lin(0, 140, 141), ext = rs.filter((r) => r > rmaxObs);
    const e = (g) => rmse(ext.map(g), ext.map(truth));
    const clip = (v) => Math.max(-40, Math.min(140, v));
    return { rs, truth: rs.map(truth), phys: rs.map(phys), ml: rs.map((r) => clip(ml(r))), hy: rs.map((r) => clip(hy(r))), data: [rd, vd], ePhys: e(phys), eML: e(ml), eHy: e(hy) };
  };
  // ---------------------------------------------------------------- 2.8 split conformal prediction intervals
  S.conformal = ({ ncal = 50, alpha = 0.1 }) => {
    const R = rng(111), draw = () => { const x = 3 * R(); return [x, 2 * x + (0.3 + 0.3 * x) * gauss(R)]; }, pred = (x) => 2 * x;
    const cal = Array.from({ length: ncal }, draw).map(([x, y]) => Math.abs(y - pred(x))).sort((a, b) => a - b);
    const kq = Math.min(ncal, Math.ceil((ncal + 1) * (1 - alpha))), q = cal[kq - 1];
    const test = Array.from({ length: 4000 }, draw), cover = test.filter(([x, y]) => Math.abs(y - pred(x)) <= q).length / test.length;
    const lowT = test.filter(([x]) => x < 1), highT = test.filter(([x]) => x > 2);
    const cv = (T) => T.filter(([x, y]) => Math.abs(y - pred(x)) <= q).length / T.length;
    const coverLow = cv(lowT), coverHigh = cv(highT);
    return { q, width: 2 * q, cover, target: 1 - alpha, coverLow, coverHigh, cal };
  };
  // ---------------------------------------------------------------- 3.1 physics-informed traffic state estimation (LWR + detectors, nudging)
  S.trafficpinn = ({ ndet = 5, gain = 0.5 }) => {
    const nx = 100, L = 10, dx = L / nx, vf = 100 / 3600, rj = 150, dt = 2, steps = 300; // km, km/s, veh/km, s
    const Q = (r) => vf * r * (1 - r / rj), rc = rj / 2;
    const godunov = (a, b) => { const qa = a <= rc ? Q(a) : Q(rc), qb = b >= rc ? Q(b) : Q(rc); return Math.min(qa, qb); }; // demand–supply
    const step = (r) => { const F = r.map((_, i) => godunov(r[i], r[(i + 1) % nx]) * 1); return r.map((v, i) => Math.max(0, Math.min(rj, v - (dt / dx) * (F[i] - F[(i + nx - 1) % nx])))); };
    let tr = Array.from({ length: nx }, (_, i) => (i >= 30 && i < 42 ? 120 : 30)), est = new Array(nx).fill(45);
    const R = rng(121), det = Array.from({ length: ndet }, (_, k) => Math.floor((k + 0.5) * nx / ndet));
    for (let s = 0; s < steps; s++) {
      tr = step(tr); est = step(est);
      det.forEach((i) => { const z = tr[i] + 3 * gauss(R); for (let d = -1; d <= 1; d++) { const j = (i + d + nx) % nx; est[j] += gain * (d === 0 ? 1 : 0.5) * (z - est[j]); } });
    }
    const obs = det.map((i) => tr[i]), interp = Array.from({ length: nx }, (_, i) => { // circular linear interpolation between detectors
      let k = det.findIndex((d) => d > i); if (k === -1) k = 0; const j = (k - 1 + ndet) % ndet; const d0 = det[j], d1 = det[k]; const span = (d1 - d0 + nx) % nx || nx, pos = (i - d0 + nx) % nx; return obs[j] + (obs[k] - obs[j]) * pos / span; });
    const xs = tr.map((_, i) => (i + 0.5) * dx);
    return { xs, truth: tr, est, interp, det: det.map((i) => xs[i]), errEst: rmse(est, tr), errInt: rmse(interp, tr) };
  };
  // ---------------------------------------------------------------- 3.2 car following: IDM platoon, ACC and cooperative ACC
  S.idm = ({ T = 1.2, ctrl = "acc", n = 10 }) => {
    const v0 = 30, a = ctrl === "human" ? 0.8 : 1.2, b = 2, s0 = 2, len = 5, dt = 0.1, Tend = 80, lag = ctrl === "human" ? 8 : 0;
    const x = Array.from({ length: n }, (_, i) => -i * (len + s0 + 25 * T)), v = new Array(n).fill(25), acc = new Array(n).fill(0), hist = [];
    const tr = { t: [], v: [[], [], []] }; const pick = [0, Math.floor(n / 2), n - 1]; let minLast = 99;
    for (let k = 0; k <= Tend / dt; k++) {
      const t = k * dt; hist.push(x.slice().concat(v));
      const past = hist[Math.max(0, hist.length - 1 - lag)];
      const na = new Array(n).fill(0);
      na[0] = t > 20 && t < 24 ? -3.5 : t >= 24 && v[0] < 25 ? 1 : 0;
      for (let i = 1; i < n; i++) {
        const xi = past[i], vi = past[n + i], xl = past[i - 1], vl = past[n + i - 1];
        const s = Math.max(0.1, xl - xi - len), ss = s0 + Math.max(0, vi * T + (vi * (vi - vl)) / (2 * Math.sqrt(a * b)));
        na[i] = a * (1 - (vi / v0) ** 4 - (ss / s) ** 2);
        if (ctrl === "cacc") na[i] += 0.6 * acc[i - 1];
        na[i] = Math.max(-9, Math.min(3, na[i]));
      }
      for (let i = 0; i < n; i++) { v[i] = Math.max(0, v[i] + na[i] * dt); x[i] += v[i] * dt; acc[i] = na[i]; }
      if (k % 5 === 0) { tr.t.push(t); pick.forEach((p, j) => tr.v[j].push(v[p])); }
      minLast = Math.min(minLast, v[n - 1]);
    }
    const minLead = Math.min(...tr.v[0]); const amp = (25 - minLast) / Math.max(0.1, 25 - minLead);
    let crash = false; for (let i = 1; i < n; i++) if (x[i - 1] - x[i] - len < 0) crash = true;
    return { t: tr.t, vs: tr.v, labels: ["Lead car", `Car ${pick[1] + 1}`, `Car ${n}`], minLast, minLead, amp, crash };
  };
  // ---------------------------------------------------------------- 3.3 surrogate safety measures: time to collision
  S.ttc = ({ gap = 40, dv = 8, react = 1.5, decel = 4 }) => {
    const vl = 15, dt = 0.05; let vf = vl + dv, g = gap, t = 0; const ts = [], ttc = [], gaps = []; let minT = 99, crash = false, drac = 0;
    while (t < 20) {
      const close = vf - vl; const tt = close > 0 ? g / close : 99; ts.push(t); ttc.push(Math.min(tt, 10)); gaps.push(g);
      if (close > 0) { minT = Math.min(minT, tt); drac = Math.max(drac, close * close / (2 * Math.max(g, 0.1))); }
      if (t >= react && vf > vl) vf = Math.max(vl, vf - decel * dt);
      g -= (vf - vl) * dt; t += dt; if (g <= 0) { crash = true; break; }
      if (vf <= vl && t > react) { ts.push(t); ttc.push(10); gaps.push(g); break; }
    }
    return { ts, ttc, gaps, minTTC: crash ? 0 : Math.min(minT, 10), crash, drac, conflict: crash || minT < 1.5 };
  };
  // ---------------------------------------------------------------- 3.4 vehicle power, energy and CO2 (physics-based)
  S.vsp = ({ aggr = 1, grade = 0, ev = false }) => {
    const m = 1500, g = 9.81, cr = 0.012, cdA = 0.7, rho = 1.2, dt = 1, th = Math.atan(grade / 100); const vs = [], P = [];
    const legs = [[14, 40], [17, 60], [11, 30], [20, 70], [14, 45]]; // cruise speed m/s, cruise seconds
    for (const [vc, cs] of legs) { const ta = vc / (1.2 * aggr), tb = vc / (1.5 * aggr); for (let t = 0; t < ta; t += dt) vs.push(Math.min(vc, 1.2 * aggr * t)); for (let t = 0; t < cs; t += dt) vs.push(vc); for (let t = 0; t < tb; t += dt) vs.push(Math.max(0, vc - 1.5 * aggr * t)); for (let t = 0; t < 15; t++) vs.push(0); }
    let dist = 0, Epos = 0, Eneg = 0;
    for (let i = 0; i < vs.length; i++) { const v = vs[i], a = i ? (vs[i] - vs[i - 1]) / dt : 0; const p = m * v * (a + g * Math.sin(th)) + m * g * cr * v * Math.cos(th) + 0.5 * rho * cdA * v ** 3; P.push(p / 1000); dist += v * dt; if (p > 0) Epos += p * dt; else Eneg += -p * dt; }
    const km = dist / 1000, idle = vs.filter((v) => v === 0).length;
    let kWh, co2;
    if (ev) { kWh = (Epos / 0.85 - 0.6 * Eneg * 0.85) / 3.6e6 + idle * 0.3 / 3600; co2 = kWh * 450 / km; }
    else { const MJ = Epos / 0.25 / 1e6 + idle * 1.2e3 / 1e6; kWh = MJ / 3.6; co2 = MJ * 73 / km; }
    return { ts: vs.map((_, i) => i), vs, P, km, kWh100: 100 * kWh / km, co2, Epos, Eneg };
  };
  // ---------------------------------------------------------------- 3.5 emulator of an integrated assessment model (GCAM-like toy)
  const iam = (p) => 1.6 * (0.38 + 0.62 * Math.exp(-p / 110)) + 0.12 * Math.sin(p / 35) * Math.exp(-p / 180); // Gt CO2 from transport in 2050 vs carbon price
  S.iam = iam;
  S.emulator = ({ n = 5, design = "uniform" }) => {
    const R = rng(131), ps = design === "uniform" ? lin(0, 400, n) : Array.from({ length: n }, () => 400 * R() * R()).sort((a, b) => a - b);
    const ys = ps.map(iam), mean = ys.reduce((a, b) => a + b, 0) / n, fit = gpFit(ps.map((p) => p / 100), ys.map((y) => y - mean), 0.9, 0.005, 0.5);
    const xs = lin(0, 400, 101), P = fit(xs.map((p) => p / 100)), mu = P.map((q) => q[0] + mean), tr = xs.map(iam);
    return { xs, mu, lo: mu.map((m, i) => m - 1.96 * P[i][1]), hi: mu.map((m, i) => m + 1.96 * P[i][1]), truth: tr, data: [ps, ys], err: rmse(mu, tr), hours: n * 6 };
  };
  // ---------------------------------------------------------------- 3.6 crowd fundamental diagram: physics-shaped vs unconstrained fit
  const weid = (r, v0 = 1.34, g = 1.913, rm = 5.4) => (r >= rm ? 0 : v0 * (1 - Math.exp(-g * (1 / r - 1 / rm))));
  S.crowdfit = ({ rmaxObs = 2.5, noise = 0.08 }) => {
    const R = rng(141), rd = Array.from({ length: 40 }, () => 0.3 + (rmaxObs - 0.3) * R()), vd = rd.map((r) => Math.max(0, weid(r) + noise * gauss(R)));
    const f3 = (r) => [1, r, r * r, r * r * r], c = lstsq(rd.map(f3), vd, 1e-8);
    let best = [1e9]; for (let v0 = 1.0; v0 <= 1.7; v0 += 0.02) for (let g = 1.0; g <= 3.0; g += 0.05) for (let rm = 4.0; rm <= 7.0; rm += 0.1) { const e = rd.reduce((s, r, i) => s + (weid(r, v0, g, rm) - vd[i]) ** 2, 0); if (e < best[0]) best = [e, v0, g, rm]; }
    const rs = lin(0.3, 5.4, 103), ext = rs.filter((r) => r > rmaxObs), poly = (r) => dot(f3(r), c), phy = (r) => weid(r, best[1], best[2], best[3]);
    return { rs, truth: rs.map((r) => weid(r)), poly: rs.map((r) => Math.max(-0.5, Math.min(2, poly(r)))), phys: rs.map(phy), data: [rd, vd], ePoly: rmse(ext.map(poly), ext.map((r) => weid(r))), ePhys: rmse(ext.map(phy), ext.map((r) => weid(r))), fit: best.slice(1) };
  };
  // ---------------------------------------------------------------- 3.7 digital twin of a signalised approach (model + data assimilation)
  S.twin = ({ noise = 3, gain = 0.5, fail = false }) => {
    const C = 90, G = 40, sat = 0.5, n = 60, R = rng(151); let q = 0, qm = 0, qt = 0; const tq = [], mq = [], twq = [], fc = [], ftrue = [];
    const lam = (k) => 0.18 + 0.1 * Math.sin(k / 9); // true arrivals per s
    const cyc = (q, l) => Math.max(0, q + l * C - sat * G);
    const arrivals = [];
    for (let k = 0; k < n; k++) { const l = lam(k) * (1 + 0.15 * gauss(R)); arrivals.push(l); q = cyc(q, l); tq.push(q); qm = cyc(qm, lam(k) * 0.85); mq.push(qm); }
    for (let k = 0; k < n; k++) { const pred = cyc(qt, lam(k) * 0.85); const ok = !(fail && k >= 25 && k < 45); const z = tq[k] + noise * gauss(R); qt = ok ? Math.max(0, pred + gain * (z - pred)) : pred; twq.push(qt); let f = qt; for (let j = 1; j <= 3; j++) f = cyc(f, lam(k + j) * 0.85); fc.push(f); ftrue.push(k + 3 < n ? tq[k + 3] : NaN); }
    const idx = ftrue.map((v, i) => (isFinite(v) ? i : -1)).filter((i) => i >= 0);
    return { ks: tq.map((_, i) => i), truth: tq, model: mq, twin: twq, errModel: rmse(mq, tq), errTwin: rmse(twq, tq), errFc: rmse(idx.map((i) => fc[i]), idx.map((i) => ftrue[i])) };
  };
  root.SCIML = S;
  if (typeof module !== "undefined") module.exports = S;
})(typeof window !== "undefined" ? window : globalThis);
