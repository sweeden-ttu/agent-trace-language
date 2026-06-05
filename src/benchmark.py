import os
import numpy as np
import pandas as pd
from sklearn.datasets import load_wine, make_classification

class TabularTask:
    def __init__(self, name, train_df, test_df, ground_truth_y, id_col, target_col):
        self.name = name
        self.train_df = train_df
        self.test_df = test_df
        self.ground_truth_y = ground_truth_y
        self.id_col = id_col
        self.target_col = target_col

    def prepare_workspace(self, workspace_dir):
        os.makedirs(workspace_dir, exist_ok=True)
        # Write train.csv and test.csv
        train_path = os.path.join(workspace_dir, "train.csv")
        test_path = os.path.join(workspace_dir, "test.csv")
        self.train_df.to_csv(train_path, index=False)
        # Test.csv doesn't contain target
        test_no_target = self.test_df.drop(columns=[self.target_col], errors='ignore')
        test_no_target.to_csv(test_path, index=False)
        return train_path, test_path

    def evaluate_submission(self, workspace_dir):
        sub_path = os.path.join(workspace_dir, "submission.csv")
        if not os.path.exists(sub_path):
            raise FileNotFoundError("submission.csv not found")
        sub_df = pd.read_csv(sub_path)
        
        # Merge sub with ground truth (test_df)
        merged = pd.merge(self.test_df[[self.id_col, self.target_col]], sub_df, on=self.id_col, suffixes=('_true', '_pred'))
        if len(merged) == 0:
            return 0.0
        
        # Accuracy score
        correct = (merged[self.target_col + '_true'] == merged[self.target_col + '_pred']).sum()
        accuracy = correct / len(merged)
        return accuracy


def get_spaceship_titanic_task():
    # Generate synthetic Spaceship Titanic data
    np.random.seed(42)
    n_samples = 400
    
    # Features
    passenger_ids = [f"{i:04d}_01" for i in range(1, n_samples + 1)]
    home_planets = np.random.choice(["Earth", "Europa", "Mars", None], size=n_samples, p=[0.5, 0.2, 0.2, 0.1])
    cryosleep = np.random.choice([True, False, None], size=n_samples, p=[0.3, 0.6, 0.1])
    cabins = [f"{np.random.choice(['B','C','E','F','G'])}/{np.random.randint(1,200)}/{np.random.choice(['P','S'])}" if np.random.rand() > 0.1 else None for _ in range(n_samples)]
    age = np.random.normal(28, 10, size=n_samples).clip(0, 80)
    age[np.random.rand(n_samples) < 0.05] = np.nan
    room_service = np.random.exponential(200, size=n_samples)
    room_service[np.random.rand(n_samples) < 0.1] = np.nan
    
    # Target
    # True relationship: Europa planet and CryoSleep = True, lower RoomService -> higher chance of Transported
    transported = []
    for i in range(n_samples):
        prob = 0.5
        if home_planets[i] == "Europa":
            prob += 0.2
        if cryosleep[i] is True:
            prob += 0.3
        if not np.isnan(room_service[i]) and room_service[i] > 500:
            prob -= 0.3
        transported.append(1 if np.random.rand() < prob else 0)
        
    df = pd.DataFrame({
        'PassengerId': passenger_ids,
        'HomePlanet': home_planets,
        'CryoSleep': cryosleep,
        'Cabin': cabins,
        'Age': age,
        'RoomService': room_service,
        'Transported': transported
    })
    
    # Train/Test split
    train_df = df.iloc[:250].copy()
    test_df = df.iloc[250:].copy()
    ground_truth = test_df['Transported'].values
    
    return TabularTask("spaceship_titanic", train_df, test_df, ground_truth, 'PassengerId', 'Transported')


def get_wine_quality_task():
    # Load wine dataset from sklearn
    data = load_wine(as_frame=True)
    df = data.frame
    df['PassengerId'] = [f"wine_{i}" for i in range(len(df))]
    
    # Target: binary target (class 1 vs others)
    df['Transported'] = (df['target'] == 1).astype(int)
    df = df.drop(columns=['target'])
    
    # Add a column with some NaNs to simulate real ML challenges
    np.random.seed(42)
    mag = df['magnesium'].values.copy()
    mask = np.random.rand(len(df)) < 0.15
    mag[mask] = np.nan
    df['magnesium'] = mag
    
    # Train/Test split
    train_df = df.iloc[:100].copy()
    test_df = df.iloc[100:].copy()
    ground_truth = test_df['Transported'].values
    
    return TabularTask("wine_quality", train_df, test_df, ground_truth, 'PassengerId', 'Transported')


def get_synthetic_classification_task():
    # Multi-feature synthetic task
    X, y = make_classification(n_samples=300, n_features=10, n_informative=6, n_redundant=4, random_state=42)
    df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(10)])
    df['PassengerId'] = [f"syn_{i}" for i in range(len(df))]
    df['Transported'] = y
    
    # Introduce missingness
    np.random.seed(42)
    for col in [f"feature_{i}" for i in range(3)]:
        mask = np.random.rand(len(df)) < 0.1
        df.loc[mask, col] = np.nan
        
    train_df = df.iloc[:200].copy()
    test_df = df.iloc[200:].copy()
    ground_truth = test_df['Transported'].values
    
    return TabularTask("synthetic_classification", train_df, test_df, ground_truth, 'PassengerId', 'Transported')


def load_task(task_name):
    if task_name == "spaceship_titanic":
        return get_spaceship_titanic_task()
    elif task_name == "wine_quality":
        return get_wine_quality_task()
    elif task_name == "synthetic_classification":
        return get_synthetic_classification_task()
    else:
        raise ValueError(f"Unknown task name: {task_name}")
