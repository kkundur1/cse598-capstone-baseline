"""
Minimal agentic baseline: a course study-assistant agent.

This is the Phase-0 capstone baseline. It is intentionally simple but is a REAL
agent: it runs an agent loop where a local LLM (via Ollama) decides to call a
tool (course-notes search), receives the tool output as an observation, and then
produces a final grounded answer. This demonstrates the core agent loop
(Observe -> Decide -> Act -> Observe -> ... -> Final) with one tool call.

Design (maps to CSE 598 Lecture 2 MDP framing):
  - State/context: the user question + conversation so far + tool outputs.
  - Actions: call `search_notes(query)` OR emit a final answer.
  - Policy: the LLM, prompted to either request a tool call or answer.
  - Transition: running the tool changes the context (adds retrieved passages).
  - Reward (eval, not used at runtime): did it answer correctly and cite a source?

No API key, no cloud: uses local Ollama. Base model configurable via --model.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import urllib.request

from tools import search_notes, TOOL_SPEC

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "qwen3.5:4b"
MAX_STEPS = 4  # hard cap on agent-loop iterations (bounded, per course guidance)

SYSTEM_PROMPT = """You are a course study assistant. Answer the student's question
using ONLY the course notes available through the search_notes tool.

Rules:
- If you need information, call the search_notes tool with a focused query.
- After you have enough context from tool results, give a concise final answer.
- Always ground your answer in the retrieved notes and cite the source file(s)
  in the form [source: <filename>]. If the notes do not contain the answer, say
  so honestly instead of guessing.
"""


def call_ollama(model: str, messages: list, tools: list | None = None) -> dict:
    """One sampling request to the local Ollama chat endpoint (non-streaming)."""
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "think": False,
    }
    if tools:
        payload["tools"] = tools
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run_agent(question: str, model: str, notes_dir: Path, verbose: bool = True) -> dict:
    """Run the bounded agent loop. Returns a trajectory dict for evaluation."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    trajectory = {"question": question, "model": model, "steps": []}

    for step in range(1, MAX_STEPS + 1):
        resp = call_ollama(model, messages, tools=[TOOL_SPEC])
        msg = resp.get("message", {})
        tool_calls = msg.get("tool_calls") or []

        if tool_calls:
            # ACT: the policy chose to call a tool.
            messages.append(msg)
            for tc in tool_calls:
                fn = tc.get("function", {})
                name = fn.get("name")
                args = fn.get("arguments", {})
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except json.JSONDecodeError:
                        args = {"query": args}
                if verbose:
                    print(f"  [step {step}] TOOL CALL: {name}({args})")
                if name == "search_notes":
                    observation = search_notes(str(args.get("query", "")), notes_dir)
                else:
                    observation = f"Unknown tool: {name}"
                # OBSERVE: feed the tool result back into the context.
                messages.append({"role": "tool", "content": observation})
                trajectory["steps"].append(
                    {"type": "tool_call", "name": name, "args": args,
                     "observation_preview": observation[:200]}
                )
            continue  # loop again so the model can use the observation

        # No tool call => final answer.
        answer = msg.get("content", "").strip()
        trajectory["steps"].append({"type": "final_answer", "content": answer})
        trajectory["final_answer"] = answer
        trajectory["num_steps"] = step
        if verbose:
            print(f"  [step {step}] FINAL ANSWER produced.")
        return trajectory

    # Hit the step cap without a final answer: force one.
    messages.append({"role": "user", "content": "Give your best final answer now, with a citation."})
    resp = call_ollama(model, messages)
    answer = resp.get("message", {}).get("content", "").strip()
    trajectory["steps"].append({"type": "final_answer_forced", "content": answer})
    trajectory["final_answer"] = answer
    trajectory["num_steps"] = MAX_STEPS
    return trajectory


def main() -> int:
    parser = argparse.ArgumentParser(description="Course study-assistant agent baseline.")
    parser.add_argument("--question", "-q", required=True, help="The student question.")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL, help="Ollama model tag.")
    parser.add_argument("--notes", "-n", default=None,
                        help="Directory of .txt course notes (default: examples/notes).")
    parser.add_argument("--json-out", default=None, help="Optional path to write the trajectory JSON.")
    args = parser.parse_args()

    notes_dir = Path(args.notes) if args.notes else Path(__file__).parent / "examples" / "notes"
    if not notes_dir.is_dir():
        print(f"ERROR: notes dir not found: {notes_dir}", file=sys.stderr)
        return 2

    print(f"Question: {args.question}")
    print(f"Model:    {args.model}   Notes: {notes_dir}")
    print("-" * 60)
    t0 = time.time()
    traj = run_agent(args.question, args.model, notes_dir)
    dt = time.time() - t0
    print("-" * 60)
    print("ANSWER:\n" + traj.get("final_answer", "(none)"))
    print(f"\n[{traj.get('num_steps')} step(s), {dt:.1f}s]")

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(traj, indent=2), encoding="utf-8")
        print(f"Trajectory written to {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
