from app.agent.sub_agent_1.state import SubGraphAgentState
from app.service.sub_agent_1.execute import execute_sql


def execute(state: SubGraphAgentState) -> dict:
    print("[EXECUTE]")

    result, error = execute_sql(state['sql_query'])

    if error:
        return {'query_result': None, 'validaton_error': error}

    return {"query_result": result, 'validation_error': None}