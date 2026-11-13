import { ChatRequest, ChatResponse, HealthResponse } from '@/types/chat';

// Default to production Render backend URL if environment variable is not defined
const RAW_API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://zyro-hr-backend.onrender.com';

// Ensure no trailing slash
export const API_BASE_URL = RAW_API_URL.replace(/\/+$/, '');

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Server error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`, {
    cache: 'no-store',
  });

  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status}`);
  }

  return response.json();
}
