import { useMutation, useQueryClient } from "@tanstack/react-query";

import { ApiClientError } from "../../../shared/api/client";
import { reindexDocument } from "../api/documents";
import styles from "./ReindexDocumentButton.module.css";

import { useRuntimeHealth } from "../../../shared/hooks/useRuntimeHealth";
export function ReindexDocumentButton({ documentId }: { documentId: string }) {
  const health = useRuntimeHealth();
  const unavailable = health.data?.capabilities?.document_management === false;
  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: () => reindexDocument(documentId),
    onSuccess: (job) => {
      void queryClient.invalidateQueries({ queryKey: ["document", documentId] });
      void queryClient.invalidateQueries({ queryKey: ["ingestion-job", job.job_id] });
    },
  });
  const error = mutation.error instanceof ApiClientError
    ? mutation.error.payload.message
    : mutation.error?.message;

  return (
    <span className={styles.container}>
      <button className={styles.button} type="button" onClick={() => mutation.mutate()} disabled={mutation.isPending || unavailable}>
        {mutation.isPending ? "Re-indexing..." : "Re-index document"}
      </button>
      {mutation.isSuccess && <span className={styles.success} role="status">Re-indexing completed.</span>}
      {error && <span className={styles.error} role="alert">{error}</span>}
    </span>
  );
}
