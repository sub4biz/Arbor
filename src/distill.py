"""Experience distillation (self-evolution line 2).

Turns a finished run into a consolidated EXPERIENCE.md in its own session folder,
layered by altitude (meta = cross-domain strategy; domain = idea-class wins/losses).
Task-specific findings stay in REPORT/trajectory. Experience is recalled per-session
by recall.find_similar, not registered as global skills. Best-effort: never fail a run.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .trajectory import _load_tree


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (s or "general").lower()).strip("-") or "general"


def _domain(tree_meta: dict[str, Any], session_dir: Path) -> str:
    d = tree_meta.get("domain") or tree_meta.get("benchmark") or tree_meta.get("cwd")
    if not d:
        # session lives at <project>/.arbor/sessions/<run>; recover the project name.
        parts = session_dir.resolve().parts
        d = parts[-4] if len(parts) >= 4 and parts[-3:-1] == ("sessions",) else ""
        if not d and ".arbor" in parts:
            d = parts[parts.index(".arbor") - 1]
    return _slug(Path(str(d)).name) if d else "general"


def _frag(name: str, desc: str, when: str, title: str, body: list[str]) -> str:
    return "\n".join(["---", f"name: {name}", f"description: {desc}",
                      f"when_to_apply: {when}", "---", f"\n# {title}\n", *body])


def build_skills(session_dir: Path) -> list[tuple[str, str, str]]:
    """Return [(level, domain, markdown), ...] — empty if nothing worth keeping."""
    session_dir = Path(session_dir)
    tree = _load_tree(session_dir)
    if not tree:
        return []
    root = tree.get("ROOT") or {}
    meta = root.get("meta", {}) if isinstance(root.get("meta"), dict) else {}
    domain = _domain(meta, session_dir)
    out: list[tuple[str, str, list[str]]] = []  # (level, domain, bullets)

    # domain layer — verified wins/losses, transferable within domain
    wins = [n for n in tree.values() if n.get("status") in ("merged", "done") and n.get("insight")]
    dom_bul = []
    if root.get("insight"):
        dom_bul.append(root["insight"].strip().split("\n")[0][:200])
    for n in sorted(wins, key=lambda x: x.get("score") or 0, reverse=True):
        dom_bul.append(f"[{n.get('status')}, score={n.get('score')}] {n.get('insight','').strip()[:200]}")
    if dom_bul:
        out.append(("domain", domain, dom_bul))

    # meta layer — strategy from the tree's shape, transfers across domains
    pruned = [n for n in tree.values() if n.get("status") == "pruned"]
    process = [f"dead-end: {n.get('insight','').strip()[:160]}" for n in pruned if n.get("insight")]
    try:
        from .experience import load_experience
        trail = [e for e in load_experience(session_dir) if e.get("status") in ("pruned", "done")]
        process += [f"{e['node_id']}: {e['insight'][:140]}" for e in trail if e.get("insight")]
    except Exception:  # pylint: disable=broad-exception-caught
        pass
    if process:
        out.append(("meta", "general", process))
    return out


def distill_to_session(session_dir: Path) -> Path | None:
    """Write a consolidated EXPERIENCE.md inside the run's own session folder.

    Experience stays per-session (not a global skill library): future runs search
    sessions, ask the user, and compose a tailored block. Returns the path or None.
    """
    session_dir = Path(session_dir)
    frags = build_skills(session_dir)
    if not frags:
        return None
    domain = next((d for lvl, d, _ in frags if lvl == "domain"), "general")
    lines: list[str] = []
    for level, _d, bullets in frags:
        lines.append(f"## {level}")
        lines += [f"- {b}" for b in bullets]
    md = _frag(f"experience-{domain}", f"Experience from a {domain} run.",
               "reuse on a similar topic", f"Experience: {domain}", lines)
    out = session_dir / "EXPERIENCE.md"
    out.write_text(md, encoding="utf-8")
    return out
