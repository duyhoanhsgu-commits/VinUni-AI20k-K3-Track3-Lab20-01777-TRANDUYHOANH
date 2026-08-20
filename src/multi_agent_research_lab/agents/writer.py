from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = AgentName.WRITER

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""
        sources_summary = "\n".join(
            [f"- [{i + 1}] {s.title} ({s.url or 'No URL'})" for i, s in enumerate(state.sources)]
        )
        prompt = (
            f"Synthesize a final report for query '{state.request.query}'.\n\n"
            f"Research Notes:\n{state.research_notes or 'None'}\n\n"
            f"Analysis Notes:\n{state.analysis_notes or 'None'}\n\n"
            f"Sources:\n{sources_summary}\n\n"
            "Format a clean, structured summary with explicit citations."
        )
        response = self.llm_client.complete(
            system_prompt="You are a professional technical writer.",
            user_prompt=prompt,
        )
        final_text = response.content
        state.final_answer = final_text
        state.agent_results.append(
            AgentResult(
                agent=AgentName.WRITER,
                content=final_text,
                metadata={
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                },
            )
        )
        state.add_trace_event("writer_completed", {"latency": response.latency_seconds})
        return state
