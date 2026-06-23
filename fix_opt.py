import json, onnx, copy, numpy as np
from onnx import helper, TensorProto

def cast_elimination(model: onnx.ModelProto):
    keep_nodes = []
    removed = 0
    for node in model.graph.node:
        if node.op_type == "Cast":
            attr = {a.name: a.i for a in node.attribute}
            to_type = attr.get("to", -1)
            inp_name = node.input[0]
            inp_type = None
            for vi in model.graph.value_info:
                if vi.name == inp_name and vi.type.HasField("tensor_type"):
                    inp_type = vi.type.tensor_type.elem_type
                    break
            if inp_type is not None and inp_type == to_type:
                removed += 1
                continue
        keep_nodes.append(node)
    new_graph = helper.make_graph(keep_nodes, model.graph.name + "_opt", model.graph.input, model.graph.output, model.graph.initializer)
    return helper.make_model(new_graph, ir_version=model.ir_version, opset_imports=model.opset_import), removed

def fp16_surgery(model: onnx.ModelProto):
    model = copy.deepcopy(model)
    conv_count = 0
    for t in model.graph.initializer:
        if t.data_type == TensorProto.FLOAT:
            arr = np.frombuffer(t.raw_data, dtype=np.float32).copy()
            arr_f16 = arr.astype(np.float16)
            t.data_type = TensorProto.FLOAT16
            t.raw_data = arr_f16.tobytes()
            conv_count += 1
    for vi in list(model.graph.value_info) + list(model.graph.input) + list(model.graph.output):
        if getattr(vi.type, "tensor_type", None) and getattr(vi.type.tensor_type, "elem_type", None) == TensorProto.FLOAT:
            vi.type.tensor_type.elem_type = TensorProto.FLOAT16
    return model, conv_count

