import Head from 'next/head'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import ControlBar from '../../components/ControlBar'
import ChatPanel from '../../components/ChatPanel'

interface Message {
  id: string
  role: 'user' | 'assistant' | 'bot' | 'system'
  content: string
  timestamp: Date
  userName?: string
}

interface CallData {
  callId: string
  status: 'initiated' | 'ivr_processing' | 'in_queue' | 'in_progress' | 'transferred' | 'completed'
  customerName?: string
  customerPhone?: string
  customerEmail?: string
  department?: 'reception' | 'sales' | 'complaints'
  serviceType?: string
  duration: number
}

export default function CallPage() {
  const router = useRouter()
  const { room, user } = router.query
  const [messages, setMessages] = useState<Message[]>([])
  const [messageInput, setMessageInput] = useState('')
  const [isMuted, setIsMuted] = useState(false)
  const [isVideoOff, setIsVideoOff] = useState(false)
  const [isChatOpen, setIsChatOpen] = useState(true)
  const [callData, setCallData] = useState<CallData | null>(null)
  const [callStartTime, setCallStartTime] = useState<Date | null>(null)

  // Initialize call
  useEffect(() => {
    if (!room) return

    const newCall: CallData = {
      callId: room as string,
      status: 'ivr_processing',
      duration: 0,
    }
    setCallData(newCall)
    setCallStartTime(new Date())

    // Add initial IVR message
    const welcomeMsg: Message = {
      id: `msg-${Date.now()}`,
      role: 'bot',
      content: 'أهلاً وسهلاً بكم في خدمة الاستقبال الآلية. Welcome to our automated reception service.',
      timestamp: new Date(),
      userName: 'IVR Bot',
    }
    setMessages([welcomeMsg])
  }, [room])

  // Update call duration
  useEffect(() => {
    if (!callStartTime || !callData) return

    const interval = setInterval(() => {
      const duration = Math.floor((Date.now() - callStartTime.getTime()) / 1000)
      setCallData((prev) => prev ? { ...prev, duration } : null)
    }, 1000)

    return () => clearInterval(interval)
  }, [callStartTime, callData])

  const handleToggleMute = () => {
    setIsMuted(!isMuted)
  }

  const handleToggleVideo = () => {
    setIsVideoOff(!isVideoOff)
  }

  const handleToggleChat = () => {
    setIsChatOpen(!isChatOpen)
  }

  const handleSendMessage = () => {
    if (!messageInput.trim()) return

    const userMsg: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: messageInput,
      timestamp: new Date(),
      userName: user as string || 'You',
    }

    setMessages((prev) => [...prev, userMsg])
    setMessageInput('')

    // Simulate bot response
    setTimeout(() => {
      const botMsg: Message = {
        id: `msg-${Date.now() + 1}`,
        role: 'bot',
        content: 'جاري معالجة طلبك... Processing your request...',
        timestamp: new Date(),
        userName: 'IVR Bot',
      }
      setMessages((prev) => [...prev, botMsg])
    }, 500)
  }

  const handleEndCall = async () => {
    if (callData) {
      setCallData({ ...callData, status: 'completed' })
      setTimeout(() => {
        router.push('/callcenter')
      }, 1500)
    }
  }

  const formatDuration = (seconds: number): string => {
    const hrs = Math.floor(seconds / 3600)
    const mins = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60

    if (hrs > 0) {
      return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  if (!callData) {
    return (
      <div className="w-full h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-white/20 border-t-white rounded-full animate-spin mx-auto mb-4"></div>
          <div className="text-white/60">Initializing call...</div>
        </div>
      </div>
    )
  }

  return (
    <>
      <Head>
        <title>Call Center - Active Call</title>
        <meta name="description" content="Active call in progress" />
      </Head>

      <div className="w-full h-screen bg-gray-900 relative flex overflow-hidden">
        {/* Background gradient effects */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600/10 via-purple-600/10 to-pink-600/10"></div>

        {/* Main Call Area */}
        <div className="flex-1 relative flex flex-col items-center justify-center">
          {/* Status Bar */}
          <div className="absolute top-8 left-1/2 -translate-x-1/2 z-10">
            <div className="flex items-center gap-4 px-6 py-3 bg-black/20 rounded-full border border-white/20 backdrop-blur-lg">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-white/80 text-sm font-medium">
                  {callData.status === 'ivr_processing' && 'IVR Processing'}
                  {callData.status === 'in_queue' && 'In Queue'}
                  {callData.status === 'in_progress' && 'Connected'}
                  {callData.status === 'transferred' && 'Transferred'}
                </span>
              </div>
              <div className="w-px h-4 bg-white/20"></div>
              <span className="text-white font-mono text-sm">{formatDuration(callData.duration)}</span>
            </div>
          </div>

          {/* Call Display Area */}
          <div className="flex flex-col items-center justify-center flex-1">
            {/* Department Badge */}
            {callData.department && (
              <div className="mb-8 px-4 py-2 bg-white/10 rounded-full border border-white/20 backdrop-blur-lg">
                <span className="text-white/80 text-sm font-medium">
                  {callData.department === 'reception' && '📞 Reception'}
                  {callData.department === 'sales' && '💼 Sales'}
                  {callData.department === 'complaints' && '⚠️ Complaints'}
                </span>
              </div>
            )}

            {/* Large Icon */}
            <div className="mb-8 w-24 h-24 rounded-full bg-white/10 border border-white/20 backdrop-blur-lg flex items-center justify-center">
              <div className="text-6xl">📞</div>
            </div>

            {/* Call Info */}
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-white mb-2">
                {callData.customerName || 'Incoming Call'}
              </h2>
              {callData.customerPhone && (
                <p className="text-white/60 font-mono">{callData.customerPhone}</p>
              )}
            </div>

            {/* Service Type */}
            {callData.serviceType && (
              <div className="px-6 py-3 bg-white/10 rounded-lg border border-white/20 backdrop-blur-lg">
                <p className="text-white/80 text-sm">
                  Service: <span className="text-white font-medium">{callData.serviceType}</span>
                </p>
              </div>
            )}
          </div>

          {/* Control Bar */}
          <ControlBar
            isMuted={isMuted}
            isVideoOff={isVideoOff}
            isChatOpen={isChatOpen}
            onToggleMute={handleToggleMute}
            onToggleVideo={handleToggleVideo}
            onToggleChat={handleToggleChat}
            onEndCall={handleEndCall}
          />
        </div>

        {/* Right Sidebar - Chat */}
        {isChatOpen && (
          <div className="w-96 border-l border-white/10 flex flex-col bg-black/20 backdrop-blur-lg">
            <div className="flex-1 overflow-hidden">
              <ChatPanel
                messages={messages}
                messageInput={messageInput}
                setMessageInput={setMessageInput}
                onSendMessage={handleSendMessage}
              />
            </div>
          </div>
        )}
      </div>
    </>
  )
}
