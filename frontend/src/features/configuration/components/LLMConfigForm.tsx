import { useEffect, useState } from "react";

import { Alert } from "../../../shared/components/Alert";
import { MaskedSecretField } from "./MaskedSecretField";
import type { LLMConfig, LLMConfigUpdate } from "../api/ai-configuration";
import styles from "../pages/AIConfigurationPage.module.css";

type LLMConfigFormProps = {
  config: LLMConfig;
  disabled?: boolean;
  busy?: boolean;
  error?: string;
  success?: boolean;
  onSave: (payload: LLMConfigUpdate) => void;
  onValidate: (payload: LLMConfigUpdate) => void;
};

export function LLMConfigForm({ config, disabled, busy, error, success, onSave, onValidate }: LLMConfigFormProps) {
  const [model, setModel] = useState(config.model);
  const [provider, setProvider] = useState(config.provider);
  const [endpoint, setEndpoint] = useState("");
  const [secret, setSecret] = useState("");
  useEffect(() => { setModel(config.model); setProvider(config.provider); }, [config.model, config.provider]);
  const payload = (): LLMConfigUpdate => ({
    provider, model, temperature: config.temperature, max_tokens: config.max_tokens,
    context_window: config.context_window, timeout_seconds: config.timeout_seconds,
    max_retries: config.max_retries, label: config.label ?? undefined,
    ...(endpoint ? { endpoint } : {}), ...(secret ? { api_key: secret } : {}),
  });
  return (
    <section className={styles.panel} aria-labelledby="llm-heading">
      <h2 id="llm-heading">Language model</h2>
      <p className={styles.help}>Provider and model changes are checked for connectivity before activation.</p>
      <form className={styles.form} onSubmit={(event) => { event.preventDefault(); onSave(payload()); }}>
        <div className={styles.fields}>
          <div className={styles.field}><label htmlFor="llm-provider">Provider</label><input id="llm-provider" value={provider} onChange={(event) => setProvider(event.target.value)} disabled={disabled} /></div>
          <div className={styles.field}><label htmlFor="llm-model">Model</label><input id="llm-model" value={model} onChange={(event) => setModel(event.target.value)} disabled={disabled} /></div>
          <div className={styles.field}><label htmlFor="llm-endpoint">Endpoint reference</label><input id="llm-endpoint" value={endpoint} placeholder="Configured endpoint retained" onChange={(event) => setEndpoint(event.target.value)} disabled={disabled} /></div>
          <div className={styles.field}><label htmlFor="llm-timeout">Timeout seconds</label><input id="llm-timeout" type="number" min="1" max="600" value={config.timeout_seconds} disabled /></div>
        </div>
        <MaskedSecretField configured={config.api_key_configured} onChange={setSecret} />
        {error ? <Alert tone="error">{error}</Alert> : null}
        {success ? <Alert tone="success">Configuration active.</Alert> : null}
        <div className={styles.actions}>
          <button className={styles.primary} type="submit" disabled={disabled || busy}>Save language model</button>
          <button className={styles.secondary} type="button" disabled={disabled || busy} onClick={() => onValidate(payload())}>Test connectivity</button>
        </div>
      </form>
    </section>
  );
}
