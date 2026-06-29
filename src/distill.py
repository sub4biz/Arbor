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
    merged = [n for n in tree.values() if n.get("status") == "merged"]
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


def _norm(b: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"\[.*?\]|score=\S+|\d+", "", b.lower())).strip()


def distill_to_library(session_dir: Path, lib_root: Path | None = None) -> list[Path]:
    """Merge layered bullets into one consolidated skill per (level, domain).

    Recurring lessons reinforce (occurrence count = confidence) instead of piling
    up one file per run. Deterministic dedup by normalized text. Returns paths.
    """
    root = lib_root or Path.home() / ".arbor" / "skills"
    paths: list[Path] = []
    for level, domain, bullets in build_skills(session_dir):
        d = root / level / domain
        d.mkdir(parents=True, exist_ok=True)
        out = d / "learned.md"
        seen: dict[str, list[str]] = {}  # norm -> [count, text]
        if out.exists():  # parse prior counts from "- [xN] text"
            for ln in out.read_text(encoding="utf-8").splitlines():
                m = re.match(r"- \[x(\d+)\] (.+)", ln)
                if m:
                    seen[_norm(m.group(2))] = [int(m.group(1)), m.group(2)]
        for b in bullets:
            k = _norm(b)
            if k in seen:
                seen[k][0] += 1
            else:
                seen[k] = [1, b]
        ranked = sorted(seen.values(), key=lambda x: -x[0])
        when = ("any task — search-strategy priors" if level == "meta"
                else f"a {domain}-like task — candidate priors, not rules")
        body = [f"- [x{c}] {t}" for c, t in ranked]
        out.write_text(_frag(f"learned-{level}-{domain}", f"Consolidated {level} lessons.",
                             f"IDEATE on {when}.", f"Learned: {level}/{domain}", body),
                       encoding="utf-8")
        paths.append(out)
    return paths
