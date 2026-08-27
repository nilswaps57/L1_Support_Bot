import { apiClient } from "../../../shared/api/client";

export type ChatCitation = {
  chunk_id: string;
  document_id: string;
  document_name: string;
  page_number: number | null;
  section: string | null;
  task_code: string | null;
};

export type ChatResponse = {
  session_id: string;
  question: string;
  answer_text: string;
  answer_type: string;
  citations: ChatCitation[];
  insufficient_information: boolean;
  model_used: string | null;
};

export async function askChat(sessionId: string, question: string): Promise<ChatResponse> {
  return apiClient.request<ChatResponse>("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, question }),
  });
}
