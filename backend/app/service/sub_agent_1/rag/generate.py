from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv
import os

from app.agent.sub_agent_1.schemas import SQLGenerationResponse

load_dotenv()

_llm = ChatGoogleGenerativeAI(
    model=os.getenv('GEMINI_MODEL'),
    google_api_key=os.getenv('GEMINI_API_KEY')
).with_structured_output(SQLGenerationResponse)

_prompt = ChatPromptTemplate.from_messages([
    ('system', """
You are a SQL generation assistant for a PostgreSQL database.
Generate a single, read-only SELECT query that answers the user's question.

Rules:
- Only use tables/columns described in the schema context below.
- Apply the business rules exactly as stated — they encode judgment calls that are not obvious from the schema alone.
- Never use DROP, DELETE, UPDATE, INSERT, ALTER, or TRUNCATE.
- If the question CANNOT be answered using only the given schema and rules (e.g. it needs a table or column that doesn't exist), set can_answer to false and leave sql_query as an empty string. Do NOT write a workaround query that returns a text message instead of real data.
- Respond ONLY with a JSON object matching this shape:
  "can_answewr": "...", sql_query": "...", "reasoning": "..."
"""),
    ('human', "{result_block}")
])

_chain = _prompt | _llm

def _build_result_block(question: str, schema_context: list[str], rules_context: list[str], correction_context: dict | None = None) -> str:
    result_block = ""

    schema_context = "\n".join(f"- {doc}" for doc in schema_context)
    rules_context = "\n".join(f"- {doc}" for doc in rules_context)

    result_block += f"""
SCHEMA_CONTEXT:
{schema_context}

BUSINESS RULES:
{rules_context}

QUESTION: {question}
"""

    if correction_context:
        result_block += f"""
PREVIOUS ATTEMPT FAILED:
SQL: {correction_context['sql_query']}
ERROR: {correction_context['error']}

Fix the query. Do not repeat the same mistake.
"""

    return result_block

def generate_sql(question: str, schema_context: list[str], rules_context: list[str], correction_context: dict | None = None) -> SQLGenerationResponse:
    result_block = _build_result_block(question, schema_context, rules_context, correction_context)

    return _chain.invoke({
        'result_block': result_block
    })