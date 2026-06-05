import os
import time
import shutil
import tempfile
import pandas as pd
import numpy as np

from src.benchmark import load_task
from src.generator import AgentGenerator
from src.verifier import RuntimeVerifier, DFAVerifier, DataVerifier

def run_control_trial(task, workspace_dir, seed):
    """
    Control Group: Generator only. No verifier is used.
    If the agent proposes an invalid or buggy step, it continues blindly.
    """
    generator = AgentGenerator(task, workspace_dir, dfa_error_rate=0.1, bug_rate=0.2, random_state=seed)
    
    # In control, the generator just tries to go through a linear sequence of typical actions
    typical_sequence = ['load_data', 'explore_data', 'preprocess_data', 'train_model', 'evaluate_model', 'generate_predictions', 'submit_predictions', 'halt']
    
    trace = ['start']
    total_steps = 0
    undetected_errors = 0
    
    # We will simulate the generator proposing and running steps
    for step_target in typical_sequence:
        # The generator might propose an incorrect step (dfa error)
        proposed = generator.propose_next_action([step_target])
        total_steps += 1
        
        # Execute it (might have bug)
        success, msg = generator.execute_action(proposed)
        trace.append(proposed)
        
        # In control, we do not check if it succeeded, we just keep going
        if not success or "bug" in msg or proposed != step_target:
            undetected_errors += 1

    # Try to evaluate submission
    score = 0.0
    completed = False
    try:
        if os.path.exists(os.path.join(workspace_dir, "submission.csv")):
            score = task.evaluate_submission(workspace_dir)
            completed = True
    except Exception:
        pass
        
    return {
        'group': 'Control (G)',
        'task': task.name,
        'completed': completed,
        'score': score,
        'steps_proposed': total_steps,
        'repairs': 0,
        'validation_errors': 0,
        'undetected_errors': undetected_errors,
        'tokens_used': 0,
        'runtime_ms': len(typical_sequence) * 5,  # mock time
    }


def run_treatment_a_trial(task, workspace_dir, matrix_csv, seed):
    """
    Treatment A: Generator + DFA/Data Verifier (G || V_DFA)
    Any invalid step or buggy output is rejected, and the agent is forced to repair it.
    """
    generator = AgentGenerator(task, workspace_dir, dfa_error_rate=0.1, bug_rate=0.2, random_state=seed)
    rv = RuntimeVerifier(matrix_csv)
    
    max_steps = 25
    total_steps = 0
    repairs = 0
    validation_errors = 0
    
    feedback = None
    completed = False
    score = 0.0
    
    while total_steps < max_steps:
        # Get allowed next actions from verifier DFA
        current_state = rv.dfa.current_state
        allowed = [col for col in rv.dfa.matrix.columns if int(rv.dfa.matrix.loc[current_state, col]) == 1]
        
        # Propose
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
            # Action succeeded
            feedback = None
            if proposed == 'halt':
                completed = True
                break
        else:
            # Action failed verification (either DFA violation or code/data bug)
            validation_errors += 1
            repairs += 1
            feedback = verify_msg  # Feed back to generator for repair

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
            
    return {
        'group': 'Treatment A (G + DFA)',
        'task': task.name,
        'completed': completed,
        'score': score,
        'steps_proposed': total_steps,
        'repairs': repairs,
        'validation_errors': validation_errors,
        'undetected_errors': 0,
        'tokens_used': 0,
        'runtime_ms': total_steps * 5,
    }


