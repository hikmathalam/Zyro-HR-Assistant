export interface SourceCitation {
  file: string;
  page: string;
  snippet?: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceCitation[];
  isRefusal?: boolean;
  timestamp: string;
}

export interface ChatRequest {
  question: string;
  session_id?: string;
}

export interface ChatResponse {
  answer: string;
  sources: SourceCitation[];
  is_refusal: boolean;
}

export interface HealthResponse {
  status: string;
  app_name: string;
  version: string;
  index_loaded: boolean;
  total_indexed_chunks: number;
  groq_configured: boolean;
  model: string;
}

export interface Conversation {
  id: string;
  title: string;
  updatedAt: string;
  messages: Message[];
}

