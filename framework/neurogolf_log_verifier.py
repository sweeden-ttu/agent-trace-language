"""Verifies log files for expected output patterns.

Checks kernel stdout/stderr logs for required patterns (must appear),
forbidden patterns (must not appear), and ordered patterns (must
appear in a specific sequence).
"""

import re
import json
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LogExpectation:
    pattern: str
    label: str = ""
    min_count: int = 1
    stream: str = "stdout"


@dataclass
class LogVerifierResult:
    passed: bool = False
    total_required: int = 0
    matched: int = 0
    forbidden_hits: list = field(default_factory=list)
    ordered_violations: list = field(default_factory=list)
    failures: list = field(default_factory=list)
    details: list = field(default_factory=list)


_REQUIRED_PATTERNS: list[LogExpectation] = [
    LogExpectation(r"ONNX:\s+\d+\.\d+\.\d+", "ONNX version present"),
    LogExpectation(r"NumPy:\s+\d+\.\d+\.\d+", "NumPy version present"),
    LogExpectation(r"Framework loaded:", "Framework loaded message"),
    LogExpectation(
        r"\d+\s+ops,\s+\d+\s+states,\s+\d+\s+transitions",
        "DFA state/transition stats"
    ),
    LogExpectation(r"Package:\s+\d+\s+tasks,\s+\d+\.\d+\s+MB", "Submission zip size"),
    LogExpectation(r"\d+ tasks", "Task count present"),
    LogExpectation(r"SHA256:\s+[0-9A-F]{64}", "SHA256 hash present"),
    LogExpectation(r"Ready for submission!", "Ready message"),
    LogExpectation(r"kaggle\.com/competitions/neurogolf-2026", "Competition URL"),
]

_FORBIDDEN_PATTERNS: list[LogExpectation] = [
    LogExpectation(r"Traceback \(most recent call last\)", "No tracebacks"),
    LogExpectation(r"\bValueError\b|\bRuntimeError\b|\bTypeError\b|\bNameError\b|\bAttributeError\b",
                   "No Python exceptions"),
]

_ORDERED_TRANSITIONS: list[str] = [
    r"INIT\s*--\[DISCOVER_BUNDLE\]-->",
    r"INIT\s*--\[LOAD_FLOOR\]-->",
    r"INIT\s*--\[ANALYZE_TASK\]--> ANALYZED",
    r"ANALYZED\s*--\[BUILD_ONNX\]--> BUILT",
    r"BUILT\s*--\[GRAPH_REWRITE\]--> OPTIMIZED",
    r"OPTIMIZED\s*--\[VERIFY_TRAIN\]--> V_TRAIN",
    r"V_TRAIN\s*--\[VERIFY_TEST\]--> V_TEST",
    r"V_TEST\s*--\[VERIFY_ARC_GEN\]--> V_ARC",
    r"V_ARC\s*--\[COMPUTE_COST\]--> COSTED",
    r"COSTED\s*--\[BLEND_BUNDLE\]--> BLENDED",
    r"BLENDED\s*--\[BLEND_OPTIMIZE\]--> BLENDED",
    r"BLENDED\s*--\[OUTPUT_SHAPE_CHECK\]--> BLENDED",
    r"BLENDED\s*--\[INFERENCE_TEST\]--> BLENDED",
    r"BLENDED\s*--\[COMPUTE_COST\]--> COSTED",
    r"COSTED\s*--\[SHA256_CHECK\]--> COSTED",
    r"COSTED\s*--\[SIZE_AUDIT\]--> COSTED",
    r"COSTED\s*--\[PACKAGE_SUBMISSION\]--> PACKAGED",
    r"PACKAGED\s*--\[SUBMIT\]--> SUBMITTED",
]

_TOP_KAGGLE_REQUIRED: list[LogExpectation] = [
    LogExpectation(r"submission\.zip", "Submission zip"),
    LogExpectation(r"\d+ tasks", "Task count"),
    LogExpectation(r"SHA256|sha256|sha", "SHA256 hash"),
    LogExpectation(r"Found \d+ task", "Task discovery"),
]

_GENERIC_REQUIRED: list[LogExpectation] = [
    LogExpectation(r"submission\.zip|Submission|Wrote.*zip", "Submission zip created"),
    LogExpectation(r"\b400\s+tasks|\b401\s+tasks|\d+\s+tasks", "Task count present"),
    LogExpectation(r"SHA256|[Ss]ha256?[:\s]+[0-9A-Fa-f]{32,}", "SHA256 hash present"),
    LogExpectation(r"Ready|ready|submit", "Ready / submit message"),
]

_GENERIC_FORBIDDEN: list[LogExpectation] = [
    LogExpectation(r"Traceback \(most recent call last\)", "No tracebacks"),
    LogExpectation(r"ValueError|RuntimeError|TypeError|NameError", "No Python exceptions"),
]


def _get_patterns(preset: str = "framework") -> tuple[list[LogExpectation], list[LogExpectation], list[str]]:
    p = preset.lower()
    if p == "framework":
        return _REQUIRED_PATTERNS, _FORBIDDEN_PATTERNS, _ORDERED_TRANSITIONS
    elif p == "generic":
        return _GENERIC_REQUIRED, _GENERIC_FORBIDDEN, []
    elif p == "top_kaggle" or p == "topkaggle":
        return _TOP_KAGGLE_REQUIRED, _GENERIC_FORBIDDEN, []
    else:
        return _REQUIRED_PATTERNS, _FORBIDDEN_PATTERNS, _ORDERED_TRANSITIONS


