'use client'

import Head from 'next/head'
import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/router'
import { Room, RoomEvent, Track, RemoteTrack, RemoteParticipant } from 'livekit-client'
import ControlBar from '../components/ControlBar'
import ChatPanel from '../components/ChatPanel'

// API Configuration - works in both development and production
const LIVEKIT_URL = process.env.NEXT_PUBLIC_LIVEKIT_URL || 'ws://localhost:7880'
console.log(`📡 LiveKit URL: ${LIVEKIT_URL}`)

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
  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(true)
  const [connectionError, setConnectionError] = useState<string | null>(null)
  const [isAgentReady, setIsAgentReady] = useState(false)
  const [audioLevel, setAudioLevel] = useState(0)

  // LiveKit refs
  const roomRef = useRef<Room | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const audioElementsRef = useRef<HTMLAudioElement[]>([])

  // Timer effect
  useEffect(() => {
    const interval = setInterval(() => {
      if (callData) {
        setCallData(prev => prev ? { ...prev, duration: prev.duration + 1 } : null)
      }
    }, 1000)

    return () => clearInterval(interval)
  }, [callData])

  // Connect to LiveKit
  useEffect(() => {
    if (!room) {
      console.log('⏳ Waiting for room parameter...')
      return
    }

    let liveKitRoom: Room | null = null
    let isConnecting = false

    const connectToLiveKit = async () => {
      // Prevent duplicate connections
      if (isConnecting || roomRef.current) {
        console.log('⚠️ Already connecting or connected, skipping...')
        return
      }

      try {
        isConnecting = true
        console.log('🔌 Connecting to LiveKit...')
        setIsConnecting(true)
        setConnectionError(null)

        // Initialize call data
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

        // Initialize audio context for microphone level monitoring
        initializeAudioContext()

        // Create room
        liveKitRoom = new Room({
          adaptiveStream: true,
          dynacast: true,
          videoCaptureDefaults: {
            resolution: {
              width: 1280,
              height: 720,
              frameRate: 30,
            },
          },
        })

        roomRef.current = liveKitRoom

        // Set up event listeners
        liveKitRoom.on(RoomEvent.Connected, async () => {
          console.log('✅ Connected to LiveKit room:', liveKitRoom?.name)
          setIsConnected(true)
          setIsConnecting(false)

          // Enable microphone after connection is established
          try {
            if (!liveKitRoom) return

            console.log('🎤 Enabling microphone...')
            await liveKitRoom.localParticipant.setMicrophoneEnabled(true)

            // Dispatch agent to the room
            console.log('🚀 Dispatching agent to room...')
            try {
              const dispatchResponse = await fetch('/api/dispatch-agent', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                  roomName: liveKitRoom.name,
                }),
              })

              if (!dispatchResponse.ok) {
                const error = await dispatchResponse.json()
                console.error('❌ Failed to dispatch agent:', error)
              } else {
                console.log('✅ Agent dispatch request sent')
              }
            } catch (error) {
              console.error('❌ Error dispatching agent:', error)
            }

            console.log('⏳ Waiting for AI agent to join...')
          } catch (error) {
            console.error('❌ Failed to enable microphone:', error)
          }
        })

        liveKitRoom.on(RoomEvent.Disconnected, () => {
          console.log('❌ Disconnected from room')
          setIsConnected(false)
        })

        liveKitRoom.on(RoomEvent.ParticipantConnected, (participant: RemoteParticipant) => {
          console.log('👥 Participant joined:', participant.identity)
          if (participant.identity.includes('agent')) {
            console.log('✅ AI Agent joined the room')
          }
        })

        liveKitRoom.on(RoomEvent.TrackSubscribed, (
          track: RemoteTrack,
          _publication: any,
          participant: RemoteParticipant
        ) => {
          console.log('🎥 Track subscribed:', track.kind, 'from', participant.identity)

          if (track.kind === Track.Kind.Audio) {
            // Attach remote audio and add to DOM
            const audioElement = track.attach()
            audioElement.autoplay = true
            audioElement.volume = 1.0
            audioElement.setAttribute('playsinline', 'true')
            document.body.appendChild(audioElement)
            audioElementsRef.current.push(audioElement)

            // Explicitly play (handles autoplay restrictions)
            audioElement.play().then(() => {
              console.log('✅ Remote audio attached and playing')
              setIsAgentReady(true)
            }).catch((error) => {
              console.error('❌ Audio play failed:', error)
              console.log('ℹ️ Click anywhere on the page to enable audio')

              // Add click handler to enable audio on user interaction
              const enableAudio = () => {
                audioElement.play().then(() => {
                  console.log('✅ Audio enabled after user interaction')
                  document.removeEventListener('click', enableAudio)
                })
              }
              document.addEventListener('click', enableAudio, { once: true })
            })
          }
        })

        liveKitRoom.on(RoomEvent.TrackUnsubscribed, (track: RemoteTrack) => {
          console.log('Track unsubscribed:', track.kind)
          track.detach()
        })

        liveKitRoom.on(RoomEvent.DataReceived, (payload: Uint8Array, participant?: RemoteParticipant) => {
          const decoder = new TextDecoder()
          const message = decoder.decode(payload)

          // Filter out system messages (JSON data)
          try {
            const parsed = JSON.parse(message)
            if (parsed.message_type === 'system' || parsed.event_type) {
              console.log('🔧 System event:', parsed.event_type || parsed.message_type)
              return
            }
          } catch (e) {
            // Not JSON, it's a regular text message - continue
          }

          console.log('💬 Chat message from', participant?.identity, ':', message)

          // Add only user/assistant text messages to chat
          setMessages(prev => [...prev, {
            id: Date.now().toString(),
            role: participant?.identity.includes('agent') ? 'assistant' : 'user',
            content: message,
            timestamp: new Date(),
            userName: participant?.identity || 'Agent'
          }])
        })

        // Generate token and connect
        const token = await generateToken(room as string, user as string || 'customer')

        console.log('🔑 Connecting with token...')
        await liveKitRoom.connect(LIVEKIT_URL, token)
        console.log('⏳ Waiting for connection to be ready...')

      } catch (error: any) {
        console.error('❌ LiveKit connection error:', error)
        setConnectionError(error.message || 'Failed to connect')
        setIsConnecting(false)
        isConnecting = false
        alert(`Failed to connect to LiveKit: ${error.message}`)
      }
    }

    const generateToken = async (roomName: string, identity: string): Promise<string> => {
      // Call API endpoint to generate properly signed JWT token
      const response = await fetch('/api/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          roomName,
          identity,
        }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Failed to get token')
      }

      const data = await response.json()
      return data.token
    }

    connectToLiveKit()

    // Cleanup
    return () => {
      if (liveKitRoom) {
        liveKitRoom.disconnect()
      }
      // Remove all audio elements
      audioElementsRef.current.forEach(audio => {
        audio.pause()
        audio.remove()
      })
      audioElementsRef.current = []
    }
  }, [room, user])

  // Initialize audio context for microphone level monitoring
  const initializeAudioContext = async () => {
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

  const handleToggleMute = async () => {
    if (roomRef.current) {
      const enabled = roomRef.current.localParticipant.isMicrophoneEnabled
      await roomRef.current.localParticipant.setMicrophoneEnabled(!enabled)
      setIsMuted(enabled)
    }
  }

  const handleToggleVideo = () => {
    setIsVideoOff(!isVideoOff)
  }

  const handleToggleChat = () => {
    setIsChatOpen(!isChatOpen)
  }

  const handleSendMessage = async () => {
    if (!messageInput.trim() || !roomRef.current) return

    // Check if room is connected
    if (!isConnected || roomRef.current.state !== 'connected') {
      console.warn('⚠️ Cannot send message: Room not connected')
      return
    }

    const newMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: messageInput,
      timestamp: new Date(),
      userName: user as string || 'You'
    }

    setMessages(prev => [...prev, newMessage])

    // Send via LiveKit data channel
    try {
      const encoder = new TextEncoder()
      const data = encoder.encode(messageInput)
      await roomRef.current.localParticipant.publishData(data, { reliable: true })
      console.log('✅ Message sent:', messageInput)
    } catch (error) {
      console.error('❌ Failed to send message:', error)
    }

    setMessageInput('')
  }

  const handleEndCall = async () => {
    if (roomRef.current) {
      roomRef.current.disconnect()
    }
    router.push('/callcenter')
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
                <div className={`w-3 h-3 rounded-full animate-pulse ${
                  isConnected ? 'bg-green-500' : 'bg-yellow-500'
                }`}></div>
                <span className="text-white/80 text-sm font-medium">
                  {!isConnected && 'Connecting...'}
                  {isConnected && !isAgentReady && 'Waiting for agent...'}
                  {isConnected && isAgentReady && 'Connected'}
                </span>
              </div>
              <div className="w-px h-4 bg-white/20"></div>
              <span className="text-white font-mono text-sm">{formatDuration(callData.duration)}</span>
            </div>
          </div>

          {/* Call Display Area */}
          <div className="flex flex-col items-center justify-center flex-1">
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
                {isMuted ? 'Muted' : 'Microphone Ready'}
              </div>
            </div>

            {/* Call Info */}
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-white mb-2">
                {isAgentReady ? 'Agent Connected' : 'Call Center Voice'}
              </h2>
              <p className="text-white/60">
                {isConnecting ? 'Connecting to LiveKit...' : ''}
                {isConnected && !isAgentReady ? 'Waiting for agent to join...' : ''}
                {isConnected && isAgentReady ? 'You can speak now' : ''}
              </p>
            </div>

            {/* Connection Status */}
            {connectionError && (
              <div className="px-6 py-3 bg-red-500/20 rounded-lg border border-red-500/50 mb-8">
                <p className="text-red-200 text-sm">
                  Connection Error: {connectionError}
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
