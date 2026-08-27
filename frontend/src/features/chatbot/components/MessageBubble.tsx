import type { ChatCitation } from "../api/chat";
import type { FeedbackRating } from "../api/feedback";
import { CitationList } from "./CitationList";
import { FeedbackForm } from "./FeedbackForm";
import { ClarificationPrompt } from "./ClarificationPrompt";
import { ResponseState } from "./ResponseState";
import { safeDisplayedText } from "../../../shared/security/nonDisclosure";
import styles from "./MessageBubble.module.css";

export function MessageBubble({
  answer,
  answerType,
  citations,
  answerId,
  onFeedback,
}: {
  answer: string;
  answerType: string;
  citations: ChatCitation[];
  answerId?: string;
  onFeedback?: (answerId: string, rating: FeedbackRating, comment?: string) => Promise<unknown>;
}) {
  const hasCitationSafeOutcome = ["INSUFFICIENT", "AMBIGUOUS", "INCORRECT_PREMISE"].includes(answerType);
  const safeAnswer = safeDisplayedText(answer);
  return (
    <article className={styles.assistant} aria-label="Support response">
      <ResponseState answerType={answerType} />
      {answerType === "AMBIGUOUS" ? <ClarificationPrompt message={safeAnswer} /> : null}
      <p className={styles.role}>Support</p>
      <p className={styles.answer}>{safeAnswer}</p>
      {hasCitationSafeOutcome ? null : <CitationList citations={citations} />}
          {answerId && onFeedback ? (
            <FeedbackForm
              answerId={answerId}
              onSubmit={(rating, comment) => onFeedback(answerId, rating, comment)}
            />
          ) : null}
    </article>
  );
}