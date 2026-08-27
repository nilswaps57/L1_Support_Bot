type StatusBadgeProps = {
  label: string;
  tone?: "neutral" | "info" | "success" | "warning" | "error";
  active?: boolean;
};

import styles from "./StatusBadge.module.css";

export function StatusBadge({ label, tone = "neutral", active = false }: StatusBadgeProps) {
  return (
    <span className={`${styles.badge} ${styles[tone]}`}>
      <span className={styles.dot} aria-hidden="true" />
      {label}
      {active ? <span className={styles.srOnly}> in progress</span> : null}
    </span>
  );
}
