"""DFA verifier for NeuroGolf multi-agent system traces.

Validates operation sequences and keyword coverage against the formal
trace language defined in neurogolf_trace_language.py.
"""

from enum import Enum, auto
from typing import Optional

from .neurogolf_trace_language import OpSymbol, TraceStep


class DFAState(Enum):
    Q_INIT = auto()
    Q_ANALYZED = auto()
    Q_BUILT = auto()
    Q_OPTIMIZED = auto()
    Q_VERIFIED_TRAIN = auto()
    Q_VERIFIED_TEST = auto()
    Q_VERIFIED_ARC_GEN = auto()
    Q_COSTED = auto()
    Q_BLENDED = auto()
    Q_PACKAGED = auto()
    Q_SUBMITTED = auto()
    Q_REJECTED = auto()
    Q_ERROR = auto()


# Transitions: (state, OpSymbol) -> state
_TRANSITIONS: dict[tuple[DFAState, OpSymbol], DFAState] = {
    # ── Initial: discover bundles or start analyzing ──
    (DFAState.Q_INIT, OpSymbol.ANALYZE_TASK): DFAState.Q_ANALYZED,
    (DFAState.Q_INIT, OpSymbol.DISCOVER_BUNDLE): DFAState.Q_INIT,
    (DFAState.Q_INIT, OpSymbol.LOAD_FLOOR): DFAState.Q_INIT,
    (DFAState.Q_INIT, OpSymbol.HALT): DFAState.Q_SUBMITTED,

    # ── Analyzed: discover patterns, build, or discover more bundles ──
    (DFAState.Q_ANALYZED, OpSymbol.DISCOVER_PATTERN): DFAState.Q_ANALYZED,
    (DFAState.Q_ANALYZED, OpSymbol.ANALYZE_TASK): DFAState.Q_ANALYZED,
    (DFAState.Q_ANALYZED, OpSymbol.DISCOVER_BUNDLE): DFAState.Q_ANALYZED,
    (DFAState.Q_ANALYZED, OpSymbol.LOAD_FLOOR): DFAState.Q_ANALYZED,
    (DFAState.Q_ANALYZED, OpSymbol.ENCODE_RULE): DFAState.Q_BUILT,
    (DFAState.Q_ANALYZED, OpSymbol.LABEL_PROPAGATE): DFAState.Q_BUILT,
    (DFAState.Q_ANALYZED, OpSymbol.CONVOLUTION): DFAState.Q_BUILT,
    (DFAState.Q_ANALYZED, OpSymbol.SCATTERND_HIST): DFAState.Q_BUILT,
    (DFAState.Q_ANALYZED, OpSymbol.BUILD_ONNX): DFAState.Q_BUILT,
    (DFAState.Q_ANALYZED, OpSymbol.REJECT): DFAState.Q_REJECTED,
    (DFAState.Q_ANALYZED, OpSymbol.HALT): DFAState.Q_SUBMITTED,

    # ── Built: optimize or verify ──
    (DFAState.Q_BUILT, OpSymbol.REDUCE_FUSION): DFAState.Q_OPTIMIZED,
    (DFAState.Q_BUILT, OpSymbol.CAST_COLLAPSE): DFAState.Q_OPTIMIZED,
    (DFAState.Q_BUILT, OpSymbol.DTYPE_NARROW): DFAState.Q_OPTIMIZED,
    (DFAState.Q_BUILT, OpSymbol.FP16_SURGERY): DFAState.Q_OPTIMIZED,
    (DFAState.Q_BUILT, OpSymbol.PRUNE): DFAState.Q_OPTIMIZED,
    (DFAState.Q_BUILT, OpSymbol.GRAPH_REWRITE): DFAState.Q_OPTIMIZED,
    (DFAState.Q_BUILT, OpSymbol.DIM_SCRUB): DFAState.Q_OPTIMIZED,
    (DFAState.Q_BUILT, OpSymbol.VERIFY_TRAIN): DFAState.Q_VERIFIED_TRAIN,
    (DFAState.Q_BUILT, OpSymbol.COMPUTE_COST): DFAState.Q_COSTED,
    (DFAState.Q_BUILT, OpSymbol.REJECT): DFAState.Q_REJECTED,

    # ── Optimized: further optimize, verify, or start next task ──
    (DFAState.Q_OPTIMIZED, OpSymbol.REDUCE_FUSION): DFAState.Q_OPTIMIZED,
    (DFAState.Q_OPTIMIZED, OpSymbol.CAST_COLLAPSE): DFAState.Q_OPTIMIZED,
    (DFAState.Q_OPTIMIZED, OpSymbol.DTYPE_NARROW): DFAState.Q_OPTIMIZED,
    (DFAState.Q_OPTIMIZED, OpSymbol.FP16_SURGERY): DFAState.Q_OPTIMIZED,
    (DFAState.Q_OPTIMIZED, OpSymbol.PRUNE): DFAState.Q_OPTIMIZED,
    (DFAState.Q_OPTIMIZED, OpSymbol.GRAPH_REWRITE): DFAState.Q_OPTIMIZED,
    (DFAState.Q_OPTIMIZED, OpSymbol.DIM_SCRUB): DFAState.Q_OPTIMIZED,
    (DFAState.Q_OPTIMIZED, OpSymbol.VERIFY_TRAIN): DFAState.Q_VERIFIED_TRAIN,
    (DFAState.Q_OPTIMIZED, OpSymbol.COMPUTE_COST): DFAState.Q_COSTED,
    (DFAState.Q_OPTIMIZED, OpSymbol.BLEND_BUNDLE): DFAState.Q_BLENDED,
    (DFAState.Q_OPTIMIZED, OpSymbol.REJECT): DFAState.Q_REJECTED,
    (DFAState.Q_OPTIMIZED, OpSymbol.BUILD_ONNX): DFAState.Q_BUILT,
    (DFAState.Q_OPTIMIZED, OpSymbol.ANALYZE_TASK): DFAState.Q_ANALYZED,
    (DFAState.Q_OPTIMIZED, OpSymbol.DISCOVER_PATTERN): DFAState.Q_ANALYZED,

    # ── Verified train: proceed to test, verify more, cost, or next task ──
    (DFAState.Q_VERIFIED_TRAIN, OpSymbol.VERIFY_TEST): DFAState.Q_VERIFIED_TEST,
    (DFAState.Q_VERIFIED_TRAIN, OpSymbol.VERIFY_TRAIN): DFAState.Q_VERIFIED_TRAIN,
    (DFAState.Q_VERIFIED_TRAIN, OpSymbol.REJECT): DFAState.Q_REJECTED,
    (DFAState.Q_VERIFIED_TRAIN, OpSymbol.BUILD_ONNX): DFAState.Q_BUILT,
    (DFAState.Q_VERIFIED_TRAIN, OpSymbol.ANALYZE_TASK): DFAState.Q_ANALYZED,
    (DFAState.Q_VERIFIED_TRAIN, OpSymbol.COMPUTE_COST): DFAState.Q_COSTED,
    (DFAState.Q_VERIFIED_TRAIN, OpSymbol.REDUCE_FUSION): DFAState.Q_OPTIMIZED,
    (DFAState.Q_VERIFIED_TRAIN, OpSymbol.CAST_COLLAPSE): DFAState.Q_OPTIMIZED,
    (DFAState.Q_VERIFIED_TRAIN, OpSymbol.GRAPH_REWRITE): DFAState.Q_OPTIMIZED,
    (DFAState.Q_VERIFIED_TRAIN, OpSymbol.DIM_SCRUB): DFAState.Q_OPTIMIZED,

    # ── Verified test: proceed to ARC-GEN, cost, optimize, or next task ──
    (DFAState.Q_VERIFIED_TEST, OpSymbol.VERIFY_ARC_GEN): DFAState.Q_VERIFIED_ARC_GEN,
    (DFAState.Q_VERIFIED_TEST, OpSymbol.VERIFY_TEST): DFAState.Q_VERIFIED_TEST,
    (DFAState.Q_VERIFIED_TEST, OpSymbol.REJECT): DFAState.Q_REJECTED,
    (DFAState.Q_VERIFIED_TEST, OpSymbol.COMPUTE_COST): DFAState.Q_COSTED,
    (DFAState.Q_VERIFIED_TEST, OpSymbol.BUILD_ONNX): DFAState.Q_BUILT,
    (DFAState.Q_VERIFIED_TEST, OpSymbol.ANALYZE_TASK): DFAState.Q_ANALYZED,
    (DFAState.Q_VERIFIED_TEST, OpSymbol.REDUCE_FUSION): DFAState.Q_OPTIMIZED,
    (DFAState.Q_VERIFIED_TEST, OpSymbol.CAST_COLLAPSE): DFAState.Q_OPTIMIZED,
    (DFAState.Q_VERIFIED_TEST, OpSymbol.DTYPE_NARROW): DFAState.Q_OPTIMIZED,
    (DFAState.Q_VERIFIED_TEST, OpSymbol.FP16_SURGERY): DFAState.Q_OPTIMIZED,
    (DFAState.Q_VERIFIED_TEST, OpSymbol.PRUNE): DFAState.Q_OPTIMIZED,
    (DFAState.Q_VERIFIED_TEST, OpSymbol.GRAPH_REWRITE): DFAState.Q_OPTIMIZED,
    (DFAState.Q_VERIFIED_TEST, OpSymbol.DIM_SCRUB): DFAState.Q_OPTIMIZED,

    # ── Verified ARC-GEN: cost, blend, rewrite, or next task ──
    (DFAState.Q_VERIFIED_ARC_GEN, OpSymbol.COMPUTE_COST): DFAState.Q_COSTED,
    (DFAState.Q_VERIFIED_ARC_GEN, OpSymbol.VERIFY_ARC_GEN): DFAState.Q_VERIFIED_ARC_GEN,
    (DFAState.Q_VERIFIED_ARC_GEN, OpSymbol.BLEND_BUNDLE): DFAState.Q_BLENDED,
    (DFAState.Q_VERIFIED_ARC_GEN, OpSymbol.GRAPH_REWRITE): DFAState.Q_OPTIMIZED,
    (DFAState.Q_VERIFIED_ARC_GEN, OpSymbol.DIM_SCRUB): DFAState.Q_OPTIMIZED,
    (DFAState.Q_VERIFIED_ARC_GEN, OpSymbol.REJECT): DFAState.Q_REJECTED,
    (DFAState.Q_VERIFIED_ARC_GEN, OpSymbol.BUILD_ONNX): DFAState.Q_BUILT,
    (DFAState.Q_VERIFIED_ARC_GEN, OpSymbol.ANALYZE_TASK): DFAState.Q_ANALYZED,
    (DFAState.Q_VERIFIED_ARC_GEN, OpSymbol.DISCOVER_BUNDLE): DFAState.Q_VERIFIED_ARC_GEN,
    (DFAState.Q_VERIFIED_ARC_GEN, OpSymbol.LOAD_FLOOR): DFAState.Q_VERIFIED_ARC_GEN,

    # ── Costed: re-grade, verify more, blend, rewrite, inference, shape-check, size-audit, package ──
    (DFAState.Q_COSTED, OpSymbol.COST_GRADER_MATCH): DFAState.Q_COSTED,
    (DFAState.Q_COSTED, OpSymbol.COMPUTE_COST): DFAState.Q_COSTED,
    (DFAState.Q_COSTED, OpSymbol.BLEND_BUNDLE): DFAState.Q_BLENDED,
    (DFAState.Q_COSTED, OpSymbol.INFERENCE_TEST): DFAState.Q_COSTED,
    (DFAState.Q_COSTED, OpSymbol.SHA256_CHECK): DFAState.Q_COSTED,
    (DFAState.Q_COSTED, OpSymbol.SIZE_AUDIT): DFAState.Q_COSTED,
    (DFAState.Q_COSTED, OpSymbol.PACKAGE_SUBMISSION): DFAState.Q_PACKAGED,
    (DFAState.Q_COSTED, OpSymbol.BUILD_ONNX): DFAState.Q_BUILT,
    (DFAState.Q_COSTED, OpSymbol.ANALYZE_TASK): DFAState.Q_ANALYZED,
    (DFAState.Q_COSTED, OpSymbol.VERIFY_TRAIN): DFAState.Q_VERIFIED_TRAIN,
    (DFAState.Q_COSTED, OpSymbol.VERIFY_TEST): DFAState.Q_VERIFIED_TEST,
    (DFAState.Q_COSTED, OpSymbol.VERIFY_ARC_GEN): DFAState.Q_VERIFIED_ARC_GEN,
    (DFAState.Q_COSTED, OpSymbol.REDUCE_FUSION): DFAState.Q_OPTIMIZED,
    (DFAState.Q_COSTED, OpSymbol.CAST_COLLAPSE): DFAState.Q_OPTIMIZED,
    (DFAState.Q_COSTED, OpSymbol.DTYPE_NARROW): DFAState.Q_OPTIMIZED,
    (DFAState.Q_COSTED, OpSymbol.FP16_SURGERY): DFAState.Q_OPTIMIZED,
    (DFAState.Q_COSTED, OpSymbol.PRUNE): DFAState.Q_OPTIMIZED,
    (DFAState.Q_COSTED, OpSymbol.GRAPH_REWRITE): DFAState.Q_OPTIMIZED,
    (DFAState.Q_COSTED, OpSymbol.DIM_SCRUB): DFAState.Q_OPTIMIZED,
    (DFAState.Q_COSTED, OpSymbol.DISCOVER_BUNDLE): DFAState.Q_COSTED,
    (DFAState.Q_COSTED, OpSymbol.LOAD_FLOOR): DFAState.Q_COSTED,

    # ── Blended: re-cost, re-blend, optimize-blend, shape-check, inference, sha256, package ──
    (DFAState.Q_BLENDED, OpSymbol.COMPUTE_COST): DFAState.Q_COSTED,
    (DFAState.Q_BLENDED, OpSymbol.BLEND_BUNDLE): DFAState.Q_BLENDED,
    (DFAState.Q_BLENDED, OpSymbol.BLEND_OPTIMIZE): DFAState.Q_BLENDED,
    (DFAState.Q_BLENDED, OpSymbol.OUTPUT_SHAPE_CHECK): DFAState.Q_BLENDED,
    (DFAState.Q_BLENDED, OpSymbol.INFERENCE_TEST): DFAState.Q_BLENDED,
    (DFAState.Q_BLENDED, OpSymbol.SHA256_CHECK): DFAState.Q_BLENDED,
    (DFAState.Q_BLENDED, OpSymbol.PACKAGE_SUBMISSION): DFAState.Q_PACKAGED,

    # ── Packaged: submit, re-blend, sha256 ──
    (DFAState.Q_PACKAGED, OpSymbol.SUBMIT): DFAState.Q_SUBMITTED,
    (DFAState.Q_PACKAGED, OpSymbol.SHA256_CHECK): DFAState.Q_PACKAGED,
    (DFAState.Q_PACKAGED, OpSymbol.BLEND_BUNDLE): DFAState.Q_BLENDED,
    (DFAState.Q_PACKAGED, OpSymbol.PACKAGE_SUBMISSION): DFAState.Q_PACKAGED,

    # ── Submitted: terminal ──
    (DFAState.Q_SUBMITTED, OpSymbol.HALT): DFAState.Q_SUBMITTED,

    # ── Rejected: terminal ──
    (DFAState.Q_REJECTED, OpSymbol.HALT): DFAState.Q_REJECTED,
}


