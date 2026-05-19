import { CardHeader, HealthIndicator, StageBadge } from "../../components/uiPrimitives";
import { OperationalShell } from "./OperationalShell";
import { NodeHealthStrip } from "./NodeHealthStrip";
import { DegradedStateBanner } from "./DegradedStateBanner";
import { NodeOverviewCard } from "./cards/NodeOverviewCard";
import { CapabilitySummaryCard } from "./cards/CapabilitySummaryCard";
import { ProviderRefreshCard } from "./cards/ProviderRefreshCard";
import { ResolvedTasksCard } from "./cards/ResolvedTasksCard";
import { RuntimeServicesCard } from "./cards/RuntimeServicesCard";
import { RecentActivityCard } from "./cards/RecentActivityCard";
import { ClientCostCard } from "./cards/ClientCostCard";
import { OperationalActionsCard } from "./cards/OperationalActionsCard";
import { ScheduledTasksSection } from "./ScheduledTasksSection";
import { DiagnosticsPage } from "../diagnostics/DiagnosticsPage";

function maskOnboardingRef(value) {
  const normalized = String(value || "").trim();
  if (!normalized) {
    return "none";
  }
  if (normalized === "operational") {
    return normalized;
  }
  if (normalized.length <= 7) {
    return `**********${normalized}`;
  }
  return `**********${normalized.slice(-7)}`;
}

function getTelemetryAgeSeconds(value) {
  const normalized = String(value || "").trim();
  if (!normalized) {
    return null;
  }
  const parsed = Date.parse(normalized);
  if (Number.isNaN(parsed)) {
    return null;
  }
  return Math.max(0, Math.floor((Date.now() - parsed) / 1000));
}

function formatTelemetryAge(value) {
  if (value === null || value === undefined) {
    return "none";
  }
  if (value < 60) {
    return `${value}s`;
  }
  if (value < 3600) {
    return `${Math.floor(value / 60)}m`;
  }
  if (value < 86400) {
    return `${Math.floor(value / 3600)}h`;
  }
  return `${Math.floor(value / 86400)}d`;
}

function telemetryFreshnessFromAge(ageSeconds, connected) {
  if (!connected) {
    return "offline";
  }
  if (ageSeconds === null) {
    return "unknown";
  }
  if (ageSeconds <= 300) {
    return "fresh";
  }
  if (ageSeconds <= 1800) {
    return "stale";
  }
  return "inactive";
}

function formatMetricValue(value, suffix = "") {
  if (value === null || value === undefined || value === "") {
    return "pending";
  }
  const numberValue = Number(value);
  if (!Number.isFinite(numberValue)) {
    return String(value);
  }
  return `${numberValue.toLocaleString(undefined, { maximumFractionDigits: 2 })}${suffix}`;
}

