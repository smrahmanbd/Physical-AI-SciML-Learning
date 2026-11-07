"""Simulation challenges per module (rendered by assets/js/challenges.js; models call the shared cores in core.js).
Every challenge has a 'solution' checked at build time. All numbers are teaching toys."""


def S(id, label, mn, mx, val, step=1, unit="", digits=0, hint=None):
    d = dict(id=id, label=label, min=mn, max=mx, value=val, step=step, unit=unit, digits=digits)
    if hint: d["hint"] = hint
    return d


def TG(id, label, val=False):
    return dict(id=id, label=label, type="toggle", value=val)


def P(q, options, answer):
    return dict(q=q, options=options, answer=answer)


CH = {}
CH["1.1"] = [dict(title="Find the sweet spot", level="Core", icon="sliders", model="spectrum", metric="errOut", metricLabel="Error beyond the data", unit="", digits=3, view="line",
    fixed=dict(n=8), controls=[S("w", "Trust in physics", 0, 1, 0, 0.05, digits=2)], op="<=", target=0.13,
    goal="Measurements stop at t = 2. Choose how much to trust physics so that the error <b>beyond the data</b> is 0.13 or less.",
    predict=P("A pure data fit far beyond its data is usually…", ["Very accurate", "Badly wrong", "Exactly zero"], 1),
    hint="The polynomial explodes after t = 2; the physics model stays sensible.", explain="The data fit has no reason to behave beyond its data; the physics model, even with slightly wrong parameters, does.", solution=dict(w=1))]
CH["1.2"] = [dict(title="Accurate enough", level="Warm-up", icon="timer", model="ode", metric="err", metricLabel="Largest error", digits=3, view="line",
    fixed=dict(model="decay", k=0.5), controls=[S("dt", "Time step (s)", 0.02, 1.5, 1.0, 0.02, digits=2)], op="<=", target=0.02,
    goal="Solve dy/dt = −0.5 y with Euler's method. Choose the largest time step with a maximum error of <b>0.02</b> or less.",
    predict=P("Halving the step roughly…", ["Doubles the error", "Halves the error", "Removes the error"], 1),
    hint="Error is roughly proportional to the step.", explain="Euler is first-order: error ∝ Δt. About 0.2 s keeps it under 0.02.", solution=dict(dt=0.2)),
    dict(title="Tame the oscillator", level="Challenge", icon="pulse", model="ode", metric="err", metricLabel="Largest error", digits=3, view="line",
    fixed=dict(model="osc", k=0.5), controls=[S("dt", "Time step (s)", 0.005, 0.5, 0.2, 0.005, digits=3)], op="<=", target=0.1,
    goal="Euler adds energy to an oscillator. Find a step that keeps the error over 10 s at <b>0.1</b> or less.",
    hint="Much smaller steps are needed than for decay.", explain="Explicit Euler is a poor choice for oscillators; tiny steps or better solvers (RK4) are needed.", solution=dict(dt=0.015))]
CH["1.3"] = [dict(title="Enough neurons", level="Core", icon="cpu", model="nnfit", metric="err", metricLabel="Error on the true curve", digits=3, view="line",
    fixed=dict(target="sine"), controls=[S("units", "Hidden neurons", 1, 40, 1)], op="<=", target=0.05,
    goal="Find the smallest network that fits the smooth wave with an error of <b>0.05</b> or less.",
    predict=P("Can one tanh neuron fit a full wave?", ["Yes", "No"], 1), hint="Try 3 to 6 neurons.", explain="Each neuron is a soft step; a wave needs several of them.", solution=dict(units=5))]