BANNED_ONNX_OPS = frozenset({
    "Loop", "Scan", "NonZero", "Unique", "Compress",
})

_OPTIMIZATION_OPS = frozenset({
    OpSymbol.FP16_SURGERY, OpSymbol.REDUCE_FUSION, OpSymbol.CAST_COLLAPSE,
    OpSymbol.DTYPE_NARROW, OpSymbol.PRUNE, OpSymbol.GRAPH_REWRITE,
    OpSymbol.DIM_SCRUB,
})

OPTIMIZATION_KEYWORDS = frozenset({
    "fp16", "half_precision", "float16", "reduce_sum", "reduce_fusion",
    "cast_collapse", "dtype_narrow", "prune", "dim_scrub", "graph_rewrite",
    "kernel_time", "parameter_count", "memory_footprint",
    "cast_elimination", "squeeze", "reshape",
})

PIPELINE_KEYWORDS = frozenset({
    "onnx", "onnxruntime", "convolution", "label_propagate", "scatternd",
    "maxpool", "onehot", "blend", "sha256", "submission_zip", "floor",
    "artifact", "arc_gen", "train_verify", "test_verify", "verify_all",
    "cost", "discover", "bundle", "rejection", "validation", "banned",
    "shape_inference", "zero_cost", "passthrough", "output_shape_check",
    "blend_optimize", "inference_test",
})

