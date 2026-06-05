---
layout: default
title: Connecting to the Paper Theory
---

# Connecting to the Paper Theory

Our empirical findings validate the core theorems and complexity claims made in the paper *"A Trace-Language Theory of Agents"*. Here is how the mathematical constructs in the paper directly correspond to the behavior observed in our experiments.

---

## 1. Theorem 2: Regular Conformance Closure

The central formal claim of the paper is **Theorem 2**:
> Let $\mathcal{G}$ be an agent with $L(\mathcal{G})$ in Chomsky class $\mathcal{L}_i$ for some $i \in \{0, 1, 2, 3\}$. Let $\mathcal{V}$ be an agent with $L(\mathcal{V}) \in \mathcal{L}_3$ (a regular language). Define the validated composition $\mathcal{G} \parallel \mathcal{V}$ as the trace filter whose accepted traces are exactly those emitted by $\mathcal{G}$ and accepted by $\mathcal{V}$'s DFA. Then:
> 
> $$L(\mathcal{G} \parallel \mathcal{V}) = L(\mathcal{G}) \cap L(\mathcal{V}) \in \mathcal{L}_i$$

### Empirical Validation
In our main experiment:
1. The generator $\mathcal{G}$ is an unrestricted Turing-complete machine (emulating a Type-0 LLM agent), prone to executing arbitrary steps and introducing code bugs.
2. The verifier $\mathcal{V}$ is implemented as a simple DFA transition matrix (`trace_matrix.csv`) and deterministic data validators, making it strictly **Type-3 (regular)**.
3. Checking verifier conformance runs in linear time $O(n)$ relative to the trace length and consumes negligible resources ($O(1)$ space).

Our run metrics confirmed this:
* **DFA Verification Latency**: $67.5 \text{ ms}$ average overhead.
* **LLM Judge Verification Latency**: $14,650.0 \text{ ms}$ average.
* **Token Cost**: The DFA consumed **0 tokens**, while the LLM Judge consumed **11,720 tokens** per trial.

This shows that constraining the generator using a Type-3 verifier does not elevate the complexity of the consumer side, preserving a bounded, linear-time verification budget.

---

## 2. Bounding the Expressive Power

The paper argues that when a Type-0 generator is bound by a Type-3 verifier, it prevents the generator's execution trace from drifting into "pathological corners of $\Sigma^*$ that the consumer was not designed to cover."

In our **Ablation 1 (Verifier Components)**, when structural DFA checks were disabled (representing the generator running without regular language bounds):
* Under a 15% transition error rate, the agent got stuck or generated out-of-order calls (e.g. attempting to train a model before datasets were loaded or preprocessed).
* This led to a **0.0% completion/success rate** for both the Control and Data-Only groups.
* In contrast, when the regular language constraints were active (Full Verifier), the agent was successfully bound, yielding a **49.5% average score**.

This shows that the regular-language envelope is not just a theoretical wrapper, but a necessary operational boundary to keep Type-0 generators convergent.

---

## 3. Auditable Verification vs. Black-Box Judges

Section VI-D of the paper explains why an Aho-Corasick or DFA verifier is superior to a black-box LLM Judge:
1. **Class Containment**: An LLM-as-judge is not a transparent regular recogniser, losing the $O(n)$ complexity guarantee.
2. **Auditability**: A DFA is mechanically derived, finite, and version-controlled.
3. **Robustness**: A DFA "cannot be talked into anything; it either matches or it does not."

Our experiments directly illustrated this:
* The LLM Judge suffered from **false negatives**, failing to catch buggy predictions or malformed CSV lengths, leading to **1.2 undetected errors** per run and dropping overall accuracy to **35.2%**.
* The DFA Verifier caught **100% of errors (0.00 undetected errors)**, guiding the agent to repair every mistake.
