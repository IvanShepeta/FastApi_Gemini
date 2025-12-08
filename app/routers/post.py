from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from app import database
from app.gemini_client import get_answer_from_gemini
from app.models import User, ChatRequest
from app.oauth2 import get_current_user
from app.schemas import ChatCreate, ChatResponse

router = APIRouter(
    prefix="/chat",
    tags=['Chat 📖 '],
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ChatResponse)
def create_prompt(
        request: ChatCreate,
        db: Session = Depends(database.get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Send a prompt to Gemini AI and save the conversation
    """
    try:
        response = get_answer_from_gemini(request.prompt)

        new_chat = ChatRequest(
            prompt=request.prompt,
            response=response,
            user_id=current_user.id,
        )
        db.add(new_chat)
        db.commit()
        db.refresh(new_chat)

        return new_chat

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating response: {str(e)}"
        )

@router.get("/history", status_code=status.HTTP_200_OK, response_model=List[ChatResponse])
def get_request(
        skip: int = 0,
        limit: int = 50,
        db: Session = Depends(database.get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Get chat history for the current authenticated user
    """
    chats = (db.query(ChatRequest)
             .filter(ChatRequest.user_id == current_user.id)
             .order_by(ChatRequest.created_at.desc())
             .offset(skip)
             .limit(limit)
             .all())

    return chats