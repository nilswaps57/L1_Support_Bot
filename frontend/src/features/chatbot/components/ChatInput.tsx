import { type FormEvent, useState } from "react";

export function ChatInput({ onSubmit, disabled = false }: { onSubmit: (question: string) => void; disabled?: boolean }) {
  const [question, setQuestion] = useState("");

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!question.trim()) return;
    onSubmit(question.trim());
    setQuestion("");
  }

  return (
    <form onSubmit={submit}>
      <label htmlFor="chat-question">Question</label>
      <textarea
        id="chat-question"
        name="question"
        value={question}
        onChange={(event) => setQuestion(event.target.value)}
        disabled={disabled}
        rows={3}
      />
      <button type="submit" disabled={disabled || !question.trim()}>Ask</button>
    </form>
  );
}
