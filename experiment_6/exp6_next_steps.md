# Experiment 6 — NeuroGolf 2026: Next Steps

## Current State

Left off on version 30. Items 6, 4 and 8 were next to be implemented from this task.

## Next Steps

### 1. Investigate v24 0.10 MB zip size
Before submitting v24, verify the zip contents. If it's genuinely 0.10 MB, something is wrong in the packaging code (identity swap loop may be over-replacing). Add zip entry count and total uncompressed size to the logging.


### 4. Add more ONNX solver types
Currently only 3 solvers: identity (Conv 1x1), recolor (Slice+Where), lprop (MaxPool). Add:
- **resize/scale** (nearest-neighbor using ONNX Resize)
- **flip/rotate** (transpose + slice)
- **crop** (slice to bounding box)
- **tile/repeat** (Concat with self)
- **color mapping** (Conv 1x1 with learned color remap)
- **gravity** (CumSum-based column shift)
- **mask extraction/recolor** (Greater + Where on color channels)

These would reduce the 398 identity fallbacks (currently ~88% of tasks are identity).

### 6. Add inference validation for key tasks
For tasks 1–3 (where training data is available), run actual ONNX Runtime inference to verify blended models produce correct outputs. This catches runtime errors before submission.

### 7. Containerized evaluation harness
Build a local test that mimics Kaggle's scoring: load each model, run with dummy input `(1, 10, 30, 30)`, verify output shape and non-NaN values. Catches ERROR submissions before pushing.

### 8. Expand dataset sources
Look for newer Kaggle submission datasets scoring 6000–6500. Currently using 4 datasets; newer public solutions may have better blends.

### 9. Package size budget
Current 1.18 MB leaves 260 KB unused. More expensive but correct models can be blended without exceeding the 1.44 MB limit. The two-pass size-budgeted packaging already handles this optimally.

### 10. DFA verifier evolution
The DFA currently has 28 ops, 13 states, 83 transitions. Consider adding:
- `INFERENCE_TEST` op for per-model runtime validation
- `OUTPUT_SHAPE_CHECK` explicit state for shape validation
- `COST_GRADER_MATCH` verification that cost estimation matches Kaggle's actual cost formula
