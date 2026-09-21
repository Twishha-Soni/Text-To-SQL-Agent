from app.agent.sub_agent_1.state import SubGraphAgentState
from app.service.sub_agent_1.explain import explain_result


def explain(state: SubGraphAgentState) -> dict:
    print("[EXPLAIN]")
    
    answer = explain_result(state['question'], state['query_result'])

    return {"final_answer": answer}