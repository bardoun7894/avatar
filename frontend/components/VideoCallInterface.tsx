import { useEffect, useState, useRef } from 'react'
import { useRouter } from 'next/router'
import { Room, RoomEvent, Track, RemoteTrack, RemoteParticipant } from 'livekit-client'
import ChatPanel from './ChatPanel'
import ControlBar from './ControlBar'
import ParticipantThumbnail from './ParticipantThumbnail'
import CallInfo from './CallInfo'

interface VideoCallInterfaceProps {
  roomName: string
  userName: string
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  userName?: string
}

export default function VideoCallInterface({ roomName, userName }: VideoCallInterfaceProps) {
  const router = useRouter()
  const [messages, setMessages] = useState<Message[]>([])
  const [isMuted, setIsMuted] = useState(false)
  const [isVideoOff, setIsVideoOff] = useState(false)
  const [isChatOpen, setIsChatOpen] = useState(true)
  const [callDuration, setCallDuration] = useState(0)
  const [isRecording, setIsRecording] = useState(true)
  const [messageInput, setMessageInput] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(true)
  const [connectionError, setConnectionError] = useState<string | null>(null)

  // LiveKit refs
  const roomRef = useRef<Room | null>(null)
  const localVideoRef = useRef<HTMLVideoElement>(null)
  const remoteVideoRef = useRef<HTMLVideoElement>(null)
  const audioElementsRef = useRef<HTMLAudioElement[]>([])

  // Timer effect
  useEffect(() => {
    const interval = setInterval(() => {
      setCallDuration(prev => prev + 1)
    }, 1000)

    return () => clearInterval(interval)
  }, [])

  // Connect to LiveKit
  useEffect(() => {
    let room: Room | null = null
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

        // Get LiveKit token from backend
        const livekitUrl = process.env.NEXT_PUBLIC_LIVEKIT_URL
        if (!livekitUrl) {
          throw new Error('NEXT_PUBLIC_LIVEKIT_URL not configured')
        }

        console.log('📡 LiveKit URL:', livekitUrl)
        console.log('🏠 Room:', roomName)
        console.log('👤 User:', userName)

        // Create room
        room = new Room({
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

        roomRef.current = room

        // Set up event listeners
        room.on(RoomEvent.Connected, async () => {
          console.log('✅ Connected to LiveKit room:', room?.name)
          setIsConnected(true)
          setIsConnecting(false)

          // Enable camera and microphone after connection is established
          try {
            if (!room) return

            console.log('📹 Enabling camera and microphone...')
            await room.localParticipant.enableCameraAndMicrophone()

            // Attach local video
            const localVideoTrack = room.localParticipant.videoTrackPublications.values().next().value?.videoTrack
            if (localVideoTrack && localVideoRef.current) {
              localVideoTrack.attach(localVideoRef.current)
              console.log('✅ Local video attached')
            }

            // Note: Agent auto-joins in dev mode, no dispatch needed
            console.log('⏳ Waiting for AI agent to join...')
          } catch (error) {
            console.error('❌ Failed to enable camera/microphone:', error)
          }
        })

        room.on(RoomEvent.Disconnected, () => {
          console.log('❌ Disconnected from room')
          setIsConnected(false)
        })

        room.on(RoomEvent.ParticipantConnected, (participant: RemoteParticipant) => {
          console.log('👥 Participant joined:', participant.identity)
          // AI agent will send its own greeting message via voice/data channel
        })

        room.on(RoomEvent.TrackSubscribed, (
          track: RemoteTrack,
          publication: any,
          participant: RemoteParticipant
        ) => {
          console.log('🎥 Track subscribed:', track.kind, 'from', participant.identity)

          if (track.kind === Track.Kind.Video) {
            // Attach remote video (AI avatar) to video element
            if (remoteVideoRef.current) {
              track.attach(remoteVideoRef.current)
              console.log('✅ Remote video attached (AI Avatar)')
            }
          } else if (track.kind === Track.Kind.Audio) {
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

        room.on(RoomEvent.TrackUnsubscribed, (track: RemoteTrack) => {
          console.log('Track unsubscribed:', track.kind)
          track.detach()
        })

        room.on(RoomEvent.DataReceived, (payload: Uint8Array, participant?: RemoteParticipant) => {
          const decoder = new TextDecoder()
          const message = decoder.decode(payload)

          // Filter out system messages (JSON data from Tavus)
          try {
            const parsed = JSON.parse(message)
            // Skip Tavus system messages and conversation events
            if (parsed.message_type === 'system' || parsed.message_type === 'conversation' || parsed.event_type) {
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
            userName: participant?.identity || 'Unknown'
          }])
        })

        // Listen for transcriptions (speech-to-text)
        room.on(RoomEvent.TranscriptionReceived, (segments, participant, publication) => {
          console.log('📝 Transcription received:', segments)

          // Combine all segments into transcript text
          const transcriptText = segments.map(s => s.text).join(' ')

          if (!transcriptText || !transcriptText.trim()) {
            console.log('⏭️ Empty transcript, skipping')
            return
          }

          // Determine role based on participant
          const isAgent = participant?.identity?.includes('agent') || participant?.identity?.includes('tavus')
          const role = isAgent ? 'assistant' : 'user'
          const userName = participant?.identity || (isAgent ? 'Ornina AI' : 'You')

          // Check if this is a final transcript or partial update
          const isFinal = segments.some(s => s.final === true)
          console.log(`📝 ${isFinal ? 'FINAL' : 'PARTIAL'} ${role} transcript:`, transcriptText)

          setMessages(prev => {
            // Find if there's an existing message from this participant that's NOT finalized yet
            const lastMessageIndex = prev.length - 1
            const lastMessage = lastMessageIndex >= 0 ? prev[lastMessageIndex] : null

            // Check if the last message is from the same role and participant (ongoing speech)
            if (lastMessage && lastMessage.role === role && lastMessage.userName === userName && !lastMessage.id.includes('-final')) {
              // This is a continuation/update of the last message (partial transcript)
              if (!isFinal) {
                // Update the last message with new transcript (partial update for real-time feedback)
                console.log('🔄 Updating partial transcript')
                const updated = [...prev]
                updated[lastMessageIndex] = {
                  ...lastMessage,
                  content: transcriptText,
                  timestamp: new Date()
                }
                return updated
              } else {
                // Final version - replace with finalized content
                console.log('✅ Finalizing transcript')
                const updated = [...prev]
                updated[lastMessageIndex] = {
                  ...lastMessage,
                  id: `${lastMessage.id}-final`,
                  content: transcriptText,
                  timestamp: new Date()
                }
                return updated
              }
            } else if (isFinal) {
              // This is a new final message from a different participant or after silence
              console.log('✅ Adding new FINAL transcript')
              return [...prev, {
                id: `transcript-${Date.now()}-final`,
                role: role,
                content: transcriptText,
                timestamp: new Date(),
                userName: userName
              }]
            } else {
              // This is a new partial message starting
              console.log('📝 Starting new partial transcript')
              return [...prev, {
                id: `transcript-${Date.now()}`,
                role: role,
                content: transcriptText,
                timestamp: new Date(),
                userName: userName
              }]
            }
          })
        })

        // Generate token and connect
        // For now, use direct connection with room name
        // In production, get token from your backend API
        const token = await generateToken(roomName, userName)

        console.log('🔑 Connecting with token...')
        await room.connect(livekitUrl, token)
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
      if (room) {
        room.disconnect()
      }
      // Remove all audio elements
      audioElementsRef.current.forEach(audio => {
        audio.pause()
        audio.remove()
      })
      audioElementsRef.current = []
    }
  }, [roomName, userName])

  const formatDuration = (seconds: number) => {
    const hrs = Math.floor(seconds / 3600)
    const mins = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
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
      userName: userName
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

  const handleEndCall = () => {
    if (roomRef.current) {
      roomRef.current.disconnect()
    }
    router.push('/')
  }

  const toggleMute = async () => {
    if (roomRef.current) {
      const enabled = roomRef.current.localParticipant.isMicrophoneEnabled
      await roomRef.current.localParticipant.setMicrophoneEnabled(!enabled)
      setIsMuted(enabled)
    }
  }

  const toggleVideo = async () => {
    if (roomRef.current) {
      const enabled = roomRef.current.localParticipant.isCameraEnabled
      await roomRef.current.localParticipant.setCameraEnabled(!enabled)
      setIsVideoOff(!enabled)
    }
  }

  const toggleChat = () => {
    setIsChatOpen(!isChatOpen)
  }

  return (
    <div className="relative flex h-screen w-full flex-col items-center justify-center bg-gray-900 overflow-hidden">
      {/* Main video feed - AI Avatar */}
      <div className="absolute inset-0 z-0 h-full w-full">
        <video
          ref={remoteVideoRef}
          autoPlay
          playsInline
          className="w-full h-full object-cover"
        />

        {/* Placeholder when connecting or no AI video */}
        {(!isConnected || connectionError) && (
          <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-blue-600 to-purple-700">
            <div className="text-center text-white">
              {isConnecting && !connectionError ? (
                <>
                  <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-white mx-auto mb-4"></div>
                  <p className="text-xl font-semibold">جارٍ الاتصال بالذكاء الاصطناعي...</p>
                  <p className="text-sm text-white/80 mt-2">Connecting to AI Avatar...</p>
                </>
              ) : connectionError ? (
                <>
                  <div className="text-6xl mb-4">⚠️</div>
                  <p className="text-xl font-semibold mb-2">فشل الاتصال</p>
                  <p className="text-sm text-white/80">{connectionError}</p>
                  <button
                    onClick={() => window.location.reload()}
                    className="mt-4 px-6 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
                  >
                    إعادة المحاولة / Retry
                  </button>
                </>
              ) : (
                <>
                  <div className="w-32 h-32 rounded-full bg-white/20 backdrop-blur-lg flex items-center justify-center mb-4 mx-auto">
                    <span className="text-6xl">🤖</span>
                  </div>
                  <p className="text-2xl font-semibold">Ornina AI</p>
                  <p className="text-sm text-white/80 mt-2">انتظر ظهور الأفاتار...</p>
                </>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Overlay */}
      <div className="absolute inset-0 bg-black/10 z-10"></div>

      {/* Local video thumbnail (User) */}
      <ParticipantThumbnail
        userName={userName}
        isMuted={isMuted}
        videoRef={localVideoRef}
      />

      {/* Call info */}
      <CallInfo
        roomName={roomName}
        duration={formatDuration(callDuration)}
        isRecording={isRecording}
      />

      {/* Chat panel */}
      {isChatOpen && (
        <ChatPanel
          messages={messages}
          messageInput={messageInput}
          setMessageInput={setMessageInput}
          onSendMessage={handleSendMessage}
        />
      )}

      {/* Control bar */}
      <ControlBar
        isMuted={isMuted}
        isVideoOff={isVideoOff}
        isChatOpen={isChatOpen}
        onToggleMute={toggleMute}
        onToggleVideo={toggleVideo}
        onToggleChat={toggleChat}
        onEndCall={handleEndCall}
      />
    </div>
  )
}