CH["1.4"] = [dict(title="Escape the local minimum", level="Core", icon="arrows", model="gd", metric="gap", metricLabel="Above the best loss", digits=3, view="line",
    fixed=dict(steps=60), controls=[S("lr", "Learning rate", 0.01, 2, 0.05, 0.01, digits=2), S("mom", "Momentum", 0, 0.95, 0, 0.05, digits=2)], op="<=", target=0.08,
    goal="Gradient descent from w = −2 gets stuck in a shallow valley. Get within <b>0.08</b> of the best possible loss.",
    predict=P("Momentum acts like…", ["Friction", "A rolling ball's inertia", "A random jump"], 1), hint="Try momentum 0.9 with a small learning rate.", explain="Momentum carries the weight over the small bump into the deeper valley.", solution=dict(lr=0.1, mom=0.9))]
CH["1.5"] = [dict(title="Let physics fill the gap", level="Core", icon="flask", model="pinn", metric="errOut", metricLabel="Error beyond the data", digits=3, view="line",
    fixed=dict(nc=20, nd=6), controls=[S("loglam", "Physics weight (log₁₀ λ)", -4, 3, -4, 0.5, digits=1)], op="<=", target=0.03,
    goal="Six measurements in the first second. Choose a physics weight that keeps the error from 1 to 5 s at <b>0.03</b> or less.",
    predict=P("With almost no physics, the model after t = 1 is…", ["Constrained", "Free to wander"], 1), hint="Values around 10⁻² to 10¹ work; too large ignores the data.", explain="The equation residual at collocation points replaces the missing measurements.", solution=dict(loglam=0)),
    dict(title="Where to check the law", level="Challenge", icon="flask", model="pinn", metric="errOut", metricLabel="Error beyond the data", digits=3, view="line",
    fixed=dict(loglam=0, nd=6), controls=[S("nc", "Collocation points", 0, 40, 2)], op="<=", target=0.03,
    goal="With λ = 1, how few collocation points still give an error of <b>0.03</b> or less beyond the data?",
    hint="Too few leave gaps where the law is not checked.", explain="Collocation points must cover the domain densely enough for the physics to constrain the model everywhere.", solution=dict(nc=20))]
CH["1.6"] = [dict(title="Not too simple, not too wiggly", level="Core", icon="sliders", model="noise", metric="test", metricLabel="Error on new data", digits=3, view="line",
    fixed=dict(sigma=0.15, n=15), controls=[S("deg", "Polynomial degree", 0, 14, 13)], op="<=", target=0.1,
    goal="A degree-13 polynomial overfits 15 noisy points. Choose a degree with error on new data of <b>0.10</b> or less.",
    predict=P("Training error as degree rises…", ["Always falls", "Always rises"], 0), hint="Try 4 to 7.", explain="Test error is lowest at intermediate complexity.", solution=dict(deg=5))]
CH["1.7"] = [dict(title="Buy as few runs as possible", level="Core", icon="box", model="surrogate", metric="err", metricLabel="Surrogate error", digits=3, view="line",
    fixed=dict(eps=1.5, design="uniform"), controls=[S("n", "Expensive runs", 3, 16, 3)], op="<=", target=0.06,
    goal="Each run of the expensive model costs one minute. Use the fewest evenly spaced runs for a surrogate error of <b>0.06</b> or less.",
    hint="The error drops sharply between 4 and 6 runs.", explain="Six well-placed runs capture this smooth function; more runs give diminishing returns.", solution=dict(n=6))]
CH["1.8"] = [dict(title="Tune the filter", level="Core", icon="radar", model="kalman", metric="ratio", metricLabel="Filter error ÷ GPS error", digits=2, view="bars",
    fixed=dict(sd=8), controls=[S("logq", "Expected change in speed (log₁₀ q)", -2, 1.5, -2, 0.1, digits=1)], op="<=", target=0.7,
    goal="Tune the filter so that its error is at most <b>70%</b> of the raw GPS error.",
    predict=P("A filter that expects almost no change will…", ["Follow every GPS jump", "Lag behind the car"], 1), hint="Neither extreme works; try −0.5 to 0.5.", explain="The Kalman gain balances trust in the motion model against trust in GPS.", solution=dict(logq=-0.3))]
