import os, glob, onnx, math, numpy as np
onnx_files = sorted(glob.glob('/Users/sweeden/kaggle/input/neurogolf-2026-agent-trace-framework-v2/optimized/task*.onnx'))
total_params = 0
total_memory = 0.0
for f in onnx_files:
    m = onnx.load(f)
    params = sum(int(np.prod(list(t.dims))) for t in m.graph.initializer if t.dims)
    size_kb = os.path.getsize(f) / 1024
    total_params += params
    total_memory += size_kb
score = 25.0 - math.log(total_params + total_memory)
print(f"Score: {score:.4f} (Cost: {total_params + total_memory:.1f})")
