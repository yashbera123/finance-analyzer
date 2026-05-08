"use client";

import { formatDate, formatCurrency } from "@/lib/utils";

/**
 * Anomaly alerts — flagged unusual transactions.
 */
export default function AnomalyAlerts({ anomalies = [] }) {
  if (!anomalies.length) {
    return (
      <div className="glass-card flex items-center gap-4 p-6">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-500/10 text-2xl">✅</div>
        <div>
          <p className="text-sm font-medium text-[var(--color-text)]">No anomalies detected</p>
          <p className="text-xs text-[var(--color-text-muted)]">Your spending patterns look consistent</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {anomalies.map((a, i) => (
        <div
          key={i}
          className="glass-card border border-red-500/15 transition-all duration-300 hover:border-red-500/30"
        >
          <div className="flex items-start gap-4 p-5">
            {/* Severity indicator */}
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-red-500/10 text-2xl">
              ⚠️
            </div>

            {/* Details */}
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <h4 className="text-sm font-semibold text-[var(--color-text)]">{a.description}</h4>
                <span className="rounded bg-red-500/10 px-2 py-0.5 text-xs font-medium text-red-400">
                  Anomaly
                </span>
              </div>

              <p className="mt-1.5 text-sm text-[var(--color-text-secondary)]">{a.reason}</p>

              <div className="mt-3 flex flex-wrap items-center gap-4 text-xs text-[var(--color-text-muted)]">
                <span className="flex items-center gap-1">
                  📅 {a.date ? formatDate(a.date) : "Unknown date"}
                </span>
                <span className="flex items-center gap-1">
                  💳 {formatCurrency(a.amount)}
                </span>
                {a.category && (
                  <span className="flex items-center gap-1">
                    📂 {a.category}
                  </span>
                )}
                <span className="flex items-center gap-1" title="Anomaly score (lower = more anomalous)">
                  📉 Score: {a.score?.toFixed(3)}
                </span>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
