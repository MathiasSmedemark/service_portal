import { formatDateRange } from "./statusUtils";

export default function StatusMessageBanner({ message }) {
  const severity = message?.severity || "info";
  const windowLabel = formatDateRange(message?.start_at, message?.end_at);

  return (
    <article className={`status-message ${severity}`}>
      <div className="status-message-header">
        <span className="status-message-eyebrow">{severity.toUpperCase()}</span>
        {message?.scope ? <span className="status-message-scope">{message.scope}</span> : null}
      </div>
      <h3>{message?.title}</h3>
      <p>{message?.body_md}</p>
      {windowLabel ? <p className="status-message-window">{windowLabel}</p> : null}
    </article>
  );
}
