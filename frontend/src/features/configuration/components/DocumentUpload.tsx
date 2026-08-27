import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRef, useState } from "react";

import { ApiClientError } from "../../../shared/api/client";
import { uploadDocument } from "../api/documents";
import styles from "./DocumentUpload.module.css";

const MAX_DOCUMENT_SIZE = 10 * 1024 * 1024;
const ACCEPTED_EXTENSIONS = [".pdf", ".docx", ".md"];

function extensionOf(filename: string): string {
  return filename.slice(filename.lastIndexOf(".")).toLowerCase();
}

import { useRuntimeHealth } from "../../../shared/hooks/useRuntimeHealth";
export function DocumentUpload() {
  const health = useRuntimeHealth();
  const unavailable = health.data?.capabilities?.document_management === false;
  const queryClient = useQueryClient();
  const fileInput = useRef<HTMLInputElement>(null);
  const [sourceType, setSourceType] = useState("flexcube_manual");
  const [name, setName] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const mutation = useMutation({
    mutationFn: () => {
      if (!selectedFile) {
        throw new Error("Choose a document to upload.");
      }
      return uploadDocument(selectedFile, sourceType, name);
    },
    onSuccess: (uploaded) => {
      setSuccessMessage(`${uploaded.name} is queued for processing.`);
      setSelectedFile(null);
      setName("");
      if (fileInput.current) {
        fileInput.current.value = "";
      }
      void queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });

  function chooseFile(file: File | undefined) {
    setValidationError(null);
    setSuccessMessage(null);
    mutation.reset();
    if (!file) {
      setSelectedFile(null);
      return;
    }
    if (!ACCEPTED_EXTENSIONS.includes(extensionOf(file.name))) {
      setSelectedFile(null);
      setValidationError("Supported formats are PDF, DOCX, and Markdown.");
      return;
    }
    if (file.size > MAX_DOCUMENT_SIZE) {
      setSelectedFile(null);
      setValidationError("The document exceeds the 10 MB size limit.");
      return;
    }
    setSelectedFile(file);
  }

  const errorMessage = validationError ?? (mutation.error instanceof ApiClientError
    ? mutation.error.payload.message
    : mutation.error?.message ?? null);

  return (
    <section className={styles.section} aria-labelledby="upload-document-heading">
      <h2 className={styles.heading} id="upload-document-heading">Upload document</h2>
      <form className={styles.form}
        onSubmit={(event) => {
          event.preventDefault();
          setSuccessMessage(null);
          mutation.mutate();
        }}
      >
        <div className={styles.fields}>
        <div className={styles.field}>
        <label className={styles.label} htmlFor="document-file">Source file</label>
        <input className={styles.fileInput}
          ref={fileInput}
          id="document-file"
          type="file"
          accept={ACCEPTED_EXTENSIONS.join(",")}
          onChange={(event) => chooseFile(event.target.files?.[0])}
        />
        </div>
        <div className={styles.field}>
        <label htmlFor="document-name">Display name (optional)</label>
        <input className={styles.input}
          id="document-name"
          value={name}
          onChange={(event) => setName(event.target.value)}
          placeholder="Use the source filename"
        />
        </div>
        <div className={styles.field}>
        <label htmlFor="document-source-type">Source type</label>
        <select className={styles.select}
          id="document-source-type"
          value={sourceType}
          onChange={(event) => setSourceType(event.target.value)}
        >
          <option value="flexcube_manual">FLEXCUBE manual</option>
          <option value="rca">RCA</option>
          <option value="procedure">Procedure</option>
          <option value="jira_export">JIRA export</option>
          <option value="other">Other</option>
        </select>
        </div>
        </div>
        <button className={styles.submit} type="submit" disabled={!selectedFile || mutation.isPending || unavailable}>
          {mutation.isPending ? "Uploading..." : "Upload"}
        </button>
      </form>
      <p className={styles.helper}>Supported formats: PDF, DOCX, Markdown. Maximum size: 10 MB.</p>
      {errorMessage && <p role="alert">{errorMessage}</p>}
      {successMessage && <p role="status">{successMessage}</p>}
      {unavailable ? <p role="status">Document management is temporarily unavailable in limited mode.</p> : null}
    </section>
  );
}