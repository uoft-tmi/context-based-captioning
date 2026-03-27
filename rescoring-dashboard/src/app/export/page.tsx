"use client";

import { useState } from "react";
import { generateDecisions, generateIncidents, generateSessions } from "../lib/mockData";

export default function ExportPage() {
  const [downloading, setDownloading] = useState(false);
  const [format, setFormat] = useState<"csv" | "json">("csv");
  const [dateRange, setDateRange] = useState("all");
  const [dataset, setDataset] = useState<"decisions" | "incidents" | "sessions">("decisions");

  const handleExport = () => {
    setDownloading(true);
    
    // Simulate API delay for generation
    setTimeout(() => {
      let data: any[] = [];
      let filename = `rescoring_${dataset}_${new Date().toISOString().split("T")[0]}`;

      if (dataset === "decisions") data = generateDecisions(100);
      else if (dataset === "incidents") data = generateIncidents();
      else if (dataset === "sessions") data = generateSessions();

      if (format === "json") {
        const jsonStr = JSON.stringify(data, null, 2);
        triggerDownload(jsonStr, "application/json", `${filename}.json`);
      } else {
        const csvStr = convertToCsv(data);
        triggerDownload(csvStr, "text/csv", `${filename}.csv`);
      }
      
      setDownloading(false);
    }, 800);
  };

  const convertToCsv = (data: any[]) => {
    if (data.length === 0) return "";
    const headers = Object.keys(data[0]);
    const rows = data.map((obj) =>
      headers
        .map((header) => {
          let val = obj[header];
          if (val === null) return "";
          if (typeof val === "string") val = val.replace(/"/g, '""');
          return `"${val}"`;
        })
        .join(",")
    );
    return [headers.join(","), ...rows].join("\n");
  };

  const triggerDownload = (content: string, type: string, filename: string) => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="page-content">
      <div className="page-header" style={{ maxWidth: 800 }}>
        <h1>Data Export</h1>
        <p>
          Download audit logs, incident histories, and session aggregated metrics for
          compliance reporting or offline analysis.
        </p>
      </div>

      <div
        style={{
          maxWidth: 600,
          background: "var(--color-surface)",
          border: "1px solid var(--color-border)",
          borderRadius: "var(--radius-md)",
          padding: "var(--space-6)",
        }}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-5)" }}>
          {/* Dataset Selection */}
          <div>
            <label
              style={{
                display: "block",
                fontSize: 13,
                fontWeight: 500,
                color: "var(--color-text-muted)",
                marginBottom: "var(--space-2)",
              }}
            >
              Select Dataset
            </label>
            <div className="grid-2">
              <RadioOption
                label="Decision Log"
                description="Word-level replacement history with context and scores."
                checked={dataset === "decisions"}
                onChange={() => setDataset("decisions")}
              />
              <RadioOption
                label="Safety Incidents"
                description="Flags, threshold alerts, and domain drift logs."
                checked={dataset === "incidents"}
                onChange={() => setDataset("incidents")}
              />
              <RadioOption
                label="Session Metrics"
                description="Aggregated statistics, WER improvement, and processing time per file."
                checked={dataset === "sessions"}
                onChange={() => setDataset("sessions")}
              />
            </div>
          </div>

          <div className="grid-2">
            {/* Format */}
            <div>
              <label
                style={{
                  display: "block",
                  fontSize: 13,
                  fontWeight: 500,
                  color: "var(--color-text-muted)",
                  marginBottom: "var(--space-2)",
                }}
              >
                Output Format
              </label>
              <select
                className="filter-select"
                style={{ width: "100%", padding: "10px 14px", height: 42 }}
                value={format}
                onChange={(e) => setFormat(e.target.value as "csv" | "json")}
              >
                <option value="csv">CSV (Comma-separated values)</option>
                <option value="json">JSON (JavaScript Object Notation)</option>
              </select>
            </div>

            {/* Date Range */}
            <div>
              <label
                style={{
                  display: "block",
                  fontSize: 13,
                  fontWeight: 500,
                  color: "var(--color-text-muted)",
                  marginBottom: "var(--space-2)",
                }}
              >
                Date Range
              </label>
              <select
                className="filter-select"
                style={{ width: "100%", padding: "10px 14px", height: 42 }}
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
              >
                <option value="all">All time (Default limit: 10,000)</option>
                <option value="today">Today</option>
                <option value="week">Past 7 days</option>
                <option value="month">Past 30 days</option>
              </select>
            </div>
          </div>

          <div
            style={{
              marginTop: "var(--space-4)",
              paddingTop: "var(--space-5)",
              borderTop: "1px solid var(--color-border)",
              display: "flex",
              justifyContent: "flex-end",
            }}
          >
            <button
              className="btn btn-primary"
              style={{ fontSize: 14, padding: "10px 24px" }}
              onClick={handleExport}
              disabled={downloading}
            >
              {downloading ? (
                <>
                  <svg
                    className="animate-spin"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    style={{ animation: "spin 1s linear infinite" }}
                  >
                    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" strokeDasharray="32" strokeLinecap="round" opacity="0.3" />
                  </svg>
                  Preparing...
                </>
              ) : (
                <>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <path
                      d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                  Download {format.toUpperCase()}
                </>
              )}
            </button>
          </div>
        </div>
      </div>
      
      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}} />
    </div>
  );
}

function RadioOption({
  label,
  description,
  checked,
  onChange,
}: {
  label: string;
  description: string;
  checked: boolean;
  onChange: () => void;
}) {
  return (
    <label
      style={{
        display: "flex",
        alignItems: "flex-start",
        gap: "var(--space-3)",
        padding: "var(--space-4)",
        border: `1px solid ${checked ? "var(--color-accent)" : "var(--color-border)"}`,
        borderRadius: "var(--radius-md)",
        background: checked ? "rgba(16, 185, 129, 0.04)" : "var(--color-bg)",
        cursor: "pointer",
        transition: "all var(--transition-fast)",
      }}
    >
      <input
        type="radio"
        checked={checked}
        onChange={onChange}
        style={{
          marginTop: 4,
          accentColor: "var(--color-accent)",
          width: 16,
          height: 16,
        }}
      />
      <div>
        <div style={{ fontSize: 14, fontWeight: 500, color: "var(--color-text)", marginBottom: 2 }}>
          {label}
        </div>
        <div style={{ fontSize: 12, color: "var(--color-text-muted)" }}>{description}</div>
      </div>
    </label>
  );
}
