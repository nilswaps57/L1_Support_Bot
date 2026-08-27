export type IngestionWarning = {
  element_type: string;
  description: string;
  page_number?: number | null;
};

import styles from "./IngestionWarnings.module.css";

export function IngestionWarnings({ warnings }: { warnings: IngestionWarning[] }) {
  if (warnings.length === 0) return null;
  return (
    <section className={styles.warnings} aria-label="Ingestion warnings">
      <details>
        <summary className={styles.summary}>Content warnings ({warnings.length})</summary>
        <ul className={styles.list}>
        {warnings.map((warning, index) => (
          <li className={styles.item} key={`${warning.element_type}-${warning.page_number ?? "na"}-${index}`}>
            {warning.description}
            {warning.page_number !== null && warning.page_number !== undefined ? ` (page ${warning.page_number})` : ""}
          </li>
        ))}
        </ul>
      </details>
    </section>
  );
}
