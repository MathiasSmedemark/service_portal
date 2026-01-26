import { STATUS_LABELS } from "./statusUtils";

export default function StatusBadge({ state = "unknown", label, size = "md" }) {
  const text = label || STATUS_LABELS[state] || STATUS_LABELS.unknown;

  return (
    <span className={`status-badge ${state} ${size}`.trim()}>
      <span className="status-dot" />
      {text}
    </span>
  );
}
