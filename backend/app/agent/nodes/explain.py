from app.agent.state import AgentState
from app.service.explain import explain_result


def explain(state: AgentState) -> dict:
    print("[EXPLAIN]")
    
    answer = explain_result(state['question'], state['query_result'])

    return {"final_answer": answer}