KEYWORD_COVERAGE = OPTIMIZATION_KEYWORDS | PIPELINE_KEYWORDS


_ACCEPTING_STATES = frozenset({
    DFAState.Q_SUBMITTED,
    DFAState.Q_PACKAGED,
})


class VerifierResult:
    def __init__(self):
        self.accepted: bool = False
        self.final_state: Optional[DFAState] = None
        self.step_results: list[tuple[int, TraceStep, bool, str]] = []
        self.keywords_found: set[str] = set()
        self.keywords_missing: set[str] = set()
        self.coverage_ratio: float = 0.0
        self.errors: list[str] = []
        self.optimizations_applied: set[OpSymbol] = set()
        self.optimization_verified: bool = False
        self.banned_ops_found: set[str] = set()
        self.validation_errors: list[str] = []
        self.models_validated: int = 0
        self.models_rejected: int = 0
        self.source_rejection_counts: dict[str, int] = {}
        self.zero_cost_tasks: list[int] = []

    def check_optimization_requirement(
        self, min_optimizations: int = 1,
    ) -> bool:
        self.optimization_verified = len(self.optimizations_applied) >= min_optimizations
        if not self.optimization_verified:
            self.errors.append(
                f"Optimization requirement not met: found {len(self.optimizations_applied)} "
                f"distinct optimization types, need ≥{min_optimizations}. "
                f"Applied: {sorted(o.name for o in self.optimizations_applied) or 'none'}"
            )
        return self.optimization_verified

    def check_model_validity(
        self, model_graph, source_label: str = "",
    ) -> bool:
        self.models_validated += 1
        banned = set()
        for node in model_graph.node:
            if node.op_type in BANNED_ONNX_OPS:
                banned.add(node.op_type)
                self.validation_errors.append(
                    f"Banned op {node.op_type} in {source_label}"
                )
        if banned:
            self.banned_ops_found.update(banned)
            self.models_rejected += 1
            self.source_rejection_counts[source_label] = \
                self.source_rejection_counts.get(source_label, 0) + 1
        return len(banned) == 0


