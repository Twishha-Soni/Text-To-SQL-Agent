from langgraph.graph import MessagesState

class AgentState(MessagesState):
    question: str | None
    sql_query: str | None
    final_answer: str | None
    retry_count: int | None
    can_answer: bool | None