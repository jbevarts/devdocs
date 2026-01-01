"""
Chat API endpoints for multi-turn conversations
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, AsyncGenerator
from datetime import datetime
import json
import asyncio

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


@router.post("/")
async def chat(request: ChatRequest):
    """
    Handle chat requests with multi-turn conversation support.
    Supports both streaming and non-streaming responses.
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
        
        # If streaming, return SSE stream
        if request.stream:
            return StreamingResponse(
                stream_chat_response(
                    processed_messages=processed_messages,
                    language=request.language,
                    conversation_id=conversation_id,
                    last_user_message=messages_dict[-1] if messages_dict else None
                ),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Conversation-Id": conversation_id,
                    "X-Accel-Buffering": "no",  # Disable nginx buffering if present
                }
            )
        
        # Non-streaming response
        response = await chat_service.generate_response(
            messages=processed_messages,
            language=request.language,
            stream=False
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


async def stream_chat_response(
    processed_messages: List[Dict[str, str]],
    language: Optional[str],
    conversation_id: str,
    last_user_message: Optional[Dict[str, str]]
) -> AsyncGenerator[str, None]:
    """
    Stream chat response as Server-Sent Events (SSE) in AI SDK v6 format.
    """
    message_id = f"msg_{int(datetime.now().timestamp() * 1000)}"
    full_content = ""
    
    try:
        # Send text-start event
        yield f"data: {json.dumps({'type': 'text-start', 'id': message_id})}\n\n"
        
        # Stream response from Claude - yield chunks immediately
        async for chunk in chat_service.stream_response(
            messages=processed_messages,
            language=language
        ):
            if chunk:
                full_content += chunk
                # Send text-delta event - yield immediately without buffering
                yield f"data: {json.dumps({'type': 'text-delta', 'id': message_id, 'delta': chunk})}\n\n"
        
        # Send text-end event
        yield f"data: {json.dumps({'type': 'text-end', 'id': message_id})}\n\n"
        
        # Store conversation state after streaming completes
        if last_user_message:
            await context_manager.store_message(
                conversation_id=conversation_id,
                message=last_user_message,
                response={"content": full_content}
            )
    
    except Exception as e:
        # Send error event
        error_msg = str(e)
        yield f"data: {json.dumps({'type': 'error', 'id': message_id, 'errorText': error_msg})}\n\n"


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

