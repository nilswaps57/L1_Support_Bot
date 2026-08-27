import { useState } from "react";
import { BrowserRouter, Link, NavLink, Navigate, Outlet, Route, Routes } from "react-router-dom";

import { DocumentsPage } from "../features/configuration/pages/DocumentsPage";
import { ChatPage } from "../features/chatbot/pages/ChatPage";
import { AIConfigurationPage } from "../features/configuration/pages/AIConfigurationPage";
import { PageHeader } from "../shared/components/PageHeader";
import { DegradedModeBanner } from "../shared/components/DegradedModeBanner";
import { useRuntimeHealth } from "../shared/hooks/useRuntimeHealth";
import styles from "./router.module.css";

function AppShell() {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const health = useRuntimeHealth();
  const linkClassName = ({ isActive }: { isActive: boolean }) =>
    `${styles.navLink} ${isActive ? styles.navLinkActive : ""}`;

  return (
    <div className={styles.shell}>
      <header className={styles.topbar}>
        <button
          className={styles.mobileMenuButton}
          type="button"
          aria-expanded={mobileNavOpen}
          aria-controls="primary-navigation"
          onClick={() => setMobileNavOpen((open) => !open)}
        >
          Menu
        </button>
        <span className={styles.mobileTitle}>L1 Support Bot</span>
      </header>
      <aside className={`${styles.rail} ${mobileNavOpen ? styles.railOpen : ""}`}>
        <Link className={styles.brand} to="/chat" onClick={() => setMobileNavOpen(false)}>
          <span className={styles.brandMark} aria-hidden="true">L1</span>
          <span>L1 Support Bot</span>
        </Link>
        <nav id="primary-navigation" className={styles.nav} aria-label="Primary navigation">
          <div className={styles.navGroup}>
            <p className={styles.navLabel}>Branch User Chatbot</p>
            <NavLink className={linkClassName} to="/chat" onClick={() => setMobileNavOpen(false)}>
              Chat
            </NavLink>
          </div>
          <div className={styles.navGroup}>
            <p className={styles.navLabel}>Configuration</p>
            <NavLink end className={linkClassName} to="/config" onClick={() => setMobileNavOpen(false)}>
              Configuration
            </NavLink>
            <NavLink className={linkClassName} to="/config/documents" onClick={() => setMobileNavOpen(false)}>
              Documents
            </NavLink>
            <NavLink className={linkClassName} to="/config/ai" onClick={() => setMobileNavOpen(false)}>
              AI configuration
            </NavLink>
          </div>
        </nav>
      </aside>
      <div className={styles.content}>
        {health.data?.status === "degraded" ? (
          <DegradedModeBanner onRetry={() => void health.refetch()} />
        ) : null}
        <Outlet />
      </div>
    </div>
  );
}

function PageBoundary({ title }: { title: string }) {
  return (
    <main className="appContainer">
      <PageHeader title={title} />
    </main>
  );
}

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/config" element={<PageBoundary title="Configuration" />} />
        <Route path="/config/documents" element={<DocumentsPage />} />
        <Route path="/config/ai" element={<AIConfigurationPage />} />
        <Route path="/" element={<Navigate replace to="/chat" />} />
        <Route path="*" element={<Navigate replace to="/chat" />} />
      </Route>
    </Routes>
  );
}

export function AppRouter() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}