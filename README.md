# A Trace-Language Theory of Agents: Experiments & Verification

This repository implements the formal verification runtime architecture and empirical validation suite for **A Trace-Language Theory of Agents** (as detailed in the AIAA Conference Paper). 

The core thesis of the paper is that **a Type-3 regular language verifier can mathematically constrain the behavior of a more expressive Type-0 generator while preserving task performance, eliminating trace errors, and optimizing runtime costs.**

---

## The 5 Core Experiments

Here is the clean description of the five experiments proposed to validate and extend the trace-language theory.

### 1. Verifier Ablation Study (Empirically Implemented)
* **Goal**: Validate that intersecting a Goal-Driven generator ($G$) with a regular Data-Driven verifier ($V_{DFA}$) improves validation rate and task accuracy while reducing costs relative to an LLM Judge.
* **Methodology**: 
  * **Control**: Generator ($G$) only, running with no constraints.
  * **Treatment A**: Generator bound by DFA and data constraints ($G \parallel V_{DFA}$).
  * **Treatment B**: Generator bound by a probabilistic LLM Judge ($G \parallel V_{LLM}$).
* **Empirical Evidence**: Successfully implemented in this repository. View details in the [Jekyll Docs Site](docs/index.md) or run the experiment script directly.

### 2. Chomsky Class Compression
* **Goal**: Prove that radically different agent architectures collapse to identical or equivalent trace languages.
* **Methodology**: 
  * Deploy three distinct agent structures: **Pure ReAct**, **MCTS/Tree Search**, and **Planner + Executor** on identical tasks.
  * Project their execution traces into canonical operation alphabets ($\Sigma'$).
  * Measure language similarity distance $d(L_1, L_2)$ using edit distance, prefix overlap, and DFA equivalence algorithms.

### 3. Emergent Sub-Agent Discovery
* **Goal**: Validate that sub-agent roles (e.g., Planner, Reviewer, Trainer) emerge automatically from the projection of traces onto specific alphabets without explicit labels.
* **Methodology**: 
  * Collect trace languages $L(G \parallel V)$ over many task runs.
  * Construct transition probability graphs for operations.
  * Apply community detection algorithms (Spectral clustering, Louvain modularity, Markov clustering) to identify clusters representing coherent agent roles.

### 4. Trace-Language Verification Framework
* **Goal**: Build a reusable, general-purpose software runtime architecture for trace verification.
* **Architecture**:
  ```
  [Goal Generator] ---> (Trace Recorder) ---> [Projection Engine] ---> [DFA Verifier] ---> [Accept/Reject]
  ```
  * **Trace Recorder**: Serializes emitted symbols.
  * **Projection Engine**: Maps complex traces to sub-alphabets $\pi_{\Sigma'}(\tau)$.
  * **DFA Validator**: Decides membership in $L(V)$ in $O(n)$ time.
  * **Language Analyzer**: Automatically classifies the Chomsky-class of the observed traces.

### 5. Safety-Critical Verification
* **Goal**: Demonstrate that a Type-3 regular verifier can guarantee compliance with strict safety constraints on an unrestricted (Type-0) generator.
* **Methodology**: 
  * Define forbidden action sequences representing hazards (e.g., `delete_database`, `drop_table`, `send_money`).
  * Compile these safety rules into a regular verifier DFA $V_{safe}$.
  * Assert that $L(G \parallel V_{safe}) \cap L(Hazards) = \emptyset$ is decidable in linear time.

---

## Repository Structure

- `data/`: Transition matrix and experimental outputs.
  - [trace_matrix.csv](file:///Users/sweeden/agent-trace-language/agent-trace-language/data/trace_matrix.csv): Human-readable cross-tab transition matrix representing the DFA.
- `src/`: Python source code.
  - [verifier.py](file:///Users/sweeden/agent-trace-language/agent-trace-language/src/verifier.py): Implements the structural DFA and physical data constraint checks.
  - [generator.py](file:///Users/sweeden/agent-trace-language/agent-trace-language/src/generator.py): Implements simulated agent loops and code repair logic.
  - [benchmark.py](file:///Users/sweeden/agent-trace-language/agent-trace-language/src/benchmark.py): Sets up synthetic datasets and Kaggle-like evaluation contexts.
  - [run_experiments.py](file:///Users/sweeden/agent-trace-language/agent-trace-language/src/run_experiments.py): Executes the Control vs. Treatment A vs. Treatment B trials.
  - [ablation.py](file:///Users/sweeden/agent-trace-language/agent-trace-language/src/ablation.py): Executes verifier component and retry budget ablation sweeps.
- `docs/`: Jekyll documentation site containing deep dives, results, and mathematical proofs.

---

## Getting Started

### 1. Run Unit Tests
To test the verifiers:
```bash
python3 -m unittest tests/test_verifier.py
```

### 2. Run Experiments
To replicate the main experiment (10 trials across Control, DFA, and LLM Judge):
```bash
PYTHONPATH=. python3 src/run_experiments.py
```

### 3. Run Ablations
To run verifier components and retry budget sweeps:
```bash
PYTHONPATH=. python3 src/ablation.py
```

### 4. Build Jekyll Site Locally
To run the documentation site:
```bash
cd docs
jekyll serve
```
The documentation is pre-configured for MathJax rendering of LaTeX equations.
