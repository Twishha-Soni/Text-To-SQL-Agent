from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.auth.dependecies import get_current_user
from app.agent.graph import build_graph
from app.db.models import Users_Texttosql_App
from app.db.session import get_db

router = APIRouter(tags=['ask agent'])
graph = build_graph()

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    question: str
    sql_query: str
    final_answer: str
    retry_count: int
    can_answer: bool

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

@router.post("/ask", response_model=AnswerResponse)
def ask_agent(
    payload: QuestionRequest,
    # current_user: Users_Texttosql_App = Depends(get_current_user),
    # db: Session = Depends(get_db)
):
    try:
        result = graph.invoke(fresh_state(payload.question))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return AnswerResponse(
        question=result['question'],
        sql_query=result['sql_query'],
        final_answer=result['final_answer'],
        retry_count=result['retry_count'],
        can_answer=result['can_answer']
    )