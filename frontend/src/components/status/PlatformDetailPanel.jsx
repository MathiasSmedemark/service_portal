import StatusBadge from "./StatusBadge.jsx";
import { formatTimestamp } from "./statusUtils";

export default function PlatformDetailPanel({ summary, messages = [] }) {
  if (!summary) {
    return (
      <section className="platform-detail empty">
        <h3>Platform drilldown</h3>
        <p className="page-subtitle">
          Select a platform tile to review checks, freshness, and status messages.
        </p>
      </section>
    );
  }

  const platform = summary.platform;

  return (
    <section className="platform-detail">
      <div className="platform-detail-header">
        <div>
          <p className="platform-eyebrow">{platform.owner}</p>
          <h3>{platform.name}</h3>
          <p className="page-subtitle">{summary.statusNote}</p>
        </div>
        <StatusBadge state={summary.state} />
      </div>

      <div className="platform-detail-grid">
        <div>
          <h4>Latest checks</h4>
          {summary.checks.length === 0 ? (
            <p className="page-subtitle">No checks have been reported for this platform.</p>
          ) : (
            <ul className="platform-checks">
              {summary.checks.map((check) => (
                <li key={check.id} className="platform-check">
                  <div>
                    <strong>{check.name}</strong>
                    <p className="page-subtitle">{check.message || "No additional context."}</p>
                  </div>
                  <div className="platform-check-meta">
                    <StatusBadge state={check.derivedState} size="sm" />
                    <span>{formatTimestamp(check.checked_at)}</span>
                    <span>
                      Freshness {check.freshness_minutes ?? "-"}m / SLA {check.sla_minutes ?? "-"}m
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
        <div>
          <h4>Messages</h4>
          {messages.length === 0 ? (
            <p className="page-subtitle">No active messages for this platform.</p>
          ) : (
            <ul className="platform-messages">
              {messages.map((message) => (
                <li key={message.id} className={`platform-message ${message.severity}`}>
                  <strong>{message.title}</strong>
                  <p>{message.body_md}</p>
                  <span>{formatTimestamp(message.created_at)}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </section>
  );
}
