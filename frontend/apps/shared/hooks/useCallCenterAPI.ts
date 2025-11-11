import { useState, useCallback, useEffect, useRef } from 'react'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  timestamp: string
}

interface WebSocketMessage {
  type: string
  data: any
  timestamp: string
}

/**
 * Hook for managing Call Center API calls and WebSocket connections
 */
export function useCallCenterAPI() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const [wsConnected, setWsConnected] = useState(false)

  // Generic API call function
  const apiCall = useCallback(
    async <T,>(
      endpoint: string,
      method: 'GET' | 'POST' | 'PATCH' = 'GET',
      params?: Record<string, any>
    ): Promise<T | null> => {
      setLoading(true)
      setError(null)

      try {
        let url = `${API_BASE_URL}${endpoint}`

        // Add query parameters
        if (params && method === 'GET') {
          const queryString = new URLSearchParams(
            Object.entries(params).reduce((acc, [key, value]) => {
              if (value !== null && value !== undefined) {
                acc[key] = String(value)
              }
              return acc
            }, {} as Record<string, string>)
          ).toString()

          if (queryString) {
            url += `?${queryString}`
          }
        }

        const options: RequestInit = {
          method,
          headers: {
            'Content-Type': 'application/json',
          },
        }

        // Add params to URL for POST/PATCH
        if ((method === 'POST' || method === 'PATCH') && params) {
          const queryString = new URLSearchParams(
            Object.entries(params).reduce((acc, [key, value]) => {
              if (value !== null && value !== undefined) {
                acc[key] = String(value)
              }
              return acc
            }, {} as Record<string, string>)
          ).toString()

          if (queryString) {
            url += `?${queryString}`
          }
        }

        const response = await fetch(url, options)

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.error || `API error: ${response.status}`)
        }

        const data = await response.json()
        return data
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Unknown error'
        setError(message)
        console.error('API Error:', message)
        return null
      } finally {
        setLoading(false)
      }
    },
    []
  )

  // Call management
  const initiatecall = useCallback(
    (phoneNumber?: string, customerName?: string) =>
      apiCall('/api/calls', 'POST', { phone_number: phoneNumber, customer_name: customerName }),
    [apiCall]
  )

  const getActivecalls = useCallback(
    (status?: string) => apiCall('/api/calls', 'GET', { status }),
    [apiCall]
  )

  const getCall = useCallback((callId: string) => apiCall(`/api/calls/${callId}`), [apiCall])

  const updateCallStatus = useCallback(
    (callId: string, status: string) => apiCall(`/api/calls/${callId}/status`, 'POST', { status }),
    [apiCall]
  )

  const routeCall = useCallback(
    (callId: string, department: string) => apiCall(`/api/calls/${callId}/route`, 'POST', { department }),
    [apiCall]
  )

  const transferCall = useCallback(
    (callId: string, targetDepartment: string, agentId?: string) =>
      apiCall(`/api/calls/${callId}/transfer`, 'POST', { target_department: targetDepartment, agent_id: agentId }),
    [apiCall]
  )

  const endCall = useCallback(
    (callId: string) => apiCall(`/api/calls/${callId}/end`, 'POST'),
    [apiCall]
  )

  const getQueue = useCallback(() => apiCall('/api/calls/queue'), [apiCall])

  // Ticket management
  const createTicket = useCallback(
    (customerName: string, customerPhone: string, subject: string, description: string, callId?: string, priority?: string, department?: string) =>
      apiCall('/api/tickets', 'POST', {
        customer_name: customerName,
        customer_phone: customerPhone,
        subject,
        description,
        call_id: callId,
        priority: priority || 'medium',
        department: department || 'complaints',
      }),
    [apiCall]
  )

  const getTickets = useCallback(
    (status?: string, priority?: string, department?: string) =>
      apiCall('/api/tickets', 'GET', { status, priority, department }),
    [apiCall]
  )

  const getTicket = useCallback((ticketId: string) => apiCall(`/api/tickets/${ticketId}`), [apiCall])

  const updateTicket = useCallback(
    (ticketId: string, updates: { status?: string; priority?: string; notes?: string; assigned_to?: string }) =>
      apiCall(`/api/tickets/${ticketId}`, 'PATCH', updates),
    [apiCall]
  )

  // Customer management
  const getCustomers = useCallback(() => apiCall('/api/customers'), [apiCall])

  const getCustomer = useCallback((customerId: string) => apiCall(`/api/customers/${customerId}`), [apiCall])

  // Agent management
  const getAgents = useCallback((status?: string) => apiCall('/api/agents', 'GET', { status }), [apiCall])

  const getAgent = useCallback((agentId: string) => apiCall(`/api/agents/${agentId}`), [apiCall])

  const updateAgentStatus = useCallback(
    (agentId: string, status: string) => apiCall(`/api/agents/${agentId}/status`, 'PATCH', { status }),
    [apiCall]
  )

  // Transcript management
  const getTranscript = useCallback((callId: string) => apiCall(`/api/transcripts/${callId}`), [apiCall])

  const addTranscriptMessage = useCallback(
    (callId: string, speaker: string, content: string, language?: string) =>
      apiCall(`/api/transcripts/${callId}/messages`, 'POST', { speaker, content, language }),
    [apiCall]
  )

  // WebSocket connection
  const connectWebSocket = useCallback((onMessage: (data: WebSocketMessage) => void) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return
    }

    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsUrl = `${protocol}//${window.location.host.replace(':3000', ':8000')}/ws/updates`

      const ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        console.log('WebSocket connected')
        setWsConnected(true)
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          onMessage(data)
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setWsConnected(false)
      }

      ws.onclose = () => {
        console.log('WebSocket disconnected')
        setWsConnected(false)
      }

      wsRef.current = ws
    } catch (err) {
      console.error('Failed to connect WebSocket:', err)
      setWsConnected(false)
    }
  }, [])

  const disconnectWebSocket = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
      setWsConnected(false)
    }
  }, [])

  const sendWebSocketMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket is not connected')
    }
  }, [])

  // Cleanup
  useEffect(() => {
    return () => {
      disconnectWebSocket()
    }
  }, [disconnectWebSocket])

  return {
    // State
    loading,
    error,
    wsConnected,

    // Call management
    initiatecall,
    getActivecalls,
    getCall,
    updateCallStatus,
    routeCall,
    transferCall,
    endCall,
    getQueue,

    // Ticket management
    createTicket,
    getTickets,
    getTicket,
    updateTicket,

    // Customer management
    getCustomers,
    getCustomer,

    // Agent management
    getAgents,
    getAgent,
    updateAgentStatus,

    // Transcript management
    getTranscript,
    addTranscriptMessage,

    // WebSocket
    connectWebSocket,
    disconnectWebSocket,
    sendWebSocketMessage,
  }
}
