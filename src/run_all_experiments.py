import os
import subprocess
import sys

def run_script(script_path):
    print(f"\n======================================================================")
    print(f"RUNNING: {script_path}")
    print(f"======================================================================")
    
    # We must add current directory to PYTHONPATH so imports resolve correctly
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath(os.path.dirname(__file__)) + ":" + env.get("PYTHONPATH", "")
    
    try:
        res = subprocess.run([sys.executable, script_path], env=env, capture_output=True, text=True, check=True)
        print(res.stdout)
    except subprocess.CalledProcessError as e:
        print(f"ERROR executing {script_path}:")
        print(e.stdout)
        print(e.stderr, file=sys.stderr)
        sys.exit(e.returncode)

def main():
    print("Starting comprehensive run of all 5 experiments...")
    
    base_dir = os.path.abspath(os.path.dirname(__file__))
    
    # Experiment 1 & Ablation 1/2
    run_script(os.path.join(base_dir, "run_experiments.py"))
    run_script(os.path.join(base_dir, "ablation.py"))
    
    # Experiment 2 (Class Compression)
    run_script(os.path.join(base_dir, "run_exp2_compression.py"))
    
    # Experiment 3 (Emergence)
    run_script(os.path.join(base_dir, "run_exp3_emergence.py"))
    
    # Experiment 4 (Analyzer)
    run_script(os.path.join(base_dir, "run_exp4_analyzer.py"))
    
    # Experiment 5 (Safety)
    run_script(os.path.join(base_dir, "run_exp5_safety.py"))
    
    print("======================================================================")
    print("ALL 5 EXPERIMENTS COMPLETED SUCCESSFULLY AND WRITTEN TO data/ DIR.")
    print("======================================================================")

if __name__ == "__main__":
    main()
