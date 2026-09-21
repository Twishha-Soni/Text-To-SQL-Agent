from app.agent.sub_agent_1.state import SubGraphAgentState


def clarify(state: SubGraphAgentState) -> dict:
    print("[CLARIFY]")
    return {"final_answer": "I can't answer this question with the current database schema and business rules."}