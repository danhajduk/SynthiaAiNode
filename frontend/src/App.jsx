import { useEffect, useState } from "react";
import { getTheme, setTheme } from "./theme/theme";
import "./app.css";

function ThemeToggle() {
  const [theme, setLocalTheme] = useState(getTheme());

  function toggleTheme() {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    setLocalTheme(next);
  }

  return (
    <button className="btn btn-primary" onClick={toggleTheme}>
      Theme: {theme}
    </button>
  );
}

export default function App() {
  const [backendStatus, setBackendStatus] = useState("unknown");

  useEffect(() => {
    setBackendStatus("running (service-managed)");
  }, []);

  return (
    <main className="page">
      <section className="card hero">
        <h1>Synthia AI Node</h1>
        <p className="muted">Frontend aligned to Core theme tokens and components.</p>
        <div className="row">
          <ThemeToggle />
          <span className="pill">{backendStatus}</span>
        </div>
      </section>

      <section className="grid">
        <article className="card">
          <h2>Onboarding</h2>
          <p className="muted">Bootstrap, registration, approval, trust activation.</p>
        </article>
        <article className="card">
          <h2>Runtime</h2>
          <p className="muted">Operational handoff, degraded recovery, telemetry.</p>
        </article>
        <article className="card">
          <h2>Service</h2>
          <p className="muted">
            Controlled with user systemd units:
            <br />
            <code>synthia-ai-node-backend.service</code>
            <br />
            <code>synthia-ai-node-frontend.service</code>
          </p>
        </article>
      </section>
    </main>
  );
}
