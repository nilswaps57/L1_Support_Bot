import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { Alert } from "../../../shared/components/Alert";
import { LoadingSkeleton } from "../../../shared/components/LoadingSkeleton";
import { PageHeader } from "../../../shared/components/PageHeader";
import styles from "./AIConfigurationPage.module.css";
import {
  getChunkingConfig,
  getEmbeddingConfig,
  getLLMConfig,
  getRetrievalConfig,
  updateChunkingConfig,
  updateEmbeddingConfig,
  updateLLMConfig,
  updateRetrievalConfig,
  validateEmbeddingConfig,
  validateLLMConfig,
} from "../api/ai-configuration";
import { ChunkingConfigForm } from "../components/ChunkingConfigForm";
import { EmbeddingConfigForm } from "../components/EmbeddingConfigForm";
import { LLMConfigForm } from "../components/LLMConfigForm";
import { RetrievalConfigForm } from "../components/RetrievalConfigForm";
import { useRuntimeHealth } from "../../../shared/hooks/useRuntimeHealth";
import { ApiClientError } from "../../../shared/api/client";

export function AIConfigurationPage() {
  const health = useRuntimeHealth();
  const queryClient = useQueryClient();
  const llm = useQuery({ queryKey: ["config", "llm"], queryFn: getLLMConfig, retry: false });
  const embedding = useQuery({ queryKey: ["config", "embedding"], queryFn: getEmbeddingConfig, retry: false });
  const retrieval = useQuery({ queryKey: ["config", "retrieval"], queryFn: getRetrievalConfig, retry: false });
  const chunking = useQuery({ queryKey: ["config", "chunking"], queryFn: getChunkingConfig, retry: false });
  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["config"] });
  const llmMutation = useMutation({ mutationFn: updateLLMConfig, onSuccess: invalidate });
  const embeddingMutation = useMutation({ mutationFn: updateEmbeddingConfig, onSuccess: invalidate });
  const retrievalMutation = useMutation({ mutationFn: updateRetrievalConfig, onSuccess: invalidate });
  const chunkingMutation = useMutation({ mutationFn: updateChunkingConfig, onSuccess: invalidate });
  const llmValidation = useMutation({ mutationFn: validateLLMConfig });
  const embeddingValidation = useMutation({ mutationFn: validateEmbeddingConfig });
  const loading = [llm, embedding, retrieval, chunking].some((query) => query.isPending);
  const loadFailed = [llm, embedding, retrieval, chunking].some((query) => query.isError);
  const limited = health.data?.capabilities?.configuration_mutations === false;
  const errorMessage = (error: unknown) => error instanceof ApiClientError ? error.message : "The configuration request could not be completed.";
  return (
    <main className={`appContainer ${styles.page}`}>
      <PageHeader
        title="AI configuration"
        description="Manage approved model, retrieval, and chunking settings. Changes are active only after validation succeeds."
        breadcrumbs={[{ label: "Configuration", href: "/config" }, { label: "AI configuration" }]}
      />
      <p className={styles.intro}>Provider and model identifiers are visible when non-secret. Secret values and sensitive endpoints are never returned to the browser.</p>
      {limited ? <Alert tone="warning">Configuration changes are disabled while the workspace is in limited mode.</Alert> : null}
      {loadFailed ? <Alert tone="error">Configuration settings are temporarily unavailable.</Alert> : null}
      {loading ? <LoadingSkeleton variant="page" label="Loading configuration" /> : null}
      {!loading && !loadFailed && llm.data && embedding.data && retrieval.data && chunking.data ? (
        <div className={styles.grid}>
          <LLMConfigForm config={llm.data} disabled={limited} busy={llmMutation.isPending || llmValidation.isPending} error={llmMutation.error ? errorMessage(llmMutation.error) : llmValidation.error ? errorMessage(llmValidation.error) : undefined} success={llmMutation.isSuccess} onSave={(payload) => llmMutation.mutate(payload)} onValidate={(payload) => llmValidation.mutate(payload)} />
          <EmbeddingConfigForm config={embedding.data} disabled={limited} busy={embeddingMutation.isPending || embeddingValidation.isPending} error={embeddingMutation.error ? errorMessage(embeddingMutation.error) : embeddingValidation.error ? errorMessage(embeddingValidation.error) : undefined} success={embeddingMutation.isSuccess} onSave={(payload) => embeddingMutation.mutate(payload)} onValidate={(payload) => embeddingValidation.mutate(payload)} />
          <RetrievalConfigForm config={retrieval.data} disabled={limited} busy={retrievalMutation.isPending} error={retrievalMutation.error ? errorMessage(retrievalMutation.error) : undefined} success={retrievalMutation.isSuccess} onSave={(payload) => retrievalMutation.mutate(payload)} />
          <ChunkingConfigForm config={chunking.data} disabled={limited} busy={chunkingMutation.isPending} error={chunkingMutation.error ? errorMessage(chunkingMutation.error) : undefined} success={chunkingMutation.isSuccess} onSave={(payload) => chunkingMutation.mutate(payload)} />
        </div>
      ) : null}
    </main>
  );
}
