import { StatusBadge } from "../../../shared/components/StatusBadge";
import styles from "./DocumentStatus.module.css";

const labels: Record<string, string> = {
  UPLOADED: "Uploaded",
  QUEUED: "Queued",
  PARSING: "Parsing",
  NORMALISING: "Normalising",
  CHUNKING: "Generating knowledge",
  READY_FOR_INDEXING: "Ready for indexing",
  READY_FOR_INDEXING_WITH_WARNING: "Ready for indexing - some content missing",
  EMBEDDING: "Embedding",
  INDEXING: "Indexing",
  COMPLETED: "Ready",
  COMPLETED_WITH_WARNING: "Ready with warnings",
  FAILED: "Failed",
  DELETING: "Deleting",
  DELETED: "Deleted",
};

function toneFor(status: string): "neutral" | "info" | "success" | "warning" | "error" {
  if (["QUEUED", "PARSING", "NORMALISING", "CHUNKING", "EMBEDDING", "INDEXING"].includes(status)) return "info";
  if (["COMPLETED"].includes(status)) return "success";
  if (["READY_FOR_INDEXING_WITH_WARNING", "COMPLETED_WITH_WARNING"].includes(status)) return "warning";
  if (["FAILED"].includes(status)) return "error";
  return "neutral";
}

export function DocumentStatus({ status, warning }: { status: string; warning?: string | null }) {
  const label = labels[status] ?? status;
  const active = ["QUEUED", "PARSING", "NORMALISING", "CHUNKING", "EMBEDDING", "INDEXING"].includes(status);
  return (
    <span className={styles.status}>
      {active ? (
        <span role="status">
          <StatusBadge label={label} tone={toneFor(status)} active />
        </span>
      ) : <StatusBadge label={label} tone={toneFor(status)} />}
      {warning ? <span className={styles.warning} role="alert">{warning}</span> : null}
    </span>
  );
}
