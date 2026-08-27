import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Alert } from "../../../src/shared/components/Alert";
import { EmptyState } from "../../../src/shared/components/EmptyState";
import { LoadingSkeleton } from "../../../src/shared/components/LoadingSkeleton";
import { StatusBadge } from "../../../src/shared/components/StatusBadge";

describe("shared UI state primitives", () => {
  it("announces error and success states with text", () => {
    render(
      <>
        <Alert tone="error">The service is unavailable.</Alert>
        <Alert tone="success">Document uploaded.</Alert>
      </>,
    );

    expect(screen.getByRole("alert")).toHaveTextContent("The service is unavailable.");
    expect(screen.getByRole("status")).toHaveTextContent("Document uploaded.");
  });

  it("keeps status meaning in the accessible text alongside its indicator", () => {
    render(<StatusBadge label="Indexing" tone="info" active />);

    expect(screen.getByText("Indexing")).toBeInTheDocument();
    expect(screen.getByText("in progress")).toBeInTheDocument();
  });

  it("provides labelled loading and empty regions", () => {
    render(
      <>
        <LoadingSkeleton variant="table" label="Loading documents" />
        <EmptyState title="No documents" description="Upload a source to begin." />
      </>,
    );

    expect(screen.getByRole("status", { name: "Loading documents" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "No documents" })).toBeInTheDocument();
  });
});
