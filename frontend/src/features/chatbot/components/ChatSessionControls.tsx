import styles from "./ChatSessionControls.module.css";

export function ChatSessionControls({
  expiresAt,
  onClear,
  disabled = false,
}: {
  expiresAt?: string;
  onClear: () => void;
  disabled?: boolean;
}) {
  return (
    <section className={styles.controls} aria-label="Chat session controls">
      <p className={styles.sessionStatus}>
        <span className={styles.sessionIndicator} aria-hidden="true" />
        {expiresAt ? `Session active until ${new Date(expiresAt).toLocaleTimeString()}` : "No active session"}
      </p>
      <button className={styles.clearButton} type="button" onClick={onClear} disabled={disabled}>
        Clear session
      </button>
    </section>
  );
}