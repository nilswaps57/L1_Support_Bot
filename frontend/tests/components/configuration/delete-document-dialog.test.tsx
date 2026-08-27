import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useRef, useState } from "react";
import { describe, expect, it } from "vitest";

import { DeleteDocumentDialog } from "../../../src/features/configuration/components/DeleteDocumentDialog";

function DialogHarness() {
  const [open, setOpen] = useState(false);
  const triggerRef = useRef<HTMLButtonElement>(null);

  return (
    <>
      <button ref={triggerRef} type="button" onClick={() => setOpen(true)}>Open delete dialog</button>
      {open ? (
        <DeleteDocumentDialog
          documentName="manual.md"
          pending={false}
          error={null}
          returnFocusRef={triggerRef}
          onCancel={() => setOpen(false)}
          onConfirm={() => setOpen(false)}
        />
      ) : null}
    </>
  );
}

describe("DeleteDocumentDialog accessibility", () => {
  it("focuses safe action, traps tab order, and returns focus on Escape", async () => {
    const user = userEvent.setup();
    render(<DialogHarness />);

    await user.click(screen.getByRole("button", { name: "Open delete dialog" }));
    expect(screen.getByRole("button", { name: "Cancel" })).toHaveFocus();

    await user.tab();
    expect(screen.getByRole("button", { name: "Confirm delete" })).toHaveFocus();
    await user.tab();
    expect(screen.getByRole("button", { name: "Cancel" })).toHaveFocus();

    await user.keyboard("{Escape}");
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Open delete dialog" })).toHaveFocus();
  });
});
