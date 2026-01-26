const terms = [
  { term: "Freshness", detail: "Time since last successful ingestion" },
  { term: "Platform ID", detail: "Primary key for owned services" },
  { term: "SLA", detail: "Service level agreement threshold" }
];

export default function Glossary() {
  return (
    <section className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Glossary</h1>
          <p className="page-subtitle">
            Shared language for platform health, ownership, and requests.
          </p>
        </div>
      </div>

      <ul className="list">
        {terms.map((term) => (
          <li key={term.term} className="list-item">
            <div>
              <strong>{term.term}</strong>
              <div className="page-subtitle">{term.detail}</div>
            </div>
            <span>Active</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
