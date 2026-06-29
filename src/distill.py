"""Skill distillation (self-evolution line 2a).

Turns a finished run into reusable skills in the cross-run library
(~/.arbor/skills/), tagged by **altitude** so recall can reuse them safely:

  * ``meta``   — research strategy from the tree shape/process (pruned dead-ends,
                 merge timing). Transfers across domains.
  * ``domain`` — what classes of idea won/lost (from verified node insights).
                 Transfers within a domain.
  * task-specific findings stay in the run's REPORT/trajectory, not the library —
    they don't transfer and would only pollute recall.

Deterministic v1: lifts what the tree already abstracted. An LLM "raise the
abstraction level" pass and dedup/confidence are later refinements. Best-effort:
never fail a finished run.
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
    run = session_dir.name
    out: list[tuple[str, str, str]] = []

    # domain layer — verified wins/losses, transferable within domain
    wins = [n for n in tree.values() if n.get("status") in ("merged", "done") and n.get("insight")]
    if wins or root.get("insight"):
        body = ([root["insight"].strip() + "\n"] if root.get("insight") else [])
        body.append("## Idea classes that won / lost (held-out verified)")
        for n in sorted(wins, key=lambda x: x.get("score") or 0, reverse=True):
            body.append(f"- [{n.get('status')}, score={n.get('score')}] {n.get('insight','').strip()}")
        out.append(("domain", domain, _frag(
            f"learned-{domain}-{run}", f"Domain lessons from a {domain} run.",
            f"IDEATE on a {domain}-like task — candidate priors, not rules.",
            f"Learned: {domain}", body)))

    # meta layer — strategy from the tree's shape, transfers across domains
    pruned = [n for n in tree.values() if n.get("status") == "pruned"]
    merged = [n for n in tree.values() if n.get("status") == "merged"]
    process = [f"- {len(merged)} merged, {len(pruned)} pruned of {max(0,len(tree)-1)} ideas — "
               f"{'broad search paid off' if merged else 'most directions died; prune faster'}."]
    process += [f"- dead-end: {n.get('insight','').strip()[:160]}" for n in pruned if n.get("insight")]
    # fold in the live process trail (lessons logged mid-run, beyond the final tree)
    try:
        from .experience import load_experience
        trail = [e for e in load_experience(session_dir) if e.get("status") in ("pruned", "done")]
        process += [f"- step {e['node_id']}: {e['insight'][:140]}" for e in trail if e.get("insight")]
    except Exception:  # pylint: disable=broad-exception-caught
        pass
    if pruned or merged:
        out.append(("meta", "general", _frag(
            f"strategy-{run}", "Cross-domain research strategy from a past run.",
            "IDEATE on any task — search-strategy priors.", "Learned: strategy", process)))
    return out


def distill_to_library(session_dir: Path, lib_root: Path | None = None) -> list[Path]:
    """Write layered skills into <lib>/<level>/<domain>/; return paths written."""
    root = lib_root or Path.home() / ".arbor" / "skills"
    paths: list[Path] = []
    for level, domain, md in build_skills(session_dir):
        d = root / level / domain
        d.mkdir(parents=True, exist_ok=True)
        out = d / f"learned-{Path(session_dir).name}.md"
        out.write_text(md, encoding="utf-8")
        paths.append(out)
    return paths
