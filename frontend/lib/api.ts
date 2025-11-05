/**
 * API utilities for communicating with Ornina backend
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
}

/**
 * Get conversation history
 */
export async function getConversationHistory(conversationId: string): Promise<ApiResponse> {
  try {
    const response = await fetch(`${API_URL}/api/conversations/${conversationId}`)
    const data = await response.json()
    return { success: true, data }
  } catch (error) {
    console.error('Error fetching conversation:', error)
    return { success: false, error: 'Failed to fetch conversation' }
  }
}

/**
 * Get all conversations
 */
export async function getConversations(): Promise<ApiResponse> {
  try {
    const response = await fetch(`${API_URL}/api/conversations`)
    const data = await response.json()
    return { success: true, data }
  } catch (error) {
    console.error('Error fetching conversations:', error)
    return { success: false, error: 'Failed to fetch conversations' }
  }
}

/**
 * Search knowledge base
 */
export async function searchKnowledgeBase(query: string): Promise<ApiResponse> {
  try {
    const response = await fetch(`${API_URL}/api/knowledge-base/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    })
    const data = await response.json()
    return { success: true, data }
  } catch (error) {
    console.error('Error searching knowledge base:', error)
    return { success: false, error: 'Failed to search knowledge base' }
  }
}

/**
 * Get company services
 */
export async function getServices(): Promise<ApiResponse> {
  try {
    const response = await fetch(`${API_URL}/api/services`)
    const data = await response.json()
    return { success: true, data }
  } catch (error) {
    console.error('Error fetching services:', error)
    return { success: false, error: 'Failed to fetch services' }
  }
}

/**
 * Get training programs
 */
export async function getTrainingPrograms(): Promise<ApiResponse> {
  try {
    const response = await fetch(`${API_URL}/api/training`)
    const data = await response.json()
    return { success: true, data }
  } catch (error) {
    console.error('Error fetching training programs:', error)
    return { success: false, error: 'Failed to fetch training programs' }
  }
}
