import type { ReactNode } from "react";
import { Link, useInRouterContext } from "react-router-dom";

import styles from "./PageHeader.module.css";

type Breadcrumb = {
  label: string;
  href?: string;
};

type PageHeaderProps = {
  title: string;
  description?: string;
  breadcrumbs?: Breadcrumb[];
  action?: ReactNode;
};

export function PageHeader({ title, description, breadcrumbs, action }: PageHeaderProps) {
  const inRouter = useInRouterContext();

  return (
    <header className={styles.header}>
      {breadcrumbs && breadcrumbs.length > 0 ? (
        <nav aria-label="Breadcrumb" className={styles.breadcrumbs}>
          <ol>
            {breadcrumbs.map((breadcrumb, index) => (
              <li key={`${breadcrumb.label}-${index}`}>
                {breadcrumb.href && inRouter ? <Link to={breadcrumb.href}>{breadcrumb.label}</Link> : breadcrumb.href ? <a href={breadcrumb.href}>{breadcrumb.label}</a> : breadcrumb.label}
              </li>
            ))}
          </ol>
        </nav>
      ) : null}
      <div className={styles.titleRow}>
        <div>
          <h1>{title}</h1>
          {description ? <p className={styles.description}>{description}</p> : null}
        </div>
        {action ? <div className={styles.action}>{action}</div> : null}
      </div>
    </header>
  );
}
