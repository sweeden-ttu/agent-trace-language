---
layout: default
title: The 5 Core Experiments
---

# The 6 Core Experiments

To test the validity of the **Trace-Language Theory of Agents**, we describe six core experiments. These range from immediate verifier ablations to sub-agent discovery, safety-critical proofs, and a real-world Kaggle competition application.

---

## 1. Verifier Ablation Study (Empirically Validated)

* **Hypothesis**: Intersecting a Goal-Driven generator ($G$) with a regular Data-Driven verifier ($V_{DFA}$) will yield higher task accuracy and trace validity at a lower cost than using an LLM Judge ($V_{LLM}$) or running without validation ($G$ alone).
* **Setup**:
  * **Control ($G$)**: The generator runs freely, outputting steps and code. No verifier intercepts errors.
  * **Treatment A ($G \parallel V_{DFA}$)**: A DFA verifier reads trace transitions from `trace_matrix.csv` and physical checks validate datasets, code formatting, and prediction schemas. When checks fail, specific error feedback triggers code repairs.
  * **Treatment B ($G \parallel V_{LLM}$)**: A simulated LLM Judge checks steps and logs, incurring API token costs and exhibiting classification noise (false positives/negatives).
* **Key Metrics**:
  * $\text{Valid Trace Rate} = \frac{\text{Accepted Traces}}{\text{Total Traces}}$
  * Average Repairs (retries before success)
  * Estimated API Token Cost & Latency
  * Leaderboard Score (Inference accuracy on test sets)

---

## 2. Chomsky Class Compression

* **Hypothesis**: Radically different internal agent architectures collapse to identical or equivalent trace languages when executing similar objectives. Let $A_1 \equiv_\tau A_2$ if $L(A_1) = L(A_2)$.
* **Setup**:
  * Implement three different agent architectures:
    1. **Pure ReAct (Type-3/2)**: Reacting to environment feedback step-by-step.
    2. **Monte Carlo Tree Search / MCTS (Type-2/1)**: Expanding tree states for planning.
    3. **Planner + Executor (Type-0)**: Creating structured JSON plans and executing them.
  * Run all three agents on identical tabular ML tasks and record their traces.
  * Project traces onto a shared operation alphabet $\Sigma_{common}$.
  * Compute trace distances $d(L_1, L_2)$ using edit distance, prefix overlap, and automata state similarity.
* **Goal**: Show that despite differing internal complexity, the emitted behavior collapses to a common trace language.

---

## 3. Emergent Sub-Agent Discovery

* **Hypothesis**: Sub-agent roles (e.g. planner, critic, researcher, dev) emerge automatically from observed traces and do not need to be designed manually.
* **Setup**:
  * Collect extensive execution trace strings from multiple runs of $L(G \parallel V)$.
  * Build a state-transition probability graph where nodes are operations (e.g., `load_data`, `preprocess_data`, `train_model`) and edge weights represent transition frequencies.
  * Run community detection algorithms (e.g., **Louvain Modularity**, **Spectral Clustering**) on the transition graph.
* **Expected Outcome**: Discovered clusters correspond directly to logical sub-agent behaviors (e.g., a "feature-engineering" sub-agent, a "model-training" sub-agent) without any manual role designation.

---

## 4. Trace-Language Verification Framework (TLV)

* **Goal**: Define and publish a generic, reusable software architecture implementing the Trace-Language theory.
* **Core Components**:
  1. **Trace Recorder**: A lightweight logger capturing serializable symbols representing agent tool calls.
  2. **Projection Engine**: Implements the projection function $\pi_{\Sigma'}(\tau)$ to map full traces onto specific sub-alphabets of interest.
  3. **DFA Validator**: Standardizes cross-tab CSV files (like `trace_matrix.csv`) and executes linear-time $O(n)$ state checks.
  4. **Language Classifier**: Automatically detects stack patterns or linear boundaries to estimate if a sub-trace language falls in Type-3, Type-2, Type-1, or Type-0 classes.

---

## 5. Safety-Critical Verification

* **Hypothesis**: A regular verifier can enforce absolute compliance with safety constraints on an unrestricted Type-0 producer.
* **Setup**:
  * Define a set of unsafe action sequences (e.g., calling `delete_database` immediately after `read_config` without checking credentials).
  * Build a DFA verifier $V_{safe}$ that rejects any trace containing these sequences.
  * Show that the intersection $L(G \parallel V_{safe}) \cap L(\text{Hazards}) = \emptyset$ is decidable in linear time.
* **Compelling Claim**: We can provide formal guarantees on LLM safety by intercepting the trace emissions before they are executed in the physical environment.

---

## 6. NeuroGolf 2026 — Trace-Language in Practice (Empirically Validated)

* **Hypothesis**: A DFA verifier derived from execution logs of top-performing agents can guide a generator to produce competitive results, even when the generator is an LLM that cannot understand "concepts" — it only matches keywords and operation order.
* **Setup**:
  * Analyzed execution logs from 18+ top-scoring Kaggle kernels on the NeuroGolf 2026 competition (ONNX-based ARC-AGI solver construction).
  * Extracted the real-world pipeline trace language: 27 operation symbols covering dataset discovery, floor loading, task analysis, ONNX construction, optimization (graph rewrite, dim scrub, fp16 surgery), verification, costing, blending, packaging, and submission.
  * Built a DFA verifier (13 states, 76 transitions) enforcing this structure, with keyword coverage (29 terms) checking that essential operations appear in the correct pipeline phase.
  * Embedded the verifier into a competition notebook generator — the LLM produces notebook cells, and the DFA validates the resulting trace.
* **Key Metrics**:
  * Competition score improvement: **2739.27 → 4127.12** (+50%)
  * Tasks covered by pre-built bundles: 2/400 → 398/400 (DFA caught the blend logic inversion)
  * Submission size: 0.74 MB (under 1.44 MB limit, thanks to raw-bytes optimization)
  * All DFA checks passing across build, blend, and final submit pipelines
* **Significance**: This experiment demonstrates that the trace-language theory works in practice. The DFA verifier — a simple Type-3 automaton with no semantic understanding — was sufficient to guide an LLM generator toward a competitive submission by enforcing the architectural patterns observed in top-performing notebooks.