function LocalLLMBenchmarkTable({ summary }) {
  const comparisons = Array.isArray(summary?.comparisons) ? summary.comparisons : [];
  const rows = comparisons.flatMap((comparison) => {
    const localResults = Array.isArray(comparison?.local_results) ? comparison.local_results : [];
    const base = {
      recordId: comparison?.record_id,
      prompt: comparison?.prompt_id || comparison?.task_family || "unattributed",
      openaiModel: comparison?.openai?.model_id || "openai",
      openaiLabel: comparison?.openai?.label || "none",
      openaiTokens: comparison?.openai?.usage?.total_tokens,
      openaiLatency: comparison?.openai?.latency_ms,
      snippet: comparison?.input_snippet || "",
    };
    if (!localResults.length) {
      return [{ ...base, localModel: "pending", status: "pending" }];
    }
    return localResults.map((result) => ({
      ...base,
      localModel: result?.model_id || "local",
      status: result?.status || "unknown",
      localLabel: result?.label || "none",
      localTokens: result?.total_tokens,
      localLatency: result?.latency_ms,
      vram: result?.vram_delta_mib ?? result?.vram_used_mib,
      error: result?.error,
    }));
  });

  return (
    <article className="card operational-card-full-span">
      <CardHeader title="Local LLM Benchmarks" subtitle="OpenAI calls replayed against the local model rotation." />
      <div className="client-usage-summary-grid">
        <div className="client-usage-metric-block">
          <strong>{formatMetricValue(summary?.status_counts?.pending || 0)}</strong>
          <span>Pending</span>
        </div>
        <div className="client-usage-metric-block">
          <strong>{formatMetricValue(summary?.status_counts?.completed || 0)}</strong>
          <span>Completed</span>
        </div>
        <div className="client-usage-metric-block">
          <strong>{formatMetricValue(summary?.status_counts?.failed || 0)}</strong>
          <span>Failed</span>
        </div>
      </div>
      <div className="client-usage-table-card">
        <div className="client-usage-table-wrap">
          <table className="client-usage-table local-llm-benchmark-table">
            <thead>
              <tr>
                <th>Prompt</th>
                <th>OpenAI</th>
                <th>Local Model</th>
                <th>Status</th>
                <th>Label</th>
                <th>Tokens</th>
                <th>Latency</th>
                <th>VRAM</th>
              </tr>
            </thead>
            <tbody>
              {rows.length ? (
                rows.map((row) => (
                  <tr key={`${row.recordId}-${row.localModel}`}>
                    <td>
                      <code>{row.prompt}</code>
                      {row.snippet ? <span className="muted tiny benchmark-snippet">{row.snippet}</span> : null}
                    </td>
                    <td>
                      <code>{row.openaiModel}</code>
                    </td>
                    <td>
                      <code>{row.localModel}</code>
                    </td>
                    <td>
                      <StageBadge value={row.status} />
                      {row.error ? <span className="error tiny benchmark-snippet">{row.error}</span> : null}
                    </td>
                    <td>
                      <code>{row.openaiLabel}</code>
                      <span className="muted tiny benchmark-snippet">{row.localLabel || "pending"}</span>
                    </td>
                    <td>
                      <code>{formatMetricValue(row.openaiTokens)}</code>
                      <span className="muted tiny benchmark-snippet">{formatMetricValue(row.localTokens)}</span>
                    </td>
                    <td>
                      <code>{formatMetricValue(row.openaiLatency, " ms")}</code>
                      <span className="muted tiny benchmark-snippet">{formatMetricValue(row.localLatency, " ms")}</span>
                    </td>
                    <td>
                      <code>{formatMetricValue(row.vram, " MiB")}</code>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="8" className="muted">
                    No OpenAI benchmark records have been captured yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </article>
  );
}

export function OperationalDashboard({
  currentSection,
  sections = [],
  healthStripProps,
  degradedBanner,
  overviewCardProps,
  coreConnection,
  runtimeHealth,
  capabilitySummaryProps,
  providerRefreshProps,
  resolvedTasks = [],
  runtimeServicesProps,
  operationalActions,
  activityItems = [],
  clientCostItems = [],
  clientUsageMonth = "",
  localLlmBenchmarkSummary = null,
  governanceStatus = null,
  scheduledTasksProps = null,
  onboardingSteps = [],
  onboardingProgress = {},
  pendingApprovalNodeId,
  diagnosticsProps,
}) {
  const telemetryAgeSeconds = getTelemetryAgeSeconds(runtimeHealth?.lastTelemetryTimestamp);
  const telemetryFreshness = telemetryFreshnessFromAge(telemetryAgeSeconds, coreConnection?.connected);

  return (
    <OperationalShell
      currentSection={currentSection}
      sections={sections}
      healthStrip={<NodeHealthStrip {...healthStripProps} />}
    >
      <section className="grid operational-dashboard-grid">
        {degradedBanner ? <DegradedStateBanner {...degradedBanner} /> : null}

        {currentSection === "overview" ? (
          <>
            <NodeOverviewCard {...overviewCardProps} />
            {coreConnection?.show ? (
              <article className="card">
                <CardHeader title="Core Connection" subtitle="Trusted Core endpoint metadata and current onboarding linkage." />
                <div className="state-grid">
                  <span>Core ID</span>
                  <code>{coreConnection.pairedCoreId}</code>
                  <span>Core API</span>
                  <code>{coreConnection.coreApiEndpoint || "unavailable"}</code>
                  <span>Operational MQTT</span>
                  <code>
                    {coreConnection.operationalMqttAddress || (coreConnection.connected ? "connected" : "unavailable")}
                  </code>
                  <span>Connection</span>
                  <HealthIndicator value={coreConnection.connected ? "connected" : "disconnected"} />
                  <span>Onboarding Ref</span>
                  <code>{maskOnboardingRef(coreConnection.onboardingReference)}</code>
                  <span>Telemetry Freshness</span>
                  <HealthIndicator value={telemetryFreshness} />
                  <span>Telemetry Age</span>
                  <code>{formatTelemetryAge(telemetryAgeSeconds)}</code>
                </div>
              </article>
            ) : null}
            <OperationalActionsCard {...operationalActions} />
          </>
        ) : null}

        {currentSection === "capabilities" ? (
          <>
            <CapabilitySummaryCard {...capabilitySummaryProps} />
            <ProviderRefreshCard {...providerRefreshProps} />
            <ResolvedTasksCard tasks={resolvedTasks} />
          </>
        ) : null}

        {currentSection === "runtime" ? (
          <>
            <article className="card">
              <CardHeader title="Runtime Health" subtitle="Runtime-only health signals live here instead of repeating across overview cards." />
              <div className="state-grid">
                <span>Core API</span>
                <HealthIndicator value={runtimeHealth.coreApiConnectivity} />
                <span>Operational MQTT</span>
                <HealthIndicator value={runtimeHealth.operationalMqttConnectivity} />
                <span>Governance</span>
                <HealthIndicator value={runtimeHealth.governanceFreshness} />
                <span>Last Telemetry</span>
                <code>{runtimeHealth.lastTelemetryTimestamp || "none"}</code>
                <span>Node Health</span>
                <HealthIndicator value={runtimeHealth.nodeHealthState} />
              </div>
            </article>
            <RuntimeServicesCard {...runtimeServicesProps} />
            <OperationalActionsCard {...operationalActions} />
          </>
        ) : null}

        {currentSection === "activity" ? (
          <>
            <article className="card">
              <CardHeader title="Onboarding" subtitle="Live onboarding progress by lifecycle stage." />
              <div className="progress-list">
                {onboardingSteps.map((step) => {
                  const state = onboardingProgress?.[step.key] || "pending";
                  return (
                    <div className="progress-row" key={step.key}>
                      <span>{step.label}</span>
                      <StageBadge value={state} />
                    </div>
                  );
                })}
              </div>
              {pendingApprovalNodeId ? (
                <p className="muted tiny">
                  Pending approval for node: <code>{pendingApprovalNodeId}</code>
                </p>
              ) : null}
            </article>
            <RecentActivityCard items={activityItems} degraded={Boolean(degradedBanner)} />
          </>
        ) : null}

        {currentSection === "clients" ? (
          <ClientCostCard
            clients={clientCostItems}
            currentMonth={clientUsageMonth}
            governanceStatus={governanceStatus}
            className="operational-card-full-span"
          />
        ) : null}

        {currentSection === "benchmarks" ? (
          <LocalLLMBenchmarkTable summary={localLlmBenchmarkSummary} />
        ) : null}

        {currentSection === "scheduled" ? (
          <ScheduledTasksSection {...(scheduledTasksProps || {})} />
        ) : null}

        {currentSection === "diagnostics" ? (
          <DiagnosticsPage {...diagnosticsProps} className="operational-card-full-span" />
        ) : null}
      </section>
    </OperationalShell>
  );
}
