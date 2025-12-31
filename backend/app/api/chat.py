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


class MessagePart(BaseModel):
    type: str  # "text", "image", "file", etc.
    text: Optional[str] = None
    # Add other fields for images/files later if needed


class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: Optional[str] = None  # Legacy format
    parts: Optional[List[MessagePart]] = None  # Modern format
    timestamp: Optional[datetime] = None
    
    def get_content(self) -> str:
        """Extract text content from either format"""
        if self.content:
            return self.content
        if self.parts:
            # Extract text from parts
            text_parts = [part.text for part in self.parts if part.type == "text" and part.text]
            return "".join(text_parts)
        return ""


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
        
        # Convert messages to dict format with extracted content
        messages_dict = [
            {
                "role": msg.role,
                "content": msg.get_content()
            }
            for msg in request.messages
        ]
        
        # Manage context - summarize if needed
        processed_messages = await context_manager.process_messages(
            messages=messages_dict,
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
        last_message = {
            "role": request.messages[-1].role,
            "content": request.messages[-1].get_content()
        }
        await context_manager.store_message(
            conversation_id=conversation_id,
            message=last_message,
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

