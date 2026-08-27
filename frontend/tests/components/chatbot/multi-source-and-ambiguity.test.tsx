import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { MessageBubble } from "../../../src/features/chatbot/components/MessageBubble";
import { ResponseState } from "../../../src/features/chatbot/components/ResponseState";
import type { ChatCitation } from "../../../src/features/chatbot/api/chat";

const citation = (documentName: string, chunkId: string): ChatCitation => ({
  chunk_id: chunkId,
  document_id: `${chunkId}-document`,
  document_name: documentName,
  page_number: null,
  section: null,
  task_code: null,
  screen_name: null,
  menu_path: null,
  prerequisites: [],
  modes: [],
  field_names: [],
  procedure_steps: [],
  error_code: null,
  jira_id: null,
  rca_reference: null,
  source_type: null,
  relevance_score: null,
});

describe("multi-source and ambiguity outcomes", () => {
  it("keeps each supporting document visible", () => {
    render(
      <MessageBubble
        answerType="GROUNDED"
        answer="The answer combines both manuals."
        citations={[citation("Task Codes", "chunk-1"), citation("Operations RCA", "chunk-2")]}
      />,
    );

    expect(screen.getByText("Task Codes")).toBeInTheDocument();
    expect(screen.getByText("Operations RCA")).toBeInTheDocument();
  });

  it("shows partial coverage and asks for clarification without sources", () => {
    render(
      <>
        <MessageBubble
          answerType="PARTIAL"
          answer="BA435 is documented, but the approval workflow is not covered."
          citations={[citation("Task Codes", "chunk-1")]}
        />
        <ResponseState answerType="AMBIGUOUS" />
        <ResponseState answerType="INCORRECT_PREMISE" />
      </>,
    );

    expect(screen.getByText("Partially supported")).toBeInTheDocument();
    expect(screen.getByText("Ambiguous question")).toBeInTheDocument();
    expect(screen.getByText(/premise is not supported/i)).toBeInTheDocument();
    expect(screen.getAllByRole("heading", { name: /sources/i })).toHaveLength(1);
  });
});