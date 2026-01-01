'use client';

import { Bot } from 'lucide-react';

export function LoadingIndicator() {
  return (
    <div className="flex gap-3 items-start">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
        <Bot className="w-4 h-4 text-white" />
      </div>
      <div className="flex-1 max-w-[80%]">
        <div className="inline-flex items-center gap-2 px-3 py-2 bg-zinc-50 dark:bg-zinc-900/50 border border-zinc-200 dark:border-zinc-700 rounded-lg">
          <div className="flex gap-1 items-center">
            <div 
              className="w-1.5 h-1.5 bg-purple-500 rounded-full animate-bounce" 
              style={{ animationDelay: '0ms', animationDuration: '1.4s' }} 
            />
            <div 
              className="w-1.5 h-1.5 bg-purple-500 rounded-full animate-bounce" 
              style={{ animationDelay: '200ms', animationDuration: '1.4s' }} 
            />
            <div 
              className="w-1.5 h-1.5 bg-purple-500 rounded-full animate-bounce" 
              style={{ animationDelay: '400ms', animationDuration: '1.4s' }} 
            />
          </div>
          <span className="text-xs text-zinc-500 dark:text-zinc-400 font-medium">AI is typing</span>
        </div>
      </div>
    </div>
  );
}

