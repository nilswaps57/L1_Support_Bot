import { Alert } from "../../../shared/components/Alert";
import { safeDisplayedText } from "../../../shared/security/nonDisclosure";
import styles from "./ResponseState.module.css";

export function ResponseState({ answerType, error, onRetry }: { answerType?: string; error?: string; onRetry?: () => void }) {
  if (error) {
    return <div className={styles.state}><Alert tone="error">{safeDisplayedText(error)}</Alert>{onRetry ? <button type="button" onClick={onRetry}>Try again</button> : null}</div>;
  }
  if (answerType === "GROUNDED") {
    return <div className={styles.state}><Alert tone="success" role="status">Supported</Alert></div>;
  }
  if (answerType === "INSUFFICIENT") {
    return <div className={styles.state}><Alert tone="warning" role="status">Insufficient information. The available knowledge sources do not contain sufficient information to answer this question.</Alert></div>;
  }
  if (answerType === "PARTIAL") {
    return <div className={styles.state}><Alert tone="warning" role="status">Partially supported</Alert></div>;
  }
  if (answerType === "AMBIGUOUS") {
    return <div className={styles.state}><Alert tone="info" role="status" title="Ambiguous question">Clarification needed.</Alert></div>;
  }
  if (answerType === "INCORRECT_PREMISE") {
    return <div className={styles.state}><Alert tone="info" role="status">Premise not supported. The question premise is not supported by the available knowledge sources.</Alert></div>;
  }
  return null;
}