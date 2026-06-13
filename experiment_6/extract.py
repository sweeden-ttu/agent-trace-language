import json
with open('neurogolf-2026-trace-language.ipynb', 'r') as f:
    nb = json.load(f)
with open('dump_notebook_code.py', 'w') as f:
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            if isinstance(cell['source'], list):
                f.write("".join(cell['source']) + "\n")
            else:
                f.write(cell['source'] + "\n")
