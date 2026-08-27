import { useState } from "react";

import { Alert } from "../../../shared/components/Alert";
import type { RetrievalConfig } from "../api/ai-configuration";
import styles from "../pages/AIConfigurationPage.module.css";

type RetrievalConfigFormProps = { config: RetrievalConfig; disabled?: boolean; busy?: boolean; error?: string; success?: boolean; onSave: (payload: Partial<RetrievalConfig>) => void };

export function RetrievalConfigForm({ config, disabled, busy, error, success, onSave }: RetrievalConfigFormProps) {
  const [threshold, setThreshold] = useState(config.similarity_threshold);
  const [dense, setDense] = useState(config.dense_weight);
  const [sparse, setSparse] = useState(config.sparse_weight);
  return (
    <section className={styles.panel} aria-labelledby="retrieval-heading">
      <h2 id="retrieval-heading">Retrieval</h2>
      <p className={styles.help}>Thresholds and weighting affect evidence quality. Changes apply to new requests after activation.</p>
      <form className={styles.form} onSubmit={(event) => { event.preventDefault(); onSave({ ...config, similarity_threshold: Number(threshold), dense_weight: Number(dense), sparse_weight: Number(sparse) }); }}>
        <div className={styles.fields}>
          <div className={styles.field}><label htmlFor="retrieval-threshold">Similarity threshold</label><input id="retrieval-threshold" type="number" min="0" max="1" step="0.01" value={threshold} onChange={(event) => setThreshold(Number(event.target.value))} disabled={disabled} /></div>
          <div className={styles.field}><label htmlFor="retrieval-dense">Dense weight</label><input id="retrieval-dense" type="number" min="0" max="1" step="0.05" value={dense} onChange={(event) => setDense(Number(event.target.value))} disabled={disabled} /></div>
          <div className={styles.field}><label htmlFor="retrieval-sparse">Sparse weight</label><input id="retrieval-sparse" type="number" min="0" max="1" step="0.05" value={sparse} onChange={(event) => setSparse(Number(event.target.value))} disabled={disabled} /></div>
          <div className={styles.field}><label htmlFor="retrieval-final-top-k">Final context chunks</label><input id="retrieval-final-top-k" type="number" min="1" value={config.final_top_k} disabled /></div>
        </div>
        {error ? <Alert tone="error">{error}</Alert> : null}
        {success ? <Alert tone="success">Configuration active.</Alert> : null}
        <button className={styles.primary} type="submit" disabled={disabled || busy || Math.abs(Number(dense) + Number(sparse) - 1) > 0.001}>Save retrieval settings</button>
      </form>
    </section>
  );
}
