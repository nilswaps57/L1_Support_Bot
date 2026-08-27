import { BrowserRouter, Link, NavLink, Navigate, Outlet, Route, Routes } from "react-router-dom";

import { DocumentsPage } from "../features/configuration/pages/DocumentsPage";
import { ChatPage } from "../features/chatbot/pages/ChatPage";

function AppShell() {
  return (
    <div>
      <header>
        <Link to="/chat">L1 Support Bot</Link>
        <nav aria-label="Primary navigation">
          <NavLink to="/chat">Chat</NavLink>
          <NavLink to="/config">Configuration</NavLink>
        </nav>
      </header>
      <Outlet />
    </div>
  );
}

function PageBoundary({ title }: { title: string }) {
  return (
    <main>
      <h1>{title}</h1>
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
        <Route path="/config/ai" element={<PageBoundary title="AI configuration" />} />
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