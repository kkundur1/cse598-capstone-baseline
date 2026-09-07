[This submission used the help of generative AI tools]

Generative AI tool used: Kiro (Claude). It assisted with the design, the baseline
code, and the drafting of this proposal. Full interaction trace available on request,
per the CSE 598 Agentic AI GenAI policy.

# Capstone Project Proposal — Course Study-Assistant Agent

**Student:** Karthik Venkata Sai Reddy Kunduru (kkundur1)
**Project title:** A grounded, tool-using study-assistant agent for course materials
**Repository / notebook link:** https://github.com/kkundur1/cse598-capstone-baseline (public)
**Configuration location:** `capstone/baseline/README.md`

---

## Section 1 — Problem Definition (15)
**Task.** Build an agent that answers a student's natural-language question about a
specific course using only that course's materials, and grounds every answer in a
cited source. Input: a question (string) plus a folder of course notes (`.txt`).
Output: a concise answer that cites the source file(s) it used, or an honest "not
found" when the notes do not contain the answer.

**Intended user & situation.** A graduate student (the stakeholder) studying across
several dense courses who needs fast, *trustworthy* answers from their own lecture
notes/readings — not a general chatbot that may hallucinate or cite nothing.

**Success vs. failure (operational).**
- Success: the answer is factually correct with respect to the notes AND includes a
  correct source citation for the claim.
- Failure: the answer is wrong, unsupported/uncited, or hallucinated; or the agent
  claims an answer when the notes lack it.

## Section 2 — Motivation and Project Scope (15)
**Why it matters.** Ungrounded LLM answers are unsafe for studying — a confident
wrong answer costs exam points. Retrieval-grounded, citation-first answering over a
student's *own* materials is directly useful and directly measurable.

**Why agentic AI is a reasonable approach.** The task benefits from a real agent
loop: the model decides *whether and what* to retrieve, reads the observation, and
can search again before answering — Observe→Decide→Act→Observe. That is tool use +
planning under the course's MDP framing, not a single prompt.

**In scope this semester:** single-course Q&A; one retrieval tool; grounded,
cited answers; an evaluation harness comparing an improved system to this baseline.
**Out of scope:** multi-course reasoning, web access, write actions, multi-agent
orchestration, and UI polish.

## Section 3 — Runnable Baseline (25)
A working agent (`capstone/baseline/`) that runs a **bounded agent loop with one
tool call** on a **local LLM via Ollama** (`qwen3.5:4b`) — no API key, no cost.

- **Model/tools/libraries:** Ollama chat API (local) for the policy; a `search_notes`
  tool (keyword-overlap retriever over `.txt` notes). Pure Python standard library.
- **Step by step:** (1) system prompt instructs "retrieve, then answer with a
  citation"; (2) LLM either calls `search_notes(query)` or answers; (3) tool output
  is appended as an observation; (4) loop repeats (cap 4 steps) until a final cited
  answer.
- **Why a reasonable starting point:** it is genuinely agentic (real tool-calling
  loop) yet simple and deterministic in its retrieval, giving a clean, honest bar to
  beat. The keyword retriever is intentionally weak so later RAG/fine-tuning shows
  measurable gains.
- **Baseline files:** `capstone/baseline/agent.py` (loop), `tools.py` (tool +
  schema), `examples/notes/` (course notes), `examples/runs/` (a saved run).

## Section 4 — Test Case and Baseline Output (25)
**Sample input (command):**
```
python agent.py -q "What are the five terms in the MDP formulation of an agent, and why is reward called a proxy?"
```
**Expected behavior:** one or more `search_notes` calls, then an answer listing the
five MDP terms (state, action, policy, reward, transition) and explaining "reward as
a proxy," each grounded with `[source: agent-loop.txt]`.

**Actual output (real local run, `qwen3.5:4b` via Ollama, 3 steps / 2 tool calls, ~71s).**
Verbatim console transcript:

