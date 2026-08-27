import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRef, useState } from "react";

import { deleteDocument, getDocument, listDocuments, type DocumentDetail } from "../api/documents";
import { ApiClientError } from "../../../shared/api/client";
import { useRuntimeHealth } from "../../../shared/hooks/useRuntimeHealth";
import { Alert } from "../../../shared/components/Alert";
import { EmptyState } from "../../../shared/components/EmptyState";
import { LoadingSkeleton } from "../../../shared/components/LoadingSkeleton";
import { DeleteDocumentDialog } from "./DeleteDocumentDialog";
import { ReindexDocumentButton } from "./ReindexDocumentButton";
import { DocumentStatus } from "./DocumentStatus";
import { IngestionWarnings } from "./IngestionWarnings";
import { useIngestionStatus } from "../hooks/useIngestionStatus";
import styles from "./DocumentList.module.css";

function formatBytes(bytes: number): string {
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function formatSourceType(sourceType: string): string {
  return sourceType.replaceAll("_", " ").replace(/\b\w/g, (character) => character.toUpperCase());
}

function formatDate(value: string): string {
  return new Date(value).toLocaleDateString();
}

export function DocumentList() {
  const health = useRuntimeHealth();
  const unavailable = health.data?.capabilities?.document_management === false;
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const documents = useQuery({ queryKey: ["documents"], queryFn: listDocuments });
  const detail = useQuery({
    queryKey: ["document", selectedId],
    queryFn: () => getDocument(selectedId as string),
    enabled: selectedId !== null,
  });

  if (documents.isLoading) {
    return <LoadingSkeleton variant="table" label="Loading documents" />;
  }
  if (documents.isError) {
    return <Alert tone="error">Documents could not be loaded.</Alert>;
  }
  if (!documents.data) {
    return <Alert tone="info">No document data is available.</Alert>;
  }

  return (
    <section className={styles.section} aria-labelledby="document-list-heading">
      <h2 className={styles.heading} id="document-list-heading">
        <span>Knowledge documents</span>
        <span className={styles.count}>{documents.data.total} total</span>
      </h2>
      {documents.data.items.length === 0 ? (
        <EmptyState title="No documents yet" description="Upload a knowledge source to make it available to branch support." />
      ) : (
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <caption className="srOnly">Knowledge documents</caption>
            <thead>
              <tr>
                <th scope="col">Document</th>
                <th scope="col">Source</th>
                <th scope="col">Status</th>
                <th scope="col">Indexed chunks</th>
                <th scope="col">Updated</th>
              </tr>
            </thead>
            <tbody>
              {documents.data.items.map((document) => (
                <tr key={document.document_id}>
                  <td>
                    <button className={styles.nameButton} type="button" onClick={() => setSelectedId(document.document_id)}>
                      {document.name}
                    </button>
                    <div className={styles.fileMeta}>
                      {document.file_type.toUpperCase()} - {formatBytes(document.file_size_bytes)}
                    </div>
                  </td>
                  <td>{formatSourceType(document.source_type)}</td>
                  <td><DocumentStatus status={document.status} /></td>
                  <td>{document.chunks_indexed}</td>
                  <td className={styles.muted}>{formatDate(document.updated_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {selectedId && detail.isLoading && <LoadingSkeleton variant="detail" label="Loading document details" />}
      {selectedId && detail.isError && <Alert tone="error">Document details could not be loaded.</Alert>}
      {detail.data && <DocumentDetails detail={detail.data} unavailable={unavailable} />}
    </section>
  );
}

function DocumentDetails({ detail, unavailable }: { detail: DocumentDetail; unavailable: boolean }) {
  const queryClient = useQueryClient();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const deleteTriggerRef = useRef<HTMLButtonElement>(null);
  const deletion = useMutation({
    mutationFn: () => deleteDocument(detail.document_id),
    onSuccess: () => {
      setDeleteDialogOpen(false);
      setSuccessMessage("Document deleted.");
      void queryClient.invalidateQueries({ queryKey: ["documents"] });
      void queryClient.invalidateQueries({ queryKey: ["document", detail.document_id] });
    },
  });
  const liveStatus = useIngestionStatus(detail.latest_job?.job_id ?? null);
  const status = liveStatus.data?.status ?? detail.status;
  const warnings = liveStatus.data?.parse_warnings ?? detail.latest_job?.parse_warnings ?? [];
  const error = deletion.error instanceof ApiClientError
    ? deletion.error.payload.message
    : deletion.error?.message ?? null;
  return (
    <article className={styles.detail} aria-labelledby="document-detail-heading">
      <h3 id="document-detail-heading">{detail.name}</h3>
      <dl className={styles.detailMeta}>
        <dt>Status</dt>
        <dd><DocumentStatus status={status} /></dd>
        <dt>File</dt>
        <dd>{detail.original_filename}</dd>
        <dt>Indexed chunks</dt>
        <dd>{detail.chunks_indexed}</dd>
      </dl>
      <IngestionWarnings warnings={warnings} />
      <div className={styles.actions}>
        {status !== "DELETED" && (
          <>
            <ReindexDocumentButton documentId={detail.document_id} />
            <button
              ref={deleteTriggerRef}
              className={styles.deleteButton}
              type="button"
              onClick={() => setDeleteDialogOpen(true)}
              disabled={unavailable}
            >
              Delete document
            </button>
          </>
        )}
      </div>
      {successMessage && <p role="status">{successMessage}</p>}
      {deleteDialogOpen && (
        <DeleteDocumentDialog
          documentName={detail.name}
          pending={deletion.isPending}
          error={error}
          returnFocusRef={deleteTriggerRef}
          onCancel={() => setDeleteDialogOpen(false)}
          onConfirm={() => deletion.mutate()}
        />
      )}
    </article>
  );
}