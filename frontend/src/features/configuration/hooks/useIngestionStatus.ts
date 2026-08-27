import { useQuery } from "@tanstack/react-query";

import { apiClient } from "../../../shared/api/client";

export type IngestionStatus = {
  job_id: string;
  document_id: string;
  status: string;
  attempt_count: number;
  chunks_created: number;
  chunks_indexed: number;
  started_at: string | null;
  completed_at: string | null;
  last_error: string | null;
  parse_warnings: { element_type: string; description: string; page_number?: number | null }[];
};

const activeStatuses = new Set(["QUEUED", "PARSING", "NORMALISING", "CHUNKING", "EMBEDDING", "INDEXING"]);

export function useIngestionStatus(jobId: string | null, enabled = true) {
  return useQuery({
    queryKey: ["ingestion-job", jobId],
    queryFn: () => apiClient.request<IngestionStatus>(`/ingestion/jobs/${jobId}`),
    enabled: enabled && jobId !== null,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status && activeStatuses.has(status) ? 2000 : false;
    },
  });
}
