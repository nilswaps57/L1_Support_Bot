import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { FeedbackForm } from "../../../src/features/chatbot/components/FeedbackForm";

describe("FeedbackForm", () => {
  it("submits a rating and optional comment once, then confirms", async () => {
    const user = userEvent.setup();
    const submit = vi.fn().mockResolvedValue({ feedback_id: "feedback-1" });
    render(<FeedbackForm answerId="answer-1" onSubmit={submit} />);

    await user.click(screen.getByRole("button", { name: "Not helpful" }));
    await user.type(screen.getByLabelText("Optional comment"), "Needs more detail");
    await user.click(screen.getByRole("button", { name: "Send feedback" }));
    await user.click(screen.getByRole("button", { name: "Send feedback" }));

    expect(submit).toHaveBeenCalledTimes(1);
    expect(await screen.findByRole("status")).toHaveTextContent("Feedback received");
  });

  it("does not enable submit before a rating is selected", () => {
    render(<FeedbackForm answerId="answer-1" onSubmit={vi.fn()} />);

    expect(screen.getByRole("button", { name: "Send feedback" })).toBeDisabled();
  });
});