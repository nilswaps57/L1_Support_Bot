import { apiClient } from "./client";

export type HealthResponse = {
  status: "healthy" | "degraded";
  version: string;
  database: "available" | "unavailable";
  vector_store: "available" | "unavailable";
  llm: "available" | "unavailable";
  embedding: "available" | "unavailable";
  degraded_capabilities: string[];
  capabilities: Record<string, boolean>;
};

export async function getHealth(): Promise<HealthResponse> {
  return apiClient.request<HealthResponse>("/health");
}