def verify_trace(
    trace: list[TraceStep],
    code_text: str = "",
    min_optimizations: int = 1,
) -> VerifierResult:
    result = VerifierResult()
    state = DFAState.Q_INIT

    for idx, step in enumerate(trace):
        # Track optimization operations
        if step.op in _OPTIMIZATION_OPS:
            result.optimizations_applied.add(step.op)

        key = (state, step.op)
        if key in _TRANSITIONS:
            state = _TRANSITIONS[key]
            result.step_results.append((idx, step, True, f"→ {state.name}"))
        else:
            result.step_results.append(
                (idx, step, False, f"Invalid: no transition from {state.name} on {step.op.name}")
            )
            state = DFAState.Q_ERROR
            result.errors.append(
                f"Step {idx}: {step.agent} issued {step.op.name} "
                f"in state {state.name}"
            )
            break

    result.final_state = state
    result.accepted = state in _ACCEPTING_STATES

    # Optimization requirement check
    if result.accepted:
        result.check_optimization_requirement(min_optimizations)

    # Keyword coverage analysis
    code_lower = code_text.lower()
    result.keywords_found = {
        kw for kw in KEYWORD_COVERAGE if kw in code_lower
    }
    result.keywords_missing = KEYWORD_COVERAGE - result.keywords_found
    result.coverage_ratio = len(result.keywords_found) / len(KEYWORD_COVERAGE)

    return result


