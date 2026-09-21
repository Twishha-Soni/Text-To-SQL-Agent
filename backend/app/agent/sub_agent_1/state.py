from langgraph.graph import MessagesState

class SubGraphAgentState(MessagesState):
    question: str
    schema_context: list[str] | None
    rules_context: list[str] | None
    can_answer: bool
    sql_query: str
    is_valid: bool
    validation_error: str | None
    query_result: list | None
    retry_count: int
    final_answer: str | None