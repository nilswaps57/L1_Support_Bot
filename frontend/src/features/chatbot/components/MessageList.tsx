export type ChatMessage = {
  question: string;
  answer?: string;
  answerType?: string;
  error?: string;
};

export function MessageList({ messages }: { messages: ChatMessage[] }) {
  return (
    <section aria-label="Conversation">
      {messages.length === 0 ? <p>Ask a FLEXCUBE question to begin.</p> : null}
      <ol>
        {messages.map((message, index) => (
          <li key={`${message.question}-${index}`}>
            <p><strong>You:</strong> {message.question}</p>
            {message.answer ? <p><strong>Support:</strong> {message.answer}</p> : null}
            {message.answerType ? <small>{message.answerType}</small> : null}
            {message.error ? <p role="alert">{message.error}</p> : null}
          </li>
        ))}
      </ol>
    </section>
  );
}
