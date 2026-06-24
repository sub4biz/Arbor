"""``arbor.zoo`` — the benchmark format, its verifier, scaffolder, and collection spine.

A benchmark is a self-contained directory under ``arbor-zoo/``: a README whose YAML
front-matter is a tiny machine contract and whose body is prose, a PROVENANCE card, a
runnable baseline (one or more code files), and a protected eval entrypoint. This package
provides pack discovery + the contract (:mod:`~arbor.zoo.pack`), the
``arbor benchmark verify`` gate (:mod:`~arbor.zoo.verify`), the scaffolder
(:mod:`~arbor.zoo.scaffold`), and the ``arbor benchmark add`` collection spine
(:mod:`~arbor.zoo.acquire` / :mod:`~arbor.zoo.cache` / :mod:`~arbor.zoo.collect`).
See ``docs/zoo.md``.
"""

from __future__ import annotations

from .acquire import Acquired, Acquirer, GitRepoAcquirer, Sources, select_acquirer
from .cache import Manifest, benchmark_cache_dir, cache_root
from .collect import CollectResult, collect
from .pack import (
    EVAL_ENTRYPOINTS,
    Contract,
    PackSummary,
    discover_packs,
    find_eval_entrypoint,
    is_pack_dir,
    load_contract,
    read_front_matter,
)
from .scaffold import ScaffoldResult, scaffold_benchmark
from .verify import VerifyResult, verify_pack

__all__ = [
    "EVAL_ENTRYPOINTS",
    "Acquired",
    "Acquirer",
    "CollectResult",
    "Contract",
    "GitRepoAcquirer",
    "Manifest",
    "PackSummary",
    "ScaffoldResult",
    "Sources",
    "VerifyResult",
    "benchmark_cache_dir",
    "cache_root",
    "collect",
    "discover_packs",
    "find_eval_entrypoint",
    "is_pack_dir",
    "load_contract",
    "read_front_matter",
    "scaffold_benchmark",
    "select_acquirer",
    "verify_pack",
]
