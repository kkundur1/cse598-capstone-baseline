# Course Study-Assistant Agent — Runnable Baseline (Phase 0)

A minimal but real **agentic** baseline for the CSE 598 capstone: a study-assistant
agent that answers questions about a course using an **agent loop with a tool call**,
running on a **local LLM via Ollama** (no API key, no cloud, no cost).

It is deliberately simple — that is the point of a baseline. Later phases replace the
keyword retriever with real embedding/RAG retrieval and/or a fine-tuned model, and
evaluate the improvement **against this baseline**.

## What makes it an agent (not just a prompt)
It runs a bounded **Observe → Decide → Act → Observe → … → Final** loop:
1. The LLM (policy) sees the question and decides whether to call the `search_notes` tool.
2. If it calls the tool, the retrieved passages are fed back as an observation.
3. The loop repeats (capped at 4 steps) until the model emits a final, cited answer.

This maps to the course MDP framing: state = question + context + tool outputs;
actions = call `search_notes` or answer; policy = the LLM; transition = running the
tool changes the context; reward (for evaluation) = correct + cited answer.

## Requirements
- **Python 3.9+** (uses only the standard library — no pip installs needed).
- **[Ollama](https://ollama.com)** running locally with a tool-capable model.
  This baseline defaults to `qwen3.5:4b`. Pull it once:
  ```
  ollama pull qwen3.5:4b
  ```
  Ollama must be running (its server listens on `http://localhost:11434`).

No API keys or environment variables are required.

## Files
```
baseline/
├─ agent.py                     # the agent loop (entry point)
├─ tools.py                     # the search_notes tool + its schema
├─ README.md                    # this file
└─ examples/
   ├─ notes/                    # the course notes the agent searches (.txt)
   │  ├─ agent-loop.txt
   │  └─ architecture.txt
   └─ runs/                     # a saved example run (transcript + trajectory JSON)
      ├─ example-run.txt
      └─ example-run.json
```

## How to run (exact command)
From the `baseline/` directory:
```
python agent.py -q "What are the five terms in the MDP formulation of an agent, and why is reward called a proxy?"
```

Options:
- `-q/--question` (required): the student question.
- `-m/--model` (default `qwen3.5:4b`): any tool-capable Ollama model tag.
- `-n/--notes` (default `examples/notes`): folder of `.txt` notes to search.
- `--json-out <path>`: also write the full trajectory (steps + tool calls) as JSON.

**Input:** the question (CLI) and the `.txt` files in `examples/notes/`.
**Output:** the final answer is printed to stdout; the step-by-step trajectory
(tool calls + observations) prints as it runs, and optionally saves to `--json-out`.

## Concrete test case (with actual output)
Command:
```
python agent.py -q "What are the five terms in the MDP formulation of an agent, and why is reward called a proxy?"
```
Expected behavior: the agent makes one or more `search_notes` calls, then answers
with the five MDP terms (state, action, policy, reward, transition) and explains
"reward as a proxy," each grounded with a `[source: agent-loop.txt]` citation.

Actual saved output: see `examples/runs/example-run.txt` (and `example-run.json`
for the full trajectory). On an RTX 3070 laptop the run completed in ~18s using
2 tool calls + 1 final answer.

## Reproducibility notes
- Deterministic-ish: the retriever is fully deterministic; the LLM has mild
  sampling variation, so wording may differ between runs but the cited facts and
  structure are stable.
- If `qwen3.5:4b` is not present, pull it or pass a different tool-capable model
  with `-m`. If Ollama is not running, start it first.
- Point `-n` at any folder of `.txt` files to use different notes (e.g. the
  extracted course notes elsewhere in this workspace).

## GenAI disclosure
This baseline was built with the help of a generative-AI tool (Kiro/Claude) per the
CSE 598 Agentic AI GenAI policy. The design, code, and this README were AI-assisted;
the full interaction trace is available on request.
