import styles from "./ClarificationPrompt.module.css";

export function ClarificationPrompt({ message }: { message: string }) {
  return (
    <section className={styles.prompt} aria-label="Clarification needed">
      <strong>Clarification needed:</strong> {message}
    </section>
  );
}