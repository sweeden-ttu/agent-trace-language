import unittest
from framework.neurogolf_trace_language import OpSymbol, TraceStep
from framework.neurogolf_dfa_verifier import DFAState, verify_trace, make_standard_pipeline
from framework.neurogolf_mas import simulate_standard_pipeline

class TestNeuroGolfVerifier(unittest.TestCase):
    def setUp(self):
        self.task_ids = [1, 2]

    def test_standard_pipeline_verification(self):
        # Generate standard pipeline trace
        trace = simulate_standard_pipeline(self.task_ids, optimizers_per_task=2, verify_all=True)
        
        # Verify the trace
        result = verify_trace(trace, min_optimizations=1)
        self.assertTrue(result.accepted, f"Standard pipeline should be accepted. Errors: {result.errors}")
        self.assertEqual(result.final_state, DFAState.SUBMITTED)

    def test_advanced_pipeline_verification(self):
        # Generate advanced pipeline trace
        trace = simulate_standard_pipeline(self.task_ids, optimizers_per_task=2, verify_all=True, advanced_ml_pipeline=True)
        
        # Verify the trace
        result = verify_trace(trace, min_optimizations=1)
        self.assertTrue(result.accepted, f"Advanced pipeline should be accepted. Errors: {result.errors}")
        self.assertEqual(result.final_state, DFAState.SUBMITTED)

    def test_invalid_advanced_transition(self):
        # Data Augmentation must be followed by FEW_SHOT_LEARNING or AutoML, cannot build directly from DATA_PREP without BUILD_ONNX or SELF_ATTENTION?
        # Wait, our transitions actually DO allow DATA_PREP -> BUILD_ONNX (as optional shortcuts).
        # Let's test a sequence that is definitely invalid, e.g. FEW_SHOT_LEARNING before ANALYZE_TASK.
        trace = [
            TraceStep(OpSymbol.FEW_SHOT_LEARNING, "data_scientist", 1),
        ]
        result = verify_trace(trace)
        self.assertFalse(result.accepted)
        self.assertEqual(result.final_state, DFAState.ERROR)
        self.assertIn("No transition from INIT on FEW_SHOT_LEARNING", result.errors[0])

    def test_missing_essential_steps_advanced(self):
        # Test an incomplete trace that ends early
        trace = [
            TraceStep(OpSymbol.DISCOVER_BUNDLE, "scanner", None),
            TraceStep(OpSymbol.LOAD_FLOOR, "scanner", None),
            TraceStep(OpSymbol.ANALYZE_TASK, "analyzer", 1),
            TraceStep(OpSymbol.DATA_AUGMENTATION, "data_scientist", 1),
        ]
        result = verify_trace(trace)
        self.assertFalse(result.accepted, "Trace ending in DATA_PREP should not be accepted")
        self.assertEqual(result.final_state, DFAState.DATA_PREP)

if __name__ == '__main__':
    unittest.main()
