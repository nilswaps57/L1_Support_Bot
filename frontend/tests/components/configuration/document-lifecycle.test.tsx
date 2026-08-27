import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { DocumentsPage } from "../../../src/features/configuration/pages/DocumentsPage";

function response(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

const document = {
  document_id: "doc-1",
  name: "manual.md",
  original_filename: "manual.md",
  file_type: "md",
  source_type: "flexcube_manual",
  status: "COMPLETED",
  file_size_bytes: 4,
  chunks_indexed: 2,
  chunks_created: 2,
  checksum: "a".repeat(64),
  description: null,
  uploaded_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  latest_job: {
    job_id: "job-1",
    status: "COMPLETED",
    chunks_created: 2,
    chunks_indexed: 2,
    parse_warnings: [],
  },
};

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <DocumentsPage />
    </QueryClientProvider>,
  );
}

describe("document lifecycle", () => {
  it("confirms deletion and refreshes after a successful delete", async () => {
    const user = userEvent.setup();
    vi.spyOn(globalThis, "fetch").mockImplementation(async (input, init) => {
      const path = String(input);
      if (init?.method === "DELETE") {
        return response({ document_id: "doc-1", status: "DELETED" }, 202);
      }
      if (path.endsWith("/doc-1")) return response(document);
      return response({ items: [document], total: 1, limit: 20, next_cursor: null });
    });
    renderPage();

    await user.click(await screen.findByRole("button", { name: "manual.md" }));
    await user.click(await screen.findByRole("button", { name: /delete document/i }));
    expect(screen.getByRole("dialog")).toHaveTextContent("Delete manual.md?");
    await user.click(screen.getByRole("button", { name: "Confirm delete" }));

    expect(await screen.findByRole("status")).toHaveTextContent("Document deleted.");
  });

  it("shows the active-ingestion conflict without removing the document", async () => {
    const user = userEvent.setup();
    vi.spyOn(globalThis, "fetch").mockImplementation(async (input, init) => {
      const path = String(input);
      if (init?.method === "DELETE") {
        return response({
          error_code: "DOCUMENT_IN_PROCESSING",
          message: "Cannot delete while ingestion is in progress.",
          request_id: "request-1",
          timestamp: new Date().toISOString(),
          details: { current_status: "EMBEDDING" },
        }, 409);
      }
      if (path.endsWith("/doc-1")) return response({ ...document, status: "EMBEDDING" });
      return response({ items: [{ ...document, status: "EMBEDDING" }], total: 1, limit: 20, next_cursor: null });
    });
    renderPage();

    await user.click(await screen.findByRole("button", { name: "manual.md" }));
    await user.click(await screen.findByRole("button", { name: /delete document/i }));
    await user.click(screen.getByRole("button", { name: "Confirm delete" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Cannot delete while ingestion is in progress");
  });

  it("shows re-index failure and keeps lifecycle controls available", async () => {
    const user = userEvent.setup();
    vi.spyOn(globalThis, "fetch").mockImplementation(async (input, init) => {
      const path = String(input);
      if (init?.method === "POST") {
        return response({
          error_code: "VECTOR_STORE_UNAVAILABLE",
          message: "The replacement index is unavailable.",
          request_id: "request-2",
          timestamp: new Date().toISOString(),
          details: {},
        }, 503);
      }
      if (path.endsWith("/doc-1")) return response(document);
      return response({ items: [document], total: 1, limit: 20, next_cursor: null });
    });
    renderPage();

    await user.click(await screen.findByRole("button", { name: "manual.md" }));
    await user.click(await screen.findByRole("button", { name: "Re-index document" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("replacement index is unavailable");
    expect(screen.getByRole("button", { name: "Re-index document" })).toBeEnabled();
  });
});
