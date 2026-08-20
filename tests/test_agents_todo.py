from multi_agent_research_lab.agents import SupervisorAgent
from multi_agent_research_lab.core.schemas import AgentName, ResearchQuery
from multi_agent_research_lab.core.state import ResearchState


def test_supervisor_routing_policy() -> None:
    state = ResearchState(request=ResearchQuery(query="Explain multi-agent systems"))

    # 1. First iteration -> route to researcher
    state = SupervisorAgent().run(state)
    assert state.route_history[-1] == AgentName.RESEARCHER

    # 2. After research notes -> route to analyst
    state.research_notes = "Some notes"
    state.sources = [{"title": "t", "snippet": "s"}]
    state = SupervisorAgent().run(state)
    assert state.route_history[-1] == AgentName.ANALYST

    # 3. After analysis notes -> route to writer
    state.analysis_notes = "Some analysis"
    state = SupervisorAgent().run(state)
    assert state.route_history[-1] == AgentName.WRITER

    # 4. After final answer -> route to done
    state.final_answer = "Final answer"
    state = SupervisorAgent().run(state)
    assert state.route_history[-1] == "done"
