import os
import json
import pandas as pd

class LanguageAnalyzer:
    def __init__(self):
        pass

    def analyze_trace(self, trace):
        """
        Analyzes a single execution trace to detect structural patterns:
        - Alphabet size
        - Cycle counts
        - Recursion/Stack nesting depth
        - Chomsky class classification hypothesis
        """
        unique_symbols = set(trace)
        alphabet_size = len(unique_symbols)
        
        # 1. Detect simple cycles (loop back-edges)
        visited = set()
        cycle_count = 0
        for token in trace:
            if token in visited:
                cycle_count += 1
            visited.add(token)
            
        # 2. Detect stack-like nesting (e.g. planner/critic open/close cycles)
        # We look for nested pairs like: preprocess_data -> train_model -> evaluate_model -> preprocess_data ...
        # Standard Dyck language matching for nested structure
        nesting_depth = 0
        max_nesting = 0
        
        # Simulating nested structures in trace
        for i, token in enumerate(trace):
            if token == 'preprocess_data':
                nesting_depth += 1
                max_nesting = max(max_nesting, nesting_depth)
            elif token == 'evaluate_model':
                if nesting_depth > 0:
                    nesting_depth -= 1

        # Heuristic Chomsky-class classification
        if max_nesting > 2:
            classification = "Type-2 (Context-Free)"
            confidence = 0.85
            reason = f"Detected stack-like nesting structure (depth={max_nesting}) in train-evaluate loop."
        elif cycle_count > 0:
            classification = "Type-3 (Regular with Loops)"
            confidence = 0.90
            reason = f"Detected simple repetitive cycles (count={cycle_count}) with no deep stack nesting."
        else:
            classification = "Type-3 (Regular Linear)"
            confidence = 0.95
            reason = "No cycles or nesting detected. Trace follows a flat linear state machine."
            
        return {
            'trace_length': len(trace),
            'alphabet_size': alphabet_size,
            'cycle_count': cycle_count,
            'max_stack_nesting': max_nesting,
            'classification': classification,
            'confidence': confidence,
            'reason': reason
        }

def run_exp4():
    print("Executing Experiment 4: Trace-Language Verification Analyzer...")
    
    analyzer = LanguageAnalyzer()
    
    # Analyze multiple sample traces from our runners
    traces_to_analyze = {
        'react_agent_trace': [
            'start', 'load_data', 'explore_data', 'preprocess_data', 
            'train_model', 'evaluate_model', 'generate_predictions', 
            'submit_predictions', 'halt'
        ],
        'tree_search_trace': [
            'start', 'load_data', 'explore_data', 'preprocess_data', 
            'train_model', 'evaluate_model', 'preprocess_data', 
            'train_model', 'evaluate_model', 'preprocess_data', 
            'train_model', 'evaluate_model', 'generate_predictions', 
            'submit_predictions', 'halt'
        ],
        'buggy_control_trace': [
            'start', 'load_data', 'train_model', 'evaluate_model', 
            'submit_predictions', 'halt'
        ]
    }
    
    classifications = {}
    for name, trace in traces_to_analyze.items():
        res = analyzer.analyze_trace(trace)
        classifications[name] = res
        print(f"\nTrace: {name}")
        print(f"  Length: {res['trace_length']}, Alphabet Size: {res['alphabet_size']}")
        print(f"  Cycle Count: {res['cycle_count']}, Nesting Depth: {res['max_stack_nesting']}")
        print(f"  Classification: {res['classification']} (Conf: {res['confidence']})")
        print(f"  Reason: {res['reason']}")
        
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
    os.makedirs(out_dir, exist_ok=True)
    
    with open(os.path.join(out_dir, "exp4_classifications.json"), 'w') as f:
        json.dump(classifications, f, indent=4)
        
    print("\nExperiment 4 completed successfully. Results written to data/exp4_classifications.json\n")

if __name__ == "__main__":
    run_exp4()
