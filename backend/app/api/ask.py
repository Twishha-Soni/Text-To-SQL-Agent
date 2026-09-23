from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, messages_to_dict, messages_from_dict

from app.auth.dependecies import get_current_user
from app.agent.graph import agent
from app.database.models import Chats_Agent, Users_Agent
from app.database.session import get_db
from app.api.rate_limit.dependencies import rate_limit

router = APIRouter(prefix= "/ask", tags=['ask agent'])

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    question: str
    sql_query: str = None
    final_answer: str
    retry_count: int
    can_answer: bool

def fresh_state(messages: str) -> dict:
    return {
        "messages": messages,
    }

@router.post("/new_chat", response_model=AnswerResponse)
def ask_agent_new_chat(
    payload: QuestionRequest,
    current_user: Users_Agent = Depends(rate_limit),
    db: Session = Depends(get_db),
):

    content = [HumanMessage(content=f"{payload.question}", name="Human"),]

    try:
        result = agent.invoke(fresh_state(content))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    content = result['messages']

    new_chat = Chats_Agent(
        user_id=current_user.id,
        name=payload.question[:49],
        content=messages_to_dict(content),
        last_updated_at = datetime.now()
    )

    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)

    return AnswerResponse(
        question=payload.question,
        sql_query=result['sql_query'],
        final_answer=result['final_answer'],
        retry_count=result['retry_count'],
        can_answer=result['can_answer']
    )



@router.post("/{thread_id}", response_model=AnswerResponse)
def ask_agent(
    thread_id: int,
    payload: QuestionRequest,
    current_user: Users_Agent = Depends(rate_limit),
    db: Session = Depends(get_db),
):
    chat = db.query(Chats_Agent).filter(
        thread_id == Chats_Agent.id,
        Chats_Agent.user_id == current_user.id
    ).first()

    if chat:
        content = messages_from_dict(chat.content)
        content.append(HumanMessage(content=f"{payload.question}", name="Human"))
    else:
        return HTTPException(
            status_code=404,
            detail="Chat not found."
        )

    try:
        result = agent.invoke(fresh_state(content))
        print("done")
    except Exception as e:
        print("done2")
        raise HTTPException(status_code=500, detail=str(e))

    content = messages_to_dict(result['messages'])
    chat.content = content
    chat.last_updated_at = datetime.now()

    db.commit()

    return AnswerResponse(
        question=payload.question,
        sql_query=result['sql_query'],
        final_answer=result['final_answer'],
        retry_count=result['retry_count'],
        can_answer=result['can_answer']
    )