from agent.state import AgentState
from rag.generate import generate_sql
from rag.retrieve import retrieve_context

MAX_RETRIES = 3

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
    # stub: force failure once so we can prove the retry loop works
    is_valid = state["retry_count"] >= 1
    return {"is_valid": is_valid, "validation_error": None if is_valid else "stub failure"}

def execute(state: AgentState) -> dict:
    print("[EXECUTE]")
    return {"query_result": [{"stub": "row"}]}

def correct(state: AgentState) -> dict:
    print("[CORRECT]")
    return {"retry_count": state["retry_count"] + 1}

def clarify(state: AgentState) -> dict:
    print("[CLARIFY]")
    return {"final_answer": "I couldn't generate a valid query after several attempts."}

def explain(state: AgentState) -> dict:
    print("[EXPLAIN]")
    return {"final_answer": "Stub explanation of results."}