import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ChatPage } from "../../../src/features/chatbot/pages/ChatPage";

describe("ChatPage", () => {
  it("renders the question input and grounded message surface", () => {
    render(<ChatPage />);
    expect(screen.getByRole("textbox", { name: /question/i })).toBeInTheDocument();
    expect(screen.getByRole("main")).toBeInTheDocument();
  });
});
