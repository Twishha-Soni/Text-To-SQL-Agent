from langgraph.graph import MessagesState

class AgentState(MessagesState):
    question: str
    schema_context: list[str]
    rules_context: list[str]
    sql_query: str
    is_valid: bool
    validation_error: str | None
    query_result: list | None
    retry_count: int
    final_answer: str | None