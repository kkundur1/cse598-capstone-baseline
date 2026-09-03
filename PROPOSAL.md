[This submission used the help of generative AI tools]

Generative AI tool used: Kiro (Claude). It assisted with the design, the baseline
code, and the drafting of this proposal. Full interaction trace available on request,
per the CSE 598 Agentic AI GenAI policy.

# Capstone Project Proposal — Course Study-Assistant Agent

**Student:** Karthik Venkata Sai Reddy Kunduru (kkundur1)
**Project title:** A grounded, tool-using study-assistant agent for course materials
**Repository / notebook link:** <ADD PUBLIC GITHUB LINK — see "How to publish" at the bottom>
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

**Actual output (real run, RTX 3070 laptop, ~18s, 2 tool calls + final answer):**
saved verbatim in `capstone/baseline/examples/runs/example-run.txt`, with the full
trajectory in `example-run.json`. The agent correctly returned all five terms with
citations and explained the reward-proxy shortcut using the booking example.
**Screenshot:** <ADD SCREENSHOT of the terminal run — see "How to publish".>

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

## How to publish (do these before submitting)
1. Create a public GitHub repo and push the `capstone/` folder (commit under your own
   account — the course requires it). With GitHub CLI: `gh auth login`, then
   `gh repo create <name> --public --source=. --push` from the capstone folder.
2. Put the repo link in "Repository / notebook link" above.
3. Take a screenshot of the terminal running the Section-4 command (or use
   `examples/runs/example-run.txt`) and add it to Section 4 / the repo.
4. Export this proposal to the required format (the template is a .docx; use
   `pandoc PROPOSAL.md -o PROPOSAL.docx` if a Word file is needed) and submit to
   Canvas by **Sep 6, 11:59 PM Phoenix**.
