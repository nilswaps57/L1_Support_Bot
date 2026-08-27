export type IngestionWarning = {
  element_type: string;
  description: string;
  page_number?: number | null;
};

export function IngestionWarnings({ warnings }: { warnings: IngestionWarning[] }) {
  if (warnings.length === 0) return null;
  return (
    <section aria-label="Ingestion warnings">
      <h4>Content warnings</h4>
      <ul>
        {warnings.map((warning, index) => (
          <li key={`${warning.element_type}-${warning.page_number ?? "na"}-${index}`}>
            {warning.description}
            {warning.page_number ? ` (page ${warning.page_number})` : ""}
          </li>
        ))}
      </ul>
    </section>
  );
}
