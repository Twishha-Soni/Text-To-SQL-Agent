from app.agent.state import AgentState
from app.service.rag.retrieve import retrieve_context


def retrieve(state: AgentState) -> dict:
    print("[RETRIEVE]")
    return retrieve_context(state['question'])