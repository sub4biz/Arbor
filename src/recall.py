"""Experience recall: find prior runs whose lessons may help the current topic.

Each finished run leaves an ``EXPERIENCE.md`` in its session folder. When a new
run starts, intake scans past sessions, scores each against the current research
topic, and (if a strong match exists) asks the user whether to reuse it. Accepted
matches are composed into a tailored experience block for the agent.

Matching is deterministic keyword overlap here — cheap and good enough to gate
the ask; an embedding/LLM judge can replace ``_score`` later.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

_STOP = {"the", "a", "an", "to", "of", "and", "for", "on", "in", "with", "without",
         "maximize", "minimize", "improve", "optimize", "score", "test", "dev", "task"}


def _tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", (text or "").lower()) if len(w) > 2 and w not in _STOP}


def _score(topic: set[str], experience: set[str]) -> float:
    if not topic or not experience:
        return 0.0
    return len(topic & experience) / len(topic)  # fraction of topic terms covered


def find_similar(cwd: str, topic: str, *, limit: int = 3, threshold: float = 0.25) -> list[dict[str, Any]]:
    """Return prior sessions ranked by topic overlap: [{name, path, score, text}]."""
    sessions = Path(cwd) / ".arbor" / "sessions"
    if not sessions.is_dir():
        return []
    tt = _tokens(topic)
    hits: list[dict[str, Any]] = []
    for exp in sessions.glob("*/EXPERIENCE.md"):
        text = exp.read_text(encoding="utf-8")
        s = _score(tt, _tokens(text))
        if s >= threshold:
            hits.append({"name": exp.parent.name, "path": str(exp), "score": round(s, 3), "text": text})
    hits.sort(key=lambda h: -h["score"])
    return hits[:limit]


def list_experiences(cwd: str, limit: int = 8) -> list[tuple[str, str]]:
    """[(session_name, first-line summary)] of prior runs that left experience."""
    sessions = Path(cwd) / ".arbor" / "sessions"
    out: list[tuple[str, str]] = []
    if not sessions.is_dir():
        return out
    for exp in sorted(sessions.glob("*/EXPERIENCE.md"), reverse=True)[:limit]:
        desc = ""
        for ln in exp.read_text(encoding="utf-8").splitlines():
            if ln.startswith("description:"):
                desc = ln.split(":", 1)[1].strip()
                break
        out.append((exp.parent.name, desc))
    return out


def compose_for_topic(cwd: str, topic: str) -> str:
    """Compose one tailored experience block from sessions matching the topic."""
    hits = find_similar(cwd, topic)
    if not hits:
        return ""
    parts = ["# Prior experience (candidate priors — verify, don't blindly apply)"]
    for h in hits:
        parts.append(f"\n## from {h['name']} (match {h['score']})\n{h['text']}")
    return "\n".join(parts)
