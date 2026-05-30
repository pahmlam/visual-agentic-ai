export type Mode = 'auto' | 'research' | 'vision'
export type Provider = 'ollama' | 'openai' | 'gemini'

export interface HealthResponse {
  status: string
  llm_provider: Provider
  vlm_provider: Provider
  text_model: string
  vision_model: string
  yolo_model_path: string
  yolo_model_exists: boolean
}

export interface ProviderSettings {
  llm_provider: Provider
  vlm_provider: Provider
  ollama_text_model: string
  ollama_vision_model: string
  openai_text_model: string
  openai_vision_model: string
  gemini_text_model: string
  gemini_vision_model: string
  has_openai_api_key: boolean
  has_gemini_api_key: boolean
}

export interface ProviderSettingsPayload {
  llm_provider: Provider
  vlm_provider: Provider
  ollama_text_model: string
  ollama_vision_model: string
  openai_text_model: string
  openai_vision_model: string
  gemini_text_model: string
  gemini_vision_model: string
  openai_api_key?: string
  gemini_api_key?: string
}

export interface UploadResponse {
  file_name: string
  path: string
  url: string
}

export interface ChatResponse {
  route: string
  answer: string
  sources: Record<string, string>
  artifacts: {
    image_path_or_url?: string
    counts?: Record<string, number>
    detections?: DetectionItem[]
    annotated_url?: string | null
    memory_used?: MemoryEntry[]
    memory_error?: string
    [key: string]: unknown
  }
}

export interface DetectionItem {
  label: string
  confidence: number
  bbox: [number, number, number, number]
}

export interface MemoryEntry {
  id: string
  created_at: string
  user_message: string
  route: string
  answer: string
  sources: Record<string, string>
  artifacts_summary: Record<string, unknown>
}

export interface MemoryListResponse {
  items: MemoryEntry[]
}

export interface MemoryClearResponse {
  deleted: number
}
