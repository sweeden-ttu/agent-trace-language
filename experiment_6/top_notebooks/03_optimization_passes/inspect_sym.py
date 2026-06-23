import onnx

model = onnx.load('/Users/sweeden/kaggle/input/neurogolf-2026-agent-trace-framework-v2/task096.onnx')
nodes = model.graph.node
print(f"Total nodes: {len(nodes)}")
for n in nodes[:20]:
    print(f"{n.op_type} inputs={n.input} outputs={n.output}")
