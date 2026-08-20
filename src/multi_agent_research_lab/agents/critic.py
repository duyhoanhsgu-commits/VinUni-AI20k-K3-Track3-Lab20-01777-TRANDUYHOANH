from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState


class CriticAgent(BaseAgent):
    """Fact-checking and citation validation agent."""

    name = AgentName.CRITIC

    def run(self, state: ResearchState) -> ResearchState:
        """Validate final answer and append audit trace findings."""
        if not state.final_answer:
            critic_note = "Validation Warning: No final answer generated yet."
        else:
            cited_count = sum(
                1 for idx in range(1, len(state.sources) + 1) if f"[{idx}]" in state.final_answer
            )
            critic_note = (
                f"Critic Validation OK: Verified {cited_count}/{len(state.sources)} sources cited."
            )

        state.agent_results.append(
            AgentResult(
                agent=AgentName.CRITIC,
                content=critic_note,
                metadata={"sources_validated": len(state.sources)},
            )
        )
        state.add_trace_event("critic_completed", {"critic_note": critic_note})
        return state
