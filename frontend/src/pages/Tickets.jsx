const items = [
  { title: "New access request", detail: "Waiting for owner assignment", age: "2h" },
  { title: "Pipeline latency", detail: "Investigating ingestion lag", age: "5h" },
  { title: "Catalog naming update", detail: "Needs schema approval", age: "1d" }
];

export default function Tickets() {
  return (
    <section className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Tickets</h1>
          <p className="page-subtitle">
            Track incidents, bugs, and service requests as they move through triage.
          </p>
        </div>
      </div>

      <ul className="list">
        {items.map((item) => (
          <li key={item.title} className="list-item">
            <div>
              <strong>{item.title}</strong>
              <div className="page-subtitle">{item.detail}</div>
            </div>
            <span>Age: {item.age}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
