import { useState } from "react";

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

function parseOutputPayload(outputText) {
  try {
    const payload = JSON.parse(String(outputText || ""));
    return payload && typeof payload === "object" ? payload : {};
  } catch {
    return {};
  }
}

function labelSummary({ label, confidence, outputText }) {
  const payload = parseOutputPayload(outputText);
  const labelValue = label || payload.label || "none";
  const score = confidence ?? payload.confidence ?? payload.score;
  return `${labelValue}${score === null || score === undefined || score === "" ? "" : ` (${formatMetricValue(score)})`}`;
}

function reasoningText(result) {
  const payload = parseOutputPayload(result?.output_text);
  return payload.rationale || payload.reasoning || payload.reason || payload.explanation || result?.output_text || "none";
}

function LocalModelCell({ result, modelId }) {
  if (!result) {
    return (
      <div className="benchmark-model-cell">
        <code>{modelId}</code>
        <StageBadge value="pending" />
      </div>
    );
  }
  return (
    <div className="benchmark-model-cell">
      <code>{result.model_id || modelId}</code>
      <StageBadge value={result.status || "unknown"} />
      <span>{labelSummary({ label: result.label, confidence: result.confidence, outputText: result.output_text })}</span>
      <span className="muted tiny">Tokens {formatMetricValue(result.total_tokens)}</span>
      <span className="muted tiny">VRAM {formatMetricValue(result.vram_used_mib ?? result.vram_delta_mib, " MiB")}</span>
      <span className="muted tiny">GPU {formatMetricValue(result.gpu_util_percent, "%")}</span>
      {result.error ? <span className="error tiny">{result.error}</span> : null}
    </div>
  );
}

function BenchmarkDetailModal({ comparison, modelIds, onClose }) {
  if (!comparison) {
    return null;
  }
  const localResults = Array.isArray(comparison.local_results) ? comparison.local_results : [];
  const resultsByModel = Object.fromEntries(localResults.map((result) => [result.model_id, result]));
  return (
    <section className="modal-overlay pricing-modal-overlay" role="dialog" aria-modal="true" aria-label="Benchmark detail">
      <article className="card modal-card benchmark-detail-modal">
        <CardHeader title="Benchmark Detail" subtitle={comparison.prompt_id || comparison.task_family || comparison.record_id} />
        <div className="state-grid">
          <span>Record</span>
          <code>{comparison.record_id}</code>
          <span>Prompt</span>
          <code>{comparison.prompt_id || "unattributed"}</code>
          <span>Created</span>
          <code>{comparison.created_at || "unknown"}</code>
        </div>
        <div className="modal-capability-data">
          <h3>OpenAI</h3>
          <div className="state-grid">
            <span>Model</span>
            <code>{comparison.openai?.model_id || "openai"}</code>
            <span>Label</span>
            <code>{labelSummary({ label: comparison.openai?.label, confidence: comparison.openai?.confidence, outputText: comparison.openai?.output_text })}</code>
            <span>Tokens</span>
            <code>{formatMetricValue(comparison.openai?.usage?.total_tokens)}</code>
            <span>Latency</span>
            <code>{formatMetricValue(comparison.openai?.latency_ms, " ms")}</code>
            <span>Reasoning</span>
            <code>{reasoningText(comparison.openai)}</code>
          </div>
        </div>
        <div className="modal-capability-data">
          <h3>Local LLMs</h3>
          {modelIds.map((modelId) => {
            const result = resultsByModel[modelId];
            return (
              <div className="benchmark-detail-block" key={modelId}>
                <strong>{modelId}</strong>
                {result ? (
                  <div className="state-grid compact-grid">
                    <span>Status</span>
                    <StageBadge value={result.status || "unknown"} />
                    <span>Label</span>
                    <code>{labelSummary({ label: result.label, confidence: result.confidence, outputText: result.output_text })}</code>
                    <span>Tokens</span>
                    <code>{formatMetricValue(result.total_tokens)}</code>
                    <span>Latency</span>
                    <code>{formatMetricValue(result.latency_ms, " ms")}</code>
                    <span>VRAM</span>
                    <code>{formatMetricValue(result.vram_used_mib ?? result.vram_delta_mib, " MiB")}</code>
                    <span>GPU Util</span>
                    <code>{formatMetricValue(result.gpu_util_percent, "%")}</code>
                    <span>Reasoning</span>
                    <code>{reasoningText(result)}</code>
                  </div>
                ) : (
                  <p className="muted tiny">Pending replay.</p>
                )}
              </div>
            );
          })}
        </div>
        <div className="modal-capability-data">
          <h3>Prompt Input</h3>
          <pre className="benchmark-raw-block">{comparison.input_snippet || "none"}</pre>
        </div>
        <div className="row">
          <button className="btn btn-primary" type="button" onClick={onClose}>
            Close
          </button>
        </div>
      </article>
    </section>
  );
}

