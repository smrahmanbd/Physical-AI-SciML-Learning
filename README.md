# Physical AI and Scientific Machine Learning in three goes

An open, interactive course on scientific machine learning (SciML) and Physical AI, built like [GCAM-Learning](https://github.com/smrahmanbd/GCAM-Learning) and [Crowd-Dynamics-Learning](https://github.com/smrahmanbd/Crowd-Dynamics-Learning). You go through the whole subject three times, each time in more depth.

| Go | Level | Modules | Focus |
|---|---|---|---|
| 1 · Foundations | Introductory | 8 | What SciML and Physical AI are; differential equations; neural networks; loss, gradients and autodiff; physics-informed learning; noise and overfitting; surrogates; the sense–estimate–decide–act loop |
| 2 · Build and Implement | Intermediate | 8 | Step by step: workflow and leakage-free splits; a PINN from scratch, including an inverse problem; PDE solvers and PINNs; SINDy and neural ODEs; neural operators (DeepONet); Gaussian processes; hybrid models; conformal prediction and deployment |
| 3 · Research Frontier: Transportation | Advanced | 8 | Physics-informed traffic state estimation; car following and automated vehicles; road safety and conflicts; vehicle energy and emissions; GCAM emulators; crowd dynamics; digital twins; the research frontier and responsible SciML |

Every module page has:
- an animated figure and an interactive diagram with a guided tour
- a simulator to explore, plus simulation challenges
- Python that runs in the browser (Pyodide)
- spoken narration in English and Arabic
- a zooming mind map with icons and images
- a memory-palace stop and a quiz

The site also includes go-level mind maps, a question bank with spaced repetition, a concept spiral of 11 threads, a method atlas of 7 SciML families, a toolkit, a glossary, PDF handbooks and lab kits.

## Build

```bash
cd content && python3 make.py && python3 validate.py m*.json && cd ..
python3 content/figs.py          # animated figures
python3 content/handbooks.py     # handbooks, mind-map PDFs, lab kits (needs Playwright)
python3 build.py                 # static site
python3 -m http.server           # open http://localhost:8000
```

## Labs

- `labs/go2` and `labs/go3` hold the scripts behind each module; each prints the numbers quoted on its page.
- Files ending in `_torch.py` need PyTorch. Everything else needs only NumPy and runs in the browser.
- `assets/js/core.js` holds the numerical cores shared by all simulators and challenges.
- All data are synthetic teaching data with fixed seeds.

## Note

This course is for teaching. The simulators illustrate methods and are not engineering or safety tools.
