from app.agent.state import AgentState
from app.service.Rewrite import give_question


def head(state: AgentState):
    print("HEAD")
    result = give_question(state['messages'])
    return {"question": result.standalone_question}