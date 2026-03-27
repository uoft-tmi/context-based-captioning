"use client";

import { useMemo } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";
import {
  generateDecisions,
  computeMetrics,
  generateTimeSeries,
  generateConfidenceBuckets,
  generateSessions,
} from "../lib/mockData";

// Custom tooltip matching our design system
function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div
      style={{
        background: "var(--color-surface-raised)",
        border: "1px solid var(--color-border-strong)",
        borderRadius: "var(--radius-sm)",
        padding: "8px 12px",
        fontSize: 12,
        fontFamily: "var(--font-mono)",
      }}
    >
      <div style={{ color: "var(--color-text-muted)", marginBottom: 4 }}>{label}</div>
      {payload.map((p: any, i: number) => (
        <div key={i} style={{ color: p.color }}>
          {p.name}: {p.value}
        </div>
      ))}
    </div>
  );
}

// Inline sparkline SVG
function Sparkline({
  data,
  width = 80,
  height = 24,
  color = "var(--color-accent)",
}: {
  data: number[];
  width?: number;
  height?: number;
  color?: string;
}) {
  if (data.length < 2) return null;
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;

  const points = data
    .map((v, i) => {
      const x = (i / (data.length - 1)) * width;
      const y = height - ((v - min) / range) * (height - 4) - 2;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <svg width={width} height={height} style={{ display: "block", marginTop: 8 }}>
      <polyline points={points} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export default function AnalyticsPage() {
  const decisions = useMemo(() => generateDecisions(200), []);
  const metrics = computeMetrics(decisions);
  const timeSeries = generateTimeSeries(decisions);
  const confidenceBuckets = generateConfidenceBuckets(decisions);
  const sessions = generateSessions();

  // Generate sparkline data from time series
  const decisionSparkline = timeSeries.map((t) => t.decisions);
  const rateSparkline = timeSeries.map((t) => t.rate);

  // WER improvement data from sessions
  const werData = sessions.map((s) => ({
    session: s.session_id.replace("session_", "S"),
    before: s.wer_before,
    after: s.wer_after,
    improvement: parseFloat((s.wer_before - s.wer_after).toFixed(1)),
  }));

  return (
    <div className="page-content">
      <div className="page-header">
        <h1>Analytics</h1>
        <p>System performance metrics and rescoring statistics across {sessions.length} sessions.</p>
      </div>

      {/* Metric Tiles */}
      <div className="grid-4" style={{ marginBottom: "var(--space-6)" }}>
        <div className="metric-tile">
          <div className="metric-tile-label">Total processed</div>
          <div className="metric-tile-value">{metrics.totalProcessed.toLocaleString()}</div>
          <Sparkline data={decisionSparkline} />
        </div>
        <div className="metric-tile">
          <div className="metric-tile-label">Replacement rate</div>
          <div className="metric-tile-value">{metrics.replacementRate}%</div>
          <div className="metric-tile-sub">
            {metrics.replacements} of {metrics.totalProcessed} words
          </div>
        </div>
        <div className="metric-tile">
          <div className="metric-tile-label">User approval</div>
          <div className="metric-tile-value">{metrics.approvalRate}%</div>
          <div className="metric-tile-sub">{metrics.reviewed} reviewed</div>
        </div>
        <div className="metric-tile">
          <div className="metric-tile-label">Avg confidence</div>
          <div className="metric-tile-value">{metrics.avgConfidence}</div>
          <Sparkline data={rateSparkline} color="var(--color-warning)" />
        </div>
      </div>

      {/* Main Charts Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "2fr 1fr",
          gap: "var(--space-4)",
          marginBottom: "var(--space-6)",
        }}
      >
        {/* Decisions Over Time */}
        <div className="chart-container">
          <div className="chart-title">Decisions over time</div>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={timeSeries} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis
                dataKey="time"
                stroke="rgba(255,255,255,0.15)"
                tick={{ fill: "var(--color-text-faint)", fontSize: 11, fontFamily: "var(--font-mono)" }}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                stroke="rgba(255,255,255,0.15)"
                tick={{ fill: "var(--color-text-faint)", fontSize: 11, fontFamily: "var(--font-mono)" }}
                tickLine={false}
                axisLine={false}
                width={36}
              />
              <Tooltip content={<ChartTooltip />} />
              <Line
                type="monotone"
                dataKey="decisions"
                stroke="#10B981"
                strokeWidth={2}
                dot={{ r: 3, fill: "#10B981", strokeWidth: 0 }}
                activeDot={{ r: 5, fill: "#10B981", strokeWidth: 0 }}
                name="Total decisions"
                animationDuration={800}
                animationEasing="ease-out"
              />
              <Line
                type="monotone"
                dataKey="replacements"
                stroke="rgba(16, 185, 129, 0.35)"
                strokeWidth={1.5}
                strokeDasharray="4 4"
                dot={false}
                name="Replacements"
                animationDuration={1000}
                animationEasing="ease-out"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* WER Improvement */}
        <div className="chart-container">
          <div className="chart-title">WER by session</div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={werData} margin={{ top: 8, right: 8, bottom: 8, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis
                dataKey="session"
                stroke="rgba(255,255,255,0.15)"
                tick={{ fill: "var(--color-text-faint)", fontSize: 11, fontFamily: "var(--font-mono)" }}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                stroke="rgba(255,255,255,0.15)"
                tick={{ fill: "var(--color-text-faint)", fontSize: 11, fontFamily: "var(--font-mono)" }}
                tickLine={false}
                axisLine={false}
                width={32}
                unit="%"
              />
              <Tooltip content={<ChartTooltip />} />
              <Bar dataKey="before" fill="rgba(239, 68, 68, 0.4)" name="WER before" radius={[2, 2, 0, 0]} />
              <Bar dataKey="after" fill="#10B981" name="WER after" radius={[2, 2, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Confidence Distribution */}
      <div className="chart-container">
        <div className="chart-title">Accuracy by confidence level</div>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={confidenceBuckets} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
            <XAxis
              dataKey="range"
              stroke="rgba(255,255,255,0.15)"
              tick={{ fill: "var(--color-text-faint)", fontSize: 11, fontFamily: "var(--font-mono)" }}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              stroke="rgba(255,255,255,0.15)"
              tick={{ fill: "var(--color-text-faint)", fontSize: 11, fontFamily: "var(--font-mono)" }}
              tickLine={false}
              axisLine={false}
              width={36}
            />
            <Tooltip content={<ChartTooltip />} />
            <Bar dataKey="count" fill="#10B981" name="Decisions" radius={[2, 2, 0, 0]} animationDuration={600} />
          </BarChart>
        </ResponsiveContainer>

        {/* Accuracy row below chart */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-around",
            marginTop: "var(--space-4)",
            paddingTop: "var(--space-4)",
            borderTop: "1px solid var(--color-border)",
          }}
        >
          {confidenceBuckets.map((b) => (
            <div key={b.range} style={{ textAlign: "center" }}>
              <div
                style={{
                  fontSize: 18,
                  fontWeight: 600,
                  color:
                    b.accuracy >= 90
                      ? "var(--color-accent)"
                      : b.accuracy >= 70
                      ? "var(--color-warning)"
                      : "var(--color-error)",
                }}
              >
                {b.accuracy}%
              </div>
              <div style={{ fontSize: 11, color: "var(--color-text-faint)", marginTop: 2 }}>
                accuracy
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
