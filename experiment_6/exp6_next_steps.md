# Experiment 6: Next Steps — Cost Engineering & Pattern Synthesis

## 1. Analysis: Why the Plateau Occurred (v27 vs. v45)

Version 27 was the "sweet spot" because it balanced aggressive blending with moderate validation. The transition to Version 45 introduced several "safety" and "quality" features that, while architecturally sound for a research paper, penalized the Kaggle score:

*   **Over-Restrictive Validation:** v45 added strict checks for dynamic shapes, banned ops, and inference consistency (`INFERENCE_TEST`, `OUTPUT_SHAPE_CHECK`). Many high-scoring public artifacts use "clever" ONNX hacks or slightly non-standard shapes that the v45 DFA rejected.
*   **The "Quality" Bias:** v45 introduced `BUNDLE_QUALITY` sorting. By prioritizing "controlled" or "manual" bundles, it selected correct but high-cost solvers over cheaper, more "hacky" ones found in the larger automated bundles that v27 accepted greedily.
*   **Optimization Overhead:** Standard `onnx.optimizer` in v45 often increased the memory footprint by unrolling constants or adding boilerplate nodes. Since the score is `25 - ln(params + memory)`, even a small increase in memory dropped the score significantly.
*   **Generic Solver Limits:** Both versions relied on `recolor` and `lprop` (Label Propagation). These only solve ~10-15% of ARC tasks. The rest depend entirely on finding a pre-built solver in external datasets.

## 2. Recommendations: A New Direction

To break the plateau, the project has shifted from "Pipeline Verification" to **"Cost Engineering and Pattern Synthesis"**:

### Completed in Version 46:
*   **Kronecker/Tiling Template:** Implemented a symbolic solver for Task 001 and similar self-similar expansion tasks ($Input \otimes Input$).
*   **Reflective Symmetry Template:** Implemented a symbolic solver for Task 112 and quadrant-reflection tasks.
*   **Full-Graph FP16 Compression:** Upgraded `fp16_surgery` to cast the entire graph (inits, I/O, value_info) to Float16, effectively halving the memory footprint.
*   **Initial Cost-Greedy Blending:** Refactored the blender to prioritize competition score over qualitative source labels.

### Status of Last Push (v46):
*   **Public Score:** 5766.19 (a drop from 5793.14).
*   **Root Cause identified:** The "Strictly Cost-Greedy" logic was incorrectly comparing correct high-cost blended solvers against the **incorrect but cheap** `identity` solver. This led the blender to favor failing identity solvers, resulting in a loss of ~30 points.

## 3. Immediate Next Steps (Priority)

### A. Fix Blending Logic (The "Correctness Priority" Rule)
*   **Update:** Modify the blender to ensure that **any** correct solver is preferred over an `identity` fallback, regardless of cost. Cost-greediness should only apply when choosing between two *correct* solvers.
*   **Target:** Recover the ~30 points lost in v46 and build upon the v29 baseline.

### B. Refine Symbolic "Cellular Automata" (CA) Solvers
*   **Target:** Tasks requiring iterative local rules (spreading, filling, gravity).
*   **Refactoring:** Replace heavy `lprop` logic (multiple `MaxPool` stages) with unrolled 3x3 `Convolution` layers.
*   **Goal:** Significant reduction in parameter count compared to the current label propagation logic.

### C. Hand-Tuning Advanced Templates
*   **Task 031 (Crop to Content):** Use `NonZero` + `ReduceMin/Max` to drive a dynamic `Slice`.
*   **Task 210 (Gravity/Falling):** Use unrolled `MaxPool` or index-sorting to "drop" pixels to the bottom of the grid.

## 4. Research & Publication Alignment
*   **Formal Kronecker Synthesis:** Incorporate formal descriptions of Kronecker product applications from "KromHC: Manifold-Constrained Hyper-Connections" (Zhou et al., 2026) to justify the symbolic template approach in the AAAI 2027 paper.
*   **Cost-Efficiency Metrics:** Document the memory-params Pareto frontier for these templates in the **Resource-Constrained Multi-Agent Verification** section of the paper.
