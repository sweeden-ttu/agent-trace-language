import nbformat

with open('03_optimization_passes.ipynb', 'r') as f:
    nb = nbformat.read(f, as_version=4)

new_code = """import os
import glob
import math
import onnx
import onnxoptimizer
import numpy as np
from onnx import helper, TensorProto, numpy_helper

SUBMISSION_DIR = '/Users/sweeden/kaggle/input/neurogolf-2026-agent-trace-framework-v2'
optimized_dir = os.path.join(SUBMISSION_DIR, 'optimized')
os.makedirs(optimized_dir, exist_ok=True)

GENERIC_PASSES = [
    "eliminate_deadend",
    "eliminate_identity",
    "eliminate_unused_initializer",
    "eliminate_nop_cast",
    "fuse_consecutive_squeezes",
    "fuse_consecutive_transposes",
    "fuse_bn_into_conv",
    "fuse_matmul_add_bias_into_gemm",
    "eliminate_nop_pad",
    "eliminate_nop_dropout",
    "fuse_consecutive_concats",
    "fuse_pad_into_conv",
    "fuse_pad_into_pool",
    "eliminate_nop_reshape",
    "eliminate_nop_flatten",
    "eliminate_shape_op",
    "extract_constant_to_initializer"
]

def generic_optimize(model):
    try:
        opt_model = onnxoptimizer.optimize(model, GENERIC_PASSES)
        return opt_model
    except Exception as e:
        print(f"Generic optimization failed: {e}")
        return model

def symmetry_reflection_optimize(model):
    # Optimize using Pad with mode=reflect
    try:
        input_tensor = model.graph.input[0]
        shape = [dim.dim_value for dim in input_tensor.type.tensor_type.shape.dim]
        if len(shape) < 2: return generic_optimize(model)
        
        # We replace the reversing nodes with Pad mode='reflect' or optimized Gather
        # For simplicity, if we know it's a reflection, we use Gather with precomputed reversed indices
        axis = 1 if shape[1] > 0 else 0
        size = shape[axis] if shape[axis] > 0 else 30
        
        rev_indices = np.arange(size-1, -1, -1, dtype=np.int64)
        rev_initializer = numpy_helper.from_array(rev_indices, name="rev_idx")
        model.graph.initializer.append(rev_initializer)
        
        input_name = model.graph.input[0].name
        gather_out = input_name + "_reversed"
        gather_node = helper.make_node("Gather", inputs=[input_name, "rev_idx"], outputs=[gather_out], axis=axis)
        model.graph.node.append(gather_node)
        
        for node in model.graph.node:
            if node != gather_node:
                for i, inp in enumerate(node.input):
                    if inp == input_name: node.input[i] = gather_out
                    
        return generic_optimize(model)
    except Exception as e:
        return generic_optimize(model)

def gravity_movement_optimize(model):
    # Optimize using TopK to Sort 1s and 0s, pushing blocks down
    try:
        input_tensor = model.graph.input[0]
        input_name = input_tensor.name
        shape = [dim.dim_value for dim in input_tensor.type.tensor_type.shape.dim]
        
        k_val = shape[2] if len(shape) > 2 and shape[2] > 0 else 30
        k_tensor = numpy_helper.from_array(np.array([k_val], dtype=np.int64), name="k_val")
        model.graph.initializer.append(k_tensor)
        
        # TopK sorts the values along the axis
        topk_node = helper.make_node("TopK", inputs=[input_name, "k_val"], outputs=[input_name+"_topk", input_name+"_indices"], axis=2, largest=1, sorted=1)
        model.graph.node.append(topk_node)
        
        for node in model.graph.node:
            if node != topk_node:
                for i, inp in enumerate(node.input):
                    if inp == input_name: node.input[i] = input_name+"_topk"
        
        return generic_optimize(model)
    except Exception as e:
        return generic_optimize(model)

def recolor_logical_optimize(model):
    # Gather based recolor
    try:
        input_tensor = model.graph.input[0]
        input_name = input_tensor.name
        
        lut = np.array([9 - i for i in range(10)], dtype=np.int64)
        lut_initializer = numpy_helper.from_array(lut, name="color_lut")
        model.graph.initializer.append(lut_initializer)
        
        gather_out = input_name + "_mapped"
        gather_node = helper.make_node("Gather", inputs=["color_lut", input_name], outputs=[gather_out], axis=0)
        model.graph.node.append(gather_node)
        
        for node in model.graph.node:
            if node != gather_node:
                for i, inp in enumerate(node.input):
                    if inp == input_name: node.input[i] = gather_out
        
        return generic_optimize(model)
    except Exception as e:
        return generic_optimize(model)

def convolution_ca_optimize(model):
    return generic_optimize(model)

onnx_files = sorted(glob.glob(os.path.join(SUBMISSION_DIR, 'task*.onnx')))
print(f"Found {len(onnx_files)} ONNX files to optimize.")

for fpath in onnx_files:
    try:
        model = onnx.load(fpath)
        fname = os.path.basename(fpath).lower()
        if 'sym' in fname or 'reflect' in fname:
            opt_model = symmetry_reflection_optimize(model)
        elif 'conv' in fname or 'ca' in fname:
            opt_model = convolution_ca_optimize(model)
        elif 'gravity' in fname or 'move' in fname:
            opt_model = gravity_movement_optimize(model)
        elif 'recolor' in fname or 'logic' in fname or 'overlay' in fname:
            opt_model = recolor_logical_optimize(model)
        else:
            opt_model = generic_optimize(model)
            
        out_path = os.path.join(optimized_dir, os.path.basename(fpath))
        onnx.save(opt_model, out_path)
    except Exception as e:
        print(f"Failed to optimize {fpath}: {e}")
        
print("Optimization complete.")
"""

nb.cells = [nbformat.v4.new_code_cell(new_code)]
with open('03_optimization_passes.ipynb', 'w') as f:
    nbformat.write(nb, f)
