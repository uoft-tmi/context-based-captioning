"use client";

import { useState, useMemo } from "react";
import {
  generateDecisions,
  generateIncidents,
  generateSessions,
  computeMetrics,
  type Incident,
} from "../lib/mockData";

export default function AlertsPage() {
  const decisions = useMemo(() => generateDecisions(200), []);
  const incidents = useMemo(() => generateIncidents(), []);
  const sessions = useMemo(() => generateSessions(), []);
  const metrics = computeMetrics(decisions);

  const activeIncidents = incidents.filter((i) => !i.resolved);
  const resolvedIncidents = incidents.filter((i) => i.resolved);

  const [dismissed, setDismissed] = useState<Set<number>>(new Set());

  const handleDismiss = (id: number) => {
    setDismissed((prev) => new Set(prev).add(id));
  };

  // System health indicators
  const replacementRate = parseFloat(metrics.replacementRate);
  const approvalRate = parseFloat(metrics.approvalRate);
  const avgConfidence = parseFloat(metrics.avgConfidence);

  const healthChecks = [
    {
      label: "Replacement rate",
      value: `${metrics.replacementRate}%`,
      threshold: "< 25%",
      status: replacementRate < 25 ? ("healthy" as const) : ("warning" as const),
    },
    {
      label: "User approval rate",
      value: `${metrics.approvalRate}%`,
      threshold: "> 85%",
      status: approvalRate > 85 ? ("healthy" as const) : ("warning" as const),
    },
    {
      label: "Mean confidence",
      value: metrics.avgConfidence,
      threshold: "> 0.50",
      status: avgConfidence > 0.5 ? ("healthy" as const) : ("critical" as const),
    },
    {
      label: "Active incidents",
      value: String(activeIncidents.filter((i) => !dismissed.has(i.id)).length),
      threshold: "0",
      status:
        activeIncidents.filter((i) => !dismissed.has(i.id)).length === 0
          ? ("healthy" as const)
          : ("warning" as const),
    },
  ];

  return (
    <div className="page-content">
      <div className="page-header">
        <h1>Alerts</h1>
        <p>Safety monitoring, incident logs, and system health indicators.</p>
      </div>

      {/* System Health */}
      <section style={{ marginBottom: "var(--space-6)" }}>
        <h3 style={{ fontSize: 13, fontWeight: 500, color: "var(--color-text-muted)", textTransform: "uppercase", letterSpacing: "0.04em", marginBottom: "var(--space-4)" }}>
          System health
        </h3>
        <div className="grid-4">
          {healthChecks.map((check) => (
            <div
              key={check.label}
              style={{
                padding: "var(--space-4)",
                border: "1px solid var(--color-border)",
                borderRadius: "var(--radius-md)",
                background: "var(--color-surface)",
                display: "flex",
                alignItems: "center",
                gap: "var(--space-3)",
              }}
            >
              <div
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  flexShrink: 0,
                  background:
                    check.status === "healthy"
                      ? "var(--color-accent)"
                      : check.status === "warning"
                      ? "var(--color-warning)"
                      : "var(--color-error)",
                }}
                aria-label={`Status: ${check.status}`}
              />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 12, color: "var(--color-text-faint)" }}>{check.label}</div>
                <div style={{ fontSize: 15, fontWeight: 600, fontFamily: "var(--font-mono)" }}>
                  {check.value}
                </div>
              </div>
              <div
                style={{
                  fontSize: 11,
                  color: "var(--color-text-faint)",
                  fontFamily: "var(--font-mono)",
                }}
              >
                {check.threshold}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Active Alerts */}
      <section style={{ marginBottom: "var(--space-6)" }}>
        <h3 style={{ fontSize: 13, fontWeight: 500, color: "var(--color-text-muted)", textTransform: "uppercase", letterSpacing: "0.04em", marginBottom: "var(--space-4)" }}>
          Active alerts ({activeIncidents.filter((i) => !dismissed.has(i.id)).length})
        </h3>

        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-3)" }}>
          {activeIncidents
            .filter((i) => !dismissed.has(i.id))
            .map((incident) => (
              <AlertItem key={incident.id} incident={incident} onDismiss={handleDismiss} />
            ))}

          {activeIncidents.filter((i) => !dismissed.has(i.id)).length === 0 && (
            <div
              style={{
                padding: "var(--space-6)",
                border: "1px dashed var(--color-border)",
                borderRadius: "var(--radius-md)",
                textAlign: "center",
                color: "var(--color-text-faint)",
                fontSize: 13,
              }}
            >
              No active alerts. System operating within defined thresholds.
            </div>
          )}
        </div>
      </section>

      {/* Resolved Alerts */}
      <section>
        <h3 style={{ fontSize: 13, fontWeight: 500, color: "var(--color-text-muted)", textTransform: "uppercase", letterSpacing: "0.04em", marginBottom: "var(--space-4)" }}>
          Resolved ({resolvedIncidents.length + dismissed.size})
        </h3>
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-3)" }}>
          {/* Show dismissed items as resolved */}
          {activeIncidents
            .filter((i) => dismissed.has(i.id))
            .map((incident) => (
              <AlertItem key={`dismissed-${incident.id}`} incident={{ ...incident, resolved: true }} />
            ))}
          {resolvedIncidents.map((incident) => (
            <AlertItem key={incident.id} incident={incident} />
          ))}
        </div>
      </section>
    </div>
  );
}

