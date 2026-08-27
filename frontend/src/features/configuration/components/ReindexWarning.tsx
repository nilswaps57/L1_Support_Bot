import { Alert } from "../../../shared/components/Alert";
import styles from "../pages/AIConfigurationPage.module.css";

type ReindexWarningProps = {
  visible: boolean;
  confirmed: boolean;
  onConfirm: (confirmed: boolean) => void;
};

export function ReindexWarning({ visible, confirmed, onConfirm }: ReindexWarningProps) {
  if (!visible) return null;
  return (
    <div className={styles.reindexBlock}>
      <Alert tone="warning" title="Re-index required">
        This change affects indexed content. The current compatible index remains active until a replacement is validated.
      </Alert>
      <label className={styles.checkbox}>
        <input
          type="checkbox"
          checked={confirmed}
          onChange={(event) => onConfirm(event.target.checked)}
        />
        I confirm a full re-index is required before this change can be active.
      </label>
    </div>
  );
}
