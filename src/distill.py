"""Skill distillation (self-evolution line 2a).

Turns a finished run's distilled insights into a reusable skill markdown in the
cross-run library (~/.arbor/skills/<domain>/), so future runs auto-load it via
the existing SkillRegistry. v1 is deterministic — it lifts the merged/done node
insights the tree already abstracted; an LLM "raise the abstraction level" pass
is a later refinement. Best-effort: never fail a finished run.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .trajectory import _load_tree


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (s or "general").lower()).strip("-") or "general"


def _domain(session_dir: Path, tree_meta: dict[str, Any]) -> str:
    d = tree_meta.get("domain") or tree_meta.get("benchmark")
    if not d:
        cwd = tree_meta.get("cwd") or ""
        d = Path(cwd).name if cwd else "general"
    return _slug(str(d))


def build_skill(session_dir: Path) -> tuple[str, str] | None:
    """Return (domain, markdown) distilled from the run, or None if nothing useful."""
    session_dir = Path(session_dir)
    tree = _load_tree(session_dir)
    if not tree:
        return None
    meta = (tree.get("ROOT") or {}).get("meta", {}) if isinstance(tree.get("ROOT"), dict) else {}
    domain = _domain(session_dir, meta if isinstance(meta, dict) else {})

    wins = [n for n in tree.values() if n.get("status") in ("merged", "done") and n.get("insight")]
    if not wins:
        return None
    root_insight = (tree.get("ROOT") or {}).get("insight", "")

    lines = [
        "---",
        f"name: learned-{domain}-{session_dir.name}",
        f"description: Lessons distilled from a past {domain} run (auto-learned).",
        f"when_to_apply: At IDEATE on a {domain}-like task — treat as candidate priors, not rules.",
        "---",
        f"\n# Learned: {domain}\n",
    ]
    if root_insight:
        lines.append(root_insight.strip() + "\n")
    lines.append("## What worked / didn't (verified by held-out gate)")
    for n in sorted(wins, key=lambda x: x.get("score") or 0, reverse=True):
        lines.append(f"- [{n.get('status')}, score={n.get('score')}] {n.get('insight','').strip()}")
    return domain, "\n".join(lines)


def distill_to_library(session_dir: Path, lib_root: Path | None = None) -> Path | None:
    """Write the distilled skill into ~/.arbor/skills/<domain>/; return path or None."""
    built = build_skill(session_dir)
    if built is None:
        return None
    domain, md = built
    lib = (lib_root or Path.home() / ".arbor" / "skills") / domain
    lib.mkdir(parents=True, exist_ok=True)
    out = lib / f"learned-{Path(session_dir).name}.md"
    out.write_text(md, encoding="utf-8")
    return out