function AlertItem({
  incident,
  onDismiss,
}: {
  incident: Incident;
  onDismiss?: (id: number) => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const severity = incident.resolved ? "resolved" : incident.severity;

  const timeAgo = getTimeAgo(incident.timestamp);

  return (
    <div className="alert-item" data-severity={severity}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", alignItems: "center", gap: "var(--space-3)", marginBottom: 4 }}>
            <span
              className="badge"
              style={{
                background:
                  severity === "critical"
                    ? "var(--color-error-muted)"
                    : severity === "medium"
                    ? "var(--color-warning-muted)"
                    : severity === "resolved"
                    ? "var(--color-accent-muted)"
                    : "var(--color-info-muted)",
                color:
                  severity === "critical"
                    ? "var(--color-error)"
                    : severity === "medium"
                    ? "var(--color-warning)"
                    : severity === "resolved"
                    ? "var(--color-accent)"
                    : "var(--color-info)",
              }}
            >
              {severity}
            </span>
            <span className="alert-title">{incident.incident_type}</span>
          </div>
          <p className="alert-description">{incident.description}</p>
          <div className="alert-meta">
            detected: {timeAgo} &middot; decision #{incident.decision_id}
          </div>
        </div>

        {!incident.resolved && onDismiss && (
          <div style={{ display: "flex", gap: "var(--space-2)", marginLeft: "var(--space-4)", flexShrink: 0 }}>
            <button className="btn btn-ghost" onClick={() => setExpanded(!expanded)}>
              {expanded ? "Hide" : "Details"}
            </button>
            <button className="btn btn-ghost" onClick={() => onDismiss(incident.id)}>
              Dismiss
            </button>
          </div>
        )}
      </div>

      {expanded && (
        <div
          className="animate-fade-in-up"
          style={{
            marginTop: "var(--space-4)",
            paddingTop: "var(--space-4)",
            borderTop: "1px solid var(--color-border)",
            fontSize: 13,
            color: "var(--color-text-muted)",
          }}
        >
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px 24px" }}>
            <div>
              <span style={{ color: "var(--color-text-faint)" }}>Incident ID: </span>
              <span style={{ fontFamily: "var(--font-mono)" }}>{incident.id}</span>
            </div>
            <div>
              <span style={{ color: "var(--color-text-faint)" }}>Decision ref: </span>
              <span style={{ fontFamily: "var(--font-mono)" }}>#{incident.decision_id}</span>
            </div>
            <div>
              <span style={{ color: "var(--color-text-faint)" }}>Timestamp: </span>
              <span style={{ fontFamily: "var(--font-mono)" }}>
                {new Date(incident.timestamp).toLocaleString()}
              </span>
            </div>
            <div>
              <span style={{ color: "var(--color-text-faint)" }}>Auto-resolve: </span>
              <span style={{ fontFamily: "var(--font-mono)" }}>disabled</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function getTimeAgo(timestamp: string): string {
  const now = new Date("2026-03-22T12:00:00Z");
  const then = new Date(timestamp);
  const diffMs = now.getTime() - then.getTime();
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));

  if (diffHours < 1) return "just now";
  if (diffHours === 1) return "1 hour ago";
  if (diffHours < 24) return `${diffHours} hours ago`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays} day${diffDays > 1 ? "s" : ""} ago`;
}
