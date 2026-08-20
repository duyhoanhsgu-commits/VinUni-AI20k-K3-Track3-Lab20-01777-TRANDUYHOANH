"""Command-line entrypoint for the lab starter."""

from typing import Annotated

import typer
from pydantic import ValidationError
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.evaluation.benchmark import run_benchmark
from multi_agent_research_lab.evaluation.report import render_markdown_report
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging
from multi_agent_research_lab.observability.tracing import init_tracing
from multi_agent_research_lab.services.llm_client import LLMClient

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()


def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    init_tracing()


def _parse_query(query: str) -> ResearchQuery:
    try:
        return ResearchQuery(query=query)
    except ValidationError as exc:
        console.print(
            Panel.fit(
                f"Invalid query: {exc.errors()[0]['msg']}",
                title="Input Error",
                style="red",
            )
        )
        raise typer.Exit(code=1) from exc


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a real single-agent baseline implementation."""

    _init()
    request = _parse_query(query)
    state = ResearchState(request=request)

    client = LLMClient()
    response = client.complete(
        system_prompt="You are a single-agent research assistant.",
        user_prompt=request.query,
    )

    state.final_answer = response.content
    state.add_trace_event(
        "baseline_completion",
        {
            "latency_seconds": response.latency_seconds,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "cost_usd": response.cost_usd,
        },
    )

    console.print(Panel.fit(state.final_answer, title="Single-Agent Baseline Result"))
    console.print(
        f"[bold green]Metrics:[/bold green] Latency: [bold]{response.latency_seconds}s[/bold] | "
        f"Tokens (In/Out): [bold]{response.input_tokens}/{response.output_tokens}[/bold] | "
        f"Cost: [bold]${response.cost_usd:.6f}[/bold]"
    )


@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow."""

    _init()
    state = ResearchState(request=_parse_query(query))
    workflow = MultiAgentWorkflow()
    try:
        result = workflow.run(state)
    except StudentTodoError as exc:
        console.print(Panel.fit(str(exc), title="Expected TODO", style="yellow"))
        raise typer.Exit(code=2) from exc
    console.print(result.model_dump_json(indent=2))


@app.command("benchmark")
def benchmark(
    query: Annotated[
        str, typer.Option("--query", "-q", help="Research query")
    ] = "Research GraphRAG state-of-the-art",
    output: Annotated[
        str, typer.Option("--output", "-o", help="Output report path")
    ] = "reports/benchmark_report.md",
) -> None:
    """Run benchmark comparing single-agent baseline vs multi-agent workflow."""
    _init()

    def baseline_runner(q: str) -> ResearchState:
        req = _parse_query(q)
        st = ResearchState(request=req)
        client = LLMClient()
        resp = client.complete(
            system_prompt="You are a helpful single-agent research assistant.",
            user_prompt=req.query,
        )
        st.final_answer = resp.content
        return st

    def multi_agent_runner(q: str) -> ResearchState:
        req = _parse_query(q)
        st = ResearchState(request=req)
        return MultiAgentWorkflow().run(st)

    console.print("[bold cyan]Running Single-Agent Baseline Benchmark...[/bold cyan]")
    _, baseline_metrics = run_benchmark("Single-Agent Baseline", query, baseline_runner)

    console.print("[bold cyan]Running Multi-Agent Workflow Benchmark...[/bold cyan]")
    _, multi_metrics = run_benchmark("Multi-Agent Workflow", query, multi_agent_runner)

    report_md = render_markdown_report([baseline_metrics, multi_metrics])

    with open(output, "w", encoding="utf-8") as f:
        f.write(report_md)

    console.print(Panel.fit(report_md, title=f"Benchmark Report Saved to {output}"))


if __name__ == "__main__":
    app()
