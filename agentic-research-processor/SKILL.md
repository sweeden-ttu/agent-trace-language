---
name: agentic-research-processor
description: Processes large textbook-scale HTML documents (concepts.html, competitions.html) and scaffolding (nextsteps.zip) for agentic system development. It shreds documents into chapters, reviews them for relevance to agentic software generation, and iteratively updates a project scaffold based on textbook concepts and competition challenges.
---

# Agentic Research Processor

This skill manages the ingestion and analysis of large-scale knowledge sources and competition requirements to build high-performing agentic software systems.

## Workflow

### 1. Initial Ingestion
The skill first looks for the following core files in the project root:
- `concepts.html`: The primary textbook or conceptual guide.
- `competitions.html`: Description of challenges and available data.
- `nextsteps.zip`: The project scaffold and directory structure.

It creates folders for each: `concepts/`, `competitions/`, and `scaffold/`.

### 2. Document Shredding
Large HTML files are broken down into smaller pieces (typically by chapter using `h1` or `h2` tags) using the bundled script.

```bash
python scripts/shred_html.py concepts.html concepts/
python scripts/shred_html.py competitions.html competitions/
```

### 3. Iterative Review and Decomposition
For each piece:
- **Analyze Relevance**: Determine if the section contributes to "agentic software generating systems".
- **Further Decomposition**: If a piece is still too large (e.g., > 100 KB), shred it again by `h2` or `h3` tags.
- **Extract Insights**: Identify experiments, software patterns, or completion strategies.

### 4. Scaffold Update
Integrate findings into the `scaffold/` directory. For every relevant concept identified:
- Explain why it benefits the project/competition.
- Propose an experiment or software package implementation.
- Update the relevant files in the scaffold.

## Relevance Criteria

A section is considered high-priority if it covers:
- Agent-oriented programming patterns.
- Automated verifiers or DFA-based logic.
- Multi-agent system orchestration.
- Trace language analysis for software generation.
- Logic decoders or constraint-based solvers.

## Bundled Resources

- `scripts/shred_html.py`: Splits HTML files into manageable chapters.
- `scripts/extract_scaffold.py`: Unzips and initializes the scaffold directory.

## Best Practices

- **Keep it Lean**: Don't read the entire 4.6 MB file at once. Use the shredded pieces.
- **Relate Concepts**: Always link a "Concept" to a "Competition Challenge".
- **Justify Changes**: Document why a specific concept from the textbook is being applied to the current project state.
