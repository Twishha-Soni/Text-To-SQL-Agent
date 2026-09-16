from pydantic import BaseModel, Field


class SQLGenerationResponse(BaseModel):
    can_answer: bool = Field(description='False if the question cannot be answered using only the given schema and rules')
    sql_query: str | None = Field(description='The generated read-only SQL query, no markdown formatting')
    reasoning: str | None = Field(description='Brief explanation of what the query does and why')