"""DFA verifier for NeuroGolf multi-agent system traces."""

from enum import Enum, auto
from typing import Optional, Any

from .neurogolf_trace_language import OpSymbol, TraceStep


class DFAState(Enum):
    INIT = auto()
    ANALYZED = auto()
    DATA_PREP = auto()
    AUTO_ML_SEARCH = auto()
    ADVANCED_LEARNING = auto()
    BUILT = auto()
    OPTIMIZED = auto()
    V_TRAIN = auto()
    V_TEST = auto()
    V_ARC = auto()
    V_KFOLD = auto()
    V_HYPOTHESIS = auto()
    V_DATAVALID = auto()
    V_EARLYSTOP = auto()
    V_GOVERNANCE = auto()
    COSTED = auto()
    BLENDED = auto()
    PACKAGED = auto()
    SUBMITTED = auto()
    REJECTED = auto()
    ERROR = auto()


_TRANSITIONS: dict[tuple[DFAState, OpSymbol], DFAState] = {
    (DFAState.INIT, OpSymbol.ANALYZE_TASK): DFAState.ANALYZED,
    (DFAState.INIT, OpSymbol.DISCOVER_BUNDLE): DFAState.INIT,
    (DFAState.INIT, OpSymbol.LOAD_FLOOR): DFAState.INIT,
    (DFAState.ANALYZED, OpSymbol.DISCOVER_PATTERN): DFAState.ANALYZED,
    (DFAState.ANALYZED, OpSymbol.ANALYZE_TASK): DFAState.ANALYZED,
    (DFAState.ANALYZED, OpSymbol.DISCOVER_BUNDLE): DFAState.ANALYZED,
    (DFAState.ANALYZED, OpSymbol.LOAD_FLOOR): DFAState.ANALYZED,
    (DFAState.ANALYZED, OpSymbol.BUILD_ONNX): DFAState.BUILT,
    (DFAState.ANALYZED, OpSymbol.ENCODE_RULE): DFAState.BUILT,
    (DFAState.ANALYZED, OpSymbol.CONVOLUTION): DFAState.BUILT,
    (DFAState.ANALYZED, OpSymbol.LABEL_PROPAGATE): DFAState.BUILT,
    (DFAState.ANALYZED, OpSymbol.SCATTERND_HIST): DFAState.BUILT,
    (DFAState.ANALYZED, OpSymbol.SELF_ATTENTION): DFAState.BUILT,
    (DFAState.ANALYZED, OpSymbol.REJECT): DFAState.REJECTED,
    
    # Advanced Data Science Prep
    (DFAState.ANALYZED, OpSymbol.DATA_AUGMENTATION): DFAState.DATA_PREP,
    (DFAState.DATA_PREP, OpSymbol.DATA_AUGMENTATION): DFAState.DATA_PREP,
    (DFAState.DATA_PREP, OpSymbol.FEW_SHOT_LEARNING): DFAState.ADVANCED_LEARNING,
    (DFAState.ADVANCED_LEARNING, OpSymbol.FEW_SHOT_LEARNING): DFAState.ADVANCED_LEARNING,
    
    # AutoML search transitions
    (DFAState.ANALYZED, OpSymbol.MCTS_SEARCH): DFAState.AUTO_ML_SEARCH,
    (DFAState.ANALYZED, OpSymbol.HYPERPARAM_OPT): DFAState.AUTO_ML_SEARCH,
    (DFAState.ANALYZED, OpSymbol.AUTO_ML): DFAState.AUTO_ML_SEARCH,
    
    (DFAState.DATA_PREP, OpSymbol.MCTS_SEARCH): DFAState.AUTO_ML_SEARCH,
    (DFAState.DATA_PREP, OpSymbol.HYPERPARAM_OPT): DFAState.AUTO_ML_SEARCH,
    (DFAState.DATA_PREP, OpSymbol.AUTO_ML): DFAState.AUTO_ML_SEARCH,
    
    (DFAState.ADVANCED_LEARNING, OpSymbol.MCTS_SEARCH): DFAState.AUTO_ML_SEARCH,
    (DFAState.ADVANCED_LEARNING, OpSymbol.HYPERPARAM_OPT): DFAState.AUTO_ML_SEARCH,
    (DFAState.ADVANCED_LEARNING, OpSymbol.AUTO_ML): DFAState.AUTO_ML_SEARCH,
    
    (DFAState.AUTO_ML_SEARCH, OpSymbol.MCTS_SEARCH): DFAState.AUTO_ML_SEARCH,
    (DFAState.AUTO_ML_SEARCH, OpSymbol.HYPERPARAM_OPT): DFAState.AUTO_ML_SEARCH,
    (DFAState.AUTO_ML_SEARCH, OpSymbol.AUTO_ML): DFAState.AUTO_ML_SEARCH,
    
    # Transitions to BUILT from advanced/AutoML states
    (DFAState.DATA_PREP, OpSymbol.BUILD_ONNX): DFAState.BUILT,
    (DFAState.DATA_PREP, OpSymbol.ENCODE_RULE): DFAState.BUILT,
    (DFAState.DATA_PREP, OpSymbol.CONVOLUTION): DFAState.BUILT,
    (DFAState.DATA_PREP, OpSymbol.LABEL_PROPAGATE): DFAState.BUILT,
    (DFAState.DATA_PREP, OpSymbol.SCATTERND_HIST): DFAState.BUILT,
    (DFAState.DATA_PREP, OpSymbol.SELF_ATTENTION): DFAState.BUILT,
    
    (DFAState.ADVANCED_LEARNING, OpSymbol.BUILD_ONNX): DFAState.BUILT,
    (DFAState.ADVANCED_LEARNING, OpSymbol.ENCODE_RULE): DFAState.BUILT,
    (DFAState.ADVANCED_LEARNING, OpSymbol.CONVOLUTION): DFAState.BUILT,
    (DFAState.ADVANCED_LEARNING, OpSymbol.LABEL_PROPAGATE): DFAState.BUILT,
    (DFAState.ADVANCED_LEARNING, OpSymbol.SCATTERND_HIST): DFAState.BUILT,
    (DFAState.ADVANCED_LEARNING, OpSymbol.SELF_ATTENTION): DFAState.BUILT,
    
    (DFAState.AUTO_ML_SEARCH, OpSymbol.BUILD_ONNX): DFAState.BUILT,
    (DFAState.AUTO_ML_SEARCH, OpSymbol.ENCODE_RULE): DFAState.BUILT,
    (DFAState.AUTO_ML_SEARCH, OpSymbol.CONVOLUTION): DFAState.BUILT,
    (DFAState.AUTO_ML_SEARCH, OpSymbol.LABEL_PROPAGATE): DFAState.BUILT,
    (DFAState.AUTO_ML_SEARCH, OpSymbol.SCATTERND_HIST): DFAState.BUILT,
    (DFAState.AUTO_ML_SEARCH, OpSymbol.SELF_ATTENTION): DFAState.BUILT,
    
    # Rejects from new states
    (DFAState.DATA_PREP, OpSymbol.REJECT): DFAState.REJECTED,
    (DFAState.ADVANCED_LEARNING, OpSymbol.REJECT): DFAState.REJECTED,
    (DFAState.AUTO_ML_SEARCH, OpSymbol.REJECT): DFAState.REJECTED,
    
    # Post-build operations (Self-Attention, Ensemble, Transfer)
    (DFAState.BUILT, OpSymbol.SELF_ATTENTION): DFAState.BUILT,
    (DFAState.BUILT, OpSymbol.ENSEMBLE_LEARNING): DFAState.BUILT,
    (DFAState.BUILT, OpSymbol.TRANSFER_LEARNING): DFAState.BUILT,
    (DFAState.BUILT, OpSymbol.BUILD_ONNX): DFAState.BUILT,
    
    # Standard BUILT transitions
    (DFAState.BUILT, OpSymbol.FP16_SURGERY): DFAState.OPTIMIZED,
    (DFAState.BUILT, OpSymbol.CAST_COLLAPSE): DFAState.OPTIMIZED,
    (DFAState.BUILT, OpSymbol.REDUCE_FUSION): DFAState.OPTIMIZED,
    (DFAState.BUILT, OpSymbol.DTYPE_NARROW): DFAState.OPTIMIZED,
    (DFAState.BUILT, OpSymbol.PRUNE): DFAState.OPTIMIZED,
    (DFAState.BUILT, OpSymbol.GRAPH_REWRITE): DFAState.OPTIMIZED,
    (DFAState.BUILT, OpSymbol.DIM_SCRUB): DFAState.OPTIMIZED,
    (DFAState.BUILT, OpSymbol.VERIFY_TRAIN): DFAState.V_TRAIN,
    (DFAState.BUILT, OpSymbol.COMPUTE_COST): DFAState.COSTED,
    (DFAState.BUILT, OpSymbol.REJECT): DFAState.REJECTED,
    
    # Standard OPTIMIZED transitions
    (DFAState.OPTIMIZED, OpSymbol.VERIFY_TRAIN): DFAState.V_TRAIN,
    (DFAState.OPTIMIZED, OpSymbol.COMPUTE_COST): DFAState.COSTED,
    (DFAState.OPTIMIZED, OpSymbol.ANALYZE_TASK): DFAState.ANALYZED,
    (DFAState.OPTIMIZED, OpSymbol.BUILD_ONNX): DFAState.BUILT,
    (DFAState.OPTIMIZED, OpSymbol.BLEND_BUNDLE): DFAState.BLENDED,
    (DFAState.OPTIMIZED, OpSymbol.REJECT): DFAState.REJECTED,
    (DFAState.OPTIMIZED, OpSymbol.FP16_SURGERY): DFAState.OPTIMIZED,
    (DFAState.OPTIMIZED, OpSymbol.REDUCE_FUSION): DFAState.OPTIMIZED,
    (DFAState.OPTIMIZED, OpSymbol.CAST_COLLAPSE): DFAState.OPTIMIZED,
    (DFAState.OPTIMIZED, OpSymbol.DTYPE_NARROW): DFAState.OPTIMIZED,
    (DFAState.OPTIMIZED, OpSymbol.PRUNE): DFAState.OPTIMIZED,
    (DFAState.OPTIMIZED, OpSymbol.GRAPH_REWRITE): DFAState.OPTIMIZED,
    (DFAState.OPTIMIZED, OpSymbol.DIM_SCRUB): DFAState.OPTIMIZED,
    (DFAState.OPTIMIZED, OpSymbol.SELF_ATTENTION): DFAState.OPTIMIZED,
    (DFAState.OPTIMIZED, OpSymbol.ENSEMBLE_LEARNING): DFAState.OPTIMIZED,
    (DFAState.OPTIMIZED, OpSymbol.TRANSFER_LEARNING): DFAState.OPTIMIZED,
    
    # Standard V_TRAIN transitions
    (DFAState.V_TRAIN, OpSymbol.VERIFY_TEST): DFAState.V_TEST,
    (DFAState.V_TRAIN, OpSymbol.ANALYZE_TASK): DFAState.ANALYZED,
    (DFAState.V_TRAIN, OpSymbol.COMPUTE_COST): DFAState.COSTED,
    (DFAState.V_TRAIN, OpSymbol.REJECT): DFAState.REJECTED,
    (DFAState.V_TRAIN, OpSymbol.BUILD_ONNX): DFAState.BUILT,
    (DFAState.V_TRAIN, OpSymbol.GRAPH_REWRITE): DFAState.OPTIMIZED,
    (DFAState.V_TRAIN, OpSymbol.DIM_SCRUB): DFAState.OPTIMIZED,
    
    # Standard V_TEST transitions
    (DFAState.V_TEST, OpSymbol.VERIFY_ARC_GEN): DFAState.V_ARC,
    (DFAState.V_TEST, OpSymbol.COMPUTE_COST): DFAState.COSTED,
    (DFAState.V_TEST, OpSymbol.ANALYZE_TASK): DFAState.ANALYZED,
    (DFAState.V_TEST, OpSymbol.REJECT): DFAState.REJECTED,
    (DFAState.V_TEST, OpSymbol.BUILD_ONNX): DFAState.BUILT,
    (DFAState.V_TEST, OpSymbol.GRAPH_REWRITE): DFAState.OPTIMIZED,
    (DFAState.V_TEST, OpSymbol.DIM_SCRUB): DFAState.OPTIMIZED,
    
    # Standard V_ARC transitions
    (DFAState.V_ARC, OpSymbol.COMPUTE_COST): DFAState.COSTED,
    (DFAState.V_ARC, OpSymbol.BLEND_BUNDLE): DFAState.BLENDED,
    (DFAState.V_ARC, OpSymbol.ANALYZE_TASK): DFAState.ANALYZED,
    (DFAState.V_ARC, OpSymbol.BUILD_ONNX): DFAState.BUILT,
    (DFAState.V_ARC, OpSymbol.REJECT): DFAState.REJECTED,
    (DFAState.V_ARC, OpSymbol.GRAPH_REWRITE): DFAState.OPTIMIZED,
    (DFAState.V_ARC, OpSymbol.DIM_SCRUB): DFAState.OPTIMIZED,
    (DFAState.V_ARC, OpSymbol.DISCOVER_BUNDLE): DFAState.V_ARC,
    (DFAState.V_ARC, OpSymbol.LOAD_FLOOR): DFAState.V_ARC,
    (DFAState.V_ARC, OpSymbol.K_FOLD_CV): DFAState.V_KFOLD,
    
    # Extended V&V transitions
    (DFAState.V_KFOLD, OpSymbol.HYPOTHESIS_TEST): DFAState.V_HYPOTHESIS,
    (DFAState.V_KFOLD, OpSymbol.REJECT): DFAState.REJECTED,
    (DFAState.V_KFOLD, OpSymbol.ANALYZE_TASK): DFAState.ANALYZED,
    (DFAState.V_KFOLD, OpSymbol.BUILD_ONNX): DFAState.BUILT,
    (DFAState.V_KFOLD, OpSymbol.GRAPH_REWRITE): DFAState.OPTIMIZED,
    (DFAState.V_KFOLD, OpSymbol.DIM_SCRUB): DFAState.OPTIMIZED,
    (DFAState.V_HYPOTHESIS, OpSymbol.DATA_VALIDATION): DFAState.V_DATAVALID,
    (DFAState.V_HYPOTHESIS, OpSymbol.REJECT): DFAState.REJECTED,
    (DFAState.V_HYPOTHESIS, OpSymbol.ANALYZE_TASK): DFAState.ANALYZED,
    (DFAState.V_HYPOTHESIS, OpSymbol.BUILD_ONNX): DFAState.BUILT,
    (DFAState.V_HYPOTHESIS, OpSymbol.GRAPH_REWRITE): DFAState.OPTIMIZED,
    (DFAState.V_HYPOTHESIS, OpSymbol.DIM_SCRUB): DFAState.OPTIMIZED,
    (DFAState.V_DATAVALID, OpSymbol.EARLY_STOPPING): DFAState.V_EARLYSTOP,
    (DFAState.V_DATAVALID, OpSymbol.REJECT): DFAState.REJECTED,
    (DFAState.V_DATAVALID, OpSymbol.ANALYZE_TASK): DFAState.ANALYZED,
    (DFAState.V_DATAVALID, OpSymbol.BUILD_ONNX): DFAState.BUILT,
    (DFAState.V_DATAVALID, OpSymbol.GRAPH_REWRITE): DFAState.OPTIMIZED,
    (DFAState.V_DATAVALID, OpSymbol.DIM_SCRUB): DFAState.OPTIMIZED,
    (DFAState.V_EARLYSTOP, OpSymbol.MODEL_GOVERNANCE): DFAState.V_GOVERNANCE,
    (DFAState.V_EARLYSTOP, OpSymbol.REJECT): DFAState.REJECTED,
    (DFAState.V_EARLYSTOP, OpSymbol.ANALYZE_TASK): DFAState.ANALYZED,
    (DFAState.V_EARLYSTOP, OpSymbol.BUILD_ONNX): DFAState.BUILT,
    (DFAState.V_EARLYSTOP, OpSymbol.GRAPH_REWRITE): DFAState.OPTIMIZED,
    (DFAState.V_EARLYSTOP, OpSymbol.DIM_SCRUB): DFAState.OPTIMIZED,
    (DFAState.V_GOVERNANCE, OpSymbol.COMPUTE_COST): DFAState.COSTED,
    (DFAState.V_GOVERNANCE, OpSymbol.REJECT): DFAState.REJECTED,
    (DFAState.V_GOVERNANCE, OpSymbol.ANALYZE_TASK): DFAState.ANALYZED,
    (DFAState.V_GOVERNANCE, OpSymbol.BUILD_ONNX): DFAState.BUILT,
    (DFAState.V_GOVERNANCE, OpSymbol.GRAPH_REWRITE): DFAState.OPTIMIZED,
    (DFAState.V_GOVERNANCE, OpSymbol.DIM_SCRUB): DFAState.OPTIMIZED,
    
    # Standard COSTED transitions
    (DFAState.COSTED, OpSymbol.BLEND_BUNDLE): DFAState.BLENDED,
    (DFAState.COSTED, OpSymbol.SHA256_CHECK): DFAState.COSTED,
    (DFAState.COSTED, OpSymbol.SIZE_AUDIT): DFAState.COSTED,
    (DFAState.COSTED, OpSymbol.PACKAGE_SUBMISSION): DFAState.PACKAGED,
    (DFAState.COSTED, OpSymbol.COMPUTE_COST): DFAState.COSTED,
    (DFAState.COSTED, OpSymbol.ANALYZE_TASK): DFAState.ANALYZED,
    (DFAState.COSTED, OpSymbol.VERIFY_TRAIN): DFAState.V_TRAIN,
    (DFAState.COSTED, OpSymbol.VERIFY_TEST): DFAState.V_TEST,
    (DFAState.COSTED, OpSymbol.VERIFY_ARC_GEN): DFAState.V_ARC,
    (DFAState.COSTED, OpSymbol.BUILD_ONNX): DFAState.BUILT,
    (DFAState.COSTED, OpSymbol.GRAPH_REWRITE): DFAState.OPTIMIZED,
    (DFAState.COSTED, OpSymbol.DIM_SCRUB): DFAState.OPTIMIZED,
    (DFAState.COSTED, OpSymbol.DISCOVER_BUNDLE): DFAState.COSTED,
    (DFAState.COSTED, OpSymbol.LOAD_FLOOR): DFAState.COSTED,
    
    # Blending & Packaging transitions
    (DFAState.BLENDED, OpSymbol.PACKAGE_SUBMISSION): DFAState.PACKAGED,
    (DFAState.BLENDED, OpSymbol.SHA256_CHECK): DFAState.BLENDED,
    (DFAState.BLENDED, OpSymbol.COMPUTE_COST): DFAState.COSTED,
    (DFAState.BLENDED, OpSymbol.BLEND_BUNDLE): DFAState.BLENDED,
    (DFAState.PACKAGED, OpSymbol.SUBMIT): DFAState.SUBMITTED,
    (DFAState.PACKAGED, OpSymbol.SHA256_CHECK): DFAState.PACKAGED,
    (DFAState.PACKAGED, OpSymbol.BLEND_BUNDLE): DFAState.BLENDED,
    (DFAState.PACKAGED, OpSymbol.PACKAGE_SUBMISSION): DFAState.PACKAGED,
    
    # Terminal transitions
    (DFAState.REJECTED, OpSymbol.HALT): DFAState.REJECTED,
    (DFAState.SUBMITTED, OpSymbol.HALT): DFAState.SUBMITTED,
}

