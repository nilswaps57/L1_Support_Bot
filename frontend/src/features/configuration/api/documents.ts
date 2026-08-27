import { apiClient } from "../../../shared/api/client";

export type DocumentListItem = {
  document_id: string;
  name: string;
  file_type: string;
  source_type: string;
  status: string;
  file_size_bytes: number;
  chunks_indexed: number;
  uploaded_at: string;
  updated_at: string;
};

export type DocumentListResponse = {
  items: DocumentListItem[];
  total: number;
  limit: number;
  next_cursor: string | null;
};

export type DocumentDetail = DocumentListItem & {
  original_filename: string;
  checksum: string;
  description: string | null;
  chunks_created: number;
  latest_job: {
    job_id: string;
    status: string;
    chunks_created: number;
    chunks_indexed: number;
    parse_warnings: { element_type: string; description: string }[];
  } | null;
};

export type UploadAccepted = {
  document_id: string;
  job_id: string;
  status: string;
  name: string;
  file_type: string;
  file_size_bytes: number;
  checksum: string;
};

export async function listDocuments(): Promise<DocumentListResponse> {
  return apiClient.request<DocumentListResponse>("/documents");
}

export async function getDocument(documentId: string): Promise<DocumentDetail> {
  return apiClient.request<DocumentDetail>(`/documents/${documentId}`);
}

export async function uploadDocument(
  file: File,
  sourceType: string,
  name?: string,
): Promise<UploadAccepted> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("source_type", sourceType);
  if (name?.trim()) {
    formData.append("name", name.trim());
  }
  return apiClient.request<UploadAccepted>("/documents/upload", {
    method: "POST",
    body: formData,
  });
}