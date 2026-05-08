"use client";

/**
 * Financial profile summary + actionable recommendations.
 */
export default function InsightsPanel({ profile = {}, recommendations = [] }) {
  const scores = profile.scores || {};

  const priorityColors = {
    high: "border-[var(--color-danger)]/30 bg-[var(--color-danger)]/5",
    medium: "border-[var(--color-warning)]/30 bg-[var(--color-warning)]/5",
    low: "border-[var(--color-success)]/30 bg-[var(--color-success)]/5",
  };

  return (
    <div className="space-y-4">
      {/* Profile card */}
      <div className="glass-card p-6">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-[var(--color-text-muted)]">
            Financial Profile
          </h3>
          <a
            href="/insights"
            className="text-xs text-[var(--color-primary)] transition-colors hover:text-[var(--color-primary-light)]"
          >
            Full Insights →
          </a>
        </div>

        {/* Personality + Risk */}
        <div className="mb-5 flex flex-wrap gap-3">
          <span
            className="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold"
            style={{ background: "var(--gradient-primary)", color: "white" }}
          >
            🧠 {(profile.personality || "unknown").replace(/_/g, " ").toUpperCase()}
          </span>
          <span
            className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold ${
              profile.risk_level === "low"
                ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
                : profile.risk_level === "moderate"
                ? "border-yellow-500/30 bg-yellow-500/10 text-yellow-400"
                : "border-red-500/30 bg-red-500/10 text-red-400"
            }`}
          >
            ⚡ Risk: {(profile.risk_level || "unknown").toUpperCase()}
          </span>
        </div>

        {/* Score bars */}
        <div className="space-y-3">
          {[
            { key: "overall", label: "Overall", color: "#6366f1" },
            { key: "savings", label: "Savings", color: "#10b981" },
            { key: "spending_control", label: "Control", color: "#06b6d4" },
            { key: "consistency", label: "Consistency", color: "#f59e0b" },
            { key: "diversification", label: "Diversity", color: "#8b5cf6" },
          ].map(({ key, label, color }) => (
            <div key={key}>
              <div className="mb-1 flex justify-between text-xs">
                <span className="text-[var(--color-text-secondary)]">{label}</span>
                <span className="font-medium text-[var(--color-text)]">{scores[key] ?? 0}</span>
              </div>
              <div className="h-1.5 rounded-full bg-[var(--color-surface-2)]">
                <div
                  className="h-full rounded-full transition-all duration-700 ease-out"
                  style={{
                    width: `${scores[key] ?? 0}%`,
                    backgroundColor: color,
                  }}
                />
              </div>
            </div>
          ))}
        </div>

        {/* Strengths & Weaknesses */}
        {((profile.strengths?.length > 0) || (profile.weaknesses?.length > 0)) && (
          <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2">
            {profile.strengths?.length > 0 && (
              <div>
                <p className="mb-2 text-xs font-medium text-[var(--color-success)]">💪 Strengths</p>
                <ul className="space-y-1">
                  {profile.strengths.map((s, i) => (
                    <li key={i} className="text-xs text-[var(--color-text-secondary)]">• {s}</li>
                  ))}
                </ul>
              </div>
            )}
            {profile.weaknesses?.length > 0 && (
              <div>
                <p className="mb-2 text-xs font-medium text-[var(--color-danger)]">⚠️ Weaknesses</p>
                <ul className="space-y-1">
                  {profile.weaknesses.map((w, i) => (
                    <li key={i} className="text-xs text-[var(--color-text-secondary)]">• {w}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-[var(--color-text-muted)]">
            Recommendations
          </h3>
          <div className="space-y-3">
            {recommendations.map((rec, i) => (
              <div
                key={i}
                className={`rounded-xl border p-4 transition-colors ${
                  priorityColors[rec.priority] || priorityColors.medium
                }`}
              >
                <div className="flex items-start gap-3">
                  <span className="mt-0.5 text-lg">{rec.icon}</span>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-[var(--color-text)]">{rec.title}</p>
                    <p className="mt-1 text-xs leading-relaxed text-[var(--color-text-secondary)]">
                      {rec.description}
                    </p>
                    {rec.potential_savings && (
                      <p className="mt-2 text-xs font-medium text-[var(--color-success)]">
                        💰 Save ~₹{rec.potential_savings.toLocaleString("en-IN", { minimumFractionDigits: 2 })}/mo
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
