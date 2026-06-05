import os
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

class AgentGenerator:
    def __init__(self, task, workspace_dir, dfa_error_rate=0.1, bug_rate=0.2, random_state=201):
        self.task = task
        self.workspace_dir = workspace_dir
        self.dfa_error_rate = dfa_error_rate
        self.bug_rate = bug_rate
        self.random_state = random_state
        self.rng = np.random.default_rng(random_state)
        
        # State tracking
        self.current_action = 'start'
        self.history = ['start']
        
        # Track if a bug was fixed
        self.bug_fixed = {}

    def propose_next_action(self, allowed_next_actions):
        """
        Proposes the next action.
        With probability `dfa_error_rate`, the agent ignores the allowed transitions 
        and proposes a random action (violating structural safety).
        """
        all_actions = ['load_data', 'explore_data', 'preprocess_data', 'train_model', 'evaluate_model', 'generate_predictions', 'submit_predictions', 'halt']
        
        if self.rng.random() < self.dfa_error_rate:
            # Violate DFA: propose a random action from the entire list
            proposed = self.rng.choice(all_actions)
        else:
            # Follow DFA: propose one of the allowed actions
            if not allowed_next_actions:
                proposed = 'halt'
            else:
                proposed = self.rng.choice(allowed_next_actions)
        
        return proposed

    def execute_action(self, action, feedback=None):
        """
        Executes the proposed action on the workspace.
        With probability `bug_rate`, a bug is introduced unless feedback was provided
        which allows the agent to repair/fix the bug.
        """
        os.makedirs(self.workspace_dir, exist_ok=True)
        is_buggy = self.rng.random() < self.bug_rate
        
        # If feedback is provided, the agent attempts to fix the bug
        if feedback:
            is_buggy = False  # Fixed via feedback

        try:
            if action == 'load_data':
                # Correct behavior: copy files
                self.task.prepare_workspace(self.workspace_dir)
                if is_buggy:
                    # Bug: delete train.csv or test.csv
                    to_remove = self.rng.choice(['train.csv', 'test.csv'])
                    os.remove(os.path.join(self.workspace_dir, to_remove))

            elif action == 'explore_data':
                eda_path = os.path.join(self.workspace_dir, "eda_summary.txt")
                if is_buggy:
                    # Bug: write empty file or omit writing
                    if self.rng.random() < 0.5:
                        with open(eda_path, 'w') as f:
                            f.write("")
                else:
                    train_df = pd.read_csv(os.path.join(self.workspace_dir, "train.csv"))
                    cols = list(train_df.columns)
                    nulls = train_df.isnull().sum().to_dict()
                    with open(eda_path, 'w') as f:
                        f.write(f"Columns: {cols}\nNull values: {nulls}\n")

            elif action == 'preprocess_data':
                train_path = os.path.join(self.workspace_dir, "train.csv")
                test_path = os.path.join(self.workspace_dir, "test.csv")
                train_proc = os.path.join(self.workspace_dir, "train_processed.csv")
                test_proc = os.path.join(self.workspace_dir, "test_processed.csv")
                
                train_df = pd.read_csv(train_path)
                test_df = pd.read_csv(test_path)
                
                # Preprocess: separate features and impute nulls
                # Identify numeric and categorical columns
                numeric_cols = train_df.select_dtypes(include=[np.number]).columns
                categorical_cols = train_df.select_dtypes(exclude=[np.number]).columns
                
                if is_buggy:
                    # Bug: don't impute missing values
                    train_df.to_csv(train_proc, index=False)
                    test_df.to_csv(test_proc, index=False)
                else:
                    # Correct imputation
                    for col in train_df.columns:
                        if col == self.task.target_col or col == self.task.id_col:
                            continue
                        if col in numeric_cols:
                            mean_val = train_df[col].mean()
                            if pd.isna(mean_val):
                                mean_val = 0
                            train_df[col] = train_df[col].fillna(mean_val)
                            if col in test_df.columns:
                                test_df[col] = test_df[col].fillna(mean_val)
                        else:
                            mode_val = train_df[col].mode().dropna()
                            mode_val = mode_val.iloc[0] if len(mode_val) > 0 else 'Unknown'
                            train_df[col] = train_df[col].fillna(mode_val)
                            if col in test_df.columns:
                                test_df[col] = test_df[col].fillna(mode_val)
                                
                    # Drop columns that are tricky or raw (like Cabin, Name in Spaceship Titanic)
                    cols_to_drop = ['Cabin', 'Name']
                    train_df = train_df.drop(columns=cols_to_drop, errors='ignore')
                    test_df = test_df.drop(columns=cols_to_drop, errors='ignore')
                    
                    # Convert categoricals to dummy variables
                    all_df = pd.concat([train_df.assign(is_train=1), test_df.assign(is_train=0)], sort=False)
                    cat_cols_to_encode = [c for c in categorical_cols if c not in cols_to_drop and c != self.task.id_col and c != self.task.target_col]
                    all_df = pd.get_dummies(all_df, columns=cat_cols_to_encode, drop_first=True)
                    
                    # Align train and test
                    train_df = all_df[all_df['is_train'] == 1].drop(columns=['is_train'])
                    test_df = all_df[all_df['is_train'] == 0].drop(columns=['is_train', self.task.target_col], errors='ignore')
                    
                    train_df.to_csv(train_proc, index=False)
                    test_df.to_csv(test_proc, index=False)

            elif action == 'train_model':
                model_path = os.path.join(self.workspace_dir, "model.pkl")
                if is_buggy:
                    # Bug: omit model saving
                    pass
                else:
                    train_proc = os.path.join(self.workspace_dir, "train_processed.csv")
                    train_df = pd.read_csv(train_proc)
                    
                    X = train_df.drop(columns=[self.task.id_col, self.task.target_col])
                    y = train_df[self.task.target_col]
                    
                    # Train Random Forest model
                    model = RandomForestClassifier(random_state=42, n_estimators=50)
                    model.fit(X, y)
                    
                    with open(model_path, 'wb') as f:
                        pickle.dump((model, list(X.columns)), f)

            elif action == 'evaluate_model':
                eval_path = os.path.join(self.workspace_dir, "val_metrics.txt")
                if is_buggy:
                    # Bug: write wrong file format
                    with open(eval_path, 'w') as f:
                        f.write("Evaluation complete, model is good.")
                else:
                    # Compute out-of-fold or train-split validation score
                    train_proc = os.path.join(self.workspace_dir, "train_processed.csv")
                    train_df = pd.read_csv(train_proc)
                    X = train_df.drop(columns=[self.task.id_col, self.task.target_col])
                    y = train_df[self.task.target_col]
                    
                    with open(os.path.join(self.workspace_dir, "model.pkl"), 'rb') as f:
                        model, _ = pickle.load(f)
                    
                    # Simulating simple training score
                    score = model.score(X, y)
                    with open(eval_path, 'w') as f:
                        f.write(f"val_score: {score:.5f}\n")

            elif action == 'generate_predictions':
                sub_path = os.path.join(workspace_dir_sub := os.path.join(self.workspace_dir, "submission.csv"))
                if is_buggy:
                    # Bug: write malformed predictions (e.g. wrong columns, empty or wrong rows)
                    bug_type = self.rng.choice(['missing_col', 'wrong_length', 'null_values'])
                    test_df = pd.read_csv(os.path.join(self.workspace_dir, "test.csv"))
                    if bug_type == 'missing_col':
                        pd.DataFrame({'PassengerId': test_df[self.task.id_col]}).to_csv(sub_path, index=False)
                    elif bug_type == 'wrong_length':
                        pd.DataFrame({
                            'PassengerId': test_df[self.task.id_col].iloc[:-5],
                            'Transported': 0
                        }).to_csv(sub_path, index=False)
                    elif bug_type == 'null_values':
                        sub = pd.DataFrame({
                            'PassengerId': test_df[self.task.id_col],
                            'Transported': 0
                        })
                        sub.loc[0, 'Transported'] = np.nan
                        sub.to_csv(sub_path, index=False)
                else:
                    test_proc = os.path.join(self.workspace_dir, "test_processed.csv")
                    test_df = pd.read_csv(test_proc)
                    
                    with open(os.path.join(self.workspace_dir, "model.pkl"), 'rb') as f:
                        model, train_cols = pickle.load(f)
                    
                    # Align test features with training features
                    test_features = test_df.drop(columns=[self.task.id_col], errors='ignore')
                    # Add missing dummy columns with 0
                    for col in train_cols:
                        if col not in test_features.columns:
                            test_features[col] = 0
                    test_features = test_features[train_cols]
                    
                    preds = model.predict(test_features)
                    
                    sub = pd.DataFrame({
                        self.task.id_col: test_df[self.task.id_col],
                        self.task.target_col: preds
                    })
                    sub.to_csv(sub_path, index=False)

            elif action == 'submit_predictions':
                # Submission occurs via verifier callback
                pass

            elif action == 'halt':
                pass

        except Exception as e:
            return False, f"Execution failure on action '{action}': {str(e)}"
        
        return True, "Executed successfully"
