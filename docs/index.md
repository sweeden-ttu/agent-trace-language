---
layout: default
title: A Trace-Language Theory of Agents
---

# A Trace-Language Theory of Agents

Welcome to the documentation site for the **Trace-Language Verification (TLV) Framework** and empirical study, verifying the concepts from the paper *"A Trace-Language Theory of Agents: Goal-Driven Type-0 Producers Bounded by Data-Driven Type-3 Consumers"*.

This framework explores how we can model, analyze, and verify complex LLM agents by observing the finite sequences (traces) of operations they emit.

---

## The Core Concept

Historically, agent architectures are compared informally. This project introduces a formal, language-theoretic boundary:
* **The Producer ($G$)**: The agent loop, modeled as an unrestricted **Type-0** machine (typically an LLM wrapper). It has the freedom to compose and execute arbitrary code and transitions.
* **The Consumer / Verifier ($V$)**: A deterministic finite automaton (**DFA**, **Type-3**), representing the structural rules of the environment and strict data constraints.

$$L(G \parallel V) = L(G) \cap L(V)$$

By intersecting the complex language of $G$ with the regular language of $V$, **Theorem 2 (Regular Conformance Closure)** ensures that the composition remains decidable on the verifier's side in linear time $O(n)$ and $O(1)$ space, keeping the overall verification bounds robust.

---

## Paper Structure (6 Sections)

The paper follows a six-section structure:

1. **Introduction** -- Three claims, contributions, related work
2. **Trace Language Model** -- Formal definitions, Theorem 2 (closure)
3. **Generator--Verifier Architecture** -- G\|V binding, Algorithm 1, Aho--Corasick, projected roles
4. **Experimental Setup** -- Benchmark, probes, reproducibility
5. **Results** -- Probe outcomes, ablation (Exp 1), class signature
6. **Discussion** -- Limitations, threats, future work

Extended theory (Chomsky classification, indexed grammars, Hoare/LTL formalism, multi-agent systems, additional experiments) is archived in the [`supplementary/`]({{ site.baseurl }}/supplementary/) directory.

---

## What is in this Documentation?

Explore the different sections of this documentation site using the navigation above:

### 1. [The 5 Experiments](experiments.html)
A clean overview of the 5 core experiments proposed to test and validate this trace-language theory.

### 2. [Running Details & Results](how_they_were_run.html)
A deep dive into how we constructed our local ML task sandbox runner, synthetic dataset generators, and the exact metric outputs of our Control vs. DFA vs. LLM Judge experiments and ablation studies.

### 3. [The Paper Connection](paper_tie_in.html)
An explanation of how the empirical findings directly validate the paper's mathematical definitions and theorems.

---

<div style="text-align: center; margin-top: 2rem;">
  <a href="experiments.html" class="btn">Explore the Experiments</a>
</div>
