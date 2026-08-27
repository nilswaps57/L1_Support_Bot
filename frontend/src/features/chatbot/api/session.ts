import { apiClient } from "../../../shared/api/client";

export type ChatSession = {
  session_id: string;
  created_at: string;
  expires_at: string;
};

export function createChatSession(): Promise<ChatSession> {
  return apiClient.request<ChatSession>("/sessions", { method: "POST" });
}

export function clearChatSession(sessionId: string): Promise<void> {
  return apiClient.request<void>(`/sessions/${sessionId}`, { method: "DELETE" });
}