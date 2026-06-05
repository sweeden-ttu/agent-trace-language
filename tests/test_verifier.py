import os
import shutil
import unittest
import tempfile
import pandas as pd
from src.verifier import DFAVerifier, DataVerifier, RuntimeVerifier

class TestVerifier(unittest.TestCase):
    def setUp(self):
        self.matrix_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/trace_matrix.csv"))
        self.temp_workspace = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_workspace)

    def test_dfa_valid_sequence(self):
        dfa = DFAVerifier(self.matrix_csv)
        self.assertEqual(dfa.current_state, 'start')
        
        # Valid path
        self.assertTrue(dfa.is_valid_transition('load_data'))
        dfa.advance('load_data')
        self.assertEqual(dfa.current_state, 'load_data')
        
        self.assertTrue(dfa.is_valid_transition('explore_data'))
        dfa.advance('explore_data')
        
        self.assertTrue(dfa.is_valid_transition('preprocess_data'))
        dfa.advance('preprocess_data')
        
        self.assertTrue(dfa.is_valid_transition('train_model'))
        dfa.advance('train_model')
        
        self.assertTrue(dfa.is_valid_transition('evaluate_model'))
        dfa.advance('evaluate_model')
        
        self.assertTrue(dfa.is_valid_transition('generate_predictions'))
        dfa.advance('generate_predictions')
        
        self.assertTrue(dfa.is_valid_transition('submit_predictions'))
        dfa.advance('submit_predictions')
        
        self.assertTrue(dfa.is_valid_transition('halt'))
        dfa.advance('halt')
        self.assertEqual(dfa.trace, ['start', 'load_data', 'explore_data', 'preprocess_data', 'train_model', 'evaluate_model', 'generate_predictions', 'submit_predictions', 'halt'])

    def test_dfa_invalid_transition(self):
        dfa = DFAVerifier(self.matrix_csv)
        # Directly trying to train model should fail
        self.assertFalse(dfa.is_valid_transition('train_model'))
        with self.assertRaises(ValueError):
            dfa.advance('train_model')

    def test_data_verifier_checks(self):
        verifier = DataVerifier()
        
        # Check load data failure
        passed, msg = verifier.check_load_data(self.temp_workspace)
        self.assertFalse(passed)
        self.assertIn("Missing train.csv", msg)
        
        # Write empty files
        train_file = os.path.join(self.temp_workspace, "train.csv")
        test_file = os.path.join(self.temp_workspace, "test.csv")
        pd.DataFrame({'a': [1]}).to_csv(train_file, index=False)
        pd.DataFrame({'a': [1]}).to_csv(test_file, index=False)
        
        passed, msg = verifier.check_load_data(self.temp_workspace)
        self.assertTrue(passed)
        
        # Check explore data failure
        passed, msg = verifier.check_explore_data(self.temp_workspace)
        self.assertFalse(passed)
        self.assertIn("Missing eda_summary.txt", msg)
        
        # Write EDA summary
        with open(os.path.join(self.temp_workspace, "eda_summary.txt"), 'w') as f:
            f.write("EDA details here")
        passed, msg = verifier.check_explore_data(self.temp_workspace)
        self.assertTrue(passed)

    def test_runtime_verifier_integration(self):
        rv = RuntimeVerifier(self.matrix_csv)
        
        # 1. Try to load data without actual files on disk
        passed, msg = rv.verify_step('load_data', self.temp_workspace)
        self.assertFalse(passed)
        self.assertIn("Data Verification Error", msg)
        self.assertEqual(rv.dfa.current_state, 'start')  # State should NOT advance
        
        # 2. Add files and retry
        pd.DataFrame({'PassengerId': [1, 2], 'Transported': [0, 1]}).to_csv(os.path.join(self.temp_workspace, "train.csv"), index=False)
        pd.DataFrame({'PassengerId': [3, 4]}).to_csv(os.path.join(self.temp_workspace, "test.csv"), index=False)
        
        passed, msg = rv.verify_step('load_data', self.temp_workspace)
        self.assertTrue(passed)
        self.assertEqual(rv.dfa.current_state, 'load_data')

if __name__ == '__main__':
    unittest.main()
