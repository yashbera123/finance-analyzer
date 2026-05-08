"use client";

const PERSONALITY_META = {
  frugal:      { emoji: "🧊", color: "#10b981", bg: "rgba(16,185,129,0.1)",  tagline: "Disciplined Saver" },
  balanced:    { emoji: "⚖️", color: "#6366f1", bg: "rgba(99,102,241,0.1)", tagline: "Healthy Balance" },
  comfortable: { emoji: "☀️", color: "#f59e0b", bg: "rgba(245,158,11,0.1)", tagline: "Comfortable Spender" },
  impulsive:   { emoji: "⚡", color: "#ef4444", bg: "rgba(239,68,68,0.1)",  tagline: "Impulsive Patterns" },
  overspender: { emoji: "🔥", color: "#dc2626", bg: "rgba(220,38,38,0.1)", tagline: "Over Budget" },
};

const RISK_META = {
  low:      { color: "#10b981", label: "Low Risk" },
  moderate: { color: "#f59e0b", label: "Moderate Risk" },
  high:     { color: "#ef4444", label: "High Risk" },
  critical: { color: "#dc2626", label: "Critical Risk" },
};

/**
 * Full-page behavior profile card with personality hero, scores, and strengths/weaknesses.
 */
export default function ProfileCard({ profile }) {
  if (!profile) return null;

  const p = profile;
  const personality = PERSONALITY_META[p.personality] || PERSONALITY_META.balanced;
  const risk = RISK_META[p.risk_level] || RISK_META.moderate;
  const scores = p.scores || {};

  const scoreItems = [
    { key: "overall",          label: "Overall Health",      color: "#6366f1", icon: "📊" },
    { key: "savings",          label: "Savings Discipline",  color: "#10b981", icon: "💰" },
    { key: "spending_control", label: "Spending Control",    color: "#06b6d4", icon: "🎯" },
    { key: "consistency",      label: "Monthly Consistency", color: "#f59e0b", icon: "📈" },
    { key: "diversification",  label: "Diversification",     color: "#8b5cf6", icon: "🎨" },
  ];

  return (
    <div className="space-y-6">
      {/* Hero — Personality */}
      <div className="glass-card overflow-hidden">
        <div className="relative p-8" style={{ background: personality.bg }}>
          <div className="flex flex-col items-center text-center sm:flex-row sm:text-left sm:gap-6">
            <div
              className="flex h-24 w-24 shrink-0 items-center justify-center rounded-3xl text-5xl"
              style={{ background: `${personality.color}20` }}
            >
              {personality.emoji}
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-widest" style={{ color: personality.color }}>
                Your Financial Personality
              </p>
              <h2 className="mt-1 text-3xl font-bold capitalize text-[var(--color-text)]">
                {p.personality?.replace(/_/g, " ")}
              </h2>
              <p className="mt-1 text-sm text-[var(--color-text-muted)]">{personality.tagline}</p>
              <p className="mt-3 max-w-lg text-sm leading-relaxed text-[var(--color-text-secondary)]">
                {p.personality_description}
              </p>
            </div>
          </div>

          {/* Risk badge */}
          <div className="mt-6 flex items-center gap-3 sm:mt-0 sm:absolute sm:right-8 sm:top-8">
            <span
              className="inline-flex items-center gap-2 rounded-full border px-4 py-2 text-sm font-semibold"
              style={{ borderColor: `${risk.color}40`, color: risk.color, background: `${risk.color}10` }}
            >
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full opacity-75" style={{ backgroundColor: risk.color }} />
                <span className="relative inline-flex h-2 w-2 rounded-full" style={{ backgroundColor: risk.color }} />
              </span>
              {risk.label}
            </span>
          </div>
        </div>
      </div>

      {/* Scores */}
      <div className="glass-card p-6">
        <h3 className="mb-5 text-sm font-semibold uppercase tracking-wider text-[var(--color-text-muted)]">
          Financial Health Scores
        </h3>
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-5">
          {scoreItems.map(({ key, label, color, icon }) => {
            const val = scores[key] ?? 0;
            return (
              <div key={key} className="text-center">
                {/* Circular progress */}
                <div className="relative mx-auto h-24 w-24">
                  <svg className="h-24 w-24 -rotate-90" viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="42" fill="none" stroke="var(--color-surface-2)" strokeWidth="8" />
                    <circle
                      cx="50" cy="50" r="42" fill="none"
                      stroke={color} strokeWidth="8" strokeLinecap="round"
                      strokeDasharray={`${val * 2.64} 264`}
                      className="transition-all duration-1000 ease-out"
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-lg">{icon}</span>
                    <span className="text-lg font-bold text-[var(--color-text)]">{val}</span>
                  </div>
                </div>
                <p className="mt-2 text-xs text-[var(--color-text-secondary)]">{label}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        {p.strengths?.length > 0 && (
          <div className="glass-card p-6">
            <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-[var(--color-success)]">
              <span>💪</span> Strengths
            </h3>
            <ul className="space-y-3">
              {p.strengths.map((s, i) => (
                <li key={i} className="flex items-start gap-3 rounded-lg bg-emerald-500/5 p-3">
                  <span className="mt-0.5 text-emerald-400">✓</span>
                  <span className="text-sm text-[var(--color-text-secondary)]">{s}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
        {p.weaknesses?.length > 0 && (
          <div className="glass-card p-6">
            <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-[var(--color-danger)]">
              <span>⚠️</span> Areas to Improve
            </h3>
            <ul className="space-y-3">
              {p.weaknesses.map((w, i) => (
                <li key={i} className="flex items-start gap-3 rounded-lg bg-red-500/5 p-3">
                  <span className="mt-0.5 text-red-400">!</span>
                  <span className="text-sm text-[var(--color-text-secondary)]">{w}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
