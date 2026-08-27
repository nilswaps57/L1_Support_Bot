import { useEffect, useRef, type RefObject } from "react";

import { Alert } from "../../../shared/components/Alert";
import styles from "./DeleteDocumentDialog.module.css";

type DeleteDocumentDialogProps = {
  documentName: string;
  pending: boolean;
  error: string | null;
  returnFocusRef?: RefObject<HTMLButtonElement | null>;
  onCancel: () => void;
  onConfirm: () => void;
};

export function DeleteDocumentDialog({
  documentName,
  pending,
  error,
  returnFocusRef,
  onCancel,
  onConfirm,
}: DeleteDocumentDialogProps) {
  const dialogRef = useRef<HTMLDivElement>(null);
  const cancelRef = useRef<HTMLButtonElement>(null);
  const pendingRef = useRef(pending);
  const onCancelRef = useRef(onCancel);
  pendingRef.current = pending;
  onCancelRef.current = onCancel;

  useEffect(() => {
    cancelRef.current?.focus();

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        if (!pendingRef.current) onCancelRef.current();
        return;
      }
      if (event.key !== "Tab" || !dialogRef.current) return;

      const focusable = Array.from(
        dialogRef.current.querySelectorAll<HTMLElement>(
          "button:not(:disabled), [href], input:not(:disabled), select:not(:disabled), textarea:not(:disabled), [tabindex]:not([tabindex=\"-1\"])",
        ),
      );
      if (focusable.length === 0) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      returnFocusRef?.current?.focus();
    };
  }, [returnFocusRef]);

  return (
    <div className={styles.backdrop}>
      <div
        ref={dialogRef}
        className={styles.dialog}
        role="dialog"
        aria-modal="true"
        aria-labelledby="delete-document-heading"
        aria-describedby="delete-document-description"
      >
        <h2 id="delete-document-heading">Delete {documentName}?</h2>
        <p id="delete-document-description" className={styles.description}>
          This removes the source file and all indexed knowledge for this document.
        </p>
        {error ? <Alert tone="error">{error}</Alert> : null}
        <div className={styles.actions}>
          <button ref={cancelRef} className={styles.cancel} type="button" onClick={onCancel} disabled={pending}>Cancel</button>
          <button className={styles.confirm} type="button" onClick={onConfirm} disabled={pending}>
            {pending ? "Deleting..." : "Confirm delete"}
          </button>
        </div>
      </div>
    </div>
  );
}
