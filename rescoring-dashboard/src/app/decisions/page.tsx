"use client";

import { useState, useMemo, useCallback, useEffect, useRef } from "react";
import { generateDecisions, type Decision } from "../lib/mockData";

type SortField = "timestamp" | "audio_file" | "original_word" | "whisper_confidence" | "action";
type SortDir = "asc" | "desc";

const PAGE_SIZE = 50;

export default function DecisionsPage() {
  const allDecisions = useMemo(() => generateDecisions(200), []);

  const [sortField, setSortField] = useState<SortField>("timestamp");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [filterAction, setFilterAction] = useState<string>("all");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [selectedIdx, setSelectedIdx] = useState<number>(0);
  const tableRef = useRef<HTMLTableElement>(null);

  // Filter & sort
  const filtered = useMemo(() => {
    let result = allDecisions;

    if (filterAction !== "all") {
      result = result.filter((d) => d.action === filterAction);
    }

    if (search.trim()) {
      const q = search.toLowerCase();
      result = result.filter(
        (d) =>
          d.original_word.toLowerCase().includes(q) ||
          (d.replacement_word && d.replacement_word.toLowerCase().includes(q)) ||
          d.audio_file.toLowerCase().includes(q) ||
          d.context_before.toLowerCase().includes(q) ||
          d.context_after.toLowerCase().includes(q)
      );
    }

    result = [...result].sort((a, b) => {
      let aVal: string | number = a[sortField] as string | number;
      let bVal: string | number = b[sortField] as string | number;
      if (sortField === "timestamp") {
        aVal = new Date(aVal as string).getTime();
        bVal = new Date(bVal as string).getTime();
      }
      if (typeof aVal === "string") {
        return sortDir === "asc"
          ? (aVal as string).localeCompare(bVal as string)
          : (bVal as string).localeCompare(aVal as string);
      }
      return sortDir === "asc"
        ? (aVal as number) - (bVal as number)
        : (bVal as number) - (aVal as number);
    });

    return result;
  }, [allDecisions, filterAction, search, sortField, sortDir]);

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  const pageData = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const handleSort = useCallback(
    (field: SortField) => {
      if (sortField === field) {
        setSortDir((d) => (d === "asc" ? "desc" : "asc"));
      } else {
        setSortField(field);
        setSortDir("desc");
      }
      setPage(1);
    },
    [sortField]
  );

  const toggleExpand = useCallback((id: number) => {
    setExpandedId((prev) => (prev === id ? null : id));
  }, []);

  // Keyboard navigation
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLSelectElement) return;

      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIdx((prev) => Math.min(prev + 1, pageData.length - 1));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIdx((prev) => Math.max(prev - 1, 0));
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (pageData[selectedIdx]) {
          toggleExpand(pageData[selectedIdx].id);
        }
      }
    };

    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [pageData, selectedIdx, toggleExpand]);

  // ⌘K / Ctrl+K to focus search
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        const input = document.getElementById("decision-search") as HTMLInputElement;
        input?.focus();
      }
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, []);

  const SortHeader = ({ field, label }: { field: SortField; label: string }) => (
    <th
      onClick={() => handleSort(field)}
      data-sorted={sortField === field}
      aria-sort={sortField === field ? (sortDir === "asc" ? "ascending" : "descending") : undefined}
    >
      {label}
      <span className="sort-indicator">
        {sortField === field ? (sortDir === "asc" ? "▲" : "▼") : "▼"}
      </span>
    </th>
  );

  return (
    <div className="page-content">
      <div className="page-header">
        <h1>Decision Log</h1>
        <p>
          Audit every autonomous rescoring decision. {filtered.length.toLocaleString()} records.
        </p>
      </div>

      {/* Filter Bar */}
      <div className="filter-bar" role="search" aria-label="Filter decisions">
        <select
          className="filter-select"
          value={filterAction}
          onChange={(e) => {
            setFilterAction(e.target.value);
            setPage(1);
          }}
          aria-label="Filter by action"
          id="filter-action"
        >
          <option value="all">All actions</option>
          <option value="replaced">Replaced</option>
          <option value="kept_original">Kept original</option>
        </select>

        <input
          id="decision-search"
          className="filter-input"
          type="text"
          placeholder="Search decisions... (⌘K)"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
          aria-label="Search decisions"
        />
      </div>

      {/* Table */}
      <div className="data-table-wrapper">
        <table className="data-table" ref={tableRef} role="grid" aria-label="Decisions log">
          <thead>
            <tr>
              <SortHeader field="timestamp" label="Timestamp" />
              <SortHeader field="audio_file" label="Audio" />
              <SortHeader field="original_word" label="Original" />
              <th>Replaced</th>
              <SortHeader field="whisper_confidence" label="Conf" />
              <SortHeader field="action" label="Status" />
            </tr>
          </thead>
          <tbody>
            {pageData.map((d, idx) => (
              <>
                <tr
                  key={d.id}
                  onClick={() => {
                    setSelectedIdx(idx);
                    toggleExpand(d.id);
                  }}
                  data-selected={selectedIdx === idx}
                  role="row"
                  aria-expanded={expandedId === d.id}
                  tabIndex={0}
                >
                  <td className="mono">
                    {new Date(d.timestamp).toLocaleTimeString("en-US", {
                      hour: "2-digit",
                      minute: "2-digit",
                      second: "2-digit",
                      hour12: false,
                    })}
                  </td>
                  <td style={{ maxWidth: 160, overflow: "hidden", textOverflow: "ellipsis" }}>
                    {d.audio_file.replace(".mp3", "")}
                  </td>
                  <td className="mono">{d.original_word}</td>
                  <td className="mono">
                    {d.action === "replaced" ? (
                      <span style={{ color: "var(--color-accent)" }}>{d.replacement_word}</span>
                    ) : (
                      <span style={{ color: "var(--color-text-faint)" }}>(kept)</span>
                    )}
                  </td>
                  <td className="mono">
                    <span
                      style={{
                        color:
                          d.whisper_confidence < 0.4
                            ? "var(--color-error)"
                            : d.whisper_confidence < 0.6
                            ? "var(--color-warning)"
                            : "var(--color-text-secondary)",
                      }}
                    >
                      {d.whisper_confidence.toFixed(2)}
                    </span>
                  </td>
                  <td>
                    {d.action === "replaced" ? (
                      <span className="badge badge-replaced">replaced</span>
                    ) : (
                      <span className="badge badge-kept">kept</span>
                    )}
                  </td>
                </tr>

                {/* Expanded Detail */}
                {expandedId === d.id && (
                  <tr className="row-detail" key={`detail-${d.id}`}>
                    <td colSpan={6}>
                      <ExpandedRow decision={d} />
                    </td>
                  </tr>
                )}
              </>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="pagination">
        <span>
          Showing {((page - 1) * PAGE_SIZE + 1).toLocaleString()}
          &ndash;
          {Math.min(page * PAGE_SIZE, filtered.length).toLocaleString()} of{" "}
          {filtered.length.toLocaleString()}
        </span>
        <div className="pagination-controls">
          <button
            className="pagination-btn"
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
            aria-label="Previous page"
          >
            Previous
          </button>
          <button
            className="pagination-btn"
            disabled={page >= totalPages}
            onClick={() => setPage((p) => p + 1)}
            aria-label="Next page"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}

// ----- Expanded Row Detail -----

function ExpandedRow({ decision: d }: { decision: Decision }) {
  const [feedbackState, setFeedbackState] = useState<"idle" | "approved" | "rejected" | "flagged">(
    d.user_approved === true
      ? "approved"
      : d.user_approved === false
      ? "rejected"
      : d.flagged
      ? "flagged"
      : "idle"
  );

  const confLevel =
    d.whisper_confidence < 0.4 ? "low" : d.whisper_confidence < 0.7 ? "medium" : "high";
  const phoneticLevel =
    d.phonetic_similarity < 0.7 ? "low" : d.phonetic_similarity < 0.85 ? "medium" : "high";
  const improvementLevel = d.improvement < 0.5 ? "low" : d.improvement < 1.0 ? "medium" : "high";

  return (
    <div className="row-detail-inner animate-fade-in-up">
      {/* Left: Scores */}
      <div>
        <h4 style={{ marginBottom: 16, color: "var(--color-text-muted)" }}>
          Decision #{d.id} &middot; {d.audio_file} &middot; {d.speaker}
        </h4>

        <div className="score-bar-group">
          <ScoreBar label="Whisper confidence" value={d.whisper_confidence} max={1} level={confLevel} />
          {d.action === "replaced" && (
            <>
              <ScoreBar
                label="Phonetic similarity"
                value={d.phonetic_similarity}
                max={1}
                level={phoneticLevel}
              />
              <ScoreBar
                label="LM improvement"
                value={d.improvement}
                max={3}
                level={improvementLevel}
                prefix="+"
              />
            </>
          )}
        </div>

        {/* Feedback Actions */}
        <div style={{ display: "flex", gap: 8, marginTop: 24 }}>
          {feedbackState === "idle" ? (
            <>
              <button className="btn btn-approve" onClick={() => setFeedbackState("approved")}>
                Approve
              </button>
              <button className="btn btn-reject" onClick={() => setFeedbackState("rejected")}>
                Reject
              </button>
              <button className="btn btn-flag" onClick={() => setFeedbackState("flagged")}>
                Flag
              </button>
            </>
          ) : (
            <span
              className="badge"
              style={{
                background:
                  feedbackState === "approved"
                    ? "var(--color-accent-muted)"
                    : feedbackState === "rejected"
                    ? "var(--color-error-muted)"
                    : "var(--color-warning-muted)",
                color:
                  feedbackState === "approved"
                    ? "var(--color-accent)"
                    : feedbackState === "rejected"
                    ? "var(--color-error)"
                    : "var(--color-warning)",
                padding: "4px 10px",
                fontSize: 12,
              }}
            >
              {feedbackState === "approved"
                ? "Approved"
                : feedbackState === "rejected"
                ? "Rejected"
                : "Flagged for review"}
            </span>
          )}
        </div>
      </div>

      {/* Right: Context */}
      <div>
        <h4 style={{ marginBottom: 16, color: "var(--color-text-muted)" }}>Context</h4>
        <div className="context-block">
          {d.context_before}{" "}
          <span className="highlight-original">{d.original_word}</span>{" "}
          {d.action === "replaced" && d.replacement_word && (
            <>
              <span className="highlight-replacement">{d.replacement_word}</span>{" "}
            </>
          )}
          {d.context_after}
        </div>

        <div
          style={{
            marginTop: 16,
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "8px 24px",
            fontSize: 12,
          }}
        >
          <MetaItem label="Domain" value={d.domain} />
          <MetaItem label="Quality" value={d.audio_quality} />
          <MetaItem label="Session" value={d.session_id} />
          <MetaItem label="Position" value={`word ${d.position}`} />
        </div>
      </div>
    </div>
  );
}

function ScoreBar({
  label,
  value,
  max,
  level,
  prefix = "",
}: {
  label: string;
  value: number;
  max: number;
  level: "low" | "medium" | "high";
  prefix?: string;
}) {
  const pct = Math.min((value / max) * 100, 100);
  return (
    <div className="score-bar">
      <span className="score-bar-label">{label}</span>
      <div className="score-bar-track">
        <div className="score-bar-fill" data-level={level} style={{ width: `${pct}%` }} />
      </div>
      <span className="score-bar-value">
        {prefix}
        {value.toFixed(2)}
      </span>
    </div>
  );
}

function MetaItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span style={{ color: "var(--color-text-faint)" }}>{label}: </span>
      <span style={{ color: "var(--color-text-secondary)", fontFamily: "var(--font-mono)" }}>
        {value}
      </span>
    </div>
  );
}
