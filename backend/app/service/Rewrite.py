from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv
import os
from typing import Any

from app.agent.schemas import QuestionResponse

load_dotenv()

_llm = ChatGoogleGenerativeAI(
    model=os.getenv('GEMINI_MODEL'),
    google_api_key=os.getenv('GEMINI_API_KEY')
).with_structured_output(QuestionResponse)

context = [SystemMessage(content="""
You rewrite a user's latest message into a standalone question, using the prior conversation only for context that's needed to understand it (e.g. resolving "that", "last month", "those customers").

Rules:
- If the latest message is already standalone, return it unchanged.
- Do not answer the question. Only rewrite it.
- Do not add information the user didn't ask for.
- Respond ONLY with JSON: "standalone_question": "..."
""", name="System Prompt")]


def give_question(messages: Any) -> QuestionResponse:
    messages = context + messages

    return _llm.invoke(messages)