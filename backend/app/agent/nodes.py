from agent.state import AgentState
from service.explain import explain_result
from service.execute import execute_sql
from service.validate import validate_sql
from service.rag.generate import generate_sql
from service.rag.retrieve import retrieve_context

def retrieve(state: AgentState) -> dict:
    print("[RETRIEVE]")
    return retrieve_context(state['question'])

def generate(state: AgentState) -> dict:
    print("[GENERATE]")
    result = generate_sql(state['question'], state['schema_context'], state['rules_context'])
    if result:
        return {"sql_query": result.sql_query, 'can_answer': result.can_answer}
    
    return {'sql_query': "", 'can_answer': result.can_answer}

def validate(state: AgentState) -> dict:
    print("[VALIDATE]")

    is_valid, validation_error = validate_sql(state['sql_query'])

    return {"is_valid": is_valid, "validation_error": validation_error}

def execute(state: AgentState) -> dict:
    print("[EXECUTE]")

    result, error = execute_sql(state['sql_query'])

    if error:
        return {'query_result': None, 'validaton_error': error}

    return {"query_result": result, 'validation_error': None}

def correct(state: AgentState) -> dict:
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

def clarify(state: AgentState) -> dict:
    print("[CLARIFY]")
    return {"final_answer": "I can't answer this question with the current database schema and business rules."}

def explain(state: AgentState) -> dict:
    print("[EXPLAIN]")
    
    answer = explain_result(state['question'], state['query_result'])

    return {"final_answer": answer}