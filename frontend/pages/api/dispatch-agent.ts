import type { NextApiRequest, NextApiResponse } from 'next'
import { RoomServiceClient, CreateIngressOptions } from 'livekit-server-sdk'

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

    // Create RoomService client
    const roomService = new RoomServiceClient(livekitUrl, apiKey, apiSecret)

    // Create a participant for the agent
    // The agent worker will automatically pick this up
    try {
      await roomService.updateRoomMetadata(roomName, JSON.stringify({
        agent_requested: true,
        timestamp: Date.now(),
        capabilities: ['voice', 'vision', 'tools'],
        language: 'ar'
      }))

      console.log('✅ Agent metadata updated, worker should pick up the job')

      return res.status(200).json({
        success: true,
        message: 'Agent dispatch requested'
      })
    } catch (error: any) {
      console.error('❌ Failed to update room metadata:', error)
      return res.status(500).json({ error: error.message })
    }

  } catch (error: any) {
    console.error('❌ Error dispatching agent:', error)
    return res.status(500).json({ error: error.message || 'Internal server error' })
  }
}
