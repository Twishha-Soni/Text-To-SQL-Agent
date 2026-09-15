from pydantic import BaseModel, Field


class SQLGenerationResponse(BaseModel):
    sql_query: str = Field(description='The generated read-only SQL query, no markdown formatting')
    reasoning: str = Field(description='Brief explanation of what the query does and why')