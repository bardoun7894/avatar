import type { NextApiRequest, NextApiResponse } from 'next'
import { WebSocketServer, WebSocket } from 'ws'
import https from 'https'
import http from 'http'

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  // Only allow WebSocket upgrade requests
  if (req.method !== 'GET') {
    res.setHeader('Allow', ['GET'])
    return res.status(405).json({ error: 'Method Not Allowed' })
  }

  // Check if this is a WebSocket upgrade request
  if (req.headers.upgrade !== 'websocket') {
    return res.status(400).json({ error: 'This endpoint only accepts WebSocket connections' })
  }

  // Get language from query parameter (default to 'en')
  const language = req.query.lang as string || 'en'
  
  // Create WebSocket server
  const wss = new WebSocketServer({ noServer: true })
  
  // Handle WebSocket connections
  wss.on('connection', (ws: WebSocket, request) => {
    console.log(`[Realtime] WebSocket connected for language: ${language}`)
    
    // Initialize OpenAI Realtime API connection
    let openaiWs: WebSocket | null = null
    
    try {
      // Connect to OpenAI Realtime API
      const openaiUrl = 'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01'
      openaiWs = new WebSocket(openaiUrl, {
        headers: {
          'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
          'OpenAI-Beta': 'realtime=v1'
        }
      })
      
      // Handle OpenAI connection
      openaiWs.on('open', () => {
        console.log('[Realtime] Connected to OpenAI Realtime API')
        
        // Configure session based on language
        const sessionConfig = {
          type: 'session.update',
          session: {
            modalities: ['text', 'audio'],
            instructions: language === 'ar' 
              ? 'أنت مساعد ذكاء اصطناعي لخدمة العملاء من شركة أورنينا. تحدث باللغة العربية بطريقة ودودة واحترافية.'
              : 'You are a helpful AI assistant from Ornina company. Speak in a friendly and professional manner.',
            voice: 'alloy',
            input_audio_format: 'pcm16',
            output_audio_format: 'pcm16',
            input_audio_transcription: {
              model: 'whisper-1'
            },
            turn_detection: {
              type: 'server_vad',
              threshold: 0.5,
              prefix_padding_ms: 300,
              silence_duration_ms: 200
            },
            tools: [],
            tool_choice: 'auto',
            temperature: 0.8,
            max_response_output_tokens: 4096
          }
        }
        
        openaiWs?.send(JSON.stringify(sessionConfig))
        
        // Send initial response creation event
        openaiWs?.send(JSON.stringify({
          type: 'response.create',
          response: {
            modalities: ['text', 'audio'],
            instructions: language === 'ar' 
              ? 'أرحب بالمستخدم وقدم نفسك كمساعد أورنينا.'
              : 'Greet the user and introduce yourself as an Ornina assistant.'
          }
        }))
      })
      
      // Handle messages from OpenAI
      openaiWs.on('message', (data) => {
        try {
          const message = JSON.parse(data.toString())
          console.log('[Realtime] Received from OpenAI:', message.type)
          
          // Forward to client
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(data.toString())
          }
        } catch (error) {
          console.error('[Realtime] Error parsing OpenAI message:', error)
        }
      })
      
      // Handle OpenAI connection errors
      openaiWs.on('error', (error) => {
        console.error('[Realtime] OpenAI WebSocket error:', error)
        ws.close(1011, 'OpenAI connection error')
      })
      
      // Handle OpenAI connection close
      openaiWs.on('close', () => {
        console.log('[Realtime] OpenAI WebSocket closed')
        ws.close(1000, 'OpenAI connection ended')
      })
      
      // Handle client messages
      ws.on('message', (data) => {
        try {
          const message = JSON.parse(data.toString())
          console.log('[Realtime] Received from client:', message.type)
          
          // Handle special client events
          if (message.type === 'connection.initializing') {
            // Respond with connection ready
            ws.send(JSON.stringify({
              type: 'connection.ready',
              timestamp: Date.now()
            }))
          } else if (message.type === 'audio.input') {
            // Forward audio to OpenAI
            if (openaiWs?.readyState === WebSocket.OPEN) {
              openaiWs.send(JSON.stringify({
                type: 'input_audio_buffer.append',
                audio: message.audio
              }))
            }
          } else {
            // Forward other messages to OpenAI
            if (openaiWs?.readyState === WebSocket.OPEN) {
              openaiWs.send(data.toString())
            }
          }
        } catch (error) {
          console.error('[Realtime] Error parsing client message:', error)
        }
      })
      
      // Handle client connection errors
      ws.on('error', (error) => {
        console.error('[Realtime] Client WebSocket error:', error)
        openaiWs?.close()
      })
      
      // Handle client connection close
      ws.on('close', () => {
        console.log('[Realtime] Client WebSocket closed')
        openaiWs?.close()
      })
      
      // Handle ping/pong for connection health
      ws.on('ping', () => {
        ws.pong()
      })
      
    } catch (error) {
      console.error('[Realtime] Error setting up OpenAI connection:', error)
      ws.close(1011, 'Failed to connect to OpenAI')
    }
  })
  
  // Upgrade the HTTP connection to WebSocket
  const socket = res.socket as any
  const server = socket?.server as http.Server | https.Server | undefined
  if (!server) {
    return res.status(500).json({ error: 'Server not available' })
  }
  
  server.emit('upgrade', req, socket, Buffer.alloc(0))
  
  // Handle the upgrade
  wss.handleUpgrade(req, req.socket as any, Buffer.alloc(0), (ws) => {
    wss.emit('connection', ws, req)
  })
}


