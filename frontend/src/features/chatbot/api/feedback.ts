import { apiClient } from "../../../shared/api/client";

export type FeedbackRating = "helpful" | "not_helpful";

export type FeedbackResponse = {
  feedback_id: string;
};

export async function submitFeedback(
  sessionId: string,
  answerId: string,
  rating: FeedbackRating,
  comment?: string,
): Promise<FeedbackResponse> {
  return apiClient.request<FeedbackResponse>("/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      answer_id: answerId,
      rating,
      ...(comment ? { comment } : {}),
    }),
  });
}