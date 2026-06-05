import os
import shutil
import tempfile
import pandas as pd
import numpy as np

from src.benchmark import load_task
from src.generator import AgentGenerator
from src.verifier import RuntimeVerifier

class AblationRuntimeVerifier(RuntimeVerifier):
    def __init__(self, matrix_csv_path, enable_dfa=True, enable_data=True):
        super().__init__(matrix_csv_path)
        self.enable_dfa = enable_dfa
        self.enable_data = enable_data

    def verify_step(self, action, workspace_dir, evaluate_fn=None):
        # 1. Structural check
        if self.enable_dfa:
            if not self.dfa.is_valid_transition(action):
                return False, f"DFA Transition Error: Cannot move from '{self.dfa.current_state}' to '{action}'"
        
        # 2. Data check
        if self.enable_data:
            check_name = f"check_{action}"
            if hasattr(self.data_verifier, check_name):
                checker = getattr(self.data_verifier, check_name)
                if action == "submit_predictions":
                    passed, msg = checker(workspace_dir, evaluate_fn)
                else:
                    passed, msg = checker(workspace_dir)
                if not passed:
                    return False, f"Data Verification Error for '{action}': {msg}"
            else:
                return False, f"Internal Error: No verification function found for '{action}'"

        # 3. Commit state change
        # Always advance DFA state internally to track where the agent goes (even if DFA checks are disabled)
        try:
            self.dfa.advance(action)
        except ValueError:
            # If DFA checks are disabled, we might have invalid transitions, just skip raising error
            if self.enable_dfa:
                raise
            else:
                self.dfa.current_state = action
                self.dfa.trace.append(action)
                
        return True, "Passed"


def run_ablation_trial(task, workspace_dir, matrix_csv, enable_dfa, enable_data, max_retries, seed):
    generator = AgentGenerator(task, workspace_dir, dfa_error_rate=0.15, bug_rate=0.25, random_state=seed)
    rv = AblationRuntimeVerifier(matrix_csv, enable_dfa=enable_dfa, enable_data=enable_data)
    
    max_steps = 30
    total_steps = 0
    repairs = 0
    validation_errors = 0
    
    feedback = None
    completed = False
    score = 0.0
    
    while total_steps < max_steps:
        # Get allowed next actions from verifier DFA (if enabled)
        if enable_dfa:
            current_state = rv.dfa.current_state
            allowed = [col for col in rv.dfa.matrix.columns if int(rv.dfa.matrix.loc[current_state, col]) == 1]
        else:
            # Allow all actions
            allowed = list(rv.dfa.matrix.columns)
            
        proposed = generator.propose_next_action(allowed)
        total_steps += 1
        
        # Execute
        exec_success, exec_msg = generator.execute_action(proposed, feedback=feedback)
        
        # Verify
        if proposed == 'submit_predictions':
            passed, verify_msg = rv.verify_step(proposed, workspace_dir, evaluate_fn=task.evaluate_submission)
        else:
            passed, verify_msg = rv.verify_step(proposed, workspace_dir)
            
        if passed:
            feedback = None
            if proposed == 'halt':
                completed = True
                break
        else:
            validation_errors += 1
            if repairs < max_retries:
                repairs += 1
                feedback = verify_msg
            else:
                # Exceeded retry budget: continue anyway (like control) or halt
                feedback = None
                # Force advance state internally if DFA is disabled
                if not enable_dfa:
                    rv.dfa.current_state = proposed
                    rv.dfa.trace.append(proposed)
                else:
                    # In DFA mode, if we can't repair, we are stuck
                    pass

    # Retrieve score
    if completed:
        try:
            score_file = os.path.join(workspace_dir, "leaderboard_score.txt")
            if os.path.exists(score_file):
                with open(score_file, 'r') as f:
                    content = f.read()
                    score = float(content.split(":")[1].strip())
        except Exception:
            pass
            
    # Fallback to test submission if the file exists anyway
    if score == 0.0:
        try:
            if os.path.exists(os.path.join(workspace_dir, "submission.csv")):
                score = task.evaluate_submission(workspace_dir)
                completed = True
        except Exception:
            pass
            
    return {
        'task': task.name,
        'completed': completed,
        'score': score,
        'steps_proposed': total_steps,
        'repairs': repairs,
        'validation_errors': validation_errors,
    }


def run_ablations(num_trials=8):
    matrix_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/trace_matrix.csv"))
    tasks = ["spaceship_titanic", "wine_quality"]
    
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
    os.makedirs(out_dir, exist_ok=True)
    
    # --- Ablation 1: Verifier Components ---
    print("\n--- Running Ablation 1: Verifier Components ---")
    ablation_modes = [
        {"name": "Full Verifier (DFA + Data)", "dfa": True, "data": True},
        {"name": "Structural-Only (DFA Only)", "dfa": True, "data": False},
        {"name": "Data-Only (Data Only)", "dfa": False, "data": True},
        {"name": "No Verifier (Control)", "dfa": False, "data": False}
    ]
    
    comp_results = []
    for mode in ablation_modes:
        print(f"Testing mode: {mode['name']}...")
        for task_name in tasks:
            task = load_task(task_name)
            for trial in range(num_trials):
                seed = 100 + trial
                workspace = tempfile.mkdtemp()
                try:
                    res = run_ablation_trial(task, workspace, matrix_csv, mode['dfa'], mode['data'], max_retries=5, seed=seed)
                    res['mode'] = mode['name']
                    comp_results.append(res)
                finally:
                    shutil.rmtree(workspace)
                    
    df_comp = pd.DataFrame(comp_results)
    df_comp.to_csv(os.path.join(out_dir, "ablation_results_verifier.csv"), index=False)
    
    summary_comp = df_comp.groupby(['mode']).agg({
        'completed': 'mean',
        'score': 'mean',
        'steps_proposed': 'mean',
        'repairs': 'mean',
        'validation_errors': 'mean'
    }).reset_index()
    
    print("\n========================= VERIFIER COMPONENT ABLATION SUMMARY =========================")
    print(summary_comp.to_string(index=False))
    
    # --- Ablation 2: Retry Budget ---
    print("\n--- Running Ablation 2: Retry Budget ---")
    budgets = [0, 1, 2, 3, 5, 8, 12]
    
    budget_results = []
    for budget in budgets:
        print(f"Testing retry budget: {budget}...")
        for task_name in tasks:
            task = load_task(task_name)
            for trial in range(num_trials):
                seed = 200 + trial
                workspace = tempfile.mkdtemp()
                try:
                    res = run_ablation_trial(task, workspace, matrix_csv, enable_dfa=True, enable_data=True, max_retries=budget, seed=seed)
                    res['budget'] = budget
                    budget_results.append(res)
                finally:
                    shutil.rmtree(workspace)
                    
    df_budget = pd.DataFrame(budget_results)
    df_budget.to_csv(os.path.join(out_dir, "ablation_results_budget.csv"), index=False)
    
    summary_budget = df_budget.groupby(['budget']).agg({
        'completed': 'mean',
        'score': 'mean',
        'steps_proposed': 'mean',
        'repairs': 'mean',
        'validation_errors': 'mean'
    }).reset_index()
    
    print("\n========================= RETRY BUDGET ABLATION SUMMARY =========================")
    print(summary_budget.to_string(index=False))
    
    return df_comp, df_budget

if __name__ == "__main__":
    run_ablations()
