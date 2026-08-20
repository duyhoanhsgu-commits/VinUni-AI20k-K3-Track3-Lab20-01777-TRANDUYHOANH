from multi_agent_research_lab.agents.analyst import AnalystAgent
from multi_agent_research_lab.agents.researcher import ResearcherAgent
from multi_agent_research_lab.agents.supervisor import SupervisorAgent
from multi_agent_research_lab.agents.writer import WriterAgent
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import AgentName
from multi_agent_research_lab.core.state import ResearchState


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph orchestration."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.supervisor = SupervisorAgent()
        self.researcher = ResearcherAgent()
        self.analyst = AnalystAgent()
        self.writer = WriterAgent()

    def build(self) -> object:
        """Create a LangGraph graph representation."""
        try:
            from langgraph.graph import END, StateGraph

            builder = StateGraph(ResearchState)

            builder.add_node("supervisor", self.supervisor.run)
            builder.add_node("researcher", self.researcher.run)
            builder.add_node("analyst", self.analyst.run)
            builder.add_node("writer", self.writer.run)

            builder.set_entry_point("supervisor")

            def route_decision(state: ResearchState) -> str:
                if not state.route_history:
                    return "supervisor"
                last_route = state.route_history[-1]
                if last_route == "done":
                    return END
                return last_route

            builder.add_conditional_edges(
                "supervisor",
                route_decision,
                {
                    "researcher": "researcher",
                    "analyst": "analyst",
                    "writer": "writer",
                    END: END,
                },
            )

            builder.add_edge("researcher", "supervisor")
            builder.add_edge("analyst", "supervisor")
            builder.add_edge("writer", "supervisor")

            return builder.compile()
        except Exception:
            return self

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the multi-agent workflow graph and return final state."""
        max_iters = self.settings.max_iterations

        while state.iteration < max_iters:
            state = self.supervisor.run(state)
            last_route = state.route_history[-1]

            if last_route == "done":
                break

            if last_route == AgentName.RESEARCHER:
                state = self.researcher.run(state)
            elif last_route == AgentName.ANALYST:
                state = self.analyst.run(state)
            elif last_route == AgentName.WRITER:
                state = self.writer.run(state)
            else:
                break

        return state
