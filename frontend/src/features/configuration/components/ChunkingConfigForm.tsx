import { useState } from "react";

import { Alert } from "../../../shared/components/Alert";
import { ReindexWarning } from "./ReindexWarning";
import type { ChunkingConfig } from "../api/ai-configuration";
import styles from "../pages/AIConfigurationPage.module.css";

type ChunkingConfigFormProps = { config: ChunkingConfig; disabled?: boolean; busy?: boolean; error?: string; success?: boolean; onSave: (payload: Partial<ChunkingConfig> & { confirm_reindex?: boolean }) => void };

export function ChunkingConfigForm({ config, disabled, busy, error, success, onSave }: ChunkingConfigFormProps) {
  const [target, setTarget] = useState(config.target_chunk_tokens);
  const [confirmed, setConfirmed] = useState(false);
  const changed = target !== config.target_chunk_tokens;
  return (
    <section className={styles.panel} aria-labelledby="chunking-heading">
      <h2 id="chunking-heading">Chunking</h2>
      <p className={styles.help}>Chunk size and overlap affect source coverage and require re-indexing when changed.</p>
      <form className={styles.form} onSubmit={(event) => { event.preventDefault(); onSave({ ...config, target_chunk_tokens: Number(target), confirm_reindex: confirmed }); }}>
        <div className={styles.fields}>
          <div className={styles.field}><label htmlFor="chunking-strategy">Strategy</label><select id="chunking-strategy" value={config.strategy} disabled><option value="SEMANTIC_STRUCTURE">Semantic structure</option><option value="FIXED_SIZE">Fixed size</option></select></div>
          <div className={styles.field}><label htmlFor="chunking-target">Target chunk tokens</label><input id="chunking-target" type="number" min="1" value={target} onChange={(event) => setTarget(Number(event.target.value))} disabled={disabled} /></div>
          <div className={styles.field}><label htmlFor="chunking-overlap">Overlap tokens</label><input id="chunking-overlap" type="number" min="0" value={config.overlap_tokens} disabled /></div>
        </div>
        <ReindexWarning visible={changed} confirmed={confirmed} onConfirm={setConfirmed} />
        {error ? <Alert tone="error">{error}</Alert> : null}
        {success ? <Alert tone="success">Configuration active.</Alert> : null}
        <button className={styles.primary} type="submit" disabled={disabled || busy || (changed && !confirmed)}>Save chunking settings</button>
      </form>
    </section>
  );
}