_ACCEPTING_STATES = {DFAState.SUBMITTED, DFAState.PACKAGED}

_OPTIMIZATION_OPS = {
    OpSymbol.FP16_SURGERY, OpSymbol.REDUCE_FUSION, OpSymbol.CAST_COLLAPSE,
    OpSymbol.DTYPE_NARROW, OpSymbol.PRUNE, OpSymbol.GRAPH_REWRITE,
    OpSymbol.DIM_SCRUB,
}

KEYWORD_COVERAGE = {
    "onnx", "onnxruntime", "convolution", "label_propagate", "scatternd",
    "blend", "sha256", "cost", "verify", "optimization", "fp16"
}


class VerifierResult:
    def __init__(self):
        self.accepted = False
        self.final_state = None
        self.step_results = []
        self.optimizations_applied = set()
        self.keywords_found = set()
        self.keywords_missing = set()
        self.coverage_ratio = 0.0
        self.errors = []
        self.warnings = []
        self.config_errors = []


def verify_trace(trace: list[TraceStep], code_text: str = "", log_text: str = "", min_optimizations: int = 1) -> VerifierResult:
    result = VerifierResult()
    state = DFAState.INIT
    
    combined_text = (code_text + "\n" + log_text).lower()
    if "not found" in combined_text:
        msg = "Configuration Error: 'not found' detected. Possible missing file or directory."
        result.config_errors.append(msg)
        result.errors.append(msg)
        
    if "glob(" in code_text and "[0]" in code_text:
        result.warnings.append("Implementation Warning: Detected list access [0] after a likely glob/search operation. May indicate single-execution loop.")
        
    if "ch=10" in combined_text:
        result.warnings.append("Performance Warning: Default configuration (e.g. CH=10) detected. Consider tuning parameters.")

    for i, step in enumerate(trace):
        if step.op in _OPTIMIZATION_OPS:
            result.optimizations_applied.add(step.op)
        
        key = (state, step.op)
        if key in _TRANSITIONS:
            state = _TRANSITIONS[key]
            result.step_results.append((i, step, True, f"-> {state.name}"))
        else:
            msg = f"No transition from {state.name} on {step.op.name}"
            result.step_results.append((i, step, False, msg))
            result.errors.append(msg)
            result.final_state = DFAState.ERROR
            return result
            
    result.final_state = state
    result.accepted = (state in _ACCEPTING_STATES) and (len(result.optimizations_applied) >= min_optimizations) and (len(result.config_errors) == 0)
    
    code_lower = code_text.lower()
    result.keywords_found = {kw for kw in KEYWORD_COVERAGE if kw in code_lower}
    result.keywords_missing = KEYWORD_COVERAGE - result.keywords_found
    result.coverage_ratio = len(result.keywords_found) / len(KEYWORD_COVERAGE) if KEYWORD_COVERAGE else 1.0
    
    return result

def make_initial_trace(task_ids: list[int]) -> list[TraceStep]:
    return [TraceStep(OpSymbol.ANALYZE_TASK, "task_analyzer", tid) for tid in task_ids]

def make_standard_pipeline(task_ids: list[int]) -> list[TraceStep]:
    from .neurogolf_mas import simulate_standard_pipeline
    return simulate_standard_pipeline(task_ids)
