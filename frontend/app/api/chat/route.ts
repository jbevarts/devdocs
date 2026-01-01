import { NextRequest } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function POST(req: NextRequest) {
  try {
    // Parse the request body - backend now accepts the modern format directly
    const body = await req.json();
    const { messages, language, conversation_id } = body;

    // Forward request to backend API with streaming enabled
    const backendResponse = await fetch(`${BACKEND_URL}/api/chat/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages: messages, // Send in modern format - backend handles it
        language: language || undefined,
        conversation_id: conversation_id || undefined,
        stream: true, // Enable streaming
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

    // Check if backend is streaming (SSE response)
    const contentType = backendResponse.headers.get('content-type');
    if (contentType?.includes('text/event-stream')) {
      // Backend is already streaming in AI SDK v6 format, pass it through
      const reader = backendResponse.body?.getReader();
      const decoder = new TextDecoder();
      
      const stream = new ReadableStream({
        async start(controller) {
          if (!reader) {
            controller.close();
            return;
          }
          
          try {
            let buffer = '';
            while (true) {
              const { done, value } = await reader.read();
              if (done) {
                // Flush any remaining buffer
                if (buffer) {
                  controller.enqueue(new TextEncoder().encode(buffer));
                }
                controller.close();
                break;
              }
              
              // Decode chunk (may be partial)
              buffer += decoder.decode(value, { stream: true });
              
              // Process complete SSE messages (lines ending with \n\n)
              const lines = buffer.split('\n\n');
              // Keep the last incomplete line in buffer
              buffer = lines.pop() || '';
              
              // Send complete SSE messages immediately
              for (const line of lines) {
                if (line.trim()) {
                  controller.enqueue(new TextEncoder().encode(line + '\n\n'));
                }
              }
            }
          } catch (error) {
            console.error('Stream error:', error);
            controller.error(error);
          }
        },
      });
      
      // Return the stream with conversation_id in headers
      const headers = new Headers({
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      });
      
      const conversationId = backendResponse.headers.get('x-conversation-id');
      if (conversationId) {
        headers.set('x-conversation-id', conversationId);
      }
      
      return new Response(stream, { headers });
    }
    
    // Fallback: non-streaming response (shouldn't happen with stream: true)
    const backendData = await backendResponse.json();
    throw new Error('Expected streaming response but received JSON');
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
