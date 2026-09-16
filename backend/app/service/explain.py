import json
import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

_llm = ChatGoogleGenerativeAI(
    model=os.getenv('GEMINI_MODEL'),
    google_api_key=os.getenv('GEMINI_API_KEY')
)

_prompt = ChatPromptTemplate.from_messages([
    ('system', """
You answer a user's question in plain English using ONLY
the query results provided. Do not invent numbers, percentages, or trends not directly supported by the data shown. Be concise — 2-3 sentences.
"""),
    ('human', "{result_block}")
])

_chain = _prompt | _llm | StrOutputParser()

def explain_result(question: str, query_result: list[dict]) -> str:
    result_block = f"""QUESTION: {question}

QUERY RESULT (JSON):
{json.dumps(query_result, default=str)}

Answer the question in plain English based on this result."""
    
    return  _chain.invoke({'result_block': result_block})