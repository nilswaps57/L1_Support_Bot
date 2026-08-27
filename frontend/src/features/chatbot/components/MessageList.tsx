import type { ChatCitation } from "../api/chat";
import type { FeedbackRating } from "../api/feedback";
import { EmptyState } from "../../../shared/components/EmptyState";
import { LoadingSkeleton } from "../../../shared/components/LoadingSkeleton";
import { MessageBubble } from "./MessageBubble";
import { ResponseState } from "./ResponseState";
import styles from "./MessageList.module.css";

export type ChatMessage = {
  question: string;
  answerId?: string;
  answer?: string;
  answerType?: string;
  citations?: ChatCitation[];
  error?: string;
  retry?: () => void;
};

export function MessageList({
    messages,
    pending = false,
    onFeedback,
  }: {
    messages: ChatMessage[];
    pending?: boolean;
    onFeedback?: (answerId: string, rating: FeedbackRating, comment?: string) => Promise<unknown>;
}) {
  return (
    <section className={styles.conversation} aria-label="Conversation">
      {messages.length === 0 ? (
        <div className={styles.empty}>
          <EmptyState title="Start with a support question" description="Ask a FLEXCUBE question to begin." />
        </div>
      ) : null}
      <ol className={styles.messages}>
        {messages.map((message, index) => (
          <li className={styles.messageGroup} key={`${message.question}-${index}`}>
            <p className={styles.question}>
              <span className={styles.role}>You</span>
              {message.question}
            </p>
            {message.answer && message.answerType ? (
              <MessageBubble
                answer={message.answer}
                answerType={message.answerType}
                citations={message.citations ?? []}
                answerId={message.answerId}
                onFeedback={onFeedback}
              />
            ) : null}
            {message.error ? <ResponseState error={message.error} onRetry={message.retry} /> : null}
          </li>
        ))}
      </ol>
      {pending ? <LoadingSkeleton variant="conversation" label="Support is preparing a response" /> : null}
    </section>
  );
}
