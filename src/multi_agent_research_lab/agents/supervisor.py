from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import AgentName
from multi_agent_research_lab.core.state import ResearchState


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = AgentName.SUPERVISOR

    def __init__(self) -> None:
        self.settings = get_settings()

    def run(self, state: ResearchState) -> ResearchState:
        """Update `state.route_history` with the next route decision."""
        if state.iteration >= self.settings.max_iterations:
            next_route = "done"
        elif not state.research_notes or not state.sources:
            next_route = AgentName.RESEARCHER
        elif not state.analysis_notes:
            next_route = AgentName.ANALYST
        elif not state.final_answer:
            next_route = AgentName.WRITER
        else:
            next_route = "done"

        state.record_route(next_route)
        state.add_trace_event(
            "supervisor_routed", {"next_route": next_route, "iteration": state.iteration}
        )
        return state
