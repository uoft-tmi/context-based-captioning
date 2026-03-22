"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import {
  generateDecisions,
  computeMetrics,
  generateTimeSeries,
} from "./lib/mockData";

// SVG sparkline for the hero section
function HeroChart({ data }: { data: { time: string; decisions: number }[] }) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setVisible(true), 300);
    return () => clearTimeout(timer);
  }, []);

  if (data.length === 0) return null;

  const W = 800;
  const H = 200;
  const PAD = 32;
  const maxVal = Math.max(...data.map((d) => d.decisions));
  const minVal = Math.min(...data.map((d) => d.decisions));
  const range = maxVal - minVal || 1;

  const points = data.map((d, i) => ({
    x: PAD + (i / (data.length - 1)) * (W - PAD * 2),
    y: PAD + (1 - (d.decisions - minVal) / range) * (H - PAD * 2),
  }));

  const linePath = points.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ");
  const areaPath = `${linePath} L ${points[points.length - 1].x} ${H - PAD} L ${points[0].x} ${H - PAD} Z`;

  return (
    <svg
      ref={svgRef}
      viewBox={`0 0 ${W} ${H}`}
      className="hero-chart"
      style={{
        width: "100%",
        maxWidth: 720,
        height: "auto",
        opacity: visible ? 1 : 0,
        transition: "opacity 600ms ease",
      }}
      aria-label="Decision activity over time"
      role="img"
    >
      {/* Grid lines */}
      {[0.25, 0.5, 0.75].map((frac) => (
        <line
          key={frac}
          x1={PAD}
          x2={W - PAD}
          y1={PAD + frac * (H - PAD * 2)}
          y2={PAD + frac * (H - PAD * 2)}
          stroke="rgba(255,255,255,0.04)"
          strokeWidth="1"
        />
      ))}

      {/* Area fill */}
      <path d={areaPath} fill="rgba(16, 185, 129, 0.06)" />

      {/* Line */}
      <path
        d={linePath}
        fill="none"
        stroke="#10B981"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        style={{
          strokeDasharray: visible ? "none" : "2000",
          strokeDashoffset: visible ? 0 : 2000,
          transition: "stroke-dashoffset 1.5s ease",
        }}
      />

      {/* Data points */}
      {points.map((p, i) => (
        <circle
          key={i}
          cx={p.x}
          cy={p.y}
          r="3"
          fill="#10B981"
          style={{
            opacity: visible ? 1 : 0,
            transition: `opacity 300ms ease ${200 + i * 80}ms`,
          }}
        />
      ))}

      {/* x-axis labels */}
      {data.map((d, i) =>
        i % Math.ceil(data.length / 6) === 0 ? (
          <text
            key={`label-${i}`}
            x={points[i].x}
            y={H - 8}
            textAnchor="middle"
            fill="rgba(255,255,255,0.3)"
            fontSize="10"
            fontFamily="var(--font-mono)"
          >
            {d.time}
          </text>
        ) : null
      )}
    </svg>
  );
}

function ScrollIndicator() {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const handler = () => {
      setVisible(window.scrollY < 50);
    };
    window.addEventListener("scroll", handler, { passive: true });
    return () => window.removeEventListener("scroll", handler);
  }, []);

  return (
    <div
      style={{
        opacity: visible ? 0.4 : 0,
        transition: "opacity 300ms ease",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 4,
        marginTop: 48,
      }}
    >
      <span style={{ fontSize: 12, color: "var(--color-text-faint)", letterSpacing: "0.06em" }}>
        scroll to explore
      </span>
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
        <path d="M4 6L8 10L12 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </div>
  );
}

