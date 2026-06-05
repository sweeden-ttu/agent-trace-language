# A Trace-Language Framework for Agent Verification

This repository implements the **Trace-Language Verification (TLV) Framework** for the paper *"A Trace-Language Framework for Agent Verification"* (AAAI-27).

The core thesis: **agent behaviour can be modelled as a trace language, and a regular (Type-3) verifier can constrain a more expressive generator while remaining computationally tractable.** Intersecting a generator's trace language with a regular verifier language preserves the generator's Chomsky class, and conformance checking runs in linear time on the verifier side.

## Paper Structure

The paper follows a six-section narrative:

1. **Introduction** — three claims, contributions, related work
2. **Trace Language Model** — formal definitions of trace, trace language, trace equivalence, Theorem 2 (regular conformance closure)
3. **Generator–Verifier Architecture** — G‖V binding, Algorithm 1 (recursive enumeration), Aho–Corasick DFA verifier, projected sub-agent roles
4. **Experimental Setup** — MLE-bench Spaceship Titanic, hardware, start language, 4 pre-registered probes (P1–P4)
5. **Results** — probe outcomes, controlled ablation (Exp 1), class-hypothesis signature, comparison with baselines
6. **Design Implications and Framework** — three design principles, reusable 4-stage verification pipeline (Trace Recorder → DFA Verifier → Projection Engine → Agent Analysis)
7. **Discussion and Limitations** — limitations, threats to validity, threats to theoretical validity, future work

Extended theory (Chomsky classification, indexed grammars, Hoare/LTL formalism, multi-agent systems, experiments 2–5) is archived in the `supplementary/` directory.

## The 6 Experiments

All six experiments have runnable Python scripts with pre-computed results:

### Experiment 1: Verifier Ablation Study
`src/run_experiments.py` + `src/ablation.py`

Compares three conditions across 3 ML tasks (spaceship_titanic, wine_quality, synthetic_classification) with 10 trials each:
- **Control (G)**: generator only, no verifier
- **Treatment A (G ‖ V_DFA)**: generator bound by DFA + data verifier
- **Treatment B (G ‖ V_LLM)**: generator bound by simulated LLM judge

The DFA verifier raises mean task score from 35.2% to 57.8% while eliminating undetected trace faults (0.00 vs 1.77), at milliseconds vs seconds for the LLM judge.

### Experiment 2: Chomsky Class Compression
`src/run_exp2_compression.py`

Three agent architectures (ReAct, Tree Search, Planner-Executor) with traces projected onto a shared core alphabet. Computes pairwise edit-distance similarity. Demonstrates that different internal architectures collapse to equivalent trace languages under projection.

### Experiment 3: Emergent Sub-Agent Discovery
`src/run_exp3_emergence.py`

Applies K-Means clustering to a transition-count matrix from 100 simulated agent runs. Discovers 3 emergent role clusters without manual role engineering.

### Experiment 4: Trace-Language Verification Analyzer
`src/run_exp4_analyzer.py`

Analyses execution traces for alphabet size, cycle count, stack nesting depth, and heuristically predicts Chomsky class (Type-3 regular linear, Type-3 regular with loops, or Type-2 context-free).

### Experiment 5: Safety-Critical Verification
`src/run_exp5_safety.py`

A safety DFA verifier intercepts forbidden operations (`drop_table`, `delete_database`, `send_money`) and forbidden sequences. Achieves 100% interception rate (3/3 violations blocked).

### Experiment 6: NeuroGolf 2026 — Trace-Language in Practice
`experiment_6/build_and_submit.py`

A proof-of-concept applying the trace-language framework to a live Kaggle competition (NeuroGolf 2026). By analyzing execution logs from top leaderboard notebooks, we reverse-engineered the trace language — the sequence of operations and keywords that characterize winning submissions. A DFA verifier (13 states, 76 transitions, 27 OpSymbols) was embedded directly into a competition notebook to enforce this structure:

1. **Log Analysis**: Extracted operation patterns from 18+ top-scoring Kaggle kernels (6154.71, 6411.7, 6663.23, etc.), identifying the real-world pipeline: dataset discovery → floor loading → task analysis → ONNX construction → optimization → verification → costing → blending → packaging → submission.
2. **DFA-Guided Generation**: The verifier checked that every generated notebook step followed the correct architectural flow and contained essential keywords (fp16, dim_scrub, sha256, blend, etc.) in the proper pipeline phase.
3. **Result**: **50% improvement** in competition score (2739.27 → 4127.12). The DFA caught structural errors in the blending pipeline — ensuring bundle models from 4 public datasets were correctly discovered and selected, replacing the identity fallback solvers for 398/400 tasks.

