import { useState, useEffect } from "react";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Nav from "./components/Nav";
import LoginPage from "./pages/LoginPage";
import ChatPage from "./pages/ChatPage";
import ResumePage from "./pages/ResumePage";
import DashboardPage from "./pages/DashboardPage";
import ApplyPage from "./pages/ApplyPage";
import InternalSearchPage from "./pages/InternalSearchPage";
import OnboardingPage from "./pages/OnboardingPage";
import ExitInterviewPage from "./pages/ExitInterviewPage";
import "./styles/global.css";

function AppInner() {
  const { auth } = useAuth();

  // Default page per role
  const defaultPage = auth?.role === "hr" ? "Dashboard" : auth?.role === "candidate" ? "Apply" : "Login";
  const [page, setPage] = useState(defaultPage);

  // When role changes (login/logout) reset page
  useEffect(() => {
    setPage(auth?.role === "hr" ? "Dashboard" : auth?.role === "candidate" ? "Apply" : "Login");
  }, [auth?.role]);

  if (!auth) return <LoginPage />;

  return (
    <div className="app">
      <Nav page={page} setPage={setPage} />

      {/* ── Candidate pages ──────────────────── */}
      {page === "Apply"  && <ApplyPage />}
      {page === "Chat"   && <ChatPage role={auth.role} />}

      {/* ── HR-only pages ────────────────────── */}
      {page === "Dashboard"      && <DashboardPage />}
      {page === "Screen"         && <ResumePage />}
      {page === "InternalSearch" && <InternalSearchPage />}
      {page === "Onboarding"     && <OnboardingPage />}
      {page === "ExitInterview"  && <ExitInterviewPage />}
      {page === "HRChat"         && <ChatPage role="hr" />}
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppInner />
    </AuthProvider>
  );
}
