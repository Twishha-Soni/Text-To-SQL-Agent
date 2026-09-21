from app.agent.sub_agent_1.state import SubGraphAgentState
from app.service.sub_agent_1.rag.generate import generate_sql


def correct(state: SubGraphAgentState) -> dict:
    if state['retry_count'] + 1 > 3:
        return {'retry_count': state['retry_count'] + 1}
    
    if not state['can_answer']:
        return {}
    
    print(f"[CORRECT] retry {state['retry_count'] + 1}")

    correction_context = {
        'sql_query': state['sql_query'],
        'error': state['validation_error']
    }

    result = generate_sql(
        state['question'],
        state['schema_context'],
        state['rules_context'],
        correction_context=correction_context
    )

    new_message = {
        'role': 'assistant',
        'content': f"Attempt failed. SQL: {state['sql_query']} | Error: {state['validation_error']} | Fixed SQL: {result.sql_query}"
    }

    return {"retry_count": state["retry_count"] + 1,
            "sql_query": result.sql_query,
            "messages": [new_message]}