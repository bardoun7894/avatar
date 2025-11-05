import type { NextApiRequest, NextApiResponse } from 'next'
import { AccessToken } from 'livekit-server-sdk'

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const { roomName, identity } = req.body

  if (!roomName || !identity) {
    return res.status(400).json({ error: 'Missing roomName or identity' })
  }

  const apiKey = process.env.LIVEKIT_API_KEY
  const apiSecret = process.env.LIVEKIT_API_SECRET

  if (!apiKey || !apiSecret) {
    return res.status(500).json({ error: 'LiveKit credentials not configured' })
  }

  try {
    const at = new AccessToken(apiKey, apiSecret, {
      identity,
      ttl: '1h',
    })

    at.addGrant({
      room: roomName,
      roomJoin: true,
      canPublish: true,
      canSubscribe: true,
      canPublishData: true,
    })

    const token = await at.toJwt()
    return res.status(200).json({ token })
  } catch (error: any) {
    console.error('Token generation error:', error)
    return res.status(500).json({ error: 'Failed to generate token' })
  }
}
