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

  // Use environment variables or fallback to hardcoded values for production
  const apiKey = process.env.LIVEKIT_API_KEY || 'APIJL8zayDiwTwV'
  const apiSecret = process.env.LIVEKIT_API_SECRET || 'fYtfW6HKKiaqxAcEhmRR4OTjZcyJbfWov4Bi9ezUvfFA'

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
    const livekitUrl = process.env.LIVEKIT_URL || process.env.NEXT_PUBLIC_LIVEKIT_URL || 'wss://tavus-agent-project-i82x78jc.livekit.cloud'
    return res.status(200).json({ 
      token,
      livekit_url: livekitUrl 
    })
  } catch (error: any) {
    console.error('Token generation error:', error)
    return res.status(500).json({ error: 'Failed to generate token' })
  }
}
