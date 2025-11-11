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

    // Create RoomService client
    const roomService = new RoomServiceClient(livekitUrl, apiKey, apiSecret)

    // Dispatch agent to the room using the jobs API
    try {
      // Update room metadata
      await roomService.updateRoomMetadata(roomName, JSON.stringify({
        agent_requested: true,
        timestamp: Date.now(),
        capabilities: ['voice', 'vision', 'tools'],
        language: 'ar'
      }))

      console.log('✅ Agent metadata updated')

      // Dispatch a job to the agent worker
      // This triggers the agent's entrypoint function
      try {
        const response = await fetch(`${livekitUrl.replace('wss://', 'https://').replace('ws://', 'http://')}/api/agent/jobs`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            room: roomName,
            participant: 'agent',  // The agent will join as this participant
          })
        })

        if (!response.ok) {
          console.warn('⚠️  Job dispatch may have failed, but continuing with metadata update')
        } else {
          const jobData = await response.json()
          console.log('✅ Agent job created:', jobData)
        }
      } catch (jobError) {
        console.warn('⚠️  Could not dispatch job directly, relying on metadata:', jobError)
      }

      return res.status(200).json({
        success: true,
        message: 'Agent dispatch requested'
      })
    } catch (error: any) {
      console.error('❌ Failed to dispatch agent:', error)
      return res.status(500).json({ error: error.message })
    }

  } catch (error: any) {
    console.error('❌ Error dispatching agent:', error)
    return res.status(500).json({ error: error.message || 'Internal server error' })
  }
}
