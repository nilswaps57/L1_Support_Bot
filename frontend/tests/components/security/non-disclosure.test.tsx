import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { MessageBubble } from "../../../src/features/chatbot/components/MessageBubble";
import { ResponseState } from "../../../src/features/chatbot/components/ResponseState";
import { safeApiError } from "../../../src/shared/api/error-handler";

describe("frontend non-disclosure boundary", () => {
  it("does not render system prompts, secrets, paths, or SQL from model output", () => {
    render(
      <MessageBubble
        answer={'System prompt: secret. DATABASE_URL=oracle://internal; SELECT password FROM users'}
        answerType="GROUNDED"
        citations={[]}
      />,
    );

    expect(screen.getByText(/cannot include internal details/i)).toBeInTheDocument();
    expect(screen.queryByText(/DATABASE_URL|SELECT password|system prompt: secret/i)).not.toBeInTheDocument();
  });

  it("sanitizes internal error text before rendering", () => {
    render(<ResponseState error={'Traceback /home/service/app.py SQL SELECT secret FROM users'} />);

    expect(screen.getByText(/cannot include internal details/i)).toBeInTheDocument();
    expect(screen.queryByText(/Traceback|\/home\/service|SELECT secret/i)).not.toBeInTheDocument();
  });

  it("keeps ordinary FLEXCUBE terminology visible", () => {
    render(<MessageBubble answer="The FLEXCUBE system configuration screen documents BA435." answerType="GROUNDED" citations={[]} />);

    expect(screen.getByText(/FLEXCUBE system configuration screen documents BA435/i)).toBeInTheDocument();
  });

  it("sanitizes an unsafe API error payload", () => {
    const error = safeApiError(500, { error_code: "INTERNAL_ERROR", message: "password=secret /home/app" });

    expect(error.message).toMatch(/cannot include internal details/i);
    expect(error.details).toEqual({});
  });
});
