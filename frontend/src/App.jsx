import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useAuth } from "./auth";
import Layout from "./components/Layout";
import LandingPage from "./pages/LandingPage";
import AuthPage from "./pages/AuthPage";
import Dashboard from "./pages/Dashboard";
import Detector from "./pages/Detector";
import Research from "./pages/Research";
import PaperDetail from "./pages/PaperDetail";
import Reports from "./pages/Reports";
import History from "./pages/History";
import Settings from "./pages/Settings";

function RequireAuth({ children }) {
  const { user, loading } = useAuth();
  const location = useLocation();
  if (loading) return <div className="app-loading"><div className="spinner" /></div>;
  if (!user) return <Navigate to="/login" state={{ from: location }} replace />;
  return children;
}

function GuestOnly({ children }) {
  const { user, loading } = useAuth();
  if (loading) return null;
  if (user) return <Navigate to="/app" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<GuestOnly><AuthPage mode="login" /></GuestOnly>} />
      <Route path="/register" element={<GuestOnly><AuthPage mode="register" /></GuestOnly>} />
      <Route element={<RequireAuth><Layout /></RequireAuth>}>
        <Route path="/app" element={<Dashboard />} />
        <Route path="/app/detector" element={<Detector />} />
        <Route path="/app/research" element={<Research />} />
        <Route path="/app/research/:id" element={<PaperDetail />} />
        <Route path="/app/reports" element={<Reports />} />
        <Route path="/app/history" element={<History />} />
        <Route path="/app/settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
