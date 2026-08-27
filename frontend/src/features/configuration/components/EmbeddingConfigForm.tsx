import { useEffect, useState } from "react";

import { Alert } from "../../../shared/components/Alert";
import { MaskedSecretField } from "./MaskedSecretField";
import { ReindexWarning } from "./ReindexWarning";
import type { EmbeddingConfig, EmbeddingConfigUpdate } from "../api/ai-configuration";
import styles from "../pages/AIConfigurationPage.module.css";

type EmbeddingConfigFormProps = {
  config: EmbeddingConfig;
  disabled?: boolean;
  busy?: boolean;
  error?: string;
  success?: boolean;
  onSave: (payload: EmbeddingConfigUpdate) => void;
  onValidate: (payload: EmbeddingConfigUpdate) => void;
};

export function EmbeddingConfigForm({ config, disabled, busy, error, success, onSave, onValidate }: EmbeddingConfigFormProps) {
  const [model, setModel] = useState(config.model);
  const [provider, setProvider] = useState(config.provider);
  const [secret, setSecret] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  useEffect(() => { setModel(config.model); setProvider(config.provider); setConfirmed(false); }, [config.model, config.provider]);
  const changed = model !== config.model || provider !== config.provider;
  const payload = (): EmbeddingConfigUpdate => ({
    provider, model, model_version: config.model_version, dimensions: config.dimensions,
    distance_method: config.distance_method, batch_size: config.batch_size,
    timeout_seconds: config.timeout_seconds, index_compat_id: `${provider}:${model}:${config.model_version}:${config.dimensions}`,
    ...(secret ? { api_key: secret } : {}), confirm_reindex: confirmed,
  });
  return (
    <section className={styles.panel} aria-labelledby="embedding-heading">
      <h2 id="embedding-heading">Embeddings</h2>
      <p className={styles.help}>Embedding model, dimensions, and chunk boundaries determine index compatibility.</p>
      <form className={styles.form} onSubmit={(event) => { event.preventDefault(); onSave(payload()); }}>
        <div className={styles.fields}>
          <div className={styles.field}><label htmlFor="embedding-provider">Provider</label><input id="embedding-provider" value={provider} onChange={(event) => setProvider(event.target.value)} disabled={disabled} /></div>
          <div className={styles.field}><label htmlFor="embedding-model">Embedding model</label><input id="embedding-model" value={model} onChange={(event) => setModel(event.target.value)} disabled={disabled} /></div>
          <div className={styles.field}><label htmlFor="embedding-dimensions">Dimensions</label><input id="embedding-dimensions" type="number" value={config.dimensions} disabled /></div>
          <div className={styles.field}><label htmlFor="embedding-batch">Batch size</label><input id="embedding-batch" type="number" value={config.batch_size} disabled /></div>
        </div>
        <MaskedSecretField configured={config.api_key_configured} onChange={setSecret} />
        <ReindexWarning visible={changed} confirmed={confirmed} onConfirm={setConfirmed} />
        {error ? <Alert tone="error">{error}</Alert> : null}
        {success ? <Alert tone="success">Configuration active.</Alert> : null}
        <div className={styles.actions}>
          <button className={styles.primary} type="submit" disabled={disabled || busy || (changed && !confirmed)}>Save embedding settings</button>
          <button className={styles.secondary} type="button" disabled={disabled || busy} onClick={() => onValidate(payload())}>Test connectivity</button>
        </div>
      </form>
    </section>
  );
}
