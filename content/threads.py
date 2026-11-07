"""Concept threads: the same idea met three times, once per go, each time deeper."""
THREADS = [
    dict(id="physdata", name="Physics plus data", icon="scale", sys="physics", stops=[
        ("1.1", "Physics extrapolates, data capture detail; SciML combines them.", "Where does a pure data model usually fail?", "Outside the range of its data."),
        ("2.7", "Hybrid models keep physics and learn only its error.", "What does a residual hybrid learn?", "The difference between data and the physics model."),
        ("3.4", "Road-load physics plus a learned correction estimates vehicle CO₂.", "What did the learned part correct in the emission model?", "Load-dependent engine efficiency missing from the constant-efficiency physics.")]),
    dict(id="equations", name="Differential equations", icon="pulse", sys="physics", stops=[
        ("1.2", "A differential equation is a rule for change; Euler steps follow it.", "What does one Euler step compute?", "y + Δt × slope."),
        ("2.3", "PDEs on grids need stability limits; PINNs need no grid.", "What is the stability limit for explicit heat diffusion?", "r = αΔt/Δx² ≤ 0.5."),
        ("3.1", "The LWR conservation law carries traffic jams between detectors.", "What does the LWR model conserve?", "Vehicles.")]),
    dict(id="residual", name="Physics-informed losses", icon="flask", sys="learn", stops=[
        ("1.5", "Add the equation residual at collocation points to the loss.", "What is a collocation point?", "A point where the equation residual is checked; no measurement needed."),
        ("2.2", "Build a PINN with autodiff and solve an inverse problem.", "How do you make a PINN estimate k?", "Make k a trainable parameter."),
        ("3.1", "Physics-informed deep learning reconstructs traffic from sparse sensors.", "What residual does PIDL for traffic use?", "The LWR conservation equation.")]),
    dict(id="learning", name="Learning and optimisation", icon="sliders", sys="learn", stops=[
        ("1.3", "Networks are sums of soft steps with adjustable weights.", "How many parameters has a 1–n–1 tanh network?", "3n + 1."),
        ("1.4", "Gradient descent with momentum or Adam minimises the loss.", "What does a too-large learning rate do?", "Overshoots and can diverge."),
        ("2.2", "Monitor data and physics losses separately while training.", "Physics loss stuck high: what do you change?", "Raise λ or add collocation points.")]),
    dict(id="overfit", name="Honest evaluation", icon="shield", sys="risk", stops=[
        ("1.6", "Only unseen data reveal overfitting.", "Which error reveals overfitting?", "Error on unseen data."),
        ("2.1", "Split time series by time to avoid leakage.", "Why does a random split flatter a forecaster?", "It can peek at neighbouring hours."),
        ("3.8", "Strong baselines, ablations and limits make results trustworthy.", "What does an ablation show?", "What each component, such as the physics term, contributes.")]),
    dict(id="uq", name="Uncertainty", icon="chart", sys="risk", stops=[
        ("1.7", "Surrogates should say where they are unsure.", "How does surrogate uncertainty help?", "It shows where to run the full model next."),
        ("2.6", "Gaussian processes give calibrated error bars.", "What does calibration mean for a 95% band?", "It contains the truth about 95% of the time."),
        ("2.8", "Conformal prediction guarantees average coverage.", "Does conformal coverage hold for every input?", "No, only on average over inputs.")]),
    dict(id="surrogates", name="Fast stand-ins", icon="box", sys="system", stops=[
        ("1.7", "A surrogate learns a slow model from a few runs.", "When does a surrogate pay off?", "When runs are expensive and many queries are needed."),
        ("2.5", "Neural operators learn whole solution maps.", "What does DeepONet's trunk net take as input?", "The query location."),
        ("3.5", "Emulators make GCAM policy studies feasible.", "How does active learning choose the next GCAM run?", "Where the emulator is most uncertain.")]),
    dict(id="discovery", name="Discovering laws", icon="search", sys="data", stops=[
        ("1.6", "Physics forbids the wiggles that noise creates.", "Why is physics a regulariser?", "It penalises shapes real systems cannot take."),
        ("2.4", "SINDy finds short equations by sparse regression.", "What does the SINDy threshold do?", "Removes small coefficients to keep the law short."),
        ("3.6", "Physics-shaped crowd laws extrapolate to dangerous densities.", "How many parameters does Weidmann's law have?", "Three: v₀, γ and ρ_max.")]),
    dict(id="estimation", name="Sensing and estimation", icon="radar", sys="data", stops=[
        ("1.8", "The Kalman filter predicts with physics and corrects with data.", "What sets the Kalman gain?", "The relative uncertainty of model and measurement."),
        ("3.1", "Nudging a traffic model towards detectors estimates density everywhere.", "Why does interpolation miss jams?", "Jams have sharp moving fronts."),
        ("3.7", "Digital twins assimilate live data continuously.", "How does a twin survive a sensor failure?", "It keeps running its physics model.")]),
    dict(id="physai", name="Physical AI", icon="car", sys="apply", stops=[
        ("1.8", "Physical AI loops: sense, estimate, decide, act.", "Name the four steps.", "Sense, estimate, decide, act."),
        ("3.2", "Automated and cooperative vehicles can damp braking waves.", "What is string stability?", "Disturbances shrink along a platoon."),
        ("3.7", "Twins test actions before they reach the real system.", "What makes a twin more than a simulation?", "Live updating and a link to decisions.")]),
    dict(id="safety", name="Safety and rare events", icon="siren", sys="risk", stops=[
        ("1.8", "Physical AI must be safe when wrong.", "Name one safety standard for automated vehicles.", "ISO 26262 or ISO 21448."),
        ("3.3", "Conflicts measured by TTC stand in for rare crashes.", "Define time to collision.", "Gap divided by closing speed."),
        ("3.8", "Verifying learned controllers and modelling rare events are open problems.", "What does a safety filter do?", "Overrides actions that would break safety constraints.")]),
]
