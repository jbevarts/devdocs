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
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is not set in environment variables")
        
        api_key = settings.ANTHROPIC_API_KEY.strip()
        
        # Basic validation - only check if key exists and has reasonable length
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set in environment variables")
        
        if len(api_key) < 20:
            raise ValueError(f"ANTHROPIC_API_KEY appears to be invalid (too short). Length: {len(api_key)}")
        
        self.client = Anthropic(api_key=api_key)
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
            # Fallback to OpenAI if configured and not a placeholder
            if settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith('your_'):
                return await self._fallback_to_openai(
                    messages=formatted_messages,
                    system_prompt=system_prompt
                )
            raise e
    
    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        language: Optional[str] = None
    ):
        """
        Stream response chunks from Claude as an async generator.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            language: Optional programming language context
        
        Yields:
            Text chunks as they arrive from Claude
        """
        import asyncio
        from queue import Queue, Empty
        from threading import Thread
        
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
            # Use a queue to bridge synchronous streaming to async generator
            chunk_queue = Queue()
            exception_queue = Queue()
            stream_done = False
            
            def _stream_sync():
                nonlocal stream_done
                try:
                    with self.client.messages.stream(
                        model=self.model,
                        max_tokens=settings.MAX_TOKENS,
                        temperature=settings.TEMPERATURE,
                        system=system_prompt,
                        messages=formatted_messages
                    ) as stream:
                        for text in stream.text_stream:
                            chunk_queue.put(text)
                    stream_done = True
                    chunk_queue.put(None)  # Signal completion
                except Exception as e:
                    exception_queue.put(e)
                    stream_done = True
                    chunk_queue.put(None)  # Signal completion
            
            # Start streaming in a separate thread
            thread = Thread(target=_stream_sync, daemon=True)
            thread.start()
            
            # Yield chunks as they arrive - use shorter timeout for more responsive streaming
            while not stream_done or not chunk_queue.empty():
                # Check for exceptions first
                if not exception_queue.empty():
                    raise exception_queue.get()
                
                # Get chunk from queue (with very short timeout for immediate yielding)
                try:
                    chunk = chunk_queue.get(timeout=0.01)  # 10ms timeout for faster response
                    if chunk is None:  # Completion signal
                        break
                    yield chunk
                except Empty:
                    # No chunk available yet, yield control and check again
                    await asyncio.sleep(0.001)  # Small sleep to yield control
                    continue
        
        except Exception as e:
            # Fallback to OpenAI if configured and not a placeholder
            if settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith('your_'):
                # OpenAI streaming fallback would go here
                raise e
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

