from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = AgentName.ANALYST

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`."""
        research_notes = state.research_notes or "No research notes available."
        prompt = (
            f"Analyze the following research notes for query '{state.request.query}':\n"
            f"{research_notes}\n\n"
            "Identify key claims, evaluate evidence strength, and list main analytical takeaways."
        )
        response = self.llm_client.complete(
            system_prompt="You are an expert technical analyst evaluating research findings.",
            user_prompt=prompt,
        )
        analysis_content = response.content
        state.analysis_notes = analysis_content
        state.agent_results.append(
            AgentResult(
                agent=AgentName.ANALYST,
                content=analysis_content,
                metadata={
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                },
            )
        )
        state.add_trace_event("analyst_completed", {"latency": response.latency_seconds})
        return state
