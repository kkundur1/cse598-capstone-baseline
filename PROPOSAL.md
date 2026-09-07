[This submission used the help of generative AI tools]

Tool: Kiro (Claude). The problem, scope, architecture choice, and all runs are mine; the
baseline code and prose drafting were AI-assisted and reviewed by me. Full interaction
trace available on request.

# Capstone Project Proposal: Course Study-Assistant Agent

| Field | Response |
| --- | --- |
| Student name | Karthik Venkata Sai Reddy Kunduru (kkundur1) |
| Project title | A grounded, tool-using study-assistant agent for course materials |
| Repository link | https://github.com/kkundur1/cse598-capstone-baseline (public) |
| Configuration location | `baseline/README.md` |

## Section 1: Problem Definition (15)

**Task.** Answer a student's natural-language question about one course using only that
course's materials, and ground every answer in a cited source.

**Input.** A question, plus a folder of course notes (`.txt`).
**Output.** A concise answer citing the source file(s) used, or an honest "not found"
when the notes do not contain the answer.

**Intended user.** A graduate student studying several dense courses who needs fast,
trustworthy answers from their own lecture notes rather than a general chatbot.

**Success.** Factually correct with respect to the notes *and* carrying a correct source
citation. **Failure.** Wrong, uncited, or hallucinated; or claiming an answer the notes
do not support.

## Section 2: Motivation and Project Scope (15)

**Why it matters.** A confident wrong answer costs exam points, so ungrounded answers are
unsafe for studying. Citation-first answering over a student's own materials is both
useful and directly measurable.

**Why agentic AI.** The model decides *whether and what* to retrieve, reads the
observation, and may search again before answering. That is tool use plus planning in the
course's MDP framing, not a single prompt.

**In scope:** single-course Q&A, one retrieval tool, cited answers, and an evaluation
harness comparing an improved system against this baseline.
**Out of scope:** multi-course reasoning, web access, write actions, multi-agent
orchestration, UI polish.

## Section 3: Runnable Baseline (25)

A bounded agent loop with one tool, on a local LLM via Ollama (`qwen3.5:4b`), requiring no
API key and no cost. Pure Python standard library.

1. A system prompt instructs the model to retrieve, then answer with a citation.
2. The model either calls `search_notes(query)` or emits a final answer.
3. Tool output is appended to the context as an observation.
4. The loop repeats, capped at 4 steps, until a final cited answer.

`search_notes` is a keyword-overlap retriever over `.txt` notes. It is deliberately weak:
retrieval is deterministic and easy to reason about, which makes it an honest bar for
later RAG or fine-tuning to beat.

**Files.** `baseline/agent.py` (loop), `baseline/tools.py` (tool and schema),
`baseline/examples/notes/` (corpus), `baseline/examples/runs/` (saved runs).

## Section 4: Test Case and Baseline Output (25)

**Sample input.**

```
python agent.py -q "What are the five terms in the MDP formulation of an agent, and why is reward called a proxy?"
```

**Expected behavior.** One or more `search_notes` calls, then an answer naming the five
MDP terms (state, action, policy, reward, transition) and explaining reward as a proxy,
each grounded with `[source: agent-loop.txt]`.

**Actual output.** The run below is unedited. The agent issued one search, then returned
all five terms with a citation on every line, plus the reward-as-proxy shortcut using the
booking example.

![Baseline agent running successfully: the search_notes tool call, the five MDP terms each with a [source: agent-loop.txt] citation, and the reward-as-proxy explanation.](baseline-run-screenshot.png){width=5.4in}

**What worked.** Grounded, cited, and correct, and the agent chose on its own how many
searches to run. **What did not.** Keyword retrieval has no semantic matching, so it can
miss paraphrased questions, and the step count varies between runs (this run took 2 steps
and 13.5 s; another took 3 steps and 71.3 s). Both are Phase-2 targets. Full transcripts
and machine-readable trajectories are committed under `baseline/examples/runs/`.

## Section 5: Reproducibility and Run Instructions (10)

- **Dependencies.** Python 3.9+ (standard library only) and Ollama running locally.
- **Setup.** `ollama pull qwen3.5:4b`, once, then ensure Ollama is running.
- **API keys or environment variables.** None.
- **Command.** Run the Section 4 command from `baseline/`.
- **Input.** `examples/notes/*.txt`, override with `-n <dir>`.
- **Output.** stdout; add `--json-out <path>` for the full trajectory.
- **Known limitation.** Wording and step count vary between runs because the policy
  samples; the cited facts are stable.

## Section 6: Initial Evaluation Plan (5)

Compare the improved system against this baseline on a held-out set of 20 to 30
question and answer pairs drawn from the notes, measuring answer correctness (graded
match or LLM-as-judge), citation validity (does the cited file actually contain the
claim), hallucination rate (unsupported claims per answer), retrieval hit rate, and cost
as steps and seconds per question. Improvement means higher correctness and citation
validity with lower hallucination on the same set.

## Section 7: Limitations and Next Steps (5)

**Weaknesses.** Keyword retrieval misses synonyms and paraphrase; a small local model can
mis-summarize; single course only.

**Expected failures.** Paraphrased and multi-hop questions, and notes that lack the
answer, where a weak model may guess instead of saying "not found."

**Next phase.** Replace keyword search with embedding-based RAG, build the Section 6
evaluation harness, and optionally QLoRA fine-tune a small open model for better tool use
and grounding on ASU's Sol cluster.

**Risks.** Sol account approval, producing a labeled evaluation set, and time.
