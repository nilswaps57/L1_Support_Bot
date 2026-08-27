import { useId, type ReactNode } from "react";

import styles from "./EmptyState.module.css";

type EmptyStateProps = {
  title: string;
  description: string;
  action?: ReactNode;
};

export function EmptyState({ title, description, action }: EmptyStateProps) {
  const titleId = useId();

  return (
    <section className={styles.emptyState} aria-labelledby={titleId}>
      <div className={styles.marker} aria-hidden="true" />
      <div>
        <h2 id={titleId}>{title}</h2>
        <p>{description}</p>
        {action ? <div className={styles.action}>{action}</div> : null}
      </div>
    </section>
  );
}
