"""ChatGPT-subscription Responses provider (experimental).

Authenticates with an OAuth access token obtained via ``arbor login openai``
and targets the ChatGPT backend (``chatgpt.com/backend-api/codex``) instead of
the pay-per-token ``api.openai.com`` endpoint. Everything else — message
conversion, reasoning replay, tool calls, parsing — is inherited from
:class:`OpenAIResponsesProvider`.

Tokens are refreshed transparently before each call. Using a ChatGPT
subscription token with third-party tooling may violate OpenAI's terms; this
backend is strictly opt-in.
"""

from __future__ import annotations

import asyncio
from typing import Any

from openai import AsyncOpenAI

from ..oauth import openai as oauth
from .base import LLMResponse
from .openai_responses import OpenAIResponsesProvider


class OpenAIOAuthProvider(OpenAIResponsesProvider):
    """Responses provider backed by a ChatGPT subscription OAuth token."""

    def __init__(
        self,
        model: str = "gpt-5",
        *,
        max_retries: int = 3,
        timeout: float = 300.0,
        reasoning_effort: str | None = "high",
        reasoning_summary: str | None = "auto",
        text_verbosity: str | None = "medium",
        parallel_tool_calls: bool | None = True,
        **_ignored: Any,
    ) -> None:
        tokens = oauth.get_valid_tokens()
        self._max_retries = max_retries
        self._access_token = tokens.access_token
        self._account_id = tokens.account_id
        super().__init__(
            model=model,
            api_key=tokens.access_token,
            base_url=oauth.CHATGPT_RESPONSES_BASE_URL,
            max_retries=max_retries,
            timeout=timeout,
            reasoning_effort=reasoning_effort,
            reasoning_summary=reasoning_summary,
            text_verbosity=text_verbosity,
            parallel_tool_calls=parallel_tool_calls,
        )
        # Replace the vanilla client built by the base class with one carrying
        # the ChatGPT backend's required routing headers.
        self._rebuild_client(tokens.access_token)

    def _rebuild_client(self, access_token: str) -> None:
        self._client = AsyncOpenAI(
            api_key=access_token,
            base_url=oauth.CHATGPT_RESPONSES_BASE_URL,
            max_retries=self._max_retries,
            timeout=self.timeout,
            default_headers={
                "chatgpt-account-id": self._account_id,
                "originator": "codex_cli_rs",
                "OpenAI-Beta": "responses=experimental",
            },
        )

    async def _ensure_fresh(self) -> None:
        """Refresh the token if it is near expiry, rebuilding the client once."""
        tokens = await asyncio.to_thread(oauth.get_valid_tokens)
        if tokens.access_token != self._access_token:
            self._access_token = tokens.access_token
            self._account_id = tokens.account_id
            self._rebuild_client(tokens.access_token)

    async def create(
        self,
        *,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int = 16384,
    ) -> LLMResponse:
        await self._ensure_fresh()
        return await super().create(
            system=system,
            messages=messages,
            tools=tools,
            max_tokens=max_tokens,
        )
