from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.search_client import SearchClient


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = AgentName.RESEARCHER

    def __init__(self, search_client: SearchClient | None = None) -> None:
        self.search_client = search_client or SearchClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`."""
        sources = self.search_client.search(
            query=state.request.query, max_results=state.request.max_sources
        )
        state.sources.extend(sources)

        notes_lines = [f"Research Notes for '{state.request.query}':"]
        for idx, doc in enumerate(sources, 1):
            notes_lines.append(f"[{idx}] {doc.title}: {doc.snippet}")

        notes = "\n".join(notes_lines)
        state.research_notes = notes
        state.agent_results.append(
            AgentResult(
                agent=AgentName.RESEARCHER,
                content=notes,
                metadata={"source_count": len(sources)},
            )
        )
        state.add_trace_event("researcher_completed", {"source_count": len(sources)})
        return state
