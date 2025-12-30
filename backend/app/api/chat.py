"""
Chat API endpoints for multi-turn conversations
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.services.chat_service import ChatService
from app.services.context_manager import ContextManager
from app.core.config import settings

router = APIRouter()
chat_service = ChatService()
context_manager = ContextManager()


class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    messages: List[Message]
    conversation_id: Optional[str] = None
    language: Optional[str] = None  # Programming language context
    stream: bool = False


class ChatResponse(BaseModel):
    message: Message
    conversation_id: str
    usage: Optional[Dict[str, Any]] = None


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handle chat requests with multi-turn conversation support
    """
    try:
        # Get or create conversation ID
        conversation_id = request.conversation_id or context_manager.create_conversation_id()
        
        # Manage context - summarize if needed
        processed_messages = await context_manager.process_messages(
            messages=request.messages,
            conversation_id=conversation_id,
            language=request.language
        )
        
        # Generate response using Claude
        response = await chat_service.generate_response(
            messages=processed_messages,
            language=request.language,
            stream=request.stream
        )
        
        # Store conversation state
        await context_manager.store_message(
            conversation_id=conversation_id,
            message=request.messages[-1].dict() if hasattr(request.messages[-1], 'dict') else request.messages[-1],
            response=response
        )
        
        return ChatResponse(
            message=Message(
                role="assistant",
                content=response["content"],
                timestamp=datetime.now()
            ),
            conversation_id=conversation_id,
            usage=response.get("usage")
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history"""
    messages = await context_manager.get_conversation(conversation_id)
    return {"conversation_id": conversation_id, "messages": messages}


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    await context_manager.delete_conversation(conversation_id)
    return {"status": "deleted", "conversation_id": conversation_id}