```
Question: What are the five terms in the MDP formulation of an agent, and why is reward called a proxy?
Model:    qwen3.5:4b   Notes: ...\baseline\examples\notes
------------------------------------------------------------
  [step 1] TOOL CALL: search_notes({'query': 'MDP formulation agent five terms'})
  [step 2] TOOL CALL: search_notes({'query': 'reward proxy MDP formulation'})
  [step 3] FINAL ANSWER produced.
------------------------------------------------------------
ANSWER:
The five terms in the MDP formulation of an agent are:
1. State (s): what information matters right now [source: agent-loop.txt]
2. Action (a): what the agent can do next [source: agent-loop.txt]
3. Policy (pi(a|s) or pi(a|o)): how the agent chooses an action [source: agent-loop.txt]
4. Transition (T): the state update produced by running tools/APIs [source: agent-loop.txt]
5. Reward (R): task success, latency/cost, and user utility [source: agent-loop.txt]

Why reward is a "proxy": the reward signal is a simplified/aggregated stand-in for the
true objective, so it can be gamed by shortcuts. Example: an agent rewarded +1 for any
completed booking may grab the first available flight and ignore price or user
preferences, because that maximizes the coarse signal [source: agent-loop.txt].
[3 step(s), 71.3s]
```

The full transcript is committed at `baseline/examples/runs/example-run.txt` and the
machine-readable trajectory at `baseline/examples/runs/example-run.json` in the public repo.

**Screenshot:** _<PASTE a screenshot of the terminal running the command above — re-run
the Section-4 command and capture the window, then insert the image here.>_

**What worked / didn't:** Worked — grounded, cited, correct, and it self-issued a
second search to cover the second half of the question. Limitation — keyword
retrieval can miss paraphrased queries (no semantic match), which motivates the
Phase-2 improvement.

## Section 5 — Reproducibility and Run Instructions (10)
- **Dependencies:** Python 3.9+ (standard library only) and Ollama running locally.
- **Setup:** `ollama pull qwen3.5:4b` (once); ensure Ollama is running.
- **API keys / env vars:** none.
- **Exact command:** from `capstone/baseline/`, run the command in Section 4.
- **Input location:** `examples/notes/*.txt` (swap with `-n <dir>`).
- **Output location:** stdout; optional trajectory via `--json-out <path>`.
- **Known limitation:** LLM wording varies slightly between runs; cited facts are
  stable. Full details in `capstone/baseline/README.md`.

## Section 6 — Initial Evaluation Plan (5)
Compare the improved system against this baseline on a held-out set of ~20–30
question/answer pairs drawn from the course notes, measuring:
- **Answer correctness** (exact/graded match or LLM-as-judge).
- **Citation validity** (does the cited source actually contain the claim?).
- **Groundedness / hallucination rate** (unsupported claims per answer).
- **Retrieval hit rate** (did the right passage get retrieved?).
- **Cost/latency** (steps per question, seconds per answer).
Evidence of improvement = higher correctness + citation validity and lower
hallucination than the baseline on the same set.

## Section 7 — Limitations and Next Steps (5)
- **Known weaknesses:** keyword retrieval misses synonyms/paraphrase; small local
  model can mis-summarize; single-course only.
- **Expected failures:** paraphrased questions, multi-hop questions, notes that lack
  the answer (should say "not found" but a weak model may guess).
- **Next phase:** (1) replace keyword search with embedding-based RAG; (2) optionally
  QLoRA-fine-tune a small open model for better tool-use/grounding, trained on ASU's
  Sol A100 cluster (needs the sponsored HPC account — see `docs/07-sol-project-plan.md`);
  (3) build the evaluation harness from Section 6.
- **Risks / help needed:** Sol account sponsor approval; a labeled Q/A eval set; time.

---

## Submission checklist
1. [DONE] Public GitHub repo pushed under this account:
   https://github.com/kkundur1/cse598-capstone-baseline
2. [DONE] Repo link recorded in "Repository / notebook link" above.
3. [TODO — you] Run the Section-4 command, screenshot the terminal, and paste it into
   Section 4 (the saved transcript is already committed at
   `baseline/examples/runs/example-run.txt`).
4. [TODO — you] Submit `PROPOSAL.docx` to Canvas by **Sep 6, 11:59 PM Phoenix**.
