from app.agent.sub_agent_1.state import SubGraphAgentState
from app.service.sub_agent_1.validate import validate_sql


def validate(state: SubGraphAgentState) -> dict:
    print("[VALIDATE]")

    is_valid, validation_error = validate_sql(state['sql_query'])

    return {"is_valid": is_valid, "validation_error": validation_error}