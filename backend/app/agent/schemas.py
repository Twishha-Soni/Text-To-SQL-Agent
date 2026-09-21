from pydantic import BaseModel


class QuestionResponse(BaseModel):
    standalone_question: str