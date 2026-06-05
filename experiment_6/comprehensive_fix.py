import json
import numpy as np

path = 'neurogolf-2026-trace-language.ipynb'
with open(path, 'r') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = cell['source']
        if isinstance(source, list):
            source = "".join(source)
        
        # 1. Fix make_symmetry to use Gather correctly (redundant but safe)
        if 'def make_symmetry(h, w):' in source and 'ReverseSequence' in source:
             source = source.replace(
                "    # Horizontal flip\n    nodes.append(onnx.helper.make_node('ReverseSequence', ['I'], ['I_hf'], sequence_lens=np.array([w]*10, dtype=np.int64), batch_axis=3, time_axis=3))\n    # Vertical flip\n    nodes.append(onnx.helper.make_node('ReverseSequence', ['I'], ['I_vf'], sequence_lens=np.array([h]*10, dtype=np.int64), batch_axis=2, time_axis=2))\n    # Both flip\n    nodes.append(onnx.helper.make_node('ReverseSequence', ['I_hf'], ['I_bf'], sequence_lens=np.array([h]*10, dtype=np.int64), batch_axis=2, time_axis=2))",
                """    # Horizontal flip indices
    idx_h = onnx.helper.make_tensor('idx_h', onnx.TensorProto.INT64, [w], np.arange(w-1, -1, -1))
    inits.append(idx_h)
    nodes.append(onnx.helper.make_node('Gather', ['I', 'idx_h'], ['I_hf'], axis=3))
    
    # Vertical flip indices
    idx_v = onnx.helper.make_tensor('idx_v', onnx.TensorProto.INT64, [h], np.arange(h-1, -1, -1))
    inits.append(idx_v)
    nodes.append(onnx.helper.make_node('Gather', ['I', 'idx_v'], ['I_vf'], axis=2))
    
    # Both flip (Horizontal then Vertical)
    nodes.append(onnx.helper.make_node('Gather', ['I_hf', 'idx_v'], ['I_bf'], axis=2))"""
            )

        # 2. Update canonical_trace loop
        if 'canonical_trace = [' in source:
            source = source.replace(
                "    canonical_trace.append(Step(Op.BUILD_ONNX, 'builder', tid))",
                """    if tid == 1:
        canonical_trace.append(Step(Op.KRONECKER_SYNTHESIS, 'builder', tid))
    elif tid == 2:
        canonical_trace.append(Step(Op.SYMMETRY_SYNTHESIS, 'builder', tid))
    else:
        canonical_trace.append(Step(Op.BUILD_ONNX, 'builder', tid))"""
            )
            # Ensure SIZE_AUDIT is present (it should be from previous step but let's be sure)
            if "Step(Op.SIZE_AUDIT, 'packager')" not in source:
                source = source.replace(
                    "Step(Op.PACKAGE_SUBMISSION, 'packager'))",
                    "Step(Op.SIZE_AUDIT, 'packager'),\n    Step(Op.PACKAGE_SUBMISSION, 'packager'))"
                )

        # 3. Initialize rejection_counts if missing
        if 'rejection_counts = {}' not in source and 'def discover_bundles():' in source:
            source = source.replace(
                'def discover_bundles():',
                'rejection_counts = {}\ndef discover_bundles():'
            )

        # 4. Check for any other errors in the DFA class
        if 'class DFA:' in source:
             # Ensure Op enum has all needed members
             if 'SIZE_AUDIT = auto()' not in source:
                  source = source.replace(
                      'SHA256_CHECK = auto()\n',
                      'SHA256_CHECK = auto(); SIZE_AUDIT = auto()\n'
                  )

        cell['source'] = source

with open(path, 'w') as f:
    json.dump(nb, f, indent=1)
