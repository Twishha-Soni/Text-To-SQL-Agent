from agent.graph import build_graph

graph = build_graph()

result = graph.invoke({
    'question': 'What is our on-time delivery rate?',
    'sql_query': '',
    'is_valid': False,
    'validation_error': None,
    'query_result': None,
    'retry_count': 0,
    'final_answer': None
})

print("\n Final State:", result)