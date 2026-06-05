import os
import pandas as pd

class DFAVerifier:
    def __init__(self, matrix_csv_path):
        self.matrix_csv_path = matrix_csv_path
        self.matrix = pd.read_csv(matrix_csv_path, index_col=0)
        self.states = list(self.matrix.index)
        self.reset()

    def reset(self):
        self.current_state = 'start'
        self.trace = ['start']

    def is_valid_transition(self, next_state):
        if next_state not in self.matrix.columns:
            return False
        # Matrix cells are integers (1 or 0)
        val = self.matrix.loc[self.current_state, next_state]
        return int(val) == 1

    def advance(self, next_state):
        if not self.is_valid_transition(next_state):
            raise ValueError(f"Invalid transition from '{self.current_state}' to '{next_state}'")
        self.current_state = next_state
        self.trace.append(next_state)
        return True


class DataVerifier:
    def __init__(self):
        pass

    def check_load_data(self, workspace_dir):
        train_path = os.path.join(workspace_dir, "train.csv")
        test_path = os.path.join(workspace_dir, "test.csv")
        if not os.path.exists(train_path):
            return False, "Missing train.csv"
        if not os.path.exists(test_path):
            return False, "Missing test.csv"
        try:
            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)
            if train_df.empty or test_df.empty:
                return False, "Empty data files"
        except Exception as e:
            return False, f"Error reading CSVs: {str(e)}"
        return True, "Data successfully loaded"

    def check_explore_data(self, workspace_dir):
        # Expect an EDA summary file or print log
        eda_path = os.path.join(workspace_dir, "eda_summary.txt")
        if not os.path.exists(eda_path):
            return False, "Missing eda_summary.txt outlining features and null values"
        return True, "EDA check passed"

    def check_preprocess_data(self, workspace_dir):
        train_proc = os.path.join(workspace_dir, "train_processed.csv")
        test_proc = os.path.join(workspace_dir, "test_processed.csv")
        if not os.path.exists(train_proc) or not os.path.exists(test_proc):
            return False, "Processed files train_processed.csv/test_processed.csv not found"
        try:
            train_df = pd.read_csv(train_proc)
            test_df = pd.read_csv(test_proc)
            if train_df.isnull().sum().sum() > 0 or test_df.isnull().sum().sum() > 0:
                return False, "Processed files still contain null values!"
        except Exception as e:
            return False, f"Error reading processed CSVs: {str(e)}"
        return True, "Data preprocessing validated successfully"

    def check_train_model(self, workspace_dir):
        model_path = os.path.join(workspace_dir, "model.pkl")
        if not os.path.exists(model_path):
            return False, "Serialized model file model.pkl not found"
        return True, "Model training validated successfully"

    def check_evaluate_model(self, workspace_dir):
        eval_path = os.path.join(workspace_dir, "val_metrics.txt")
        if not os.path.exists(eval_path):
            return False, "Missing val_metrics.txt containing validation scores"
        try:
            with open(eval_path, 'r') as f:
                content = f.read()
                if "val_score" not in content:
                    return False, "val_metrics.txt must contain 'val_score'"
        except Exception as e:
            return False, f"Error reading val_metrics.txt: {str(e)}"
        return True, "Model evaluation validated successfully"

    def check_generate_predictions(self, workspace_dir):
        sub_path = os.path.join(workspace_dir, "submission.csv")
        test_path = os.path.join(workspace_dir, "test.csv")
        if not os.path.exists(sub_path):
            return False, "Missing submission.csv"
        try:
            sub_df = pd.read_csv(sub_path)
            test_df = pd.read_csv(test_path)
            
            # Check length match
            if len(sub_df) != len(test_df):
                return False, f"Predictions row count ({len(sub_df)}) does not match test set ({len(test_df)})"
            
            # Check expected columns
            if 'PassengerId' not in sub_df.columns or 'Transported' not in sub_df.columns:
                return False, "submission.csv columns must contain 'PassengerId' and 'Transported'"
                
            # Check for nulls
            if sub_df['Transported'].isnull().any():
                return False, "submission.csv contains null predictions"
        except Exception as e:
            return False, f"Error verifying submission.csv: {str(e)}"
        return True, "Predictions generation validated successfully"

    def check_submit_predictions(self, workspace_dir, evaluate_fn=None):
        if evaluate_fn is None:
            return True, "Skipped evaluation callback"
        try:
            score = evaluate_fn(workspace_dir)
            score_path = os.path.join(workspace_dir, "leaderboard_score.txt")
            with open(score_path, 'w') as f:
                f.write(f"accuracy: {score:.5f}\n")
            return True, f"Submission accepted! Score: {score:.4f}"
        except Exception as e:
            return False, f"Error checking submission score: {str(e)}"

    def check_halt(self, workspace_dir):
        return True, "Halted successfully"


class RuntimeVerifier:
    def __init__(self, matrix_csv_path):
        self.dfa = DFAVerifier(matrix_csv_path)
        self.data_verifier = DataVerifier()

    def reset(self):
        self.dfa.reset()

    def verify_step(self, action, workspace_dir, evaluate_fn=None):
        # 1. Structural check
        if not self.dfa.is_valid_transition(action):
            return False, f"DFA Transition Error: Cannot move from '{self.dfa.current_state}' to '{action}'"

        # 2. Data check
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
        self.dfa.advance(action)
        return True, msg
