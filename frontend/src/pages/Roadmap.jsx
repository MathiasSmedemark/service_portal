const milestones = [
  { title: "M0 Walking skeleton", detail: "FastAPI + SPA wiring" },
  { title: "M1 Status MVP", detail: "Databricks-only health signals" },
  { title: "M2 Ticketing MVP", detail: "Requests, incidents, and voting" }
];

export default function Roadmap() {
  return (
    <section className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Roadmap</h1>
          <p className="page-subtitle">
            What is shipping next and which dependencies are in flight.
          </p>
        </div>
      </div>

      <ul className="list">
        {milestones.map((milestone) => (
          <li key={milestone.title} className="list-item">
            <div>
              <strong>{milestone.title}</strong>
              <div className="page-subtitle">{milestone.detail}</div>
            </div>
            <span>Planned</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
