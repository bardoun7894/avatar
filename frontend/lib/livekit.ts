/**
 * LiveKit Client Configuration and Utilities
 * Connects to Ornina AI Avatar backend
 */

import { Room, RoomEvent, VideoPresets, Track } from 'livekit-client'

export interface LiveKitConfig {
  url: string
  token: string
}

export interface ConnectionConfig {
  roomName: string
  userName: string
  apiUrl?: string
}

/**
 * Get LiveKit access token from backend
 */
export async function getLiveKitToken(config: ConnectionConfig): Promise<string> {
  const apiUrl = config.apiUrl || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  try {
    const response = await fetch(`${apiUrl}/api/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        room: config.roomName,
        identity: config.userName,
      }),
    })

    if (!response.ok) {
      throw new Error(`Failed to get token: ${response.statusText}`)
    }

    const data = await response.json()
    return data.token
  } catch (error) {
    console.error('Error getting LiveKit token:', error)
    throw error
  }
}

/**
 * Connect to LiveKit room with Ornina AI Avatar
 */
export async function connectToRoom(
  config: ConnectionConfig,
  callbacks?: {
    onConnected?: (room: Room) => void
    onDisconnected?: () => void
    onParticipantConnected?: (identity: string) => void
    onTrackSubscribed?: (track: Track) => void
  }
): Promise<Room> {
  const livekitUrl = process.env.NEXT_PUBLIC_LIVEKIT_URL

  if (!livekitUrl) {
    throw new Error('LiveKit URL not configured. Set NEXT_PUBLIC_LIVEKIT_URL in .env')
  }

  // Get access token
  const token = await getLiveKitToken(config)

  // Create room instance
  const room = new Room({
    adaptiveStream: true,
    dynacast: true,
    videoCaptureDefaults: {
      resolution: VideoPresets.h720.resolution,
    },
  })

  // Set up event listeners
  room.on(RoomEvent.Connected, () => {
    console.log('Connected to room:', room.name)
    callbacks?.onConnected?.(room)
  })

  room.on(RoomEvent.Disconnected, () => {
    console.log('Disconnected from room')
    callbacks?.onDisconnected?.()
  })

  room.on(RoomEvent.ParticipantConnected, (participant) => {
    console.log('Participant connected:', participant.identity)
    callbacks?.onParticipantConnected?.(participant.identity)
  })

  room.on(RoomEvent.TrackSubscribed, (track, publication, participant) => {
    console.log('Track subscribed:', track.kind, 'from', participant.identity)
    callbacks?.onTrackSubscribed?.(track)
  })

  room.on(RoomEvent.DataReceived, (payload, participant) => {
    const decoder = new TextDecoder()
    const message = decoder.decode(payload)
    console.log('Data received from', participant?.identity, ':', message)
  })

  // Connect to room
  await room.connect(livekitUrl, token)

  // Enable local audio and video
  await room.localParticipant.enableCameraAndMicrophone()

  return room
}

/**
 * Send text message through data channel
 */
export async function sendMessage(room: Room, message: string) {
  const encoder = new TextEncoder()
  const data = encoder.encode(message)
  await room.localParticipant.publishData(data, { reliable: true })
}

/**
 * Toggle microphone mute
 */
export async function toggleMicrophone(room: Room): Promise<boolean> {
  const isMuted = room.localParticipant.isMicrophoneEnabled
  await room.localParticipant.setMicrophoneEnabled(!isMuted)
  return !isMuted
}

/**
 * Toggle camera on/off
 */
export async function toggleCamera(room: Room): Promise<boolean> {
  const isCameraOn = room.localParticipant.isCameraEnabled
  await room.localParticipant.setCameraEnabled(!isCameraOn)
  return !isCameraOn
}

/**
 * Disconnect from room
 */
export async function disconnectFromRoom(room: Room) {
  await room.disconnect()
}
