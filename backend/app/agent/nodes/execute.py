from app.agent.state import AgentState
from app.service.execute import execute_sql


def execute(state: AgentState) -> dict:
    print("[EXECUTE]")

    result, error = execute_sql(state['sql_query'])

    if error:
        return {'query_result': None, 'validaton_error': error}

    return {"query_result": result, 'validation_error': None}