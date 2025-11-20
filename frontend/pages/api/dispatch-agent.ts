import type { NextApiRequest, NextApiResponse } from 'next'
import { RoomServiceClient } from 'livekit-server-sdk'

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    const { roomName } = req.body

    if (!roomName) {
      return res.status(400).json({ error: 'Room name is required' })
    }

    const livekitUrl = process.env.NEXT_PUBLIC_LIVEKIT_URL
    const apiKey = process.env.LIVEKIT_API_KEY
    const apiSecret = process.env.LIVEKIT_API_SECRET

    if (!livekitUrl || !apiKey || !apiSecret) {
      return res.status(500).json({ error: 'LiveKit credentials not configured' })
    }

    console.log('🚀 Dispatching agent to room:', roomName)

    // Convert WebSocket URL to HTTP URL for RoomServiceClient
    const httpUrl = livekitUrl.replace('wss://', 'https://').replace('ws://', 'http://')
    console.log('🔗 Using LiveKit HTTP URL:', httpUrl)

    // Note: LiveKit Cloud doesn't support /api/agent/jobs endpoint
    // The agent worker auto-joins rooms based on room creation
    console.log('ℹ️  Agent will auto-join room based on room creation')

    // Create RoomService client
    const roomService = new RoomServiceClient(httpUrl, apiKey, apiSecret)

    // Update room metadata (helps agent identify capabilities needed)
    try {
      const metadataPromise = roomService.updateRoomMetadata(roomName, JSON.stringify({
        agent_requested: true,
        timestamp: Date.now(),
        capabilities: ['voice', 'vision', 'tools'],
        language: 'ar'
      }))

      // Set a 3-second timeout for metadata update
      const timeoutPromise = new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Metadata update timeout')), 3000)
      )

      await Promise.race([metadataPromise, timeoutPromise])
      console.log('✅ Agent metadata updated')

    } catch (metadataError: any) {
      // This is non-critical - agent will still auto-join based on room creation
      console.log('ℹ️  Metadata update skipped (agent will still auto-join)')
    }

    // Always return success - the agent auto-joins when room is created
    return res.status(200).json({
      success: true,
      message: 'Agent will join room automatically',
      note: 'LiveKit agent worker monitors for new rooms and auto-joins'
    })

  } catch (error: any) {
    console.error('❌ Error dispatching agent:', error)
    return res.status(500).json({ error: error.message || 'Internal server error' })
  }
}