CH["2.1"] = [dict(title="Report an honest error", level="Core", icon="shield", model="split", metric="valErr", metricLabel="Validation error", unit=" veh/h", digits=0, view="bars",
    fixed=dict(frac=0.7), controls=[dict(id="mode", label="Split by time (instead of random hours)", type="toggle", value=False)], op=">=", target=200,
    goal="Choose a split whose validation error is <b>at least 200 veh/h</b>, i.e. closer to the real error next week (about 400).",
    predict=P("Random hourly splits make validation error look…", ["Better than reality", "Worse than reality"], 0), hint="Tick the time-based split.", explain="Splitting by time prevents the forecaster from peeking at neighbouring hours.", solution=dict(mode=True))]
CH["2.2"] = [dict(title="Train it well", level="Core", icon="cpu", model="pinntrain", metric="errOut", metricLabel="Error beyond the data", digits=3, view="line",
    fixed=dict(epochs=400), controls=[S("loglam", "Physics weight (log₁₀ λ)", -3, 2, -3, 0.5, digits=1), S("lr", "Learning rate", 0.005, 0.3, 0.005, 0.005, digits=3)], op="<=", target=0.03,
    goal="In 400 Adam epochs, reach an error beyond the data of <b>0.03</b> or less.",
    hint="Physics weight around 1 and a learning rate around 0.05.", explain="Both the balance of the loss and the optimiser settings matter.", solution=dict(loglam=0, lr=0.05))]
CH["2.3"] = [dict(title="Stay stable, go fast", level="Core", icon="timer", model="heat", metric="steps", metricLabel="Time steps", digits=0, view="line",
    fixed={}, controls=[S("r", "Stability number r", 0.1, 0.6, 0.1, 0.01, digits=2)], op="<=", target=100,
    goal="Use at most <b>100 time steps</b> without the solution blowing up (error must stay tiny).",
    predict=P("The explicit heat scheme is stable for…", ["r ≤ 0.5", "Any r", "r ≥ 1"], 0), hint="The largest stable r gives the fewest steps.", explain="r = 0.5 is the stability limit: the biggest steps that still work.", solution=dict(r=0.5))]
CH["2.4"] = [dict(title="Find exactly the right terms", level="Challenge", icon="search", model="sindy", metric="ok", metricLabel="Correct law found (1 = yes)", digits=0, view="bars",
    fixed=dict(noise=0.05), controls=[S("thr", "Sparsity threshold", 0.005, 1, 0.01, 0.005, digits=3)], op=">=", target=1,
    goal="With noise 0.05, find a threshold that recovers <b>exactly</b> the terms x and v.",
    hint="Too low keeps x³; too high deletes v. Try 0.15 to 0.25.", explain="The threshold must sit between the smallest true coefficient (0.3) and the largest spurious one.", solution=dict(thr=0.2))]
CH["2.5"] = [dict(title="Learn the operator", level="Core", icon="layers", model="operator", metric="err", metricLabel="Error on new inputs", digits=3, view="line",
    fixed=dict(m=24), controls=[S("ntrain", "Training pairs", 1, 16, 2)], op="<=", target=0.01,
    goal="Use the fewest training pairs that give an error below <b>1%</b> on new inputs.",
    hint="Inputs are built from 8 shapes.", explain="With 8 independent examples, the operator on this input family is fully determined.", solution=dict(ntrain=8))]
CH["2.6"] = [dict(title="Honest uncertainty", level="Core", icon="chart", model="gp", metric="cover", metricLabel="Truth inside the 95% band", digits=2, view="line",
    fixed=dict(n=8, sn=0.1), controls=[S("ell", "Length scale", 0.1, 3, 3, 0.05, digits=2)], op=">=", target=0.95,
    goal="A too-long length scale makes the GP overconfident. Choose ℓ so the band contains the truth at least <b>95%</b> of the time.",
    hint="Try values below 1.", explain="Shorter length scales let the band widen between observations.", solution=dict(ell=0.6))]
