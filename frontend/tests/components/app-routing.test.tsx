import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MemoryRouter } from "react-router-dom";

import { AppRoutes } from "../../src/app/router";
import { Providers } from "../../src/app/providers";

const renderRoute = (path: string) =>
  render(
    <MemoryRouter initialEntries={[path]}>
      <Providers>
        <AppRoutes />
      </Providers>
    </MemoryRouter>,
  );

describe("application route shell", () => {
  it.each([
    ["/chat", "Chat"],
    ["/config", "Configuration"],
    ["/config/documents", "Documents"],
    ["/config/ai", "AI configuration"],
  ])("renders the %s route boundary", (path, heading) => {
    renderRoute(path);

    expect(screen.getByRole("heading", { name: heading })).toBeInTheDocument();
  });

  it("renders a stable navigation shell", () => {
    renderRoute("/chat");

    expect(screen.getByRole("navigation")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Chat" })).toHaveAttribute("href", "/chat");
    expect(screen.getByRole("link", { name: "Configuration" })).toHaveAttribute(
      "href",
      "/config",
    );
  });
});