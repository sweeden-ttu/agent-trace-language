import onnx
import glob
import os

files = glob.glob('/Users/sweeden/kaggle/input/neurogolf-2026-agent-trace-framework-v2/task*.onnx')
sym_files = []
for f in files:
    m = onnx.load(f)
    ops = set(n.op_type for n in m.graph.node)
    # Pure symmetry: Slice, Gather, Concat, Pad (and maybe Identity/Constant)
    if 'Gather' in ops and 'Concat' in ops and 'Pad' in ops and len(ops) < 10:
        if not 'Mul' in ops and not 'Add' in ops:
            sym_files.append((os.path.basename(f), len(m.graph.node), ops))

print("Symmetry files found:", len(sym_files))
for sf in sym_files:
    print(sf[0], sf[1], sf[2])
