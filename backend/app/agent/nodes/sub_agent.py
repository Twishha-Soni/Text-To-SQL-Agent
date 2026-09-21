from app.agent.state import AgentState
from app.agent.sub_agent_1.graph import sub_agent

from langchain_core.messages import AIMessage


def sub_agent_node(state: AgentState):
    print("SUB_AGENT_NODE")
    result = sub_agent.invoke(_fresh_state(state['question']))
    final_answer = AIMessage(content=f"{result['final_answer']}", name="Model")
    return {
        "messages": final_answer,
        "can_answer": result['can_answer'],
        "sql_query": result['sql_query'],
        "retry_count": result['retry_count'],
        "final_answer": result['final_answer'],
    }

def _fresh_state(question: str):
    return {
            "question": question,
            "messages": [],
            "schema_context": [],
            "rules_context": [],
            "can_answer": True,
            "sql_query": "",
            "is_valid": False,
            "validation_error": None,
            "query_result": None,
            "retry_count": 0,
            "final_answer": None,
        }