def make_initial_trace(task_ids: list[int]) -> list[TraceStep]:
    return [
        TraceStep(OpSymbol.ANALYZE_TASK, "task_analyzer", tid)
        for tid in task_ids
    ]


def make_standard_pipeline(
    task_ids: list[int],
    optimizer_agents: list[str] | None = None,
    num_verify_subset: int = 3,
) -> list[TraceStep]:
    """Produce a canonical correct trace for a multi-agent system."""
    if optimizer_agents is None:
        optimizer_agents = ["cost_optimizer", "fp16_optimizer"]

    build_techniques = [OpSymbol.BUILD_ONNX, OpSymbol.ENCODE_RULE,
                         OpSymbol.CONVOLUTION, OpSymbol.LABEL_PROPAGATE,
                         OpSymbol.SCATTERND_HIST]
    optimizations = [OpSymbol.FP16_SURGERY, OpSymbol.REDUCE_FUSION,
                      OpSymbol.CAST_COLLAPSE, OpSymbol.DTYPE_NARROW,
                      OpSymbol.PRUNE, OpSymbol.GRAPH_REWRITE,
                      OpSymbol.DIM_SCRUB]

    trace = []
    # Phase 1: discover datasets and load floor solutions
    trace.append(TraceStep(OpSymbol.DISCOVER_BUNDLE, "dataset_scanner"))
    trace.append(TraceStep(OpSymbol.LOAD_FLOOR, "floor_loader"))
    # Phase 2: per-task analysis, build, optimize, verify, cost
    for tid in task_ids:
        trace.append(TraceStep(OpSymbol.ANALYZE_TASK, "task_analyzer", tid))
        trace.append(TraceStep(OpSymbol.DISCOVER_PATTERN, "pattern_miner", tid))
        tech = build_techniques[tid % len(build_techniques)]
        trace.append(TraceStep(tech, "onnx_builder", tid))
        for _ in range(2):
            opt = optimizations[(tid + _) % len(optimizations)]
            ag = optimizer_agents[_ % len(optimizer_agents)]
            trace.append(TraceStep(opt, ag, tid))
    # Phase 3: verify and cost a subset
    for tid in task_ids[:num_verify_subset]:
        trace.append(TraceStep(OpSymbol.VERIFY_TRAIN, "verifier", tid))
        trace.append(TraceStep(OpSymbol.VERIFY_TEST, "verifier", tid))
        trace.append(TraceStep(OpSymbol.VERIFY_ARC_GEN, "verifier", tid))
        trace.append(TraceStep(OpSymbol.COMPUTE_COST, "cost_grader", tid))
    # Phase 4: global blend, optimize-blend, shape-validate, inference, cost, checksum, size-audit, package, submit
    trace.append(TraceStep(OpSymbol.BLEND_BUNDLE, "blender", None))
    trace.append(TraceStep(OpSymbol.BLEND_OPTIMIZE, "blender", None))
    trace.append(TraceStep(OpSymbol.OUTPUT_SHAPE_CHECK, "verifier", None))
    trace.append(TraceStep(OpSymbol.INFERENCE_TEST, "verifier", None))
    trace.append(TraceStep(OpSymbol.COMPUTE_COST, "cost_grader", None))
    trace.append(TraceStep(OpSymbol.SHA256_CHECK, "verifier", None))
    trace.append(TraceStep(OpSymbol.SIZE_AUDIT, "packager", None))
    trace.append(TraceStep(OpSymbol.PACKAGE_SUBMISSION, "packager", None))
    trace.append(TraceStep(OpSymbol.SUBMIT, "orchestrator", None))
    return trace
