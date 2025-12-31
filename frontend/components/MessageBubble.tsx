'use client';

import { Message } from 'ai/react';
import { User, Bot } from 'lucide-react';

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  
  // Handle different content formats from AI SDK
  const getMessageContent = () => {
    const msgAny = message as any;
    
    // Case 1: Content is a string (most common)
    if (typeof msgAny.content === 'string') {
      return msgAny.content;
    }
    
    // Case 2: Content is an array (parts format)
    if (Array.isArray(msgAny.content)) {
      return msgAny.content
        .filter((part: any) => part && (part.type === 'text' || part.text))
        .map((part: any) => part.text || part.content || String(part))
        .join('');
    }
    
    // Case 3: Content is an object with text property
    if (msgAny.content && typeof msgAny.content === 'object') {
      if (msgAny.content.text) {
        return msgAny.content.text;
      }
      if (msgAny.content.content) {
        return msgAny.content.content;
      }
    }
    
    // Case 4: Try to extract from parts if it exists
    if (msgAny.parts && Array.isArray(msgAny.parts)) {
      return msgAny.parts
        .filter((part: any) => part && part.type === 'text')
        .map((part: any) => part.text)
        .join('');
    }
    
    // Fallback: convert to string
    const content = String(msgAny.content || msgAny.text || '');
    return content;
  };

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser
            ? 'bg-blue-500 text-white'
            : 'bg-gradient-to-br from-purple-500 to-blue-600 text-white'
        }`}
      >
        {isUser ? (
          <User className="w-4 h-4" />
        ) : (
          <Bot className="w-4 h-4" />
        )}
      </div>
      <div
        className={`flex-1 max-w-[80%] rounded-lg px-4 py-3 ${
          isUser
            ? 'bg-blue-500 text-white'
            : 'bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-50'
        }`}
      >
        <div className="whitespace-pre-wrap break-words">{getMessageContent()}</div>
      </div>
    </div>
  );
}

