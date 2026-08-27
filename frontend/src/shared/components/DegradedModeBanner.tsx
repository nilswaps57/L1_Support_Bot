import { Alert } from "./Alert";
import styles from "./DegradedModeBanner.module.css";

export function DegradedModeBanner({ onRetry }: { onRetry?: () => void }) {
  return (
    <div className={styles.banner}>
      <Alert tone="warning" role="status" title="Limited mode">
        Chat remains available for indexed knowledge. Document management, feedback, and configuration changes are temporarily unavailable.
      </Alert>
      {onRetry ? (
        <button className={styles.retry} type="button" onClick={onRetry}>
          Check availability
        </button>
      ) : null}
    </div>
  );
}
