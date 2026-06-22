"""``arbor idea-check`` — zero-config novelty / prior-art check for one idea.

Runs a single SearchAgent over the public alphaXiv API (no endpoint, no API
key) and prints a lightweight novelty verdict: a summary of what's been done in
the space, the closest related papers, a novelty assessment, and overlap risks.

This is the standalone counterpart to the coordinator's in-loop
``SearchIdeaContext`` annotation — useful for sanity-checking an idea before
ever starting a run.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

import typer


def idea_check_command(
    hypothesis: str = typer.Argument(
        ..., help="The research hypothesis / idea to novelty-check."
    ),
    focus: str | None = typer.Option(
        None, "--focus", help="Optional focus directive (e.g. 'prefer arxiv 2024')."
    ),
    model: str | None = typer.Option(
        None, "--model", help="Override the model used for the check."
    ),
    as_json: bool = typer.Option(
        False, "--json", help="Print the raw SearchAgent JSON instead of Markdown."
    ),
    cwd: Path | None = typer.Option(
        None, "--cwd", help="Working directory (default: current directory)."
    ),
) -> None:
    """Zero-config novelty / prior-art check for one idea via the alphaXiv public API."""
    from ...coordinator.config import CoordinatorConfig
    from ...coordinator.main import create_provider
    from ...coordinator.tools.search_ctx import _extract_json_block, _render_markdown
    from ...search_agent.agent import build_search_agent
    from ...search_agent.prompts import build_search_user_prompt
    from ..user_config import llm_defaults

    # Build a CoordinatorConfig from the saved global LLM defaults
    # (~/.arbor/config.yaml: provider / model / base_url / api_key / openai_api),
    # the same source `arbor run` uses, then force the alphaXiv backend on.
    work_dir = os.path.abspath(str(cwd) if cwd is not None else ".")
    llm = llm_defaults()
    kw: dict = {"cwd": work_dir}
    for key in ("provider", "model", "base_url", "api_key", "openai_api"):
        if llm.get(key) is not None:
            kw[key] = llm[key]
    if model:
        kw["model"] = model
    try:
        config = CoordinatorConfig(**kw)
    except Exception as exc:  # noqa: BLE001
        typer.secho(f"error: could not build config: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    config.search.enabled = True
    config.search.builtin_backend = "alphaxiv"

    try:
        provider = create_provider(config)
    except Exception as exc:  # noqa: BLE001
        typer.secho(
            f"error: could not create an LLM provider — check your credentials "
            f"(run `arbor login` or `arbor setup`): {exc}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1) from exc

    typer.secho(
        "Checking idea novelty against alphaXiv… (this runs one SearchAgent)",
        fg=typer.colors.CYAN,
        err=True,
    )

    async def _run() -> str:
        agent = build_search_agent(
            provider=provider,
            search_config=config.search,
            cwd=work_dir,
            meta_config=config,
            context_window=config.context_window,
        )
        return await agent.run(
            build_search_user_prompt(hypothesis=hypothesis, focus=focus)
        )

    try:
        raw = asyncio.run(_run())
    except Exception as exc:  # noqa: BLE001
        typer.secho(f"error: idea check failed: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    parsed = _extract_json_block(raw)
    if as_json or parsed is None:
        if parsed is None and not as_json:
            typer.secho(
                "warning: could not parse a JSON verdict — showing raw output.",
                fg=typer.colors.YELLOW,
                err=True,
            )
        typer.echo(raw.strip())
        return

    try:
        from rich.console import Console
        from rich.markdown import Markdown

        Console().print(Markdown(_render_markdown(parsed)))
    except Exception:  # noqa: BLE001 - rich is optional / TTY-less fallback
        typer.echo(_render_markdown(parsed))