function LocalLLMBenchmarkTable({ summary, onCycleModel, cyclingModel = false }) {
  const [selectedComparison, setSelectedComparison] = useState(null);
  const comparisons = Array.isArray(summary?.comparisons) ? summary.comparisons : [];
  const configuredModels = Array.isArray(summary?.rotation?.models)
    ? summary.rotation.models.map((model) => model?.id).filter(Boolean)
    : [];
  const discoveredModels = comparisons.flatMap((comparison) =>
    Array.isArray(comparison?.local_results) ? comparison.local_results.map((result) => result?.model_id).filter(Boolean) : []
  );
  const modelIds = Array.from(new Set([...configuredModels, ...discoveredModels])).slice(0, 4);
  const currentModelId = summary?.rotation?.current_model_id || "unknown";

  return (
    <>
      <article className="card operational-card-full-span">
      <CardHeader title="Local LLM Benchmarks" subtitle="OpenAI calls replayed against the local model rotation." />
      <div className="benchmark-toolbar">
        <div className="state-grid compact-grid">
          <span>Current Model</span>
          <code>{currentModelId}</code>
          <span>Last Switch</span>
          <code>{summary?.rotation?.updated_at || "none"}</code>
        </div>
        <button className="btn btn-primary" type="button" onClick={onCycleModel} disabled={!onCycleModel || cyclingModel}>
          {cyclingModel ? "Cycling..." : "Cycle Model"}
        </button>
      </div>
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
                <th>OpenAI Model</th>
                {modelIds.map((modelId) => (
                  <th key={modelId}>Local LLM {modelIds.indexOf(modelId) + 1}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {comparisons.length ? (
                comparisons.map((comparison) => {
                  const resultsByModel = Object.fromEntries(
                    (Array.isArray(comparison.local_results) ? comparison.local_results : []).map((result) => [result.model_id, result])
                  );
                  return (
                  <tr
                    className="benchmark-clickable-row"
                    key={comparison.record_id}
                    onClick={() => setSelectedComparison(comparison)}
                    tabIndex={0}
                    onKeyDown={(event) => {
                      if (event.key === "Enter" || event.key === " ") {
                        setSelectedComparison(comparison);
                      }
                    }}
                  >
                    <td>
                      <code>{comparison.prompt_id || comparison.task_family || "unattributed"}</code>
                      {comparison.input_snippet ? <span className="muted tiny benchmark-snippet">{comparison.input_snippet}</span> : null}
                    </td>
                    <td>
                      <div className="benchmark-model-cell">
                        <code>{comparison.openai?.model_id || "openai"}</code>
                        <span>{labelSummary({ label: comparison.openai?.label, confidence: comparison.openai?.confidence, outputText: comparison.openai?.output_text })}</span>
                        <span className="muted tiny">Tokens {formatMetricValue(comparison.openai?.usage?.total_tokens)}</span>
                      </div>
                    </td>
                    {modelIds.map((modelId) => (
                      <td key={`${comparison.record_id}-${modelId}`}>
                        <LocalModelCell modelId={modelId} result={resultsByModel[modelId]} />
                      </td>
                    ))}
                  </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={2 + Math.max(modelIds.length, 1)} className="muted">
                    No OpenAI benchmark records have been captured yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
      </article>
      <BenchmarkDetailModal
        comparison={selectedComparison}
        modelIds={modelIds}
        onClose={() => setSelectedComparison(null)}
      />
    </>
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
  onCycleLocalLlmModel,
  cyclingLocalLlmModel = false,
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
          <LocalLLMBenchmarkTable
            summary={localLlmBenchmarkSummary}
            onCycleModel={onCycleLocalLlmModel}
            cyclingModel={cyclingLocalLlmModel}
          />
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