CH["2.7"] = [dict(title="Hybrid beats ML", level="Core", icon="layers", model="hybrid", metric="eHy", metricLabel="Hybrid error beyond the data", unit=" km/h", digits=1, view="line",
    fixed=dict(n=20), controls=[S("rmaxObs", "Highest density observed", 30, 130, 30, 5, unit=" veh/km")], op="<=", target=5,
    goal="How far up in density must data reach for the hybrid error beyond the data to fall to <b>5 km/h</b>?",
    hint="Try 50 to 70 veh/km.", explain="The hybrid needs enough data to learn the curvature the physics misses.", solution=dict(rmaxObs=60))]
CH["2.8"] = [dict(title="Hit the target coverage", level="Core", icon="shield", model="conformal", metric="cover", metricLabel="Coverage on new data (%)", digits=1, view="bars",
    fixed=dict(target=90), controls=[S("ncal", "Calibration examples", 10, 500, 10, 10)], op=">=", target=89,
    goal="Ask for 90% coverage. Use enough calibration examples to reach at least <b>89%</b> achieved coverage.",
    predict=P("With very few calibration examples, coverage is…", ["Exactly 90%", "Noisy around the target"], 1), hint="Try 100 or more.", explain="Conformal coverage holds on average; small calibration sets make it noisy.", solution=dict(ncal=100))]
CH["3.1"] = [dict(title="Locate the jam", level="Core", icon="radar", model="trafficpinn", metric="errEst", metricLabel="Estimation error", unit=" veh/km", digits=1, view="line",
    fixed=dict(ndet=2), controls=[S("gain", "Trust in detectors (gain)", 0, 1, 0, 0.05, digits=2)], op="<=", target=2.5,
    goal="With only two detectors, choose a gain that keeps the physics-informed error at <b>2.5 veh/km</b> or less.",
    predict=P("With gain 0, the model…", ["Never learns about the jam", "Follows detectors exactly"], 0), hint="Any moderate gain works.", explain="The LWR model carries the jam between detectors once it is told about it.", solution=dict(gain=0.5))]
CH["3.2"] = [dict(title="Stop the phantom jam", level="Core", icon="car", model="idm", metric="amp", metricLabel="Amplification", digits=2, view="line",
    fixed=dict(T=1.2), controls=[S("ctrl", "Controller (0 human, 1 ACC, 2 CACC)", 0, 2, 0)], op="<=", target=0.35,
    goal="Choose a controller that shrinks the braking wave to <b>0.35×</b> or less by the last car.",
    hint="Communication helps most.", explain="Cooperative ACC hears the leader's braking by radio and damps the wave.", solution=dict(ctrl=2)),
    dict(title="Human drivers, longer gaps", level="Challenge", icon="car", model="idm", metric="amp", metricLabel="Amplification", digits=2, view="line",
    fixed=dict(ctrl=0), controls=[S("T", "Time gap (s)", 0.6, 2.5, 0.8, 0.1, digits=1)], op="<=", target=1.0,
    goal="With human drivers, find the shortest time gap that makes the platoon string stable (<b>amplification ≤ 1</b>).",
    hint="Look between 1.2 and 1.8 s.", explain="Longer gaps buy stability but cost road capacity.", solution=dict(T=1.6))]
CH["3.3"] = [dict(title="Keep a safe gap", level="Core", icon="siren", model="ttc", metric="minTTC", metricLabel="Minimum time to collision", unit=" s", digits=2, view="line",
    fixed=dict(dv=8, react=1.5, decel=4), controls=[S("gap", "Initial gap (m)", 5, 80, 10)], op=">=", target=1.5,
    goal="Closing at 8 m/s with 1.5 s reaction. Choose the smallest gap that keeps minimum TTC at <b>1.5 s</b> or more.",
    predict=P("Doubling the gap roughly…", ["Doubles the TTC", "Halves it"], 0), hint="Try 25 to 35 m.", explain="Gap must cover the distance closed during reaction plus braking.", solution=dict(gap=30))]
