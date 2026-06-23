import onnx
from onnx import numpy_helper

m = onnx.load('/Users/sweeden/kaggle/input/neurogolf-2026-agent-trace-framework-v2/task096.onnx')
for n in m.graph.node:
    if n.op_type == 'Gather':
        print(n.name, n.input, n.output)
        for init in m.graph.initializer:
            if init.name in n.input:
                val = numpy_helper.to_array(init)
                print("Initializer:", init.name, val)