export default function LandingPage() {
  const decisions = generateDecisions(200);
  const metrics = computeMetrics(decisions);
  const timeSeries = generateTimeSeries(decisions);

  return (
    <>
      {/* Hero Section */}
      <section
        style={{
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "120px 32px 64px",
          textAlign: "center",
        }}
      >
        <h1
          style={{
            fontSize: "clamp(32px, 5vw, 48px)",
            fontWeight: 700,
            letterSpacing: "-0.02em",
            lineHeight: 1.1,
            marginBottom: 8,
            color: "var(--color-text)",
          }}
        >
          Speech Correction Monitoring
        </h1>

        <div
          style={{
            width: 64,
            height: 2,
            background: "var(--color-accent)",
            margin: "24px auto",
          }}
          aria-hidden="true"
        />

        <p
          style={{
            fontSize: 18,
            fontWeight: 400,
            color: "var(--color-text-muted)",
            maxWidth: 560,
            lineHeight: 1.6,
            margin: "0 auto 48px",
          }}
        >
          Real-time visibility into every decision made by the shallow fusion
          rescoring system. Monitor, audit, and validate autonomous transcription
          corrections.
        </p>

        {/* Live Chart Preview */}
        <HeroChart data={timeSeries} />

        {/* Key Metrics Row */}
        <div
          style={{
            display: "flex",
            gap: 48,
            justifyContent: "center",
            marginTop: 48,
            flexWrap: "wrap",
          }}
        >
          <MetricInline label="Total processed" value={metrics.totalProcessed.toLocaleString()} />
          <MetricInline label="Replacement rate" value={`${metrics.replacementRate}%`} />
          <MetricInline label="User approval" value={`${metrics.approvalRate}%`} />
          <MetricInline label="Avg confidence" value={metrics.avgConfidence} />
        </div>

        <ScrollIndicator />
      </section>

      {/* Quick Access Section */}
      <section className="page-content" style={{ paddingTop: 0 }}>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
            gap: "var(--space-4)",
            marginBottom: "var(--space-8)",
          }}
        >
          <QuickLink
            href="/decisions"
            title="Decision Log"
            description="Audit every rescoring decision. Sortable table with expandable detail rows, inline feedback actions."
          />
          <QuickLink
            href="/analytics"
            title="Analytics"
            description="Replacement rates, confidence distributions, and accuracy trends across sessions."
          />
          <QuickLink
            href="/safety"
            title="Alerts"
            description="Active safety alerts, incident logs, and system health monitoring."
          />
          <QuickLink
            href="/export"
            title="Export"
            description="Download decision logs as CSV or JSON. Filter by date range, session, or action type."
          />
        </div>
      </section>
    </>
  );
}

function MetricInline({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ textAlign: "center" }}>
      <div
        style={{
          fontSize: 28,
          fontWeight: 600,
          letterSpacing: "-0.02em",
          color: "var(--color-text)",
          fontFamily: "var(--font-sans)",
        }}
      >
        {value}
      </div>
      <div
        style={{
          fontSize: 12,
          fontWeight: 500,
          color: "var(--color-text-faint)",
          textTransform: "uppercase" as const,
          letterSpacing: "0.04em",
          marginTop: 4,
        }}
      >
        {label}
      </div>
    </div>
  );
}

function QuickLink({
  href,
  title,
  description,
}: {
  href: string;
  title: string;
  description: string;
}) {
  return (
    <Link
      id={`quick-link-${title.toLowerCase().replace(/\s/g, "-")}`}
      href={href}
      style={{
        display: "block",
        padding: "var(--space-5)",
        border: "1px solid var(--color-border)",
        borderRadius: "var(--radius-md)",
        background: "var(--color-surface)",
        textDecoration: "none",
        transition: "border-color var(--transition-fast), background var(--transition-fast)",
      }}
      onMouseOver={(e) => {
        e.currentTarget.style.borderColor = "var(--color-border-strong)";
        e.currentTarget.style.background = "var(--color-surface-raised)";
      }}
      onMouseOut={(e) => {
        e.currentTarget.style.borderColor = "var(--color-border)";
        e.currentTarget.style.background = "var(--color-surface)";
      }}
    >
      <h3 style={{ fontSize: 15, fontWeight: 600, color: "var(--color-text)", marginBottom: 8 }}>
        {title}
      </h3>
      <p style={{ fontSize: 13, color: "var(--color-text-muted)", lineHeight: 1.5 }}>
        {description}
      </p>
    </Link>
  );
}
