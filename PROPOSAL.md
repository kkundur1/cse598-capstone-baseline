[This submission used the help of generative AI tools]

Tool: Kiro (Claude). The problem, scope, architecture choice, and all runs are mine; the
baseline code and prose drafting were AI-assisted and reviewed by me. Full interaction
trace available on request.

# Capstone Project Proposal

## Basic Information

| Field | Response |
| --- | --- |
| **Student name** | Karthik Venkata Sai Reddy Kunduru (kkundur1) |
| **Project title** | A grounded, tool-using study-assistant agent for course materials |
| **Repository link** | https://github.com/kkundur1/cse598-capstone-baseline (public) |
| **Configuration** | `baseline/README.md` |

## 1. Problem Definition

**Task:** answer a student's natural-language question about one course using only that
course's materials, and ground every answer in a cited source.

**User:** a graduate student studying several dense courses who needs fast, verifiable
answers from their own notes, where each citation can be checked against the source.

**Input:** a question plus a directory of course notes (`.txt`). **Output:** a concise
answer citing the source file(s) used, or an explicit "not found" when the notes do not
contain the answer.

**Success:** factually correct with respect to the notes *and* carrying a correct source
citation. **Failure:** uncited or unsupported by the notes, or asserting an answer the
notes do not contain.

## 2. Motivation and Project Scope

**Why it matters:** a confident wrong answer costs exam points, so an answer is only useful
for studying if its source can be checked. Citation-first retrieval over a student's own
materials makes correctness measurable rather than a matter of trust.

**Agentic fit:** the model decides *whether and what* to retrieve, reads the observation,
and may search again before answering. Control flow depends on what retrieval returns, so
this is tool use plus planning in the course's MDP framing, not a single prompt.

**In scope:** single-course Q&A, one retrieval tool, cited answers, and an evaluation
harness measuring an improved system against this baseline. **Out of scope:** multi-course
reasoning, web access, write actions, multi-agent orchestration, interface work.

## 3. Runnable Baseline

**Type:** a bounded agent loop with one tool, running a local LLM through Ollama
(`qwen3.5:4b`). No API key and no per-run cost, Python standard library only.

**Step by step:** a system prompt instructs the model to retrieve first, then answer with a
citation. The model either calls `search_notes(query)` or emits a final answer. Tool output
is appended to the context as an observation, and the loop repeats, capped at 4 steps,
until a final cited answer.

**Why reasonable:** `search_notes` is a keyword-overlap retriever, chosen because it is
deterministic and fully inspectable, so later gains from RAG or fine-tuning are
attributable to the retriever rather than to sampling noise.

**Files:** `baseline/agent.py` (loop), `baseline/tools.py` (tool and schema),
`baseline/examples/notes/` (corpus), `baseline/examples/runs/` (saved runs).

## 4. Test Case and Baseline Output

**Sample input:**

```
python agent.py -q "What are the five terms in the MDP formulation of an agent, and why is reward called a proxy?"
```

**Expected behavior:** one or more `search_notes` calls, then an answer naming the five MDP
terms (state, action, policy, reward, transition) and explaining reward as a proxy, each
grounded with `[source: agent-loop.txt]`.

**Actual output** (unedited):

![Baseline agent running successfully: the search_notes tool call, the five MDP terms each with a [source: agent-loop.txt] citation, and the reward-as-proxy explanation.](baseline-run-screenshot.png){width=4.1in}

**What worked:** retrieval, grounding, and citation were correct, and the agent chose the
number of searches itself rather than following a fixed script.

**Measured limits:** retrieval is lexical, so a paraphrased question sharing no keywords
will not match. Step count varies with sampling (2 steps / 13.5 s here, 3 steps / 71.3 s on
another run) while cited facts stayed identical. Both feed Section 6 and are the targets of
Phase 2. Full transcripts are committed under `baseline/examples/runs/`.

## 5. Reproducibility and Run Instructions

**Dependencies:** Python 3.9+ (standard library only) and Ollama running locally.
**Setup:** `ollama pull qwen3.5:4b` once, then confirm Ollama is running. No API keys or
environment variables are required. **Command:** run the Section 4 command from
`baseline/`. **Input:** `examples/notes/*.txt`, override with `-n <dir>`. **Output:**
stdout, with `--json-out <path>` to save the full trajectory. Cited facts are stable across
runs; phrasing and step count vary because the policy samples, so the trajectory JSON is
provided for exact comparison.

## 6. Initial Evaluation Plan

Measure the improved system against this baseline on a held-out set of 20 to 30 question and
answer pairs drawn from the notes, scoring **answer correctness** (graded match or
LLM-as-judge), **citation validity** (does the cited file contain the claim), **groundedness**
(unsupported claims per answer), **retrieval hit rate** (was the answer passage retrieved at
all), and **cost** (steps and seconds per question). Improvement means higher correctness and
citation validity at equal or lower cost on the same set, against the baseline numbers above.

## 7. Limitations and Next Steps

**Current limits:** retrieval matches on shared keywords, so synonyms and paraphrase fall
outside its reach; a 4B local model has limited headroom for summarizing long passages;
scope is a single course.

**Anticipated failure modes:** paraphrased and multi-hop questions, and questions whose
answer is absent from the notes, where the correct behavior is an explicit "not found" and a
small model may instead attempt an answer. Section 6 measures exactly this.

**Next phase:** replace keyword search with embedding-based retrieval, build the Section 6
harness, and optionally QLoRA fine-tune a small open model on ASU's Sol cluster.

**Dependencies:** Sol approval for the fine-tuning path and a hand-labeled evaluation set.
The retrieval and evaluation work requires neither, so progress does not block on them.
