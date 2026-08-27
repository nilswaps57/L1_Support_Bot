import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { CitationList } from "../../../src/features/chatbot/components/CitationList";
import type { ChatCitation } from "../../../src/features/chatbot/api/chat";

const citation = (overrides: Partial<ChatCitation> = {}): ChatCitation => ({
  chunk_id: "chunk-1",
  document_id: "document-1",
  document_name: "FLEXCUBE Manual",
  page_number: 142,
  section: "Task Codes > BA435",
  task_code: "BA435",
  screen_name: "Customer Account Screen",
  menu_path: null,
  prerequisites: [],
  modes: [],
  field_names: [],
  procedure_steps: [],
  error_code: null,
  jira_id: null,
  rca_reference: null,
  source_type: "flexcube_manual",
  relevance_score: 0.92,
  ...overrides,
});

describe("CitationList", () => {
  it("renders document, page, section, and task metadata", () => {
    render(<CitationList citations={[citation()]} />);

    expect(screen.getByRole("list", { name: /sources/i })).toBeInTheDocument();
    expect(screen.getByText("FLEXCUBE Manual")).toBeInTheDocument();
    expect(screen.getByText("Page 142")).toBeInTheDocument();
    expect(screen.getByText("Task Codes > BA435")).toBeInTheDocument();
    expect(screen.getByText("Task: BA435")).toBeInTheDocument();
  });

  it("omits unavailable page metadata", () => {
    render(<CitationList citations={[citation({ page_number: null })]} />);

    expect(screen.queryByText(/Page/)).not.toBeInTheDocument();
  });

  it("renders multiple source citations", () => {
    render(
      <CitationList
        citations={[
          citation(),
          citation({ chunk_id: "chunk-2", document_name: "Operations RCA", page_number: 8 }),
        ]}
      />,
    );

    expect(screen.getAllByRole("listitem")).toHaveLength(2);
    expect(screen.getByText("Operations RCA")).toBeInTheDocument();
  });
});
