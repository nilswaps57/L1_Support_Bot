import { DocumentList } from "../components/DocumentList";
import { DocumentUpload } from "../components/DocumentUpload";

export function DocumentsPage() {
  return (
    <main>
      <h1>Documents</h1>
      <DocumentUpload />
      <DocumentList />
    </main>
  );
}