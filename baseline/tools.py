"""
Tools available to the study-assistant agent.

Currently one tool: search_notes. It is a simple keyword-overlap retriever over
a folder of plain-text course notes. Deliberately basic (this is the BASELINE):
the improved system proposed for later phases replaces this with real embeddings
/ RAG and/or a fine-tuned model, and is evaluated against this baseline.
"""

from __future__ import annotations

import re
from pathlib import Path

# Ollama/OpenAI-style tool (function) schema the model sees.
TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "search_notes",
        "description": "Search the course notes for passages relevant to a query. "
                       "Returns the most relevant text chunks with their source filename.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A focused search query, e.g. 'agent loop MDP reward'.",
                }
            },
            "required": ["query"],
        },
    },
}

_WORD = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _WORD.findall(text.lower())


def _chunk(text: str, size: int = 900, overlap: int = 150) -> list[str]:
    """Split a document into overlapping character chunks."""
    chunks = []
    i = 0
    n = len(text)
    while i < n:
        chunks.append(text[i : i + size])
        i += size - overlap
    return chunks


def search_notes(query: str, notes_dir: Path, top_k: int = 3) -> str:
    """Keyword-overlap retrieval over .txt files in notes_dir.

    Returns a formatted string of the top_k chunks, each tagged with its source
    filename so the agent can cite it.
    """
    q_tokens = set(_tokenize(query))
    if not q_tokens:
        return "No query provided."

    scored: list[tuple[float, str, str]] = []  # (score, source, chunk)
    for path in sorted(notes_dir.glob("*.txt")):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for chunk in _chunk(text):
            c_tokens = _tokenize(chunk)
            if not c_tokens:
                continue
            overlap = sum(1 for t in c_tokens if t in q_tokens)
            if overlap == 0:
                continue
            # normalize a little by chunk length so long chunks don't dominate
            score = overlap / (1 + len(c_tokens) ** 0.5)
            scored.append((score, path.name, chunk.strip()))

    if not scored:
        return "No relevant passages found in the course notes."

    scored.sort(key=lambda x: x[0], reverse=True)
    out = []
    for rank, (score, source, chunk) in enumerate(scored[:top_k], start=1):
        snippet = " ".join(chunk.split())  # collapse whitespace
        if len(snippet) > 600:
            snippet = snippet[:600] + "..."
        out.append(f"[{rank}] source: {source}\n{snippet}")
    return "\n\n".join(out)
