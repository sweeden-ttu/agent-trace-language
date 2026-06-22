# baselines/llm_trace.py
"""Simple LLM‑only trace‑language baseline.
This script loads the trace CSV, feeds each trace step to an LLM via litellm, and records
the generated output. It uses the same prompt as the NeuroGolf pipeline but does *not*
apply any DFA verification, providing a pure language‑model baseline.
"""
import csv
import os
from litellm import completion

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
CSV_PATH = os.path.join(DATA_DIR, "trace_language.csv")
OUTPUT_PATH = os.path.join(DATA_DIR, "baseline_output.txt")

def load_traces(csv_path):
    traces = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            traces.append(row["trace"])
    return traces

def run_baseline(traces):
    results = []
    for i, trace in enumerate(traces):
        # Simple prompt – you can customise as needed.
        prompt = f"Given the partial trace: {trace}\nComplete the next step."
        try:
            response = completion(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
            results.append({"index": i, "prompt": prompt, "output": response.choices[0].message.content})
        except Exception as e:
            results.append({"index": i, "prompt": prompt, "error": str(e)})
    return results

if __name__ == "__main__":
    traces = load_traces(CSV_PATH)
    results = run_baseline(traces)
    with open(OUTPUT_PATH, "w") as f:
        for r in results:
            f.write(str(r) + "\n")
    print(f"Baseline results written to {OUTPUT_PATH}")
