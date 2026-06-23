"""Integrity guard for protected paths.

Pure helpers (no git): build a SHA-256 manifest of the files matched by a set
of protected globs, verify a worktree against that manifest, and best-effort
mark those files read-only. The manifest is the portable tamper-detection
guarantee; read-only is opportunistic prevention (strong on POSIX, weak on
Windows) and every OS operation is wrapped so it can never fail a run.
"""

from __future__ import annotations

import hashlib
import logging
import os
import stat
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
from typing import Iterator, Literal

log = logging.getLogger(__name__)

_CHUNK = 1 << 20  # 1 MiB


def iter_protected_files(root: Path, protected_paths: list[str]) -> Iterator[Path]:
    """Yield every existing file under *root* matching any protected glob.

    Patterns are ``fnmatch``-style relative to *root* (e.g. ``data/**`` matches
    anything under ``data/``) — the same convention the merge guard in
    ``git_ops.py`` already uses, so runtime and merge-time enforcement agree.
    Only regular files are yielded, sorted for determinism, de-duplicated.
    """
    if not protected_paths:
        return
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if any(fnmatch(rel, pattern) for pattern in protected_paths):
            yield path


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(_CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def build_protected_manifest(root: Path, protected_paths: list[str]) -> dict[str, str]:
    """Map ``posix-relpath -> sha256`` for every protected file under *root*."""
    manifest: dict[str, str] = {}
    for path in iter_protected_files(root, protected_paths):
        rel = path.relative_to(root).as_posix()
        manifest[rel] = _sha256(path)
    return manifest


@dataclass(frozen=True)
class ProtectedChange:
    path: str
    kind: Literal["modified", "added", "removed"]


def verify_protected_manifest(
    root: Path, protected_paths: list[str], manifest: dict[str, str]
) -> list[ProtectedChange]:
    """Return the changes between *manifest* and the current files under *root*."""
    current = build_protected_manifest(root, protected_paths)
    changes: list[ProtectedChange] = []
    for rel, digest in current.items():
        if rel not in manifest:
            changes.append(ProtectedChange(rel, "added"))
        elif manifest[rel] != digest:
            changes.append(ProtectedChange(rel, "modified"))
    for rel in manifest:
        if rel not in current:
            changes.append(ProtectedChange(rel, "removed"))
    return sorted(changes, key=lambda c: c.path)


def _chmod(path: Path, mode: int) -> None:
    try:
        os.chmod(path, mode)
    except OSError as exc:  # pragma: no cover - platform dependent
        log.warning("integrity: chmod failed on %s: %s", path, exc)


def apply_readonly(root: Path, protected_paths: list[str]) -> None:
    """Best-effort: make protected files read-only. Never raises."""
    for path in iter_protected_files(root, protected_paths):
        _chmod(path, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)


def clear_readonly(root: Path, protected_paths: list[str]) -> None:
    """Best-effort: restore writability so cleanup never fails. Never raises."""
    for path in iter_protected_files(root, protected_paths):
        _chmod(path, stat.S_IWRITE | stat.S_IREAD)
