import onnx
from onnx import numpy_helper

m = onnx.load('/Users/sweeden/kaggle/input/neurogolf-2026-agent-trace-framework-v2/task214.onnx')
for init in m.graph.initializer:
    val = numpy_helper.to_array(init)
    print("Initializer:", init.name, val.shape, val)
