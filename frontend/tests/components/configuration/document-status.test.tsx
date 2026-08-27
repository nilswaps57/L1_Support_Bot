import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { DocumentStatus } from "../../../src/features/configuration/components/DocumentStatus";


describe("DocumentStatus", () => {
  it("shows human-readable active progress", () => {
    render(<DocumentStatus status="PARSING" />);
    expect(screen.getByRole("status")).toHaveTextContent("Parsing");
  });

  it("shows warnings without exposing implementation details", () => {
    render(<DocumentStatus status="READY_FOR_INDEXING_WITH_WARNING" warning="Table content could not be parsed" />);
    expect(screen.getByRole("alert")).toHaveTextContent("Table content could not be parsed");
    expect(screen.queryByText(/traceback|\/home\//i)).not.toBeInTheDocument();
  });
});
