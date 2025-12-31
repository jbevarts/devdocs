import { NextRequest } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function POST(req: NextRequest) {
  try {
    // Parse the request body - backend now accepts the modern format directly
    const body = await req.json();
    const { messages, language, conversation_id } = body;

    // Forward request to backend API
    const backendResponse = await fetch(`${BACKEND_URL}/api/chat/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages: messages, // Send in modern format - backend handles it
        language: language || undefined,
        conversation_id: conversation_id || undefined,
        stream: false,
      }),
    });

    if (!backendResponse.ok) {
      let errorMessage = `Backend error: ${backendResponse.statusText}`;
      try {
        const error = await backendResponse.json();
        // Handle different error formats
        if (typeof error.detail === 'string') {
          errorMessage = error.detail;
        } else if (error.detail && typeof error.detail === 'object') {
          errorMessage = JSON.stringify(error.detail);
        } else if (error.message) {
          errorMessage = error.message;
        } else if (typeof error === 'string') {
          errorMessage = error;
        }
      } catch {
        // If JSON parsing fails, use status text
      }
      throw new Error(errorMessage);
    }

    const backendData = await backendResponse.json();

    // Format response for AI SDK v6 - use native AI SDK format
    // AI SDK v6 expects: text-start, text-delta, text-end format
    const encoder = new TextEncoder();
    const assistantMessage = backendData.message?.content || '';
    const messageId = `msg_${Date.now()}`;
    
    const stream = new ReadableStream({
      start(controller) {
        // Send text-start
        try {
          const startChunk = { 
            type: 'text-start',
            id: messageId,
          };
          const startData = `data: ${JSON.stringify(startChunk)}\n\n`;
          controller.enqueue(encoder.encode(startData));
        } catch (e) {
          console.error('Error sending start chunk:', e);
        }
        
        // Send content in chunks to simulate streaming
        const chunkSize = 20;
        let index = 0;
        let isClosed = false;
        
        const sendChunk = () => {
          // Check if we're done or if controller is closed
          if (isClosed || index >= assistantMessage.length) {
            if (!isClosed) {
              try {
                // Send text-end
                const endChunk = { 
                  type: 'text-end',
                  id: messageId,
                };
                // Use standard SSE format with 'data:' prefix
                const endData = `data: ${JSON.stringify(endChunk)}\n\n`;
                controller.enqueue(encoder.encode(endData));
                controller.close();
                isClosed = true;
              } catch (e) {
                // Controller already closed, ignore
                isClosed = true;
              }
            }
            return;
          }
          
          // Check if controller is still open before trying to enqueue
          try {
            const chunk = assistantMessage.slice(index, Math.min(index + chunkSize, assistantMessage.length));
            // AI SDK v6 format: type: "text-delta", delta: "string"
            const deltaChunk = {
              type: 'text-delta',
              id: messageId,
              delta: chunk,
            };
            // Use standard SSE format with 'data:' prefix
            const deltaData = `data: ${JSON.stringify(deltaChunk)}\n\n`;
            controller.enqueue(encoder.encode(deltaData));
            index += chunkSize;
            // Send next chunk immediately (synchronously) for better compatibility
            // DefaultChatTransport may need chunks sent faster
            if (!isClosed) {
              // Use setImmediate or process.nextTick equivalent for browser
              Promise.resolve().then(() => {
                if (!isClosed) {
                  sendChunk();
                }
              });
            }
          } catch (e: any) {
            // Controller was closed, stop sending chunks
            if (e?.name !== 'TypeError' || !e?.message?.includes('closed')) {
              console.error('Error sending chunk:', e);
            }
            isClosed = true;
          }
        };
        
        sendChunk();
      },
    });

    // Return with conversation_id in headers
    const headers = new Headers({
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    });
    
    if (backendData.conversation_id) {
      headers.set('x-conversation-id', backendData.conversation_id);
    }

    return new Response(stream, { headers });
  } catch (error: any) {
    console.error('Chat API error:', error);
    return new Response(
      JSON.stringify({ error: error.message || 'Internal server error' }),
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }
}
