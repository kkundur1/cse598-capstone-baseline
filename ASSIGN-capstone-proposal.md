# Assignment: Capstone Project Proposal (Phase 0)

Authoritative source: Canvas assignment page text (captured 2026-09-02).
This is the graded spec. Where a lecture slide disagrees, THIS wins.

## Deadline: Sunday Sep 6, 2026, 11:59 PM Phoenix time
- Canvas: "Due Sunday by 11:59pm ... This assignment must be submitted to Canvas by September 6,
  11:59 PM Phoenix Time." Available Aug 24 – Sep 6.
- Points: 100. Submission type: file upload.
- Deadline conflict resolved: the Lab 1 slide deck (p12) says "Due on Sep 9" — that is WRONG.
  The graded Canvas page says Sep 6. **Plan for Sep 6.**
- This is an INDIVIDUAL proposal. Each student proposes their own problem and submits their own
  runnable baseline.

## Purpose
Ensure each student has proposed a concrete capstone problem and created a minimal, runnable baseline.

## Deliverables (what to submit)
1. **Complete and submit the capstone project proposal template.**
   - Template file present locally: `../course_export/CSE598-capstone-proposal-template.docx`
     (text extract: `../course_export/_text/capstone-template.txt`).
2. **A link to your runnable code repository or notebook** — must be accessible to everyone.
3. **A clear README.md** explaining how to reproduce the baseline, including:
   - dependencies, setup steps
   - required API keys or environment variables
   - the exact command or notebook cells to run
   - where to find the input and the output
4. **At least one concrete test case + the actual output** from your baseline, plus a **screenshot**
   showing the baseline runs successfully and produces output.

## The most important requirement: REPRODUCIBILITY
The TA must be able to follow your README.md and run your baseline in a reasonable amount of time.

## Content the proposal must cover (from lab guidance)
- A real problem you care about (domains: traffic, healthcare, education, code, math, data, ...).
- Why it requires/benefits from agentic AI (which part the agent handles).
- An initial solution / baseline (may be AI-generated; disclose which parts).
- Measurable success criteria / metrics.

## Baseline implementation options
- **Paid API** (recommended for cost/simplicity): GPT-4o mini, GPT-4.1 mini, GPT-5 mini, etc. TA
  reported a full project costing < $5 with mini models; good instruction-following.
- **Open-source model** via Ollama (DeepSeek, Qwen, ...): free but needs a GPU. Sol offers A100/A40
  but queue waits can be long. See `SOL-supercomputer-guide.md`.
- "Runnable" bar is low: one prompt in → output out is enough. No benchmark run required.

## GenAI disclosure (course rule)
You may use AI to help draft the proposal and generate the baseline, but you MUST clearly separate
your own work from AI-generated parts and provide the interaction trace. For Claude/Kiro, contact the
TA for the submission format (ChatGPT users export the conversation to HTML).

## Open decisions needed from Karthik (see ../QUESTIONS.md)
- The problem/domain to propose.
- API vs open-source-on-Sol for the baseline.
- Where the code repo/notebook will live (GitHub recommended).
