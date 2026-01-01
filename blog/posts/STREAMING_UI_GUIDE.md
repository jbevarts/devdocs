# How Streaming Responses Work in the UI

## Overview

The DevDocs AI chat interface displays streaming responses automatically. As text chunks arrive from the backend, they appear incrementally in the UI, creating a real-time typing effect.

## Architecture Flow

```
User Types Message
    ↓
Chat Component (useChat hook)
    ↓
Frontend API Route (/api/chat)
    ↓
Backend API (/api/chat/) - Streaming SSE
    ↓
Chat Service - Streams from Claude
    ↓
Chunks flow back through the chain
    ↓
UI Updates Automatically
```

## How It Works

### 1. **AI SDK's `useChat` Hook**

The `useChat` hook from `@ai-sdk/react` automatically handles streaming:

```typescript
const { messages, sendMessage, status, error } = useChat({
  transport: new DefaultChatTransport({
    api: '/api/chat',
    // ...
  }),
});
```

**Key Features:**
- `messages` array updates **incrementally** as chunks arrive
- `status` changes to `'streaming'` during active streaming
- No manual state management needed

### 2. **Message Updates**

As chunks arrive via Server-Sent Events (SSE), the `useChat` hook:
1. Receives `text-delta` events
2. Appends each delta to the current assistant message
3. Triggers React re-render automatically

### 3. **UI Components**

The UI components automatically reflect streaming:

**MessageList Component:**
```typescript
{messages.map((message) => (
  <MessageBubble key={message.id} message={message} />
))}
{isLoading && <LoadingIndicator />}
```

- Each message in the `messages` array is rendered
- As the assistant message content grows, `MessageBubble` re-renders
- `isLoading` shows a loading indicator while `status === 'streaming'`

**MessageBubble Component:**
```typescript
<div className="whitespace-pre-wrap break-words">
  {getMessageContent()}
</div>
```

- Extracts content from the message object
- Displays it with proper formatting
- Updates automatically as content changes

### 4. **Auto-Scrolling**

The chat automatically scrolls to show the latest content:

```typescript
useEffect(() => {
  if (scrollContainerRef.current) {
    requestAnimationFrame(() => {
      scrollContainerRef.current?.scrollTo({
        top: scrollContainerRef.current.scrollHeight,
        behavior: 'smooth',
      });
    });
  }
}, [messages, isLoading]);
```

- Scrolls when `messages` array changes (new chunks arrive)
- Scrolls when `isLoading` state changes
- Uses `requestAnimationFrame` for smooth scrolling

## Visual Experience

### During Streaming:
1. **User sends message** → Appears immediately in chat
2. **Loading indicator** → Shows while waiting for response
3. **Assistant message appears** → Starts with first chunk
4. **Text grows incrementally** → Each chunk appends to the message
5. **Auto-scroll** → Keeps latest content visible
6. **Streaming completes** → Loading indicator disappears

### Example Timeline:
```
t=0ms:   User: "Explain this code"
t=100ms: [Loading...]
t=500ms: Assistant: "This code"
t=800ms: Assistant: "This code demonstrates"
t=1200ms: Assistant: "This code demonstrates how to..."
...continues...
t=5000ms: Assistant: [Complete response]
t=5000ms: [Loading indicator disappears]
```

## Technical Details

### Backend Streaming Format

The backend sends Server-Sent Events in AI SDK v6 format:

```json
{"type": "text-start", "id": "msg_123"}
{"type": "text-delta", "id": "msg_123", "delta": "This"}
{"type": "text-delta", "id": "msg_123", "delta": " code"}
{"type": "text-delta", "id": "msg_123", "delta": " demonstrates"}
{"type": "text-end", "id": "msg_123"}
```

### Frontend Processing

1. **Frontend API Route** receives SSE stream from backend
2. **Passes through** to `useChat` hook unchanged
3. **AI SDK** parses events and updates `messages` array
4. **React** re-renders components automatically

## Why It Works Automatically

The beauty of using AI SDK's `useChat` hook is that it handles all the complexity:

✅ **Automatic message updates** - No manual state management  
✅ **Incremental rendering** - Chunks appear as they arrive  
✅ **Type safety** - Full TypeScript support  
✅ **Error handling** - Built-in error states  
✅ **Loading states** - Automatic loading indicators  

## Customization

### Show Typing Indicator

The `isLoading` state can be used to show custom indicators:

```typescript
{isLoading && (
  <div className="typing-indicator">
    <span>●</span><span>●</span><span>●</span>
  </div>
)}
```

### Custom Message Formatting

The `MessageBubble` component can be customized to:
- Add syntax highlighting for code
- Format markdown
- Add animations
- Show timestamps

### Streaming Speed

The streaming speed is controlled by:
- **Backend**: Claude's response generation speed
- **Network**: Connection latency
- **Frontend**: No artificial delays (real-time)

## Troubleshooting

### If streaming doesn't work:

1. **Check backend** - Ensure `stream: true` is sent
2. **Check headers** - Verify `Content-Type: text/event-stream
3. **Check network** - Verify SSE connection is established
4. **Check console** - Look for errors in browser console

### Common Issues:

- **Messages not updating**: Check that `useChat` is receiving events
- **No loading indicator**: Verify `status === 'streaming'`
- **Scrolling issues**: Check `scrollContainerRef` is set correctly

## Summary

Streaming in the UI works automatically because:
1. **Backend streams** chunks via SSE
2. **Frontend passes through** the stream to AI SDK
3. **AI SDK updates** the `messages` array incrementally
4. **React re-renders** components as messages change
5. **Auto-scroll** keeps the latest content visible

No additional code is needed in the UI components - they automatically display streaming responses!

