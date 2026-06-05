"""NeuroGolf Trace Language — operation alphabet for ONNX solver multi-agent system."""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class OpSymbol(Enum):
    ANALYZE_TASK = auto()
    DISCOVER_PATTERN = auto()
    BUILD_ONNX = auto()
    ENCODE_RULE = auto()
    LABEL_PROPAGATE = auto()
    CONVOLUTION = auto()
    SCATTERND_HIST = auto()
    REDUCE_FUSION = auto()
    CAST_COLLAPSE = auto()
    DTYPE_NARROW = auto()
    FP16_SURGERY = auto()
    PRUNE = auto()
    GRAPH_REWRITE = auto()
    DIM_SCRUB = auto()
    VERIFY_TRAIN = auto()
    VERIFY_TEST = auto()
    VERIFY_ARC_GEN = auto()
    COMPUTE_COST = auto()
    COST_GRADER_MATCH = auto()
    DISCOVER_BUNDLE = auto()
    LOAD_FLOOR = auto()
    BLEND_BUNDLE = auto()
    SHA256_CHECK = auto()
    SIZE_AUDIT = auto()
    OUTPUT_SHAPE_CHECK = auto()
    BLEND_OPTIMIZE = auto()
    INFERENCE_TEST = auto()
    PACKAGE_SUBMISSION = auto()
    SUBMIT = auto()
    REJECT = auto()
    HALT = auto()


@dataclass
class TraceStep:
    op: OpSymbol
    agent: str
    task_id: Optional[int] = None
    detail: str = ""
    metadata: dict = field(default_factory=dict)


Sigma = {
    OpSymbol.ANALYZE_TASK: "analyze_task",
    OpSymbol.DISCOVER_PATTERN: "discover_pattern",
    OpSymbol.BUILD_ONNX: "build_onnx",
    OpSymbol.ENCODE_RULE: "encode_rule",
    OpSymbol.LABEL_PROPAGATE: "label_propagate",
    OpSymbol.CONVOLUTION: "convolution",
    OpSymbol.SCATTERND_HIST: "scatternd_histogram",
    OpSymbol.REDUCE_FUSION: "reduce_fusion",
    OpSymbol.CAST_COLLAPSE: "cast_collapse",
    OpSymbol.DTYPE_NARROW: "dtype_narrow",
    OpSymbol.FP16_SURGERY: "fp16_surgery",
    OpSymbol.PRUNE: "prune",
    OpSymbol.GRAPH_REWRITE: "graph_rewrite",
    OpSymbol.DIM_SCRUB: "dim_scrub",
    OpSymbol.VERIFY_TRAIN: "verify_train",
    OpSymbol.VERIFY_TEST: "verify_test",
    OpSymbol.VERIFY_ARC_GEN: "verify_arc_gen",
    OpSymbol.COMPUTE_COST: "compute_cost",
    OpSymbol.COST_GRADER_MATCH: "cost_grader_match",
    OpSymbol.DISCOVER_BUNDLE: "discover_bundle",
    OpSymbol.LOAD_FLOOR: "load_floor",
    OpSymbol.BLEND_BUNDLE: "blend_bundle",
    OpSymbol.SHA256_CHECK: "sha256_check",
    OpSymbol.SIZE_AUDIT: "size_audit",
    OpSymbol.OUTPUT_SHAPE_CHECK: "output_shape_check",
    OpSymbol.BLEND_OPTIMIZE: "blend_optimize",
    OpSymbol.INFERENCE_TEST: "inference_test",
    OpSymbol.PACKAGE_SUBMISSION: "package_submission",
    OpSymbol.SUBMIT: "submit",
    OpSymbol.REJECT: "reject",
    OpSymbol.HALT: "halt",
}
