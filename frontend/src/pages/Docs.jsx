const docs = [
  { title: "Getting started", detail: "Connect to the platform and request access" },
  { title: "Status checks", detail: "Understand the freshness and SLA logic" },
  { title: "Incident playbook", detail: "Steps for escalations and comms" }
];

export default function Docs() {
  return (
    <section className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Docs</h1>
          <p className="page-subtitle">
            Curated guidance for platform users and operators.
          </p>
        </div>
      </div>

      <ul className="list">
        {docs.map((doc) => (
          <li key={doc.title} className="list-item">
            <div>
              <strong>{doc.title}</strong>
              <div className="page-subtitle">{doc.detail}</div>
            </div>
            <span>Draft</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
