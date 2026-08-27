import { apiClient } from "../../../shared/api/client";

export type LLMConfig = {
  provider: string;
  model: string;
  temperature: number;
  max_tokens: number;
  context_window: number;
  timeout_seconds: number;
  max_retries: number;
  label: string | null;
  api_key_configured: boolean;
  status: string;
};

export type EmbeddingConfig = {
  provider: string;
  model: string;
  model_version: string;
  dimensions: number;
  distance_method: string;
  index_compatible: boolean;
  batch_size: number;
  timeout_seconds: number;
  label: string | null;
  api_key_configured: boolean;
  status: string;
};

export type RetrievalConfig = {
  top_k_candidates: number;
  final_top_k: number;
  similarity_threshold: number;
  dense_weight: number;
  sparse_weight: number;
  rerank_enabled: boolean;
  rerank_top_k: number;
  exact_id_boost: boolean;
  min_evidence_tokens: number;
  status: string;
};

export type ChunkingConfig = {
  strategy: string;
  target_chunk_tokens: number;
  min_chunk_tokens: number;
  max_chunk_tokens: number;
  overlap_tokens: number;
  table_as_unit: boolean;
  procedure_grouping: boolean;
  status: string;
};

export type ActivationResponse = {
  status: string;
  requires_reindex: boolean;
  reindex_reasons: string[];
};

export type ConnectivityResponse = {
  category: string;
  status: string;
  model: string;
  latency_ms: number;
};

export type LLMConfigUpdate = Partial<LLMConfig> & {
  provider: string;
  model: string;
  endpoint?: string;
  api_key?: string;
  api_key_env_var?: string;
};

export type EmbeddingConfigUpdate = Partial<EmbeddingConfig> & {
  provider: string;
  model: string;
  model_version: string;
  dimensions: number;
  index_compat_id: string;
  endpoint?: string;
  api_key?: string;
  api_key_env_var?: string;
  confirm_reindex?: boolean;
};

export async function getLLMConfig(): Promise<LLMConfig> {
  return apiClient.request<LLMConfig>("/config/llm");
}

export async function getEmbeddingConfig(): Promise<EmbeddingConfig> {
  return apiClient.request<EmbeddingConfig>("/config/embedding");
}

export async function getRetrievalConfig(): Promise<RetrievalConfig> {
  return apiClient.request<RetrievalConfig>("/config/retrieval");
}

export async function getChunkingConfig(): Promise<ChunkingConfig> {
  return apiClient.request<ChunkingConfig>("/config/chunking");
}

export async function updateLLMConfig(payload: LLMConfigUpdate): Promise<ActivationResponse> {
  return apiClient.request<ActivationResponse>("/config/llm", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function updateEmbeddingConfig(payload: EmbeddingConfigUpdate): Promise<ActivationResponse> {
  return apiClient.request<ActivationResponse>("/config/embedding", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function updateRetrievalConfig(payload: Partial<RetrievalConfig>): Promise<ActivationResponse> {
  return apiClient.request<ActivationResponse>("/config/retrieval", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function updateChunkingConfig(payload: Partial<ChunkingConfig> & { confirm_reindex?: boolean }): Promise<ActivationResponse> {
  return apiClient.request<ActivationResponse>("/config/chunking", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function validateLLMConfig(payload: LLMConfigUpdate): Promise<ConnectivityResponse> {
  return apiClient.request<ConnectivityResponse>("/config/llm/validate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function validateEmbeddingConfig(payload: EmbeddingConfigUpdate): Promise<ConnectivityResponse> {
  return apiClient.request<ConnectivityResponse>("/config/embedding/validate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}
