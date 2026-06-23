import json

path = '/Users/sweeden/agent-trace-language/agent-trace-language/experiment_6/neurogolf-2026-trace-language.ipynb'
with open(path, 'r') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = cell['source']
        if isinstance(source, list):
            source = "".join(source)
            
        if 'def make_symmetry(h, w):' in source:
            new_sym = """def make_symmetry(h, w, sym_type='quadrant'):
    x = onnx.helper.make_tensor_value_info('input', DT, GS)
    y = onnx.helper.make_tensor_value_info('output', DT, GS)
    inits, nodes = [], []
    st = onnx.helper.make_tensor('st_s', onnx.TensorProto.INT64, [4], [0, 0, 0, 0])
    en = onnx.helper.make_tensor('en_s', onnx.TensorProto.INT64, [4], [1, 10, h, w])
    ax = onnx.helper.make_tensor('ax_s', onnx.TensorProto.INT64, [4], [0, 1, 2, 3])
    sp = onnx.helper.make_tensor('sp_s', onnx.TensorProto.INT64, [4], [1, 1, 1, 1])
    inits.extend([st, en, ax, sp])
    nodes.append(onnx.helper.make_node('Slice', ['input', 'st_s', 'en_s', 'ax_s', 'sp_s'], ['I']))
    
    idx_h = onnx.helper.make_tensor('idx_h', onnx.TensorProto.INT64, [w], np.arange(w-1, -1, -1))
    inits.append(idx_h)
    nodes.append(onnx.helper.make_node('Gather', ['I', 'idx_h'], ['I_hf'], axis=3))
    
    idx_v = onnx.helper.make_tensor('idx_v', onnx.TensorProto.INT64, [h], np.arange(h-1, -1, -1))
    inits.append(idx_v)
    nodes.append(onnx.helper.make_node('Gather', ['I', 'idx_v'], ['I_vf'], axis=2))
    
    nodes.append(onnx.helper.make_node('Gather', ['I_hf', 'idx_v'], ['I_bf'], axis=2))
    
    if sym_type == 'horizontal':
        nodes.append(onnx.helper.make_node('Concat', ['I', 'I_hf'], ['Full'], axis=3))
        pd = onnx.helper.make_tensor('pd_s', onnx.TensorProto.INT64, [8], [0, 0, 0, 0, 0, 0, H - h, W - (2*w)])
    elif sym_type == 'vertical':
        nodes.append(onnx.helper.make_node('Concat', ['I', 'I_vf'], ['Full'], axis=2))
        pd = onnx.helper.make_tensor('pd_s', onnx.TensorProto.INT64, [8], [0, 0, 0, 0, 0, 0, H - (2*h), W - w])
    else: # quadrant
        nodes.append(onnx.helper.make_node('Concat', ['I', 'I_hf'], ['Row1'], axis=3))
        nodes.append(onnx.helper.make_node('Concat', ['I_vf', 'I_bf'], ['Row2'], axis=3))
        nodes.append(onnx.helper.make_node('Concat', ['Row1', 'Row2'], ['Full'], axis=2))
        pd = onnx.helper.make_tensor('pd_s', onnx.TensorProto.INT64, [8], [0, 0, 0, 0, 0, 0, H - (2*h), W - (2*w)])
        
    inits.append(pd)
    nodes.append(onnx.helper.make_node('Pad', ['Full', 'pd_s'], ['output'], mode='constant'))
    
    g = onnx.helper.make_graph(nodes, f'sym_{sym_type}', [x], [y], inits)
    m = onnx.helper.make_model(g, ir_version=IR, opset_imports=OPSET)
    m = onnx.shape_inference.infer_shapes(m)
    return m"""
            
            # Find the old make_symmetry function and replace it
            import re
            source = re.sub(r'def make_symmetry\(h, w\):.*?(?=\n\n|\Z)', new_sym, source, flags=re.DOTALL)
            cell['source'] = source

        if 'if kind == \'symmetry\' and data:' in source:
            new_get_solver = """    if kind == 'symmetry' and data:
        h, w = data
        for sym_type in ['horizontal', 'vertical', 'quadrant']:
            m = make_symmetry(h, w, sym_type)
            if verify(m, exs): 
                try: m = optimize_model(m)
                except: pass
                cache[tid] = ('symmetry', m, cost_est(m)); return cache[tid]"""
            
            source = re.sub(
                r"    if kind == 'symmetry' and data:.*?return cache\[tid\]",
                new_get_solver,
                source,
                flags=re.DOTALL
            )
            
            # Update the solo_probe validator as well
            source = source.replace('all_pass &= solo_probe(make_symmetry(2, 2), "Symmetry")', 
                                    'all_pass &= solo_probe(make_symmetry(2, 2, "quadrant"), "Symmetry")')
            
            cell['source'] = source

with open(path, 'w') as f:
    json.dump(nb, f, indent=1)

print("Updated make_symmetry in notebook successfully!")
