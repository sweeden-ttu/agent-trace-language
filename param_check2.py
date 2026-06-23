import glob, onnx, numpy as np
for f in glob.glob('/Users/sweeden/kaggle/input/neurogolf-2026-agent-trace-framework-v2/optimized/task*.onnx'):
    m = onnx.load(f)
    params = sum(int(np.prod(list(t.dims))) for t in m.graph.initializer if t.dims)
    if params > 500:
        print(f"{f}: {params} params")
