import { useRef, useEffect } from 'react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  userName?: string
}

interface ChatPanelProps {
  messages: Message[]
  messageInput: string
  setMessageInput: (value: string) => void
  onSendMessage: () => void
}

export default function ChatPanel({ messages, messageInput, setMessageInput, onSendMessage }: ChatPanelProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      onSendMessage()
    }
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true })
  }

  return (
    <div className="absolute bottom-8 left-6 z-10 max-w-sm w-full md:w-80">
      <div className="flex flex-col gap-3 rounded-2xl border border-white/20 bg-black/20 p-4 backdrop-blur-lg shadow-2xl max-h-[260px]">
        {/* Messages container */}
        <div className="flex h-full flex-col gap-3 overflow-y-auto pr-2 flex-1">
          {messages.map((message) => (
            <div key={message.id} className="flex items-start gap-2.5">
              {/* Avatar */}
              <div className="h-8 w-8 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center flex-shrink-0">
                <span className="text-sm">
                  {message.role === 'user' ? '👤' : '🤖'}
                </span>
              </div>

              {/* Message content */}
              <div className="flex flex-col gap-1 flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className="font-semibold text-white text-sm truncate">
                    {message.userName || (message.role === 'user' ? 'You' : 'Ornina AI')}
                  </p>
                  <span className="text-xs text-gray-400 flex-shrink-0">
                    {formatTime(message.timestamp)}
                  </span>
                </div>
                <p className="text-sm text-gray-200 break-words">{message.content}</p>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div className="mt-2">
          <div className="relative">
            <input
              type="text"
              value={messageInput}
              onChange={(e) => setMessageInput(e.target.value)}
              onKeyPress={handleKeyPress}
              className="w-full rounded-lg border border-white/20 bg-white/10 px-4 py-2 text-sm text-white placeholder-gray-400 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-primary/80 focus:border-transparent transition-shadow duration-300"
              placeholder="اكتب رسالة... Type a message..."
            />
            <button
              onClick={onSendMessage}
              aria-label="Send message"
              className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-white transition-colors"
            >
              <span className="material-symbols-outlined text-xl">send</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
