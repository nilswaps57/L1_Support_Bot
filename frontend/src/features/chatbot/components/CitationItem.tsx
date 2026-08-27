import type { ChatCitation } from "../api/chat";
import styles from "./CitationItem.module.css";

function sourceTypeLabel(sourceType: string | null): string | null {
  if (!sourceType) return null;
  return sourceType.replaceAll("_", " ").replace(/\b\w/g, (character) => character.toUpperCase());
}

function locatorFor(citation: ChatCitation): string {
  if (citation.page_number !== null && citation.page_number !== undefined) {
    return `Page ${citation.page_number}`;
  }
  if (citation.section) return citation.section;
  if (citation.task_code) return `Task ${citation.task_code}`;
  return "Source details";
}

export function CitationItem({ citation }: { citation: ChatCitation }) {
  return (
    <li className={styles.item} aria-label={`Source: ${citation.document_name}`}>
      <details>
        <summary className={styles.summary}>
          <strong className={styles.sourceName}>{citation.document_name}</strong>
          <span className={styles.locator}>{locatorFor(citation)}</span>
        </summary>
        <div className={styles.content}>
          <dl className={styles.metadata}>
            {sourceTypeLabel(citation.source_type) ? (
              <div>
                <dt>Source type</dt>
                <dd>{sourceTypeLabel(citation.source_type)}</dd>
              </div>
            ) : null}
        {citation.page_number !== null && citation.page_number !== undefined ? (
          <div>
            <dt>Page</dt>
                <dd>{citation.page_number}</dd>
          </div>
        ) : null}
        {citation.section ? (
          <div>
            <dt>Section</dt>
            <dd>{citation.section}</dd>
          </div>
        ) : null}
        {citation.task_code ? (
          <div>
            <dt>Task code</dt>
            <dd>Task: {citation.task_code}</dd>
          </div>
        ) : null}
        {citation.screen_name ? (
          <div>
            <dt>Screen</dt>
            <dd>Screen: {citation.screen_name}</dd>
          </div>
        ) : null}
        {citation.error_code ? (
          <div>
            <dt>Error code</dt>
            <dd>Error: {citation.error_code}</dd>
          </div>
        ) : null}
        {citation.jira_id ? (
          <div>
            <dt>JIRA</dt>
            <dd>JIRA: {citation.jira_id}</dd>
          </div>
        ) : null}
            {citation.menu_path ? (
              <div>
                <dt>Menu</dt>
                <dd>{citation.menu_path}</dd>
              </div>
            ) : null}
            {citation.rca_reference ? (
              <div>
                <dt>RCA reference</dt>
                <dd>{citation.rca_reference}</dd>
              </div>
            ) : null}
          </dl>
          {citation.prerequisites.length > 0 ? (
            <p className={styles.context}><strong>Prerequisites:</strong> {citation.prerequisites.join(", ")}</p>
          ) : null}
          {citation.modes.length > 0 ? (
            <p className={styles.context}><strong>Modes:</strong> {citation.modes.join(", ")}</p>
          ) : null}
          {citation.field_names.length > 0 ? (
            <p className={styles.context}><strong>Fields:</strong> {citation.field_names.join(", ")}</p>
          ) : null}
          {citation.procedure_steps.length > 0 ? (
            <div className={styles.context}>
              <strong>Procedure:</strong>
              <ol>
                {citation.procedure_steps.map((step, index) => <li key={`${step}-${index}`}>{step}</li>)}
              </ol>
            </div>
          ) : null}
        </div>
      </details>
    </li>
  );
}