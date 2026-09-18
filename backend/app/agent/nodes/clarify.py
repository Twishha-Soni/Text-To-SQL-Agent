from app.agent.state import AgentState


def clarify(state: AgentState) -> dict:
    print("[CLARIFY]")
    return {"final_answer": "I can't answer this question with the current database schema and business rules."}