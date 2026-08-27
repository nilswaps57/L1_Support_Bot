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

export function DocumentStatus({ status, warning }: { status: string; warning?: string | null }) {
  const label = labels[status] ?? status;
  const active = ["QUEUED", "PARSING", "NORMALISING", "CHUNKING", "EMBEDDING", "INDEXING"].includes(status);
  return (
    <span>
      {active ? <span role="status">{label}</span> : <span>{label}</span>}
      {warning ? <span role="alert">{warning}</span> : null}
    </span>
  );
}
