import StatusBadge from "./StatusBadge.jsx";
import { formatTimestamp } from "./statusUtils";

export default function PlatformTile({ summary, isSelected, onSelect }) {
  const platform = summary?.platform;
  const handleClick = () => {
    if (onSelect && platform?.id) {
      onSelect(platform.id);
    }
  };

  return (
    <article
      className={`platform-tile ${isSelected ? "selected" : ""}`.trim()}
      data-selected={isSelected}
    >
      <div className="platform-tile-header">
        <div>
          <p className="platform-eyebrow">{platform?.owner || "Platform owner"}</p>
          <h3>{platform?.name || "Platform"}</h3>
        </div>
        <StatusBadge state={summary?.state} size="sm" />
      </div>
      <p className="platform-note">{summary?.statusNote}</p>
      <div className="platform-meta">
        <div>
          <p className="meta-title">Checks</p>
          <p className="meta-value">{summary?.checkCount ?? 0}</p>
        </div>
        <div>
          <p className="meta-title">Stale</p>
          <p className="meta-value">{summary?.staleCount ?? 0}</p>
        </div>
        <div>
          <p className="meta-title">Last check</p>
          <p className="meta-value">{formatTimestamp(summary?.lastCheckedAt)}</p>
        </div>
      </div>
      <button className="platform-action" type="button" onClick={handleClick}>
        View checks
      </button>
    </article>
  );
}
