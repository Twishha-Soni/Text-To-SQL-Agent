import os
from dotenv import load_dotenv

from agent.state import AgentState

load_dotenv()

MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))

def route_after_validate(state: AgentState) -> str:
    return 'execute' if state['is_valid'] else 'correct'

def route_after_execute(state: AgentState) -> str:
    return 'correct' if state['query_result'] is None else 'explain'

def route_after_correct(state: AgentState) -> str:
    return 'clarify' if state['retry_count'] >= MAX_RETRIES else 'validate'