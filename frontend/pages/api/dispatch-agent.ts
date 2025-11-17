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

    // Note: The agent worker auto-joins rooms, so this endpoint is optional.
    // We'll try to dispatch, but if it fails due to network issues, that's okay.
    
    console.log('ℹ️  Agent will auto-join room based on room creation')
    console.log('ℹ️  Optional: Attempting to dispatch via LiveKit API...')

    // Create RoomService client with shorter timeout
    const roomService = new RoomServiceClient(httpUrl, apiKey, apiSecret)

    // Try to update room metadata (non-critical - agent auto-joins anyway)
    try {
      const metadataPromise = roomService.updateRoomMetadata(roomName, JSON.stringify({
        agent_requested: true,
        timestamp: Date.now(),
        capabilities: ['voice', 'vision', 'tools'],
        language: 'ar'
      }))

      // Set a 5-second timeout
      const timeoutPromise = new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Metadata update timeout')), 5000)
      )

      await Promise.race([metadataPromise, timeoutPromise])
      console.log('✅ Agent metadata updated')

    } catch (metadataError: any) {
      console.warn('⚠️  Metadata update failed (agent will still auto-join):', metadataError.message)
    }

    // Try to dispatch job (non-critical - agent auto-joins anyway)
    try {
      const jobPromise = fetch(`${httpUrl}/api/agent/jobs`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          room: roomName,
          participant: 'agent',
        })
      })

      // Set a 5-second timeout
      const timeoutPromise = new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Job dispatch timeout')), 5000)
      )

      const response: any = await Promise.race([jobPromise, timeoutPromise])

      if (response.ok) {
        const jobData = await response.json()
        console.log('✅ Agent job created:', jobData)
      } else {
        console.warn('⚠️  Job dispatch failed (agent will still auto-join)')
      }
    } catch (jobError: any) {
      console.warn('⚠️  Job dispatch failed (agent will still auto-join):', jobError.message)
    }

    // Always return success - the agent will auto-join
    return res.status(200).json({
      success: true,
      message: 'Agent will join room automatically',
      note: 'The LiveKit agent worker monitors for new rooms and auto-joins'
    })

  } catch (error: any) {
    console.error('❌ Error dispatching agent:', error)
    return res.status(500).json({ error: error.message || 'Internal server error' })
  }
}
