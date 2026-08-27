import type { ReactNode } from "react";

import styles from "./Alert.module.css";

type AlertTone = "info" | "success" | "warning" | "error";

type AlertProps = {
  tone: AlertTone;
  children: ReactNode;
  title?: string;
  role?: "alert" | "status";
};

export function Alert({ tone, children, title, role }: AlertProps) {
  const liveRole = role ?? (tone === "error" ? "alert" : "status");
  return (
    <div className={`${styles.alert} ${styles[tone]}`} role={liveRole}>
      <span className={styles.indicator} aria-hidden="true" />
      <div>
        {title ? <strong className={styles.title}>{title}</strong> : null}
        <div>{children}</div>
      </div>
    </div>
  );
}
