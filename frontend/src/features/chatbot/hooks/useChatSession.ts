import { useEffect, useState } from "react";

import { ApiClientError } from "../../../shared/api/client";
import { askChat, type ChatResponse } from "../api/chat";
import { submitFeedback as sendFeedback, type FeedbackRating } from "../api/feedback";
import { clearChatSession, createChatSession, type ChatSession } from "../api/session";
import type { ChatMessage } from "../components/MessageList";

const MAX_CLIENT_MESSAGES = 20;

function isExpiredSession(error: unknown): boolean {
  return error instanceof ApiClientError
    ? error.payload.error_code === "SESSION_NOT_FOUND"
    : Boolean(
        error &&
          typeof error === "object" &&
          "payload" in error &&
          (error as { payload?: { error_code?: string } }).payload?.error_code ===
            "SESSION_NOT_FOUND",
      );
}

export function useChatSession() {
  const [session, setSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionError, setSessionError] = useState<string>();
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);

  async function startNewSession() {
    setIsLoading(true);
    try {
      const nextSession = await createChatSession();
      setSession(nextSession);
      setMessages([]);
      setSessionError(undefined);
    } catch {
      setSession(null);
      setSessionError("A new chat session could not be started.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void startNewSession();
  }, []);

  async function send(question: string) {
    if (!session) return;
    setIsSending(true);
    try {
      const response: ChatResponse = await askChat(session.session_id, question);
      setMessages((current) => [
        ...current,
        {
          question,
          answerId: response.answer_id,
          answer: response.answer_text,
          answerType: response.answer_type,
          citations: response.citations,
        },
      ].slice(-MAX_CLIENT_MESSAGES));
    } catch (error) {
      if (isExpiredSession(error)) {
        setSession(null);
        setSessionError("Your chat session has expired. Start a new session to continue.");
        return;
      }
      setMessages((current) => [
        ...current,
        {
          question,
          error: error instanceof ApiClientError ? error.payload.message : "Answer generation is temporarily unavailable.",
          retry: () => void send(question),
        },
      ].slice(-MAX_CLIENT_MESSAGES));
    } finally {
      setIsSending(false);
    }
  }

  async function submitFeedback(answerId: string, rating: FeedbackRating, comment?: string) {
    if (!session) throw new Error("A chat session is not available.");
    await sendFeedback(session.session_id, answerId, rating, comment);
  }

  async function clear() {
    if (session) {
      try {
        await clearChatSession(session.session_id);
      } catch (error) {
        if (!isExpiredSession(error)) {
          setSessionError("The chat session could not be cleared.");
          return;
        }
      }
    }
    await startNewSession();
  }

  return {
    session,
    messages,
    sessionError,
    isLoading,
    isSending,
    send,
    clear,
    startNewSession,
    submitFeedback,
  };
}