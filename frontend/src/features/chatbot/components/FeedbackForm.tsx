import { type FormEvent, useState } from "react";

import type { FeedbackRating } from "../api/feedback";
import styles from "./FeedbackForm.module.css";

type FeedbackFormProps = {
  answerId: string;
  onSubmit: (rating: FeedbackRating, comment?: string) => Promise<unknown>;
};

export function FeedbackForm({ answerId, onSubmit }: FeedbackFormProps) {
  const [rating, setRating] = useState<FeedbackRating>();
  const [comment, setComment] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<string>();

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!rating || isSubmitting || submitted) return;
    setIsSubmitting(true);
    setError(undefined);
    try {
      await onSubmit(rating, comment.trim() || undefined);
      setSubmitted(true);
    } catch {
      setError("Feedback could not be sent. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className={styles.form} aria-label="Answer feedback" onSubmit={submit}>
      <fieldset className={styles.fieldset} disabled={isSubmitting || submitted}>
        <legend className={styles.legend}>Was this answer helpful?</legend>
        <div className={styles.ratingGroup}>
          <button
            className={rating === "helpful" ? styles.selected : styles.rating}
            type="button"
            aria-pressed={rating === "helpful"}
            onClick={() => setRating("helpful")}
          >
            Helpful
          </button>
          <button
            className={rating === "not_helpful" ? styles.selected : styles.rating}
            type="button"
            aria-pressed={rating === "not_helpful"}
            onClick={() => setRating("not_helpful")}
          >
            Not helpful
          </button>
        </div>
        <label className={styles.commentLabel} htmlFor={`feedback-comment-${answerId}`}>
          Optional comment
        </label>
        <textarea
          id={`feedback-comment-${answerId}`}
          className={styles.comment}
          value={comment}
          maxLength={1000}
          rows={2}
          onChange={(event) => setComment(event.target.value)}
        />
        <button className={styles.submit} type="submit" disabled={!rating || isSubmitting || submitted}>
          {isSubmitting ? "Sending" : "Send feedback"}
        </button>
      </fieldset>
      {submitted ? <p className={styles.confirmation} role="status">Feedback received. Thank you.</p> : null}
      {error ? <p className={styles.error} role="alert">{error}</p> : null}
    </form>
  );
}