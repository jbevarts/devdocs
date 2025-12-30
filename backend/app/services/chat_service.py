"""
Chat service for handling AI model interactions
"""
from typing import List, Dict, Any, Optional
from anthropic import Anthropic
import json

from app.core.config import settings
from app.services.prompts import get_system_prompt


class ChatService:
    """Service for managing chat interactions with AI models"""
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.DEFAULT_MODEL
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        language: Optional[str] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a response using Claude
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            language: Optional programming language context
            stream: Whether to stream the response
        
        Returns:
            Dict with 'content' and 'usage' keys
        """
        # Get system prompt based on language
        system_prompt = get_system_prompt(language)
        
        # Format messages for Anthropic API
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        try:
            if stream:
                # Handle streaming response (synchronous Anthropic client)
                response_text = ""
                with self.client.messages.stream(
                    model=self.model,
                    max_tokens=settings.MAX_TOKENS,
                    temperature=settings.TEMPERATURE,
                    system=system_prompt,
                    messages=formatted_messages
                ) as stream:
                    for text in stream.text_stream:
                        response_text += text
                
                return {
                    "content": response_text,
                    "usage": None  # Usage not available for streaming
                }
            else:
                # Non-streaming response (synchronous Anthropic client)
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=settings.MAX_TOKENS,
                    temperature=settings.TEMPERATURE,
                    system=system_prompt,
                    messages=formatted_messages
                )
                
                return {
                    "content": response.content[0].text,
                    "usage": {
                        "input_tokens": response.usage.input_tokens,
                        "output_tokens": response.usage.output_tokens
                    }
                }
        
        except Exception as e:
            # Fallback to OpenAI if configured
            if settings.OPENAI_API_KEY:
                return await self._fallback_to_openai(
                    messages=formatted_messages,
                    system_prompt=system_prompt
                )
            raise e
    
    async def _fallback_to_openai(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str
    ) -> Dict[str, Any]:
        """Fallback to OpenAI GPT-4 if Claude fails"""
        import asyncio
        from openai import OpenAI
        
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Convert messages format for OpenAI
        openai_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            # Skip system role messages as we already have one
            if msg.get("role") != "system":
                openai_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Run synchronous OpenAI call in thread pool
        def _create_completion():
            return client.chat.completions.create(
                model=settings.FALLBACK_MODEL,
                messages=openai_messages,
                max_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE
            )
        
        response = await asyncio.to_thread(_create_completion)
        
        return {
            "content": response.choices[0].message.content or "",
            "usage": {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens
            }
        }

