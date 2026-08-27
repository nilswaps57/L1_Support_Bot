import styles from "./LoadingSkeleton.module.css";

type LoadingSkeletonProps = {
  variant?: "page" | "conversation" | "table" | "detail";
  label?: string;
};

export function LoadingSkeleton({ variant = "page", label = "Loading" }: LoadingSkeletonProps) {
  return (
    <div className={`${styles.skeleton} ${styles[variant]}`} role="status" aria-label={label}>
      <span className={styles.block} />
      <span className={styles.block} />
      <span className={styles.blockShort} />
    </div>
  );
}
