import { DocumentList } from "../components/DocumentList";
import { DocumentUpload } from "../components/DocumentUpload";
import { PageHeader } from "../../../shared/components/PageHeader";
import styles from "./DocumentsPage.module.css";

export function DocumentsPage() {
  return (
    <main className={`appContainer ${styles.page}`}>
      <PageHeader
        title="Documents"
        description="Manage the knowledge sources available to branch support."
        breadcrumbs={[{ label: "Configuration", href: "/config" }, { label: "Documents" }]}
      />
      <section className={styles.uploadRegion} aria-label="Document upload">
        <DocumentUpload />
      </section>
      <section className={styles.documentsRegion} aria-label="Knowledge document management">
        <DocumentList />
      </section>
    </main>
  );
}