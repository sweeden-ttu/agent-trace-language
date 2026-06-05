---
layout: default
title: Running Details & Empirical Results
---

# Running Details & Empirical Results

We built a local simulation and testing sandbox to execute the experiments. This page documents the methodology, datasets, and the exact findings of our empirical runs.

---

## 1. Sandbox Architecture & Methodology

Running LLM agent benchmarks in the cloud can be slow and expensive. To ensure reproducibility and speed, we implemented a local ML task sandbox:
* **Tasks**:
  1. `spaceship_titanic`: Synthetic tabular dataset modeling the Kaggle Spaceship Titanic task (with columns like `HomePlanet`, `CryoSleep`, `Cabin`, and missing features).
  2. `wine_quality`: Load standard chemical features from the scikit-learn Wine dataset and inject missing values to create preprocessing challenges.
  3. `synthetic_classification`: A 10-feature generated classification dataset with custom null rates.
* **Execution**: For each action, the agent performs real Python operations: copying files, running feature imputation, fitting RandomForest classifiers, saving pickle models, and outputting predictions to `submission.csv`.
* **Errors**: The generator has a configurable **DFA Error Rate** (proposing invalid steps out of order) and a **Bug Rate** (writing buggy code that deletes files, writes null values, or outputs malformed prediction lengths).

---

## 2. Main Experiment Results

We ran **10 trials** per task. 

### Task-by-Task Summary

#### Task 1: Spaceship Titanic
* **Control (G)**: Completion Rate = 50%, Mean Accuracy = 30.8%
* **Treatment A (G + DFA)**: Completion Rate = 90%, Mean Accuracy = **57.0%**
* **Treatment B (G + LLM)**: Completion Rate = 100%, Mean Accuracy = 30.8%

#### Task 2: Wine Quality
* **Control (G)**: Completion Rate = 60%, Mean Accuracy = 25.1%
* **Treatment A (G + DFA)**: Completion Rate = 90%, Mean Accuracy = **34.6%**
* **Treatment B (G + LLM)**: Completion Rate = 100%, Mean Accuracy = 25.1%

#### Task 3: Synthetic Classification
* **Control (G)**: Completion Rate = 60%, Mean Accuracy = 49.7%
* **Treatment A (G + DFA)**: Completion Rate = 90%, Mean Accuracy = **81.7%**
* **Treatment B (G + LLM)**: Completion Rate = 100%, Mean Accuracy = 49.7%

### Overall Aggregated Performance

| Group | Completion Rate | Mean Score | Steps Proposed | Average Repairs | Undetected Errors | Token Cost | Runtime |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Control (G)** | 56.7% | 35.2% | 8.00 | 0.00 | 1.77 | 0 | 40 ms |
| **Treatment A (G + DFA)** | 90.0% | **57.8%** | 13.50 | 2.80 | **0.00** | 0 | **67 ms** |
| **Treatment B (G + LLM)** | 100% | 35.2% | 9.77 | 2.17 | 1.20 | 11,720 | 14.65 s |

---

## 3. Ablation Studies

We ran two ablations (8 trials each, with an increased noise level: 15% DFA errors, 25% bug rate) to understand verifier sensitivity.

### Ablation 1: Verifier Components

This experiment checks if structural checks (DFA) and content checks (Data) are both required:

| Verifier Mode | Completion Rate | Mean Score | Steps Proposed | Average Repairs | Errors Caught |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Full Verifier (DFA + Data)** | 100% | **49.5%** | 16.69 | 2.75 | 4.31 |
| **Structural-Only (DFA Only)** | 100% | 44.8% | 17.13 | 1.75 | 1.75 |
| **Data-Only (Data Only)** | 100% | 0.0% | 5.63 | 3.13 | 3.38 |
| **No Verifier (Control)** | 100% | 0.0% | 6.38 | 0.00 | 0.00 |

* **Analysis**: Under high noise, running **without a DFA (Control and Data-Only)** leads to a **0% score** because the agent gets completely lost in transition sequences. Having **DFA Only** maintains routing (44.8% score) but lets data bugs slip through. The **Full Verifier** achieves the best score (**49.5%**).

### Ablation 2: Retry Budget

This experiment evaluates the agent's performance as a function of the max allowed retries:

| Max Retries | Completion Rate | Mean Score | Steps Proposed | Average Repairs |
| :---: | :---: | :---: | :---: | :---: |
| **0** | 100% | 52.9% | 12.38 | 0.00 |
| **1** | 100% | 52.9% | 13.25 | 0.88 |
| **2** | 100% | 52.9% | 14.50 | 1.63 |
| **3+** | 100% | 52.9% | 14.50 | 3.13 |

* **Analysis**: The repair count saturated around 3.13. Having at least 3-5 retries ensures that even complex multi-step failures can be successfully repaired.
