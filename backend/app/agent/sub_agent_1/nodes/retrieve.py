from app.agent.sub_agent_1.state import SubGraphAgentState
from app.service.sub_agent_1.rag.retrieve import retrieve_context


def retrieve(state: SubGraphAgentState) -> dict:
    print("[RETRIEVE]")
    retrieved = retrieve_context(state['question'])
    return retrieved