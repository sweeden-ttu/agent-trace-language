"""Verifies notebook cell outputs appear in the expected order.

Two modes:
  1. Notebook JSON — checks each code cell's output text against expected patterns
  2. Kaggle log — splits sequential stdout by section markers into virtual cells
"""

import re
import json
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CellExpectation:
    pattern: str
    label: str = ""
    optional: bool = False
    min_count: int = 1


@dataclass
class CellVerifierResult:
    passed: bool = False
    total: int = 0
    matched: int = 0
    skipped: int = 0
    failures: list = field(default_factory=list)
    details: list = field(default_factory=list)


_NOTEBOOK_PATTERNS: list[CellExpectation] = [
    CellExpectation(r"ONNX:\s+\d+\.\d+\.\d+", "ONNX version"),
    CellExpectation(r"NumPy:\s+\d+\.\d+\.\d+", "NumPy version"),
    CellExpectation(
        r"Framework loaded:\s+\d+\s+ops,\s+\d+\s+states", "Framework loaded"
    ),
    CellExpectation(r"state=SUBMITTED accepted=True", "Pre-flight DFA pass"),
    CellExpectation(r"PHASE 1: Discover datasets", "Phase 1 header"),
    CellExpectation(
        r"✓ discover_bundles:\s+\S+\s+--\[DISCOVER_BUNDLE\]-->",
        "Discover bundles transition",
    ),
    CellExpectation(
        r"✓ load_floor:\s+\S+\s+--\[LOAD_FLOOR\]-->", "Load floor transition"
    ),
    CellExpectation(r"PHASE 2: Build ONNX solvers", "Phase 2 header"),
    CellExpectation(r"Solver type distribution:", "Solver type distribution"),
    CellExpectation(
        r"✓ analyze_task:\s+\S+\s+--\[ANALYZE_TASK\]--> ANALYZED",
        "Analyze task transition",
    ),
    CellExpectation(
        r"✓ build_onnx:\s+\S+\s+--\[BUILD_ONNX\]--> BUILT", "Build ONNX transition"
    ),
    CellExpectation(
        r"✓ graph_rewrite:\s+\S+\s+--\[GRAPH_REWRITE\]--> OPTIMIZED",
        "Graph rewrite transition",
    ),
    CellExpectation(r"PHASE 3: Verify and cost", "Phase 3 header"),
    CellExpectation(
        r"✓ verify_train:\s+\S+\s+--\[VERIFY_TRAIN\]--> V_TRAIN",
        "Verify train transition",
    ),
    CellExpectation(
        r"✓ verify_test:\s+\S+\s+--\[VERIFY_TEST\]--> V_TEST",
        "Verify test transition",
    ),
    CellExpectation(
        r"✓ verify_arc_gen:\s+\S+\s+--\[VERIFY_ARC_GEN\]--> V_ARC",
        "Verify ARC-GEN transition",
    ),
    CellExpectation(
        r"✓ compute_cost:\s+\S+\s+--\[COMPUTE_COST\]--> COSTED",
        "Compute cost transition",
    ),
    CellExpectation(r"PHASE 4: Blend, checksum, package, submit", "Phase 4 header"),
    CellExpectation(r"Blending from datasets", "Blend start", optional=True),
    CellExpectation(
        r"accepted=\d+ rejected=\d+", "Source acceptance/rejection", optional=True
    ),
    CellExpectation(
        r"✓ blend_bundle:\s+\S+\s+--\[BLEND_BUNDLE\]--> BLENDED",
        "Blend bundle transition",
    ),
    CellExpectation(
        r"✓ blend_optimize:\s+\S+\s+--\[BLEND_OPTIMIZE\]--> BLENDED",
        "Blend optimize transition", optional=True,
    ),
    CellExpectation(
        r"✓ output_shape_check:\s+\S+\s+--\[OUTPUT_SHAPE_CHECK\]--> BLENDED",
        "Output shape check transition", optional=True,
    ),
    CellExpectation(
        r"✓ inference_test:\s+\S+\s+--\[INFERENCE_TEST\]-->",
        "Inference test transition", optional=True,
    ),
    CellExpectation(
        r"✓ sha256_check:\s+\S+\s+--\[SHA256_CHECK\]-->", "SHA256 check transition"
    ),
    CellExpectation(
        r"✓ size_audit:\s+\S+\s+--\[SIZE_AUDIT\]-->", "Size audit transition"
    ),
    CellExpectation(
        r"✓ package_submission:\s+\S+\s+--\[PACKAGE_SUBMISSION\]--> PACKAGED",
        "Package submission transition",
    ),
    CellExpectation(
        r"✓ submit:\s+\S+\s+--\[SUBMIT\]--> SUBMITTED", "Submit transition"
    ),
    CellExpectation(r"Package:\s+\d+\s+tasks,\s+\d+\.\d+\s+MB", "Package summary"),
    CellExpectation(r"SHA256:\s+[0-9A-F]{64}", "SHA256 hash"),
    CellExpectation(r"Ready for submission!", "Submission ready"),
    CellExpectation(r"kaggle\.com/competitions/neurogolf-2026", "Kaggle submission URL"),
]

_TOP_KAGGLE_PATTERNS: list[CellExpectation] = [
    CellExpectation(r"Found \d+ task", "Task discovery"),
    CellExpectation(r"Processing task\d+\.+", "Task processing", optional=True),
    CellExpectation(r"submission\.zip", "Submission zip output"),
    CellExpectation(r"\d+ tasks", "Task count in summary"),
    CellExpectation(r"SHA256|sha256|sha", "SHA256 hash"),
    CellExpectation(r"Ready|ready", "Ready message"),
]