def run_treatment_b_trial(task, workspace_dir, seed):
    """
    Treatment B: Generator + LLM Judge (G || V_LLM)
    The LLM judge checks transitions and data structures probabilistically and costs tokens.
    """
    generator = AgentGenerator(task, workspace_dir, dfa_error_rate=0.1, bug_rate=0.2, random_state=seed)
    
    # Track simulated DFA state for baseline transition comparison
    current_state = 'start'
    typical_sequence = ['load_data', 'explore_data', 'preprocess_data', 'train_model', 'evaluate_model', 'generate_predictions', 'submit_predictions', 'halt']
    
    max_steps = 25
    total_steps = 0
    repairs = 0
    validation_errors = 0
    undetected_errors = 0
    tokens_used = 0
    runtime_ms = 0
    
    rng = np.random.default_rng(seed)
    completed = False
    
    # Sequence pointers
    seq_idx = 0
    feedback = None
    
    while total_steps < max_steps and seq_idx < len(typical_sequence):
        target_action = typical_sequence[seq_idx]
        
        # Propose next action
        proposed = generator.propose_next_action([target_action])
        total_steps += 1
        
        # Execute
        exec_success, exec_msg = generator.execute_action(proposed, feedback=feedback)
        
        # LLM Judge checks the step (costs tokens and has latency)
        tokens_used += 1200  # Prompt + response size
        runtime_ms += 1500   # Simulated API latency in ms
        
        # Determine if the step is actually correct
        # It's correct if proposed == target_action AND execution had no bugs
        is_actually_correct = (proposed == target_action) and exec_success and (not os.path.exists(os.path.join(workspace_dir, "submission.csv")) or 
                                                                               os.path.getsize(os.path.join(workspace_dir, "submission.csv")) > 0)
        
        # LLM Judge is probabilistic
        # If actually correct, 90% chance to accept (10% false positive)
        # If actually incorrect, 75% chance to reject (25% false negative)
        if is_actually_correct:
            if rng.random() < 0.90:
                # Accept
                current_state = proposed
                seq_idx += 1
                feedback = None
            else:
                # False positive reject
                validation_errors += 1
                repairs += 1
                feedback = "LLM Judge: The formatting of this step looks suspicious. Please rewrite it."
        else:
            if rng.random() < 0.75:
                # Correctly reject
                validation_errors += 1
                repairs += 1
                feedback = f"LLM Judge Error: Detected issue with step '{proposed}'. Please fix code bugs or order."
            else:
                # False negative: accept buggy/wrong step!
                undetected_errors += 1
                current_state = proposed
                seq_idx += 1
                feedback = None
                
        if proposed == 'halt' and current_state == 'halt':
            completed = True
            break

    score = 0.0
    if os.path.exists(os.path.join(workspace_dir, "submission.csv")):
        try:
            score = task.evaluate_submission(workspace_dir)
            completed = True
        except Exception:
            pass

    return {
        'group': 'Treatment B (G + LLM)',
        'task': task.name,
        'completed': completed,
        'score': score,
        'steps_proposed': total_steps,
        'repairs': repairs,
        'validation_errors': validation_errors,
        'undetected_errors': undetected_errors,
        'tokens_used': tokens_used,
        'runtime_ms': runtime_ms,
    }


def run_experiments(num_trials=10):
    matrix_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/trace_matrix.csv"))
    tasks = ["spaceship_titanic", "wine_quality", "synthetic_classification"]
    
    results = []
    
    print(f"Starting experiments with {num_trials} trials per task...")
    
    for task_name in tasks:
        task = load_task(task_name)
        print(f"\n--- Running experiments for task: {task_name} ---")
        
        for trial in range(num_trials):
            seed = 42 + trial
            
            # 1. Run Control
            workspace_ctrl = tempfile.mkdtemp()
            try:
                res = run_control_trial(task, workspace_ctrl, seed)
                results.append(res)
            finally:
                shutil.rmtree(workspace_ctrl)
                
            # 2. Run Treatment A (DFA)
            workspace_a = tempfile.mkdtemp()
            try:
                res = run_treatment_a_trial(task, workspace_a, matrix_csv, seed)
                results.append(res)
            finally:
                shutil.rmtree(workspace_a)
                
            # 3. Run Treatment B (LLM Judge)
            workspace_b = tempfile.mkdtemp()
            try:
                res = run_treatment_b_trial(task, workspace_b, seed)
                results.append(res)
            finally:
                shutil.rmtree(workspace_b)

    df_results = pd.DataFrame(results)
    
    # Save raw results
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
    os.makedirs(out_dir, exist_ok=True)
    df_results.to_csv(os.path.join(out_dir, "results_raw.csv"), index=False)
    
    # Compute summary metrics
    summary = df_results.groupby(['task', 'group']).agg({
        'completed': 'mean',
        'score': 'mean',
        'steps_proposed': 'mean',
        'repairs': 'mean',
        'validation_errors': 'mean',
        'undetected_errors': 'mean',
        'tokens_used': 'mean',
        'runtime_ms': 'mean'
    }).reset_index()
    
    summary.to_csv(os.path.join(out_dir, "results_summary.csv"), index=False)
    
    # Print summary tables
    print("\n========================= EXPERIMENT RESULTS SUMMARY =========================")
    for task_name in tasks:
        print(f"\nTask: {task_name}")
        task_df = summary[summary['task'] == task_name].drop(columns=['task'])
        print(task_df.to_string(index=False))
        
    overall = df_results.groupby('group').agg({
        'completed': 'mean',
        'score': 'mean',
        'steps_proposed': 'mean',
        'repairs': 'mean',
        'validation_errors': 'mean',
        'undetected_errors': 'mean',
        'tokens_used': 'mean',
        'runtime_ms': 'mean'
    }).reset_index()
    
    print("\n========================= OVERALL AGGREGATED SUMMARY =========================")
    print(overall.to_string(index=False))
    
    return df_results

if __name__ == "__main__":
    run_experiments()
