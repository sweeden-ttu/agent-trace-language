import onnx, numpy as np
m = onnx.load('/Users/sweeden/kaggle/input/neurogolf-2026-agent-trace-framework-v2/task005.onnx')
for t in m.graph.initializer:
    print(t.name, list(t.dims), int(np.prod(list(t.dims))))
