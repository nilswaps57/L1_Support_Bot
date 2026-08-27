import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ChatPage } from "../../../src/features/chatbot/pages/ChatPage";

const askChat = vi.hoisted(() => vi.fn());
const createChatSession = vi.hoisted(() => vi.fn());
const clearChatSession = vi.hoisted(() => vi.fn());

vi.mock("../../../src/features/chatbot/api/chat", () => ({ askChat }));
vi.mock("../../../src/features/chatbot/api/session", () => ({
  createChatSession,
  clearChatSession,
}));

describe("chat session lifecycle", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("creates a session, keeps follow-up messages, and clears them", async () => {
    createChatSession.mockResolvedValue({
      session_id: "session-1",
      created_at: "2026-08-27T10:00:00Z",
      expires_at: "2026-08-27T10:30:00Z",
    });
    clearChatSession.mockResolvedValue(undefined);
    askChat
      .mockResolvedValueOnce({ answer_text: "BA435 is documented.", answer_type: "GROUNDED", citations: [] })
      .mockResolvedValueOnce({ answer_text: "Its prerequisites are documented.", answer_type: "GROUNDED", citations: [] });

    const user = userEvent.setup();
    render(<ChatPage />);
    await waitFor(() => expect(createChatSession).toHaveBeenCalledOnce());

    const input = screen.getByRole("textbox", { name: /question/i });
    await user.type(input, "What is BA435?");
    await user.click(screen.getByRole("button", { name: "Ask" }));
    await waitFor(() => expect(screen.getByText("BA435 is documented.")).toBeInTheDocument());
    await user.type(input, "What are its prerequisites?");
    await user.click(screen.getByRole("button", { name: "Ask" }));
    await waitFor(() => expect(screen.getByText("Its prerequisites are documented.")).toBeInTheDocument());

    await user.click(screen.getByRole("button", { name: /clear session/i }));
    await waitFor(() => expect(clearChatSession).toHaveBeenCalledWith("session-1"));
    expect(screen.queryByText("BA435 is documented.")).not.toBeInTheDocument();
    expect(screen.queryByText("Its prerequisites are documented.")).not.toBeInTheDocument();
  });

  it("recovers from an expired session with a new-session action", async () => {
    createChatSession
      .mockResolvedValueOnce({ session_id: "expired", created_at: "2026-08-27T10:00:00Z", expires_at: "2026-08-27T10:01:00Z" })
      .mockResolvedValueOnce({ session_id: "session-2", created_at: "2026-08-27T10:02:00Z", expires_at: "2026-08-27T10:32:00Z" });
    askChat.mockRejectedValueOnce({
      payload: { error_code: "SESSION_NOT_FOUND", message: "Session expired." },
      status: 404,
    });

    const user = userEvent.setup();
    render(<ChatPage />);
    await waitFor(() => expect(createChatSession).toHaveBeenCalledOnce());
    await user.type(screen.getByRole("textbox", { name: /question/i }), "What is it?");
    await user.click(screen.getByRole("button", { name: "Ask" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/expired/i);
    await user.click(screen.getByRole("button", { name: /start new session/i }));
    await waitFor(() => expect(createChatSession).toHaveBeenCalledTimes(2));
  });
});