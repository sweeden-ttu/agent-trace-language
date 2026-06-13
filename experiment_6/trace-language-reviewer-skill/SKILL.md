---
name: trace-language-reviewer
description: >-
  Iteratively parses cleaned_logs/ and trace_language.csv to correlate architectural 
  operations with changes in Kaggle notebook score.
---

# Trace Language Reviewer

## Overview
This skill extracts cost and score data from stdout logs in the `cleaned_logs/` directory and correlates them against the agentic operations executed in `trace_language.csv`. It helps identify which architectural operations (e.g., FP16 surgery, Krönecker templates) yield the largest improvements in competition scores.

## Dependencies
None.

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
- Pointing to a logs directory that does not contain text files with `cost=` or `score=` metrics.
- Missing the `estimated_improvement` column in the trace CSV when running `correlate-trace`.
