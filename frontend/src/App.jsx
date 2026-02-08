import { NavLink, Route, Routes } from "react-router-dom";
import Docs from "./pages/Docs.jsx";
import Glossary from "./pages/Glossary.jsx";
import NotFound from "./pages/NotFound.jsx";
import Roadmap from "./pages/Roadmap.jsx";
import StatusDashboard from "./pages/StatusDashboard.tsx";
import Tickets from "./pages/Tickets.jsx";

const navItems = [
  { path: "/", label: "Status" },
  { path: "/tickets", label: "Tickets" },
  { path: "/docs", label: "Docs" },
  { path: "/glossary", label: "Glossary" },
  { path: "/roadmap", label: "Roadmap" }
];

function App() {
  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">SP</div>
          <div>
            <p className="brand-title">Service Portal</p>
            <p className="brand-subtitle">Signals, incidents, and platform requests in one place.</p>
          </div>
        </div>
        <nav className="topbar-nav">
          {navItems.map((item, index) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              style={{ "--i": index }}
              end={item.path === "/"}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="status-chip">
          <span className="status-dot" />
          Environment: Local
        </div>
      </header>

      <div className="layout">
        <main className="content">
          <div className="pulse-card">
            <p className="pulse-card-title">Today&apos;s pulse</p>
            <p className="pulse-card-body">
              Status checks run every 5 minutes. Expect occasional delays during
              maintenance windows.
            </p>
          </div>
          <Routes>
            <Route path="/" element={<StatusDashboard />} />
            <Route path="/tickets" element={<Tickets />} />
            <Route path="/docs" element={<Docs />} />
            <Route path="/glossary" element={<Glossary />} />
            <Route path="/roadmap" element={<Roadmap />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;
