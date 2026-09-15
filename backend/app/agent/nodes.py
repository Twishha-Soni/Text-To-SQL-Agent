from agent.state import AgentState
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
        return {"sql_query": result.sql_query}
    
    return {'sql_query': ""}

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
    print("[CORRECT]")
    return {"retry_count": state["retry_count"] + 1}

def clarify(state: AgentState) -> dict:
    print("[CLARIFY]")
    return {"final_answer": "I couldn't generate a valid query after several attempts."}

def explain(state: AgentState) -> dict:
    print("[EXPLAIN]")
    return {"final_answer": "Stub explanation of results."}