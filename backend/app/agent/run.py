import time

from agent.graph import build_graph

graph = build_graph()

TEST_QUESTIONS = [
    "What is our on-time delivery rate?",                      # happy path
    "How many unique customers do we have?",                    # tests customer_unique_id rule
    "What is the total revenue excluding freight?",              # tests revenue rule
    "What is our seller performance rating?",                    # should hit CLARIFY
    "Which customers paid in more than 3 installments?",         # tests order_payments join
]

def fresh_state(question: str) -> dict:
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

for i, q in enumerate(TEST_QUESTIONS, start=1):
    print(f"\n{'='*60}\nQ{i}: {q}\n{'='*60}")
    time.sleep(30)
    result = graph.invoke(fresh_state(q))
    print(f"SQL: {result['sql_query']}")
    print(f"RETRIES: {result['retry_count']}")
    print(f"ANSWER: {result['final_answer']}")