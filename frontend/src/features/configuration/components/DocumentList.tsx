import { useQuery } from "@tanstack/react-query";

import { getDocument, listDocuments, type DocumentDetail } from "../api/documents";
import { DocumentStatus } from "./DocumentStatus";
import { IngestionWarnings } from "./IngestionWarnings";
import { useIngestionStatus } from "../hooks/useIngestionStatus";
import { useState } from "react";

function formatBytes(bytes: number): string {
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

export function DocumentList() {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const documents = useQuery({ queryKey: ["documents"], queryFn: listDocuments });
  const detail = useQuery({
    queryKey: ["document", selectedId],
    queryFn: () => getDocument(selectedId as string),
    enabled: selectedId !== null,
  });

  if (documents.isLoading) {
    return <p role="status">Loading documents...</p>;
  }
  if (documents.isError) {
    return <p role="alert">Documents could not be loaded.</p>;
  }
  if (!documents.data) {
    return <p role="status">No document data is available.</p>;
  }

  return (
    <section aria-labelledby="document-list-heading">
      <h2 id="document-list-heading">Knowledge documents ({documents.data.total})</h2>
      {documents.data.items.length === 0 ? (
        <p>No documents have been uploaded.</p>
      ) : (
        <ul>
          {documents.data.items.map((document) => (
            <li key={document.document_id}>
              <button type="button" onClick={() => setSelectedId(document.document_id)}>
                {document.name}
              </button>
              <span>{` ${document.file_type.toUpperCase()} - ${formatBytes(document.file_size_bytes)} `}</span>
              <DocumentStatus status={document.status} />
            </li>
          ))}
        </ul>
      )}
      {selectedId && detail.isLoading && <p role="status">Loading document details...</p>}
      {selectedId && detail.isError && <p role="alert">Document details could not be loaded.</p>}
      {detail.data && <DocumentDetails detail={detail.data} />}
    </section>
  );
}

function DocumentDetails({ detail }: { detail: DocumentDetail }) {
  const liveStatus = useIngestionStatus(detail.latest_job?.job_id ?? null);
  const status = liveStatus.data?.status ?? detail.status;
  const warnings = liveStatus.data?.parse_warnings ?? detail.latest_job?.parse_warnings ?? [];
  return (
    <article aria-labelledby="document-detail-heading">
      <h3 id="document-detail-heading">{detail.name}</h3>
      <dl>
        <dt>Status</dt>
        <dd><DocumentStatus status={status} /></dd>
        <dt>Checksum</dt>
        <dd>{detail.checksum}</dd>
        <dt>Indexed chunks</dt>
        <dd>{detail.chunks_indexed}</dd>
      </dl>
      <IngestionWarnings warnings={warnings} />
    </article>
  );
}