import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  // Only allow GET requests for health check
  if (req.method !== 'GET') {
    res.setHeader('Allow', ['GET'])
    return res.status(405).json({ error: 'Method Not Allowed' })
  }

  try {
    // Check if required environment variables are set
    const livekitUrl = process.env.NEXT_PUBLIC_LIVEKIT_URL
    const openaiKey = process.env.OPENAI_API_KEY
    
    const healthStatus = {
      status: 'ok',
      timestamp: new Date().toISOString(),
      services: {
        livekit: {
          configured: !!livekitUrl,
          url: livekitUrl || 'not configured'
        },
        openai: {
          configured: !!openaiKey,
          key: openaiKey ? 'configured' : 'not configured'
        }
      }
    }

    res.status(200).json(healthStatus)
  } catch (error) {
    console.error('Health check error:', error)
    res.status(500).json({
      status: 'error',
      message: 'Health check failed',
      error: error instanceof Error ? error.message : 'Unknown error'
    })
  }
}