# ─── Log parser (shared with log_verifier) ─────────────────────


def _parse_kaggle_log(log_path: str) -> list[tuple[str, str, float]]:
    """Parse Kaggle JSON-lines log into (stream, data, time) tuples."""
    with open(log_path) as f:
        raw = f.read().strip()
    if not raw:
        return []
    records = []
    try:
        if raw.startswith("["):
            records = json.loads(raw)
        else:
            records = [json.loads(line) for line in raw.split("\n") if line.strip()]
    except json.JSONDecodeError:
        return []
    entries = []
    for rec in records:
        stream = rec.get("stream_name", "stdout")
        data = rec.get("data", "")
        t = rec.get("time", 0.0)
        entries.append((stream, data, t))
    return entries


def _get_stdout_text(entries: list[tuple[str, str, float]]) -> str:
    return "".join(data for stream, data, _ in entries if stream == "stdout")


# ─── Virtual cell splitting ────────────────────────────────────


def split_log_by_phase(log_text: str) -> list[str]:
    """Split a single stdout stream into virtual cells at phase boundaries."""
    sections = re.split(r"(?=={2,}\s*\n)", log_text)
    return [s.strip() for s in sections if s.strip()]


def split_log_by_markers(log_text: str, markers: list[str]) -> list[str]:
    """Split stdout at any of the given marker patterns."""
    pattern = "|".join(f"(?={re.escape(m)})" for m in markers)
    sections = re.split(pattern, log_text)
    return [s.strip() for s in sections if s.strip()]


# ─── Notebook extraction ───────────────────────────────────────


def extract_cell_outputs(notebook_path: str) -> list[str]:
    """Extract stdout text from each code cell in a notebook."""
    with open(notebook_path) as f:
        nb = json.load(f)
    outputs = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        text = ""
        for out in cell.get("outputs", []):
            for line in out.get("text", []):
                text += line
            for line in out.get("data", {}).get("text/plain", []):
                text += line
        outputs.append(text)
    return outputs


# ─── Core checking ─────────────────────────────────────────────


def check_cell_outputs(
    cell_outputs: list[str],
    expectations: list[CellExpectation],
    label: str = "Cell Verification",
) -> CellVerifierResult:
    """Match cell output texts against expected patterns in order."""
    result = CellVerifierResult()
    result.total = len(expectations)
    unmatched = list(expectations)

    for cell_idx, output in enumerate(cell_outputs):
        still_unmatched = []
        for exp in unmatched:
            count = len(re.findall(exp.pattern, output))
            if count >= exp.min_count:
                result.matched += 1
                result.details.append(
                    f"  ✓ Virtual cell {cell_idx}: {exp.label}"
                )
            elif exp.optional:
                result.skipped += 1
                result.details.append(
                    f"  - Virtual cell {cell_idx}: {exp.label} skipped (optional)"
                )
            else:
                still_unmatched.append(exp)
        unmatched = still_unmatched
        if not unmatched:
            break

    for exp in unmatched:
        if exp.optional:
            result.skipped += 1
        else:
            result.failures.append(f"  ✗ Never matched: {exp.label}")

    result.passed = len(result.failures) == 0
    return result


# ─── Convenience entry points ──────────────────────────────────


def check_notebook(
    notebook_path: str,
    expectations: Optional[list[CellExpectation]] = None,
    label: str = "Notebook Cell Output Verification",
) -> CellVerifierResult:
    """Check a notebook JSON (with execution outputs) against patterns."""
    if expectations is None:
        expectations = _NOTEBOOK_PATTERNS
    outputs = extract_cell_outputs(notebook_path)
    return check_cell_outputs(outputs, expectations, label)


def check_log(
    log_path: str,
    expectations: Optional[list[CellExpectation]] = None,
    label: str = "Log Cell Output Verification",
) -> CellVerifierResult:
    """Check a Kaggle kernel log (JSON-lines) against patterns.

    Splits sequential stdout into virtual cells at phase-boundary
    markers, then verifies patterns appear in the right order.
    """
    if expectations is None:
        expectations = _NOTEBOOK_PATTERNS
    entries = _parse_kaggle_log(log_path)
    text = _get_stdout_text(entries)
    virtual_cells = split_log_by_phase(text)
    if not virtual_cells:
        virtual_cells = [text]
    return check_cell_outputs(virtual_cells, expectations, label)


def check_text(
    text: str,
    expectations: Optional[list[CellExpectation]] = None,
    label: str = "Text Output Verification",
) -> CellVerifierResult:
    """Check a raw text string against expected patterns."""
    if expectations is None:
        expectations = _NOTEBOOK_PATTERNS
    return check_cell_outputs([text], expectations, label)


# ─── Pretty-print ──────────────────────────────────────────────


def print_result(result: CellVerifierResult):
    """Pretty-print a CellVerifierResult."""
    print(f"Cell Output Verification Results")
    print(f"  Total expectations: {result.total}")
    print(f"  Matched:        {result.matched}")
    print(f"  Skipped (opt):  {result.skipped}")
    print(f"  Failures:       {len(result.failures)}")
    print()
    for d in result.details:
        print(d)
    print()
    if result.failures:
        print("FAILURES:")
        for f in result.failures:
            print(f)
        print()
    print(f"Overall: {'PASS' if result.passed else 'FAIL'}")
    return result.passed
