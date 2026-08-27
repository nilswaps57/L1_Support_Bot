import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { DocumentsPage } from "../../../src/features/configuration/pages/DocumentsPage";

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <DocumentsPage />
    </QueryClientProvider>,
  );
}

function response(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

const emptyDocuments = { items: [], total: 0, limit: 20, next_cursor: null };

describe("document upload", () => {
  it("accepts a supported file and displays queued status", async () => {
    const user = userEvent.setup();
    vi.spyOn(globalThis, "fetch").mockImplementation(async (_input, init) => {
      if (init?.method === "POST") {
        return response({
          document_id: "doc-1",
          job_id: "job-1",
          status: "QUEUED",
          name: "manual.pdf",
          file_type: "pdf",
          file_size_bytes: 14,
          checksum: "a".repeat(64),
        }, 202);
      }
      return response(emptyDocuments);
    });
    renderPage();

    await user.upload(
      screen.getByLabelText("Source file"),
      new File(["%PDF-1.7 source"], "manual.pdf", { type: "application/pdf" }),
    );
    await user.click(screen.getByRole("button", { name: "Upload" }));

    expect(await screen.findByRole("status")).toHaveTextContent(
      "manual.pdf is queued for processing.",
    );
  });

  it("rejects unsupported formats and oversized files before upload", async () => {
    const user = userEvent.setup();
    vi.spyOn(globalThis, "fetch").mockResolvedValue(response(emptyDocuments));
    renderPage();
    const input = screen.getByLabelText("Source file");

    fireEvent.change(input, {
      target: { files: [new File(["data"], "manual.xlsx")] },
    });
    expect(screen.getByRole("alert")).toHaveTextContent("Supported formats");
    expect(screen.getByRole("button", { name: "Upload" })).toBeDisabled();

    const oversized = new File([new Uint8Array(10 * 1024 * 1024 + 1)], "large.md", {
      type: "text/markdown",
    });
    const files = {
      0: oversized,
      length: 1,
      item: (index: number) => (index === 0 ? oversized : null),
    } as unknown as FileList;
    fireEvent.change(input, { target: { files } });
    expect(screen.getByRole("alert")).toHaveTextContent("10 MB size limit");
    expect(globalThis.fetch).not.toHaveBeenCalledWith(
      expect.stringContaining("/documents/upload"),
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("shows the duplicate error returned by the API", async () => {
    const user = userEvent.setup();
    vi.spyOn(globalThis, "fetch").mockImplementation(async (_input, init) => {
      if (init?.method === "POST") {
        return response(
          {
            error_code: "DUPLICATE_DOCUMENT",
            message: "A document with identical content is already registered.",
            request_id: "request-1",
            timestamp: new Date().toISOString(),
            details: {},
          },
          409,
        );
      }
      return response(emptyDocuments);
    });
    renderPage();
    await user.upload(
      screen.getByLabelText("Source file"),
      new File(["# FLEXCUBE"], "manual.md", { type: "text/markdown" }),
    );
    await user.click(screen.getByRole("button", { name: "Upload" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("identical content");
  });
});