from app.agent.state import AgentState
from app.service.validate import validate_sql


def validate(state: AgentState) -> dict:
    print("[VALIDATE]")

    is_valid, validation_error = validate_sql(state['sql_query'])

    return {"is_valid": is_valid, "validation_error": validation_error}