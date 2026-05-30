import type {
  ChatResponse,
  HealthResponse,
  MemoryClearResponse,
  MemoryListResponse,
  Mode,
  ProviderSettings,
  ProviderSettingsPayload,
  UploadResponse,
} from '../types/api'

export class ApiClientError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiClientError'
    this.status = status
  }
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    const message = body.detail || body.error?.message || `HTTP ${response.status}`
    throw new ApiClientError(message, response.status)
  }
  return response.json() as Promise<T>
}

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch('/api/health')
  return parseResponse<HealthResponse>(response)
}

export async function uploadImage(file: File): Promise<UploadResponse> {
  const form = new FormData()
  form.append('file', file)
  const response = await fetch('/api/upload', {
    method: 'POST',
    body: form,
  })
  return parseResponse<UploadResponse>(response)
}

export async function runChat(message: string, mode: Mode, imagePath?: string | null): Promise<ChatResponse> {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      mode,
      image_path_or_url: imagePath || null,
    }),
  })
  return parseResponse<ChatResponse>(response)
}

export async function getProviderSettings(): Promise<ProviderSettings> {
  const response = await fetch('/api/settings')
  return parseResponse<ProviderSettings>(response)
}

export async function saveProviderSettings(payload: ProviderSettingsPayload): Promise<ProviderSettings> {
  const response = await fetch('/api/settings', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  return parseResponse<ProviderSettings>(response)
}

export async function getMemory(limit = 50): Promise<MemoryListResponse> {
  const response = await fetch(`/api/memory?limit=${encodeURIComponent(limit)}`)
  return parseResponse<MemoryListResponse>(response)
}

export async function clearMemory(): Promise<MemoryClearResponse> {
  const response = await fetch('/api/memory', {
    method: 'DELETE',
  })
  return parseResponse<MemoryClearResponse>(response)
}
