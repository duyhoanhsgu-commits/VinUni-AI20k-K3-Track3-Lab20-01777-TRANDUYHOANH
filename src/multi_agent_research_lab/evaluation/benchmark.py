from collections.abc import Callable
from time import perf_counter

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState

Runner = Callable[[str], ResearchState]


def compute_citation_coverage(state: ResearchState) -> float:
    """Calculate the ratio of claims/sections backed by citations."""
    if not state.final_answer or not state.sources:
        return 0.0
    cited = 0
    total_sources = len(state.sources)
    for idx in range(1, total_sources + 1):
        if f"[{idx}]" in state.final_answer or (
            state.sources[idx - 1].url and state.sources[idx - 1].url in state.final_answer
        ):
            cited += 1
    return round(cited / total_sources, 2)


def compute_estimated_cost(state: ResearchState) -> float:
    """Sum estimated cost across all agent LLM calls."""
    total_cost = 0.0
    for res in state.agent_results:
        in_t = res.metadata.get("input_tokens", 0) or 0
        out_t = res.metadata.get("output_tokens", 0) or 0
        total_cost += (in_t * 0.15 + out_t * 0.60) / 1_000_000
    return round(total_cost, 6)


def run_benchmark(
    run_name: str, query: str, runner: Runner
) -> tuple[ResearchState, BenchmarkMetrics]:
    """Execute runner and compute full metrics."""
    started = perf_counter()
    failure_rate = 0.0
    try:
        state = runner(query)
    except Exception as exc:
        latency = perf_counter() - started
        metrics = BenchmarkMetrics(
            run_name=run_name,
            latency_seconds=round(latency, 2),
            failure_rate=1.0,
            notes=f"Failed with exception: {exc}",
        )
        raise

    latency = perf_counter() - started
    cost = compute_estimated_cost(state)
    citation_cov = compute_citation_coverage(state)

    # Basic heuristic quality score (0 - 10)
    has_answer = 1.0 if state.final_answer else 0.0
    has_notes = 1.0 if state.analysis_notes else 0.0
    answer_length_bonus = (
        min(len(state.final_answer or "") / 500, 1.0) if state.final_answer else 0.0
    )
    quality = round(
        (has_answer * 5.0) + (has_notes * 2.5) + (citation_cov * 1.5) + (answer_length_bonus * 1.0),
        1,
    )

    notes = f"Processed in {state.iteration} iterations across {len(state.route_history)} hops."

    metrics = BenchmarkMetrics(
        run_name=run_name,
        latency_seconds=round(latency, 2),
        estimated_cost_usd=cost,
        quality_score=quality,
        citation_coverage=citation_cov,
        failure_rate=failure_rate,
        notes=notes,
    )
    return state, metrics
