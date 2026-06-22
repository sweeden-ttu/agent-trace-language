"""NeuroGolf Trace Language — operation alphabet for ONNX solver multi-agent system."""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional


class OpSymbol(Enum):
    ANALYZE_TASK = auto()
    DISCOVER_PATTERN = auto()
    BUILD_ONNX = auto()
    ENCODE_RULE = auto()
    LABEL_PROPAGATE = auto()
    CONVOLUTION = auto()
    SCATTERND_HIST = auto()
    FP16_SURGERY = auto()
    CAST_COLLAPSE = auto()
    REDUCE_FUSION = auto()
    DTYPE_NARROW = auto()
    PRUNE = auto()
    GRAPH_REWRITE = auto()
    DIM_SCRUB = auto()
    VERIFY_TRAIN = auto()
    VERIFY_TEST = auto()
    VERIFY_ARC_GEN = auto()
    K_FOLD_CV = auto()
    HYPOTHESIS_TEST = auto()
    DATA_VALIDATION = auto()
    EARLY_STOPPING = auto()
    MODEL_GOVERNANCE = auto()
    COMPUTE_COST = auto()
    COST_GRADER_MATCH = auto()
    DISCOVER_BUNDLE = auto()
    LOAD_FLOOR = auto()
    BLEND_BUNDLE = auto()
    SHA256_CHECK = auto()
    SIZE_AUDIT = auto()
    PACKAGE_SUBMISSION = auto()
    SUBMIT = auto()
    REJECT = auto()
    HALT = auto()
    AUTO_ML = auto()
    MCTS_SEARCH = auto()
    SELF_ATTENTION = auto()
    FEW_SHOT_LEARNING = auto()
    DATA_AUGMENTATION = auto()
    HYPERPARAM_OPT = auto()
    ENSEMBLE_LEARNING = auto()
    TRANSFER_LEARNING = auto()


@dataclass
class TraceStep:
    op: OpSymbol
    agent: str
    task_id: Optional[int] = None
    detail: str = ""
    metadata: dict = field(default_factory=dict)


Sigma = {op: op.name.lower() for op in OpSymbol}
