import { useState } from "react";
import Nav from "./components/Nav";
import HomePage from "./pages/HomePage";
import ChatPage from "./pages/ChatPage";
import ResumePage from "./pages/ResumePage";
import DashboardPage from "./pages/DashboardPage";
import "./styles/global.css";

export default function App() {
  const [page, setPage] = useState("Home");

  return (
    <div className="app">
      <Nav page={page} setPage={setPage} />
      {page === "Home"      && <HomePage setPage={setPage} />}
      {page === "Chat"      && <ChatPage />}
      {page === "Resume"    && <ResumePage />}
      {page === "Dashboard" && <DashboardPage />}
    </div>
  );
}