CH["3.4"] = [dict(title="Drive greener", level="Core", icon="leaf", model="vsp", metric="co2", metricLabel="CO₂", unit=" g/km", digits=0, view="bars",
    fixed=dict(grade=0, aggr=1), controls=[TG("ev", "Electric car (450 g/kWh grid)")], op="<=", target=80,
    goal="Bring trip CO₂ to <b>80 g/km</b> or less.", hint="Switch vehicle.", explain="The electric car is about three times as efficient and recovers braking energy.", solution=dict(ev=True)),
    dict(title="Gentle driving", level="Warm-up", icon="leaf", model="vsp", metric="co2", metricLabel="CO₂", unit=" g/km", digits=0, view="bars",
    fixed=dict(grade=0, ev=False), controls=[S("aggr", "Driving style (acceleration ×)", 0.5, 2.5, 2.5, 0.1, digits=1)], op="<=", target=140,
    goal="In the petrol car, find a driving style that keeps CO₂ at <b>140 g/km</b> or less.", hint="Gentler acceleration.", explain="Hard acceleration means more energy is lost in braking.", solution=dict(aggr=1.0))]
CH["3.5"] = [dict(title="Buy GCAM runs wisely", level="Core", icon="globe", model="emulator", metric="err", metricLabel="Emulator error (Gt)", digits=3, view="line",
    fixed=dict(clustered=False), controls=[S("n", "Full model runs", 2, 12, 2)], op="<=", target=0.02,
    goal="Each run takes 6 hours. Use the fewest evenly spread runs for an emulator error of <b>0.02 Gt</b> or less.",
    hint="Try 4 to 6.", explain="A handful of well-placed runs is enough for a smooth response.", solution=dict(n=5))]
CH["3.6"] = [dict(title="Safe at high density", level="Core", icon="crowd", model="crowdfit", metric="ePoly", metricLabel="Cubic error beyond data", unit=" m/s", digits=2, view="line",
    fixed=dict(noise=0.08), controls=[S("rmaxObs", "Highest density observed", 1.2, 4.5, 1.5, 0.1, digits=1)], op="<=", target=0.3,
    goal="How dense must the observed crowd be before even a free cubic curve is within <b>0.3 m/s</b> beyond the data? (The physics-shaped fit is fine almost from the start.)",
    hint="Try 3.5 to 4.5.", explain="Free curves need data close to the conditions they predict; physics-shaped laws do not.", solution=dict(rmaxObs=4.0))]
CH["3.7"] = [dict(title="Tune the twin", level="Core", icon="layers", model="twin", metric="errTwin", metricLabel="Twin error", unit=" veh", digits=1, view="line",
    fixed=dict(noise=3, fail=False), controls=[S("gain", "Correction gain", 0, 1, 0, 0.05, digits=2)], op="<=", target=4,
    goal="Correct the queue model with detector data so the twin's error is <b>4 vehicles</b> or less.",
    hint="Anything from about 0.3 upwards.", explain="Assimilation pulls the drifting model back to reality each cycle.", solution=dict(gain=0.5))]
CH["3.8"] = [dict(title="Is physics worth it?", level="Core", icon="flag", model="hybrid", metric="eML", metricLabel="ML-only error beyond data", unit=" km/h", digits=1, view="line",
    fixed=dict(n=40), controls=[S("rmaxObs", "Highest density observed", 30, 130, 40, 5, unit=" veh/km")], op="<=", target=15,
    goal="An ablation: how much data range does the ML-only model need before its error beyond the data falls to <b>15 km/h</b>? (The hybrid gets under 9 km/h with data only to 60.) This is what the physics saves you.",
    hint="Look near the top of the range.", explain="Ablations show the value of physics: the hybrid reached this accuracy with far less data.", solution=dict(rmaxObs=120))]
