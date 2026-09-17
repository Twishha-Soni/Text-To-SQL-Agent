from app.agent.state import AgentState
from app.service.rag.generate import generate_sql


def generate(state: AgentState) -> dict:
    print("[GENERATE]")
    result = generate_sql(state['question'], state['schema_context'], state['rules_context'])
    if result:
        return {"sql_query": result.sql_query, 'can_answer': result.can_answer}
    
    return {'sql_query': "", 'can_answer': result.can_answer}