import os
import pandas as pd
import numpy as np

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def normalized_edit_similarity(s1, s2):
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    dist = levenshtein_distance(s1, s2)
    return 1.0 - (dist / max_len)

def jaccard_similarity(s1, s2):
    set1, set2 = set(s1), set(set(s2))
    if not set1 and not set2:
        return 1.0
    return len(set1.intersection(set2)) / len(set1.union(set2))

def run_exp2():
    print("Executing Experiment 2: Chomsky Class Compression...")
    
    # 1. Define base traces from different architectures
    react_trace = [
        'load_data', 'explore_data', 'preprocess_data', 'train_model', 
        'evaluate_model', 'generate_predictions', 'submit_predictions', 'halt'
    ]
    
    tree_search_trace = [
        'load_data', 'explore_data', 'preprocess_data', 'train_model', 
        'evaluate_model', 'train_model', 'evaluate_model', 'preprocess_data', 
        'train_model', 'evaluate_model', 'generate_predictions', 'submit_predictions', 'halt'
    ]
    
    planner_executor_trace = [
        'load_data', 'explore_data', 'preprocess_data', 'train_model', 
        'evaluate_model', 'generate_predictions', 'submit_predictions', 'halt'
    ]
    
    traces = {
        'ReAct': react_trace,
        'Tree Search': tree_search_trace,
        'Planner-Executor': planner_executor_trace
    }
    
    # 2. Define projection alphabet Sigma'
    # Projecting onto the load-train-submit core pipeline
    sigma_prime = ['load_data', 'train_model', 'submit_predictions']
    
    projected_traces = {}
    for name, trace in traces.items():
        projected = [token for token in trace if token in sigma_prime]
        projected_traces[name] = projected
        print(f"Agent {name} full trace length: {len(trace)}, projected length: {len(projected)}")
        print(f"  Projected: {projected}")
        
    # 3. Calculate similarities
    agents = list(traces.keys())
    results = []
    
    for a1 in agents:
        row = {'Agent': a1}
        for a2 in agents:
            # Edit similarity on projected traces
            sim = normalized_edit_similarity(projected_traces[a1], projected_traces[a2])
            row[a2] = f"{sim:.2f}"
        results.append(row)
        
    df_sim = pd.DataFrame(results)
    
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
    os.makedirs(out_dir, exist_ok=True)
    df_sim.to_csv(os.path.join(out_dir, "exp2_similarity.csv"), index=False)
    
    print("\nPairwise Normalized Edit Similarity Matrix (Projected onto Sigma'):")
    print(df_sim.to_string(index=False))
    print("Experiment 2 completed successfully.\n")

if __name__ == "__main__":
    run_exp2()
