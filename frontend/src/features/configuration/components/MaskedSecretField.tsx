import { useState } from "react";

import styles from "../pages/AIConfigurationPage.module.css";

type MaskedSecretFieldProps = {
  configured: boolean;
  onChange: (value: string) => void;
};

export function MaskedSecretField({ configured, onChange }: MaskedSecretFieldProps) {
  const [value, setValue] = useState("");
  return (
    <div className={styles.field}>
      <label htmlFor="api-key">Provider secret</label>
      <input
        id="api-key"
        type="password"
        value={value}
        autoComplete="new-password"
        placeholder={configured ? "Configured secret retained" : "No secret configured"}
        onChange={(event) => {
          const next = event.target.value;
          setValue(next);
          onChange(next);
        }}
      />
      <small>No secret value is returned to this form.</small>
    </div>
  );
}
