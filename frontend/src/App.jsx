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
  const [backendStatus, setBackendStatus] = useState("loading");
  const [mqttHost, setMqttHost] = useState("");
  const [nodeName, setNodeName] = useState("main-ai-node");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function loadStatus() {
    try {
      const response = await fetch("/api/node/status");
      if (!response.ok) {
        throw new Error(`status request failed (${response.status})`);
      }
      const payload = await response.json();
      setBackendStatus(payload.status || "unknown");
      setError("");
    } catch (err) {
      setBackendStatus("offline");
      setError(String(err?.message || err));
    }
  }

  useEffect(() => {
    loadStatus();
    const id = setInterval(loadStatus, 5000);
    return () => clearInterval(id);
  }, []);

  async function onSubmit(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      const response = await fetch("/api/onboarding/initiate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          mqtt_host: mqttHost,
          node_name: nodeName,
        }),
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || `request failed (${response.status})`);
      }
      setBackendStatus(payload.status || "bootstrap_connecting");
    } catch (err) {
      setError(String(err?.message || err));
    } finally {
      setSaving(false);
    }
  }

  const isUnconfigured = backendStatus === "unconfigured";

  return (
    <main className="page">
      <section className="card hero">
        <h1>Synthia AI Node</h1>
        <p className="muted">Node setup and onboarding controls</p>
        <div className="row">
          <ThemeToggle />
          <span className="pill">{backendStatus}</span>
        </div>
        {error ? <p className="error">{error}</p> : null}
      </section>

      {isUnconfigured ? (
        <section className="card setup-card">
          <h2>Setup Node</h2>
          <p className="muted">
            Node is <code>UNCONFIGURED</code>. Enter bootstrap MQTT host to begin onboarding.
          </p>
          <form onSubmit={onSubmit} className="setup-form">
            <label>
              MQTT Host
              <input
                value={mqttHost}
                onChange={(event) => setMqttHost(event.target.value)}
                placeholder="10.0.0.100"
                required
              />
            </label>
            <label>
              Node Name
              <input
                value={nodeName}
                onChange={(event) => setNodeName(event.target.value)}
                placeholder="main-ai-node"
                required
              />
            </label>
            <button className="btn btn-primary" type="submit" disabled={saving}>
              {saving ? "Starting..." : "Start Onboarding"}
            </button>
          </form>
        </section>
      ) : (
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
      )}
    </main>
  );
}
