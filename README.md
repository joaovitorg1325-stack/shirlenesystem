# Agent Instance

This repository contains the structure for an AI agent instance based on the 3-layer architecture defined in `Agente.md`.

## Structure

- **directives/**: Contains Standard Operating Procedures (SOPs) in Markdown.
- **execution/**: Contains deterministic Python scripts for executing tasks.
- **.tmp/**: Directory for temporary files (not committed to version control).
- **.env**: Environment variables (create from `.env.example`).

## Usage

1.  Define a goal in a directive within `directives/`.
2.  Implement the necessary logic in a script within `execution/`.
3.  Run the agent to orchestrate the execution.

## Example

See `directives/multiply_numbers.md` and `execution/multiply_numbers.py` for a simple example.
