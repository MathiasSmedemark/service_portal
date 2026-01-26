import StatusBadge from "./StatusBadge.jsx";
import { STATUS_LABELS, formatTimestamp } from "./statusUtils";

const SUMMARY_COPY = {
  healthy: {
    title: "All systems healthy",
    message: "Status checks are within SLA across the platform.",
    label: STATUS_LABELS.healthy
  },
  degraded: {
    title: "Degraded performance",
    message: "Some platforms are reporting warnings or partial outages.",
    label: STATUS_LABELS.degraded
  },
  critical: {
    title: "Major incident",
    message: "Critical issues detected. Escalation in progress.",
    label: STATUS_LABELS.critical
  },
  stale: {
    title: "Signals delayed",
    message: "Freshness SLA is breached for one or more checks.",
    label: STATUS_LABELS.stale
  },
  unknown: {
    title: "Visibility limited",
    message: "Waiting on fresh status signals from ingestion.",
    label: STATUS_LABELS.unknown
  },
  empty: {
    title: "No status data yet",
    message: "Status checks will appear once ingestion starts.",
    label: STATUS_LABELS.empty
  },
  loading: {
    title: "Loading status signals",
    message: "Pulling the latest checks now.",
    label: STATUS_LABELS.loading
  },
  error: {
    title: "Status feed unavailable",
    message: "We could not reach the status APIs.",
    label: STATUS_LABELS.error
  }
};

export default function StatusSummary({ summary, metrics = [] }) {
  const state = summary?.state || "unknown";
  const copy = SUMMARY_COPY[state] || SUMMARY_COPY.unknown;
  const title = summary?.title || copy.title;
  const message = summary?.message || copy.message;
  const lastUpdated = summary?.lastUpdated ? formatTimestamp(summary.lastUpdated) : "Not available";
  const platformCount = summary?.platformCount ?? 0;
  const fallbackLabels = ["Healthy", "Attention", "Stale signals", "Unknown"];
  const showSkeleton = metrics.length === 0 && state === "loading";

  return (
    <section className={`status-summary ${state}`}>
      <div className="status-summary-header">
        <div>
          <p className="status-summary-eyebrow">Global health</p>
          <h2>{title}</h2>
          <p className="page-subtitle">{message}</p>
        </div>
        <StatusBadge state={state} label={copy.label} />
      </div>
      <div className="status-summary-meta">
        <span>Platforms tracked: {platformCount}</span>
        <span>Last check: {lastUpdated}</span>
      </div>
      <div className="status-metrics">
        {metrics.length === 0
          ? showSkeleton
            ? Array.from({ length: 4 }, (_, index) => (
                <div key={index} className="status-metric skeleton" aria-hidden="true" />
              ))
            : fallbackLabels.map((label) => (
                <div key={label} className="status-metric">
                  <p className="meta-title">{label}</p>
                  <p className="meta-value">-</p>
                </div>
              ))
          : metrics.map((metric) => (
              <div key={metric.label} className="status-metric">
                <p className="meta-title">{metric.label}</p>
                <p className="meta-value">{metric.value}</p>
              </div>
            ))}
      </div>
    </section>
  );
}
