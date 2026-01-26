import { useEffect, useState } from "react";
import { apiFetch } from "../api/client";

const cards = [
  {
    title: "Databricks status",
    detail: "Core compute and SQL warehouse checks",
    status: "Operating"
  },
  {
    title: "Power BI ingestion",
    detail: "Dataset refresh and Fabric sync",
    status: "Monitoring"
  },
  {
    title: "Service requests",
    detail: "Queue health and triage latency",
    status: "Green"
  },
  {
    title: "Incident desk",
    detail: "On-call coverage and SLA timers",
    status: "Ready"
  }
];

export default function Status() {
  const [health, setHealth] = useState({ state: "loading", message: "Checking API" });

  useEffect(() => {
    let active = true;
    apiFetch("/healthz")
      .then(() => {
        if (active) {
          setHealth({ state: "ok", message: "API reachable" });
        }
      })
      .catch(() => {
        if (active) {
          setHealth({ state: "error", message: "API unavailable" });
        }
      });

    return () => {
      active = false;
    };
  }, []);

  return (
    <section className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Platform status</h1>
          <p className="page-subtitle">
            Live signal board for core systems and ingestion.
          </p>
        </div>
        <div className={`status-pill ${health.state}`}>
          <span className="status-dot" />
          {health.message}
        </div>
      </div>

      <div className="status-grid">
        {cards.map((card, index) => (
          <article key={card.title} className="card" style={{ "--i": index }}>
            <h3>{card.title}</h3>
            <p>{card.detail}</p>
            <p className="meta-value">{card.status}</p>
          </article>
        ))}
      </div>

      <div className="meta-list">
        <div className="meta-item">
          <p className="meta-title">Last successful run</p>
          <p className="meta-value">2024-07-12 09:15 UTC</p>
        </div>
        <div className="meta-item">
          <p className="meta-title">Freshness SLA</p>
          <p className="meta-value">15 min</p>
        </div>
        <div className="meta-item">
          <p className="meta-title">Open incidents</p>
          <p className="meta-value">0 active</p>
        </div>
      </div>
    </section>
  );
}