This demonstrates the trace-language theory in practice: an LLM-generated notebook, when bound by a regular (Type-3) DFA verifier derived from real-world traces, produces results that follow the proven architectural patterns of top performers. The verifier cannot understand "concepts" — it checks keyword presence and operation ordering — yet this lightweight structural enforcement was sufficient to guide the generator toward a competitive submission.

## Repository Structure

```
├── experiment_6/          # NeuroGolf 2026: TLV in practice (Kaggle competition)
│   ├── build_and_submit.py        # Notebook generator with embedded DFA verifier
│   ├── neurogolf-2026-trace-language.ipynb  # Generated competition notebook
│   └── kernel-metadata.json       # Kaggle dataset sources
├── src/                  # Experiment runner scripts (Python)
│   ├── run_all_experiments.py   # Master orchestrator for all 5 experiments
│   ├── run_experiments.py       # Experiment 1: Verifier Ablation
│   ├── run_exp2_compression.py  # Experiment 2: Chomsky Compression
│   ├── run_exp3_emergence.py    # Experiment 3: Emergent Discovery
│   ├── run_exp4_analyzer.py     # Experiment 4: TLV Analyzer
│   ├── run_exp5_safety.py       # Experiment 5: Safety Verification
│   ├── ablation.py              # Ablation studies (verifier components, retry budget)
│   ├── benchmark.py             # ML task benchmark generators
│   ├── generator.py             # Agent generator simulation
│   └── verifier.py              # DFA, data, and runtime verifiers
├── framework/            # Reusable TLV library modules
│   ├── dfa_verifier.py          # Generic DFA implementation
│   ├── language_analysis.py     # Trace analysis utilities
│   ├── projection.py            # Trace projection functions
│   └── trace_recording.py       # Trace recording utilities
├── tests/                       # Unit tests
│   └── test_verifier.py         # Verifier unit tests
├── data/                        # Pre-computed experiment outputs
│   ├── results_raw.csv
│   ├── results_summary.csv
│   ├── exp2_similarity.csv
│   ├── exp3_clusters.csv
│   ├── exp4_classifications.json
│   ├── exp5_safety.csv
│   ├── ablation_results_verifier.csv
│   ├── ablation_results_budget.csv
│   └── trace_matrix.csv
├── docs/                        # GitHub Pages documentation
│   ├── index.html
│   ├── experiments.html
│   ├── how_they_were_run.html
│   └── paper_tie_in.html
├── sec/                         # LaTeX paper sections
├── supplementary/               # Archived extended theory
├── Makefile                     # LaTeX build targets
└── main.tex                     # Paper entry point
```

## Building the Paper

```bash
make pdf        # Full build: pdflatex → bibtex → pdflatex → pdflatex
make review     # Build with empty acknowledgments (double-blind)
make pages      # Count content pages (excludes references)
make count      # Word count estimate
```

## Documentation Site

GitHub Pages: https://sweeden-ttu.github.io/agent-trace-language/

## Reproducing Experiments

All experiments can be run from the repo root:

```bash
python src/run_all_experiments.py          # Run all 5 experiments
python src/run_experiments.py              # Experiment 1 only
python src/run_exp2_compression.py         # Experiment 2 only
python src/run_exp3_emergence.py           # Experiment 3 only
python src/run_exp4_analyzer.py            # Experiment 4 only
python src/run_exp5_safety.py              # Experiment 5 only
python src/ablation.py                     # Ablation studies
```


## Experiment 6

This is an iterative experiment not included in the original paper, being used to slowly climb the submission latter of the Neuro Golf competition in Kaggle. As of day 1 it climbed from a position of 590 out of 5,877 Entrants placing it in the top 10% of all entries. https://www.kaggle.com/competitions/neurogolf-2026/leaderboard#

This experiment is ongoing up until the submission deadline for the AAAI competition.  The neurogolf files represent its submission and the DFA verifier scans the log outputs and cell outputs for expected changes each time an architectural change is made to the pipeline. The producer is OpenCode BigPickle model.