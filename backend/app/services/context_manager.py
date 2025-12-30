"""
Context manager for handling conversation history and summarization
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import json

from app.core.config import settings
from anthropic import Anthropic


class ContextManager:
    """Manages conversation context and summarization"""
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        # In-memory storage (replace with Redis/DB in production)
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
        self.summaries: Dict[str, str] = {}
    
    def create_conversation_id(self) -> str:
        """Generate a new conversation ID"""
        return str(uuid.uuid4())
    
    async def process_messages(
        self,
        messages: List[Dict[str, Any]],
        conversation_id: str,
        language: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Process messages and manage context length
        
        If conversation is too long, summarize older messages
        """
        # Get existing conversation history
        history = self.conversations.get(conversation_id, [])
        
        # Combine history with new messages
        all_messages = history + [msg.dict() if hasattr(msg, 'dict') else msg for msg in messages]
        
        # Check if we need to summarize
        if len(all_messages) > settings.SUMMARIZATION_THRESHOLD:
            # Summarize older messages
            summary = await self._summarize_conversation(
                messages=all_messages[:-len(messages)],  # All except the new ones
                language=language
            )
            
            # Store summary
            self.summaries[conversation_id] = summary
            
            # Keep recent messages + summary
            recent_messages = all_messages[-settings.SUMMARIZATION_THRESHOLD:]
            
            # Format for API: summary as system context + recent messages
            processed = [
                {
                    "role": "system",
                    "content": f"Previous conversation summary: {summary}"
                }
            ]
            
            for msg in recent_messages:
                processed.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
            
            return processed
        
        # If within limits, return all messages
        return [
            {
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            }
            for msg in all_messages
        ]
    
    async def _summarize_conversation(
        self,
        messages: List[Dict[str, Any]],
        language: Optional[str] = None
    ) -> str:
        """
        Summarize a conversation to reduce context length
        
        Uses Claude to create a concise summary of the conversation
        """
        # Format messages for summarization
        conversation_text = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('content', '')}"
            for msg in messages
        ])
        
        summary_prompt = f"""Summarize the following conversation in a concise way, preserving:
- Key topics discussed
- Important decisions or conclusions
- Relevant code examples or patterns mentioned
- User preferences or context

Language context: {language or 'general'}

Conversation:
{conversation_text}

Provide a clear, concise summary:"""
        
        try:
            # Anthropic client is synchronous
            response = self.client.messages.create(
                model=settings.DEFAULT_MODEL,
                max_tokens=500,
                temperature=0.3,  # Lower temperature for more factual summaries
                messages=[{
                    "role": "user",
                    "content": summary_prompt
                }]
            )
            
            return response.content[0].text
        
        except Exception as e:
            # Fallback: simple truncation if summarization fails
            return f"Previous conversation about {language or 'code'} ({len(messages)} messages)"
    
    async def store_message(
        self,
        conversation_id: str,
        message: Dict[str, Any],
        response: Dict[str, Any]
    ):
        """Store a message and response in conversation history"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        # Store user message
        self.conversations[conversation_id].append({
            "role": "user",
            "content": message.get("content", ""),
            "timestamp": datetime.now().isoformat()
        })
        
        # Store assistant response
        self.conversations[conversation_id].append({
            "role": "assistant",
            "content": response.get("content", ""),
            "timestamp": datetime.now().isoformat()
        })
    
    async def get_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Retrieve conversation history"""
        return self.conversations.get(conversation_id, [])
    
    async def delete_conversation(self, conversation_id: str):
        """Delete a conversation"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
        if conversation_id in self.summaries:
            del self.summaries[conversation_id]

