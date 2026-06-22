"""Tests for the pre-experiment auto-search wiring.

``dispatch_auto_search`` fires a background SearchAgent on a freshly-added node,
bypassing the post-experiment validation gate. Here we patch ``_run_one`` so no
real SearchAgent / network is involved.
"""

from __future__ import annotations

import asyncio


from arbor.coordinator.config import CoordinatorConfig
from arbor.coordinator.idea_tree import IdeaTree, Node
from arbor.coordinator.tools import search_ctx
from arbor.coordinator.tools.search_ctx import (
    dispatch_auto_search,
    wait_for_pending_searches,
)
from arbor.coordinator.tools.tree_ops import TreeAddNodeTool


class _Provider:
    model = "m"


def _tree() -> IdeaTree:
    return IdeaTree(Node(id="ROOT", parent_id=None, depth=0))


def _cfg(*, auto: bool, backend: str = "alphaxiv") -> CoordinatorConfig:
    cfg = CoordinatorConfig(cwd=".")
    cfg.search.enabled = True
    cfg.search.builtin_backend = backend
    cfg.search.auto_search_on_add = auto
    return cfg


def _patch_run_one(monkeypatch, calls):
    async def fake_run_one(*, tree, config, provider, node_id, focus):
        calls.append((node_id, focus))
        await tree.async_update_node(node_id, related_work="[fake novelty verdict]")
        return f"{node_id}: done"

    monkeypatch.setattr(search_ctx, "_run_one", fake_run_one)


def test_dispatch_auto_search_runs_when_enabled(monkeypatch):
    calls: list = []
    _patch_run_one(monkeypatch, calls)
    tree = _tree()
    # Add a child node directly so we have something to annotate.
    node = Node(id="1", parent_id="ROOT", depth=1, hypothesis="Some idea")
    tree.add_node(node)

    async def _go():
        dispatched = dispatch_auto_search(tree, _cfg(auto=True), _Provider(), "1")
        assert dispatched is True
        await wait_for_pending_searches()

    asyncio.run(_go())
    assert calls == [("1", None)]
    assert tree.get_node("1").related_work == "[fake novelty verdict]"


def test_dispatch_auto_search_noop_when_disabled(monkeypatch):
    calls: list = []
    _patch_run_one(monkeypatch, calls)
    tree = _tree()
    node = Node(id="1", parent_id="ROOT", depth=1, hypothesis="Some idea")
    tree.add_node(node)

    async def _go():
        return dispatch_auto_search(tree, _cfg(auto=False), _Provider(), "1")

    assert asyncio.run(_go()) is False
    assert calls == []


def test_dispatch_auto_search_noop_without_backend(monkeypatch):
    calls: list = []
    _patch_run_one(monkeypatch, calls)
    tree = _tree()
    node = Node(id="1", parent_id="ROOT", depth=1, hypothesis="Some idea")
    tree.add_node(node)

    async def _go():
        return dispatch_auto_search(tree, _cfg(auto=True, backend="none"), _Provider(), "1")

    assert asyncio.run(_go()) is False
    assert calls == []


def test_tree_add_node_triggers_auto_search(monkeypatch):
    calls: list = []
    _patch_run_one(monkeypatch, calls)
    tree = _tree()
    tool = TreeAddNodeTool(cwd=".", tree=tree, config=_cfg(auto=True), provider=_Provider())

    async def _go():
        msg = await tool.execute(parent_id="ROOT", hypothesis="A novel idea")
        await wait_for_pending_searches()
        return msg

    msg = asyncio.run(_go())
    assert "pre-experiment novelty check dispatched" in msg
    assert len(calls) == 1
    # The freshly-added node got the annotation.
    node_id = calls[0][0]
    assert tree.get_node(node_id).related_work == "[fake novelty verdict]"


def test_tree_add_node_no_auto_search_when_disabled(monkeypatch):
    calls: list = []
    _patch_run_one(monkeypatch, calls)
    tree = _tree()
    tool = TreeAddNodeTool(cwd=".", tree=tree, config=_cfg(auto=False), provider=_Provider())

    async def _go():
        return await tool.execute(parent_id="ROOT", hypothesis="A plain idea")

    msg = asyncio.run(_go())
    assert "pre-experiment novelty check" not in msg
    assert calls == []
