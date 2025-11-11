'use client'

import Head from 'next/head'
import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/router'
import ControlBar from '../../components/ControlBar'
import ChatPanel from '../../components/ChatPanel'

// API Configuration - works in both development and production
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
console.log(`🌐 API Base URL: ${API_BASE_URL}`)

interface Message {
  id: string
  role: 'user' | 'assistant' | 'bot' | 'system'
  content: string
  timestamp: Date
  userName?: string
  audioUrl?: string
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

export default function CallPageWithAudio() {
  const router = useRouter()
  const { room, user } = router.query
  const [messages, setMessages] = useState<Message[]>([])
  const [messageInput, setMessageInput] = useState('')
  const [isMuted, setIsMuted] = useState(false)
  const [isVideoOff, setIsVideoOff] = useState(false)
  const [isChatOpen, setIsChatOpen] = useState(true)
  const [callData, setCallData] = useState<CallData | null>(null)
  const [callStartTime, setCallStartTime] = useState<Date | null>(null)
  const [isRecording, setIsRecording] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [audioLevel, setAudioLevel] = useState(0)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const streamRef = useRef<MediaStream | null>(null)
  const audioElementRef = useRef<HTMLAudioElement>(null)

  // Initialize call
  useEffect(() => {
    if (!room) {
      console.log('⏳ Waiting for room parameter...')
      return
    }

    console.log('🎙️ Initializing audio call...')
    console.log(`📍 Room: ${room}`)
    console.log(`👤 User: ${user}`)

    const newCall: CallData = {
      callId: room as string,
      status: 'ivr_processing',
      duration: 0,
    }
    setCallData(newCall)
    setCallStartTime(new Date())
    console.log('✅ Call initialized')

    // Add initial IVR message
    const welcomeMsg: Message = {
      id: `msg-${Date.now()}`,
      role: 'bot',
      content: 'أهلاً وسهلاً بكم في خدمة الاستقبال الآلية. Welcome to our automated reception service.',
      timestamp: new Date(),
      userName: 'IVR Bot',
    }
    setMessages([welcomeMsg])
    console.log('✅ Welcome message added')

    // Initialize audio context for microphone level monitoring
    initializeAudio()
  }, [room, user])

  // Initialize Web Audio API
  const initializeAudio = async () => {
    try {
      console.log('🎤 Requesting microphone access...')
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: false,
        },
        video: false
      })

      streamRef.current = stream
      console.log('✅ Microphone access granted')

      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
      audioContextRef.current = audioContext
      console.log('✅ Audio context created')

      const source = audioContext.createMediaStreamSource(stream)
      const analyser = audioContext.createAnalyser()
      analyser.fftSize = 256
      analyserRef.current = analyser

      source.connect(analyser)
      console.log('✅ Audio analyser connected')

