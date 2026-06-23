import onnx
import collections

model = onnx.load('/Users/sweeden/agent-trace-language/agent-trace-language/submission/task096.onnx')
counts = collections.Counter([n.op_type for n in model.graph.node])
print("task096 op_type counts:")
for op, c in counts.most_common():
    print(f"  {op}: {c}")
