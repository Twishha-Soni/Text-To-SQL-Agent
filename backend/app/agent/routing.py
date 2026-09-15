from agent.state import AgentState
from agent.nodes import MAX_RETRIES


def route_after_validate(state: AgentState) -> str:
    return 'execute' if state['is_valid'] else 'correct'

def route_after_execute(state: AgentState) -> str:
    return 'explain'

def route_after_correct(state: AgentState) -> str:
    return 'clarify' if state['retry_count'] >= MAX_RETRIES else 'validate'