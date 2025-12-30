'use client';

import { useChat } from 'ai/react';
import { useState } from 'react';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { LanguageSelector } from './LanguageSelector';

export function Chat() {
  const [language, setLanguage] = useState<string>('');
  const [conversationId, setConversationId] = useState<string | null>(null);

  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: '/api/chat',
    body: {
      language: language || undefined,
      conversation_id: conversationId || undefined,
    },
    onResponse: (response) => {
      // Extract conversation ID from response if available
      const convId = response.headers.get('x-conversation-id');
      if (convId) {
        setConversationId(convId);
      }
    },
  });

  return (
    <div className="flex flex-col h-[calc(100vh-200px)] bg-white dark:bg-zinc-900 rounded-lg border border-zinc-200 dark:border-zinc-800 shadow-lg">
      <div className="p-4 border-b border-zinc-200 dark:border-zinc-800">
        <LanguageSelector value={language} onChange={setLanguage} />
      </div>
      
      <div className="flex-1 overflow-y-auto p-4">
        <MessageList messages={messages} isLoading={isLoading} />
      </div>
      
      <div className="p-4 border-t border-zinc-200 dark:border-zinc-800">
        <MessageInput
          input={input}
          handleInputChange={handleInputChange}
          handleSubmit={handleSubmit}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}

