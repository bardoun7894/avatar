import { useRef, useEffect, useState } from 'react'

interface Message {
  id: string
  role: 'user' | 'assistant' | 'bot' | 'system'
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
  const [isArabic, setIsArabic] = useState(false)

  // Detect RTL language on mount
  useEffect(() => {
    const lang = document.documentElement.lang || document.documentElement.getAttribute('dir')
    setIsArabic(lang === 'ar' || lang === 'rtl')
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleKeyDown = (e: React.KeyboardEvent) => {
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
      <style>{`
        @keyframes typing-cursor {
          0%, 49% { opacity: 1; }
          50%, 100% { opacity: 0; }
        }
      `}</style>
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
                <p className="text-sm text-gray-200 break-words">
                  {message.content}
                  {/* Show typing cursor for the last assistant message */}
                  {message.role === 'assistant' && message.id === messages[messages.length - 1]?.id && (
                    <span className="inline-block ml-1 w-2 h-4 bg-gray-200 animate-pulse" style={{animation: 'typing-cursor 1s infinite'}}></span>
                  )}
                </p>
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
              onKeyDown={handleKeyDown}
              className={`w-full rounded-lg border border-white/20 bg-white/10 px-4 py-2 text-sm text-white placeholder-gray-400 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-primary/80 focus:border-transparent transition-shadow duration-300 ${isArabic ? 'text-right pl-12 pr-4' : 'text-left pr-12 pl-4'}`}
              placeholder={isArabic ? 'اكتب رسالة...' : 'Type a message...'}
              dir={isArabic ? 'rtl' : 'ltr'}
            />
            <button
              onClick={onSendMessage}
              disabled={!messageInput.trim()}
              aria-label={isArabic ? 'إرسال الرسالة' : 'Send message'}
              title={isArabic ? 'إرسال (Enter)' : 'Send (Enter)'}
              className={`absolute inset-y-0 flex items-center justify-center w-9 h-9 rounded-lg transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed ${
                messageInput.trim()
                  ? 'text-white bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 shadow-lg hover:shadow-xl'
                  : 'text-gray-500 bg-transparent'
              } ${isArabic ? 'left-1.5' : 'right-1.5'}`}
            >
              {/* Modern Send Icon - Clean Arrow */}
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                {isArabic ? (
                  <>
                    {/* Left arrow for RTL */}
                    <line x1="19" y1="12" x2="5" y2="12" />
                    <polyline points="12 19 5 12 12 5" />
                  </>
                ) : (
                  <>
                    {/* Right arrow for LTR */}
                    <line x1="5" y1="12" x2="19" y2="12" />
                    <polyline points="12 5 19 12 12 19" />
                  </>
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
