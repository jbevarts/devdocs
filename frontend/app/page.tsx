'use client';

import { Chat } from '@/components/Chat';
import { Header } from '@/components/Header';

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-b from-zinc-50 to-white dark:from-black dark:to-zinc-900">
      <Header />
      <main className="flex-1 container mx-auto px-4 py-8 max-w-4xl">
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-zinc-900 dark:text-zinc-50 mb-2">
            DevDocs AI
          </h1>
          <p className="text-lg text-zinc-600 dark:text-zinc-400">
            Intelligent documentation assistant for developers
          </p>
        </div>
        <Chat />
      </main>
    </div>
  );
}
