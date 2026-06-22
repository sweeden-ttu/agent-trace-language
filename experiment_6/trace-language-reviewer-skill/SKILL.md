---
name: trace-language-reviewer
description: >-
  Prioritizes browsing notebooks, submissions, outputs, and log files of better performing 
  competition entries to learn successful architectures first, before developing the trace 
  language for agent verification.
---

# Trace Language Reviewer

## Overview
This skill outlines the workflow to systematically research, design, and verify the trace language for multi-agent systems. It mandates:
1. **Prior Research (Browsing Top Entries First)**: Browsing, reading, and analyzing notebooks, submissions, outputs, and log files of better-performing competition entries. This identifies the actual patterns, operations (e.g., Krönecker templates, symmetry reflections, custom optimization passes), and pipelines that yield high scores before formalizing a trace language.
2. **Post-Execution Correlation**: Scanning log files in `cleaned_logs/` and correlating them against the agentic operations executed in `trace_language.csv` using parser utilities. This quantifies which operations yield the largest improvements in competition scores.

## Dependencies
None.

## Workflow: Browsing & Analyzing Top Entries First

Before designing or modifying any trace language operations, you must perform the following analysis:

1. **Locate Better Performing Entries**:
   - Access top Kaggle notebooks, public submissions, log files, and outputs (often located under `/kaggle/input/` or shared directories).
   - Find relevant `.log` and output files containing evaluation scores, parameter/layer details, and performance stats.

2. **Deconstruct the Architecture**:
   - Document the specific operations utilized (e.g., few-shot adaptive learning, special data augmentations, attention modules, model ensembles, FP16 conversions, or pruning).
   - Map out the sequence of states: e.g. how data prep flows to model building, optimization, verification, and final blending.

3. **Align Trace Language Definitions**:
   - Map the discovered operations directly to `OpSymbol` values.
   - Define agent assignments (e.g., which agent executes each operation).
   - Define valid DFA states and transitions to match successful pipelines.

## Quick Start
```bash
uv run scripts/log_parser_cli.py analyze-logs --logs-dir ../cleaned_logs --output score_analysis.json
uv run scripts/log_parser_cli.py correlate-trace --trace-csv ../trace_language.csv --score-data score_analysis.json --output correlation.json
```

## Utility Scripts

### `log_parser_cli.py analyze-logs`
Scans stdout logs for lines matching `cost=<value> score=<value>`.
**Arguments**:
- `--logs-dir` (required): Path to the `cleaned_logs/` directory.
- `--output` (required): Path to save the extracted JSON data.

### `log_parser_cli.py correlate-trace`
Maps the extracted scores to operations in the trace CSV to compute estimated improvements.
**Arguments**:
- `--trace-csv` (required): Path to `trace_language.csv`.
- `--score-data` (required): Path to the output of `analyze-logs`.
- `--output` (required): Path to save the correlation results.

## Rate Limiting
N/A (Local file processing only).

## Common Mistakes
- Developing a trace language and DFA transitions without analyzing the actual architectures used by top-performing competition entries.
- Pointing to a logs directory that does not contain text files with `cost=` or `score=` metrics.
- Missing the `estimated_improvement` column in the trace CSV when running `correlate-trace`.