      // Monitor audio levels
      monitorAudioLevel()
      console.log('✅ Audio level monitoring started')
    } catch (err) {
      console.error('❌ Failed to initialize audio:', err)
      alert('Microphone access denied. Please allow microphone permission to use the call center.')
    }
  }

  const monitorAudioLevel = () => {
    if (!analyserRef.current) return

    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount)
    analyserRef.current.getByteFrequencyData(dataArray)

    const average = dataArray.reduce((a, b) => a + b) / dataArray.length
    setAudioLevel(Math.round(average))

    requestAnimationFrame(monitorAudioLevel)
  }

  // Start recording user input
  const startRecording = async () => {
    if (!streamRef.current || isRecording) return

    try {
      audioChunksRef.current = []
      const mediaRecorder = new MediaRecorder(streamRef.current)
      mediaRecorderRef.current = mediaRecorder

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data)
      }

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        handleAudioSubmission(audioBlob)
      }

      mediaRecorder.start()
      setIsRecording(true)
    } catch (err) {
      console.error('Failed to start recording:', err)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const handleAudioSubmission = async (audioBlob: Blob) => {
    try {
      // Convert audio to text using transcription
      const formData = new FormData()
      formData.append('audio_file', audioBlob)

      console.log('🎤 Sending audio for transcription to backend...')
      const response = await fetch(`${API_BASE_URL}/api/transcribe`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        console.error(`❌ Transcription API error: ${response.status}`)
        throw new Error(`API error: ${response.status}`)
      }

      const data = await response.json()
      console.log('✅ Transcription received:', data.text)

      if (data.text) {
        // Add user's transcribed message
        const userMsg: Message = {
          id: `msg-${Date.now()}`,
          role: 'user',
          content: data.text,
          timestamp: new Date(),
          userName: user as string || 'You',
          audioUrl: URL.createObjectURL(audioBlob),
        }

        setMessages((prev) => [...prev, userMsg])
        console.log('✅ User message added to chat')

        // Get AI response and synthesize audio
        await getAIResponseWithAudio(data.text)
      }
    } catch (err) {
      console.error('❌ Failed to process audio:', err)
      alert('Failed to process audio. Please check your microphone and try again.')
    }
  }

  const getAIResponseWithAudio = async (userText: string) => {
    try {
      console.log('🤖 Sending message to AI for response...')
      const response = await fetch(`${API_BASE_URL}/api/conversation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          call_id: callData?.callId,
          message: userText,
          language: 'ar', // Detect from context
        }),
      })

      if (!response.ok) {
        console.error(`❌ Conversation API error: ${response.status}`)
        throw new Error(`API error: ${response.status}`)
      }

      const data = await response.json()
      console.log('✅ AI response received:', data.text || data.response)

      // Add AI response message
      const aiMsg: Message = {
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        content: data.text || data.response,
        timestamp: new Date(),
        userName: data.persona || 'Agent',
        audioUrl: data.audio_url, // Backend should provide synthesized audio
      }

      setMessages((prev) => [...prev, aiMsg])
      console.log('✅ AI message added to chat')

      // Play audio response if available
      if (data.audio_url && audioElementRef.current) {
        console.log('🔊 Playing audio response...')
        audioElementRef.current.src = data.audio_url
        audioElementRef.current.play()
        setIsPlaying(true)
      }
    } catch (err) {
      console.error('❌ Failed to get AI response:', err)
      alert('Failed to get AI response. Please try again.')
    }
  }

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
    if (streamRef.current) {
      streamRef.current.getAudioTracks().forEach(track => {
        track.enabled = !isMuted
      })
    }
  }

  const handleToggleVideo = () => {
    setIsVideoOff(!isVideoOff)
  }

  const handleToggleChat = () => {
    setIsChatOpen(!isChatOpen)
  }

  const handleSendMessage = async () => {
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

    // Get AI response with audio synthesis
    await getAIResponseWithAudio(messageInput)
  }

  const handleEndCall = async () => {
    if (callData) {
      setCallData({ ...callData, status: 'completed' })

      // Stop recording if active
      if (isRecording) {
        stopRecording()
      }

      // Clean up audio resources
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
      }

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
        <title>Call Center - Active Call with Audio</title>
        <meta name="description" content="Active call with audio support" />
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

            {/* Microphone Audio Level */}
            <div className="mb-8 flex flex-col items-center">
              <div className="text-6xl mb-4">🎙️</div>
              <div className="flex items-center gap-1 bg-black/40 px-4 py-2 rounded-lg">
                {[...Array(20)].map((_, i) => (
                  <div
                    key={i}
                    className={`h-1 w-1 rounded-full transition-all ${
                      audioLevel > i * 6 ? 'bg-green-500' : 'bg-white/20'
                    }`}
                  ></div>
                ))}
              </div>
              <div className="text-white/60 text-xs mt-2">
                {isRecording ? 'Recording...' : 'Microphone Ready'}
              </div>
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

            {/* Recording Controls */}
            <div className="flex gap-4 mb-8">
              {isRecording ? (
                <button
                  onClick={stopRecording}
                  className="px-6 py-3 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
                >
                  <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>
                  Stop Recording
                </button>
              ) : (
                <button
                  onClick={startRecording}
                  className="px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
                >
                  🎤 Start Recording
                </button>
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

        {/* Hidden audio element for playback */}
        <audio ref={audioElementRef} onEnded={() => setIsPlaying(false)} />
      </div>
    </>
  )
}