def parse_kaggle_log(log_path: str) -> list[tuple[str, str, float]]:
    """Parse Kaggle JSON-lines log into (stream, data, time) tuples."""
    entries = []
    with open(log_path) as f:
        raw = f.read().strip()
    if not raw.startswith("["):
        raw = "[" + raw + "]"
    try:
        records = json.loads(raw)
    except json.JSONDecodeError:
        records = [json.loads(line) for line in raw.strip().split("\n") if line.strip()]

    for rec in records:
        stream = rec.get("stream_name", "stdout")
        data = rec.get("data", "")
        t = rec.get("time", 0.0)
        entries.append((stream, data, t))
    return entries


def parse_simple_log(log_path: str) -> str:
    """Parse a plain-text log file (stdout-only, one line per entry)."""
    with open(log_path) as f:
        return f.read()


def get_all_text(entries: list[tuple[str, str, float]]) -> str:
    """Concatenate all stdout data from parsed log entries."""
    lines = []
    for stream, data, _ in entries:
        if stream == "stdout":
            lines.append(data)
    return "".join(lines)


def check_log_entries(
    log_path: str,
    required: Optional[list[LogExpectation]] = None,
    forbidden: Optional[list[LogExpectation]] = None,
    ordered: Optional[list[str]] = None,
    preset: str = "framework",
    label: str = "Log Verification",
) -> LogVerifierResult:
    """Check a Kaggle JSON-lines log against required/forbidden/ordered patterns."""
    if required is None or forbidden is None or ordered is None:
        default_req, default_forb, default_ord = _get_patterns(preset)
        if required is None:
            required = default_req
        if forbidden is None:
            forbidden = default_forb
        if ordered is None:
            ordered = default_ord

    result = LogVerifierResult()
    entries = parse_kaggle_log(log_path)
    full_text = get_all_text(entries)
    stream_map: dict[str, str] = {}
    for stream, data, _ in entries:
        stream_map[stream] = stream_map.get(stream, "") + data

    # Check required patterns
    result.total_required = len(required)
    for exp in required:
        text = stream_map.get(exp.stream, "")
        count = len(re.findall(exp.pattern, text))
        if count >= exp.min_count:
            result.matched += 1
            result.details.append(f"  ✓ {exp.label}: found ({exp.pattern})")
        else:
            # Fallback: search all text
            count_all = len(re.findall(exp.pattern, full_text))
            if count_all >= exp.min_count:
                result.matched += 1
                result.details.append(
                    f"  ✓ {exp.label}: found in stdout ({exp.pattern})"
                )
            else:
                result.failures.append(
                    f"  ✗ {exp.label}: not found ({exp.pattern})"
                )

    # Check forbidden patterns
    for exp in forbidden:
        text = stream_map.get(exp.stream, "") + full_text
        hits = re.findall(exp.pattern, text, re.IGNORECASE)
        if hits:
            result.forbidden_hits.append(f"  !! {exp.label}: found ({hits[:3]})")

    # Check ordered DFA transitions
    if ordered:
        positions = []
        for pattern in ordered:
            m = re.search(pattern, full_text)
            if m:
                positions.append((m.start(), pattern))
        if positions:
            sorted_patterns = [p for _, p in sorted(positions, key=lambda x: x[0])]
            if sorted_patterns != ordered:
                for i, (a, b) in enumerate(zip(sorted_patterns, ordered)):
                    if a != b:
                        result.ordered_violations.append(
                            f"  ! Order mismatch at index {i}: expected {b[:50]}, got {a[:50]}"
                        )
                        break
        else:
            result.ordered_violations.append("  ! No ordered transitions found in text")

    result.passed = (
        len(result.failures) == 0
        and len(result.forbidden_hits) == 0
        and len(result.ordered_violations) == 0
    )
    return result


def check_simple_log(
    log_path: str,
    required: Optional[list[LogExpectation]] = None,
    forbidden: Optional[list[LogExpectation]] = None,
    preset: str = "framework",
    label: str = "Simple Log Verification",
) -> LogVerifierResult:
    """Check a plain-text log for required/forbidden patterns."""
    if required is None or forbidden is None:
        default_req, default_forb, _ = _get_patterns(preset)
        if required is None:
            required = default_req
        if forbidden is None:
            forbidden = default_forb

    result = LogVerifierResult()
    text = parse_simple_log(log_path)

    result.total_required = len(required)
    for exp in required:
        count = len(re.findall(exp.pattern, text))
        if count >= exp.min_count:
            result.matched += 1
            result.details.append(f"  ✓ {exp.label}: found")
        else:
            result.failures.append(f"  ✗ {exp.label}: not found ({exp.pattern})")

    for exp in (forbidden or []):
        hits = re.findall(exp.pattern, text, re.IGNORECASE)
        if hits:
            result.forbidden_hits.append(f"  !! {exp.label}: found ({hits[:3]})")

    result.passed = len(result.failures) == 0 and len(result.forbidden_hits) == 0
    return result


def print_result(result: LogVerifierResult):
    """Pretty-print a LogVerifierResult."""
    print(f"Log Verification Results")
    print(f"  Required patterns: {result.total_required}")
    print(f"  Matched:           {result.matched}")
    print(f"  Forbidden hits:    {len(result.forbidden_hits)}")
    print(f"  Ordered violations: {len(result.ordered_violations)}")
    print(f"  Failures:          {len(result.failures)}")
    print()
    for d in result.details:
        print(d)
    print()
    if result.forbidden_hits:
        print("FORBIDDEN PATTERNS FOUND:")
        for f in result.forbidden_hits:
            print(f)
        print()
    if result.ordered_violations:
        print("ORDERED TRANSITION VIOLATIONS:")
        for v in result.ordered_violations:
            print(v)
        print()
    if result.failures:
        print("FAILURES:")
        for f in result.failures:
            print(f)
        print()
    print(f"Overall: {'PASS' if result.passed else 'FAIL'}")
    return result.passed
