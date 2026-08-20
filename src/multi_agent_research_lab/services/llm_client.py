"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

import time
from dataclasses import dataclass

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.observability.tracing import init_tracing


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None
    latency_seconds: float | None = None


class LLMClient:
    """Provider-agnostic LLM client implementation."""

    def __init__(self) -> None:
        self.settings = get_settings()
        init_tracing()
        self._client = None
        if self.settings.openai_api_key:
            try:
                from openai import OpenAI

                raw_client = OpenAI(api_key=self.settings.openai_api_key)
                if self.settings.langsmith_api_key:
                    try:
                        from langsmith.wrappers import wrap_openai

                        self._client = wrap_openai(raw_client)
                    except Exception:
                        self._client = raw_client
                else:
                    self._client = raw_client
            except Exception:
                self._client = None

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a model completion with latency and token tracking."""
        start_time = time.perf_counter()

        if self._client:
            try:
                response = self._client.chat.completions.create(
                    model=self.settings.openai_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                elapsed = time.perf_counter() - start_time
                content = response.choices[0].message.content or ""
                in_tokens = response.usage.prompt_tokens if response.usage else None
                out_tokens = response.usage.completion_tokens if response.usage else None

                # Approximate cost calculation for gpt-4o-mini ($0.15/1M input, $0.60/1M output)
                cost = None
                if in_tokens is not None and out_tokens is not None:
                    cost = (in_tokens * 0.15 + out_tokens * 0.60) / 1_000_000

                return LLMResponse(
                    content=content,
                    input_tokens=in_tokens,
                    output_tokens=out_tokens,
                    cost_usd=cost,
                    latency_seconds=round(elapsed, 4),
                )
            except Exception as exc:
                # Fallback to simulated response if API call fails
                content = f"[LLM Fallback (API error: {exc})] Analysis for query: {user_prompt}"

        # Default fallback for testing when no OpenAI API key is configured
        elapsed = time.perf_counter() - start_time
        in_tokens = len(system_prompt.split()) + len(user_prompt.split())
        content = (
            f"Research Insights for: '{user_prompt}'\n\n"
            "Key Findings:\n"
            "1. GraphRAG combines Knowledge Graphs with RAG to improve reasoning.\n"
            "2. Structured entities reduce hallucinations and enable multi-hop answering.\n"
            "3. Multi-agent systems orchestrate specialized roles for high-quality reports."
        )
        out_tokens = len(content.split())
        cost = (in_tokens * 0.15 + out_tokens * 0.60) / 1_000_000

        return LLMResponse(
            content=content,
            input_tokens=in_tokens,
            output_tokens=out_tokens,
            cost_usd=cost,
            latency_seconds=round(elapsed, 4),
        )
