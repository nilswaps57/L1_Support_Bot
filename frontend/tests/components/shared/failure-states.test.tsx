import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { DegradedModeBanner } from "../../../src/shared/components/DegradedModeBanner";
import { ResponseState } from "../../../src/features/chatbot/components/ResponseState";
import { DocumentsPage } from "../../../src/features/configuration/pages/DocumentsPage";

function renderWithQuery(ui: React.ReactNode) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
}

function healthResponse() {
  return new Response(JSON.stringify({
    status: "degraded",
    version: "0.1.0",
    database: "unavailable",
    vector_store: "available",
    llm: "available",
    embedding: "available",
    degraded_capabilities: ["document_management"],
    capabilities: {
      chat: true,
      document_management: false,
      configuration_mutations: false,
      feedback_submission: false,
    },
  }), { status: 200, headers: { "Content-Type": "application/json" } });
}

describe("failure and degraded states", () => {
  it("presents limited mode without infrastructure details", () => {
    const retry = vi.fn();
    render(<DegradedModeBanner onRetry={retry} />);

    expect(screen.getByRole("status")).toHaveTextContent("Limited mode");
    expect(screen.getByRole("button", { name: "Check availability" })).toBeInTheDocument();
    expect(screen.queryByText(/oracle|password|endpoint|database/i)).not.toBeInTheDocument();
  });

  it("offers one safe retry action for a failed answer", async () => {
    const retry = vi.fn();
    render(<ResponseState error="Answer generation is temporarily unavailable." onRetry={retry} />);

    expect(screen.getByRole("alert")).toHaveTextContent("temporarily unavailable");
    expect(screen.getByRole("button", { name: "Try again" })).toBeInTheDocument();
  });

  it("disables document mutations while health reports limited mode", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
      if (String(input).endsWith("/health")) return healthResponse();
      return new Response(JSON.stringify({ items: [], total: 0, limit: 20, next_cursor: null }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    });

    renderWithQuery(<DocumentsPage />);

    expect(await screen.findByText(/document management is temporarily unavailable/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Upload" })).toBeDisabled();
  });
});
