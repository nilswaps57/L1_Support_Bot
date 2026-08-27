import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { MessageBubble } from "../../../src/features/chatbot/components/MessageBubble";
import { ResponseState } from "../../../src/features/chatbot/components/ResponseState";

describe("chat response states", () => {
  it("renders insufficient information without a sources region", () => {
    render(<ResponseState answerType="INSUFFICIENT" />);

    expect(screen.getByText(/knowledge sources do not contain sufficient information/i)).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: /sources/i })).not.toBeInTheDocument();
  });

  it("renders partial and ambiguous states explicitly", () => {
    render(
      <>
        <MessageBubble answerType="PARTIAL" answer="The supported portion is documented." citations={[]} />
        <MessageBubble answerType="AMBIGUOUS" answer="Please clarify which screen you mean." citations={[]} />
      </>,
    );

    expect(screen.getByText("Partially supported")).toBeInTheDocument();
    expect(screen.getByText("Ambiguous question")).toBeInTheDocument();
  });

  it("renders service failures as alerts", () => {
    render(<ResponseState error="Answer generation is temporarily unavailable." />);

    expect(screen.getByRole("alert")).toHaveTextContent(/temporarily unavailable/i);
  });
});