import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { AIConfigurationPage } from "../../../src/features/configuration/pages/AIConfigurationPage";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

const llm = {
  provider: "ollama", model: "phi3.5", temperature: 0.1, max_tokens: 2048,
  context_window: 4096, timeout_seconds: 30, max_retries: 2, label: "Local model",
  api_key_configured: false, status: "active",
};
const embedding = {
  provider: "ollama", model: "nomic-embed-text", model_version: "dev", dimensions: 768,
  distance_method: "cosine", index_compatible: true, batch_size: 32, timeout_seconds: 30,
  label: null, api_key_configured: false, status: "active",
};
const retrieval = {
  top_k_candidates: 20, final_top_k: 5, similarity_threshold: 0.4,
  dense_weight: 0.7, sparse_weight: 0.3, rerank_enabled: false, rerank_top_k: 20,
  exact_id_boost: true, min_evidence_tokens: 100, status: "active",
};
const chunking = {
  strategy: "SEMANTIC_STRUCTURE", target_chunk_tokens: 512, min_chunk_tokens: 64,
  max_chunk_tokens: 1024, overlap_tokens: 64, table_as_unit: true,
  procedure_grouping: true, status: "active",
};

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <AIConfigurationPage />
    </QueryClientProvider>,
  );
}

describe("AI configuration", () => {
  it("renders grouped settings without receiving a secret value", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
      const path = String(input);
      if (path.endsWith("/config/llm")) return jsonResponse(llm);
      if (path.endsWith("/config/embedding")) return jsonResponse(embedding);
      if (path.endsWith("/config/retrieval")) return jsonResponse(retrieval);
      if (path.endsWith("/config/chunking")) return jsonResponse(chunking);
      return jsonResponse({ status: "healthy", capabilities: { configuration_mutations: true } });
    });

    renderPage();

    expect(await screen.findByRole("heading", { name: "Language model" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Embeddings" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Retrieval" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Chunking" })).toBeInTheDocument();
    expect(screen.getAllByText("No secret value is returned to this form.")).toHaveLength(2);
    expect(screen.queryByDisplayValue(/secret|token|password/i)).not.toBeInTheDocument();
  });

  it("shows a safe connectivity error and does not claim activation", async () => {
    const user = userEvent.setup();
    vi.spyOn(globalThis, "fetch").mockImplementation(async (input, init) => {
      const path = String(input);
      if (init?.method === "PUT" && path.endsWith("/config/llm")) {
        return jsonResponse({
          error_code: "LLM_CONNECTIVITY_FAILED",
          message: "The configured LLM endpoint could not be validated.",
          request_id: "request-1", timestamp: new Date().toISOString(), details: {},
        }, 422);
      }
      if (path.endsWith("/config/llm")) return jsonResponse(llm);
      if (path.endsWith("/config/embedding")) return jsonResponse(embedding);
      if (path.endsWith("/config/retrieval")) return jsonResponse(retrieval);
      if (path.endsWith("/config/chunking")) return jsonResponse(chunking);
      return jsonResponse({ status: "healthy", capabilities: { configuration_mutations: true } });
    });

    renderPage();
    await user.click(await screen.findByRole("button", { name: "Save language model" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("could not be validated");
    expect(screen.queryByText("Configuration active")).not.toBeInTheDocument();
  });

  it("requires confirmation before saving an embedding change that needs re-indexing", async () => {
    const user = userEvent.setup();
    vi.spyOn(globalThis, "fetch").mockImplementation(async (input, init) => {
      const path = String(input);
      if (init?.method === "PUT" && path.endsWith("/config/embedding")) {
        return jsonResponse({
          error_code: "REINDEX_REQUIRED",
          message: "This change requires a successful re-index before activation.",
          request_id: "request-2", timestamp: new Date().toISOString(), details: {},
        }, 409);
      }
      if (path.endsWith("/config/llm")) return jsonResponse(llm);
      if (path.endsWith("/config/embedding")) return jsonResponse(embedding);
      if (path.endsWith("/config/retrieval")) return jsonResponse(retrieval);
      if (path.endsWith("/config/chunking")) return jsonResponse(chunking);
      return jsonResponse({ status: "healthy", capabilities: { configuration_mutations: true } });
    });

    renderPage();
    const model = await screen.findByLabelText("Embedding model");
    await user.clear(model);
    await user.type(model, "bge-m3");

    expect(screen.getByRole("status")).toHaveTextContent(/re-index/i);
    const save = screen.getByRole("button", { name: "Save embedding settings" });
    expect(save).toBeDisabled();
    await user.click(screen.getByRole("checkbox", { name: /confirm.*re-index/i }));
    expect(save).toBeEnabled();
    await user.click(save);
    expect(await screen.findByRole("alert")).toHaveTextContent("requires a successful re-index");
  });
});