import { type FormEvent, useState } from "react";
import styles from "./ChatInput.module.css";

export function ChatInput({ onSubmit, disabled = false }: { onSubmit: (question: string) => void; disabled?: boolean }) {
  const [question, setQuestion] = useState("");

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!question.trim()) return;
    onSubmit(question.trim());
    setQuestion("");
  }

  return (
    <form className={styles.form} onSubmit={submit}>
      <div className={styles.labelGroup}>
        <label className={styles.label} htmlFor="chat-question">Question</label>
      <textarea
        className={styles.textarea}
        id="chat-question"
        name="question"
        value={question}
        onChange={(event) => setQuestion(event.target.value)}
        disabled={disabled}
        rows={3}
      />
        <p className={styles.helper}>Ask about a FLEXCUBE task, screen, procedure, or error.</p>
      </div>
      <button className={styles.askButton} type="submit" disabled={disabled || !question.trim()}>
        {disabled ? "Ask" : "Ask"}
      </button>
    </form>
  );
}
