import { useState } from "react";

import { askChat } from "../api/chat";
import { ChatInput } from "../components/ChatInput";
import { MessageList, type ChatMessage } from "../components/MessageList";

const sessionId = globalThis.crypto?.randomUUID?.() ?? "00000000-0000-0000-0000-000000000001";

export function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);

  async function submit(question: string) {
    setIsSending(true);
    try {
      const response = await askChat(sessionId, question);
      setMessages((current) => [
        ...current,
        { question, answer: response.answer_text, answerType: response.answer_type },
      ]);
    } catch {
      setMessages((current) => [
        ...current,
        { question, error: "Answer generation is temporarily unavailable." },
      ]);
    } finally {
      setIsSending(false);
    }
  }

  return (
    <main>
      <h1>Chat</h1>
      <p>FLEXCUBE Support</p>
      <MessageList messages={messages} />
      <ChatInput onSubmit={submit} disabled={isSending} />
    </main>
  );
}
