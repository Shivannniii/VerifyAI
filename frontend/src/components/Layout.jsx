import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { Bell, ChevronLeft, ChevronRight, FileCheck2, FileText, History as HistoryIcon, LayoutDashboard, LogOut, Moon, Search, Settings, Sun, Sparkles } from "lucide-react";
import { useState } from "react";
import { useAuth } from "../auth";
import Logo from "./Logo";

const nav = [
  ["/app", "Dashboard", LayoutDashboard],
  ["/app/detector", "AI Detector", Sparkles],
  ["/app/research", "Research Verification", FileCheck2],
  ["/app/reports", "Reports", FileText],
  ["/app/history", "History", HistoryIcon],
];

export default function Layout() {
  const { user, logout } = useAuth();
  const [collapsed, setCollapsed] = useState(false);
  const [dark, setDark] = useState(document.documentElement.dataset.theme === "dark");
  const navigate = useNavigate();
  const initials = (user?.email || "SV").slice(0,2).toUpperCase();

  function toggleTheme() {
    const next = !dark;
    setDark(next);
    document.documentElement.dataset.theme = next ? "dark" : "light";
    localStorage.setItem("verifyai_theme", next ? "dark" : "light");
  }

  return (
    <div className="app-shell">
      <aside className={`sidebar ${collapsed ? "collapsed" : ""}`}>
        <div className="sidebar-head">
          <NavLink to="/app"><Logo compact={collapsed} /></NavLink>
          <button className="sidebar-toggle" onClick={() => setCollapsed(v => !v)} aria-label="Toggle sidebar">
            {collapsed ? <ChevronRight size={16}/> : <ChevronLeft size={16}/>} 
          </button>
        </div>
        <div className="nav-section">
          <div className="workspace-label">Workspace</div>
          <nav className="nav-list">
            {nav.map(([to,label,Icon]) => <NavLink key={to} to={to} end={to === "/app"} className={({isActive}) => `nav-item ${isActive ? "active" : ""}`}><Icon size={17}/><span className="nav-label">{label}</span></NavLink>)}
          </nav>
        </div>
        <div className="sidebar-bottom">
          <NavLink to="/app/settings" className={({isActive}) => `nav-item ${isActive ? "active" : ""}`}><Settings size={17}/><span className="nav-label">Settings</span></NavLink>
          <div className="profile-mini">
            <div className="avatar">{initials}</div>
            <div className="profile-info"><strong>{user?.email || "Demo user"}</strong><span>VerifyAI workspace</span></div>
          </div>
          <button className="nav-item" onClick={() => { logout(); navigate("/"); }}><LogOut size={17}/><span className="nav-label">Log out</span></button>
        </div>
      </aside>
      <main className="app-main">
        <header className="topbar">
          <div className="search-box"><Search size={15}/><input placeholder="Search your workspace..." /></div>
          <div className="top-actions">
            <button className="icon-btn" aria-label="Notifications"><Bell size={16}/></button>
            <button className="icon-btn" onClick={toggleTheme} aria-label="Toggle theme">{dark ? <Sun size={16}/> : <Moon size={16}/>}</button>
            <div className="avatar">{initials}</div>
          </div>
        </header>
        <Outlet />
      </main>
    </div>
  );
}
