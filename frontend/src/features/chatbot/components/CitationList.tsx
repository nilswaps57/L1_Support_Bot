import type { ChatCitation } from "../api/chat";
import { CitationItem } from "./CitationItem";
import styles from "./CitationList.module.css";

export function CitationList({ citations }: { citations: ChatCitation[] }) {
  if (citations.length === 0) {
    return null;
  }

  return (
    <section className={styles.sources} aria-labelledby="sources-heading">
      <h2 className={styles.heading} id="sources-heading">Sources ({citations.length})</h2>
      <ol className={styles.items} aria-label="Sources">
        {citations.map((citation) => (
          <CitationItem key={citation.chunk_id} citation={citation} />
        ))}
      </ol>
    </section>
  );